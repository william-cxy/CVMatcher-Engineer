import sys
import os
import json
import threading
import time
import traceback
from datetime import datetime
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QPushButton, QTextEdit, QLineEdit, QComboBox, 
    QProgressBar, QFileDialog, QMessageBox, QFrame, QListWidget,
    QSplitter, QGroupBox, QGridLayout, QCheckBox, QScrollArea,
    QDialog, QFormLayout, QListWidgetItem, QListView
)
from PySide6.QtCore import Qt, QTimer, Signal, Slot, QSize, QThread
from PySide6.QtGui import QFont, QColor, QPalette, QIcon, QTextCursor, QFontDatabase

# 尝试导入文件处理相关库
try:
    import PyPDF2
    PDF_SUPPORT = True
except ImportError:
    PDF_SUPPORT = False

try:
    import docx
    DOCX_SUPPORT = True
except ImportError:
    DOCX_SUPPORT = False

try:
    import pandas as pd
    EXCEL_SUPPORT = True
except ImportError:
    EXCEL_SUPPORT = False

# 尝试导入OpenAI客户端
try:
    from openai import OpenAI
    OPENAI_SUPPORT = True
except ImportError:
    OPENAI_SUPPORT = False

class SaveJobDialog(QDialog):
    """保存职位对话框"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("保存职位信息")
        self.setMinimumWidth(300)
        
        layout = QFormLayout(self)
        
        self.job_name_input = QLineEdit()
        layout.addRow("岗位名称:", self.job_name_input)
        
        self.company_name_input = QLineEdit()
        layout.addRow("公司名称:", self.company_name_input)
        
        button_layout = QHBoxLayout()
        self.save_button = QPushButton("保存")
        self.save_button.clicked.connect(self.accept)
        self.cancel_button = QPushButton("取消")
        self.cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.cancel_button)
        layout.addRow("", button_layout)
    
    def get_job_info(self):
        """获取职位信息"""
        return {
            "name": self.job_name_input.text(),
            "company": self.company_name_input.text()
        }

class LoadJobDialog(QDialog):
    """加载职位对话框"""
    def __init__(self, job_history, parent=None):
        super().__init__(parent)
        self.setWindowTitle("加载历史职位")
        self.setMinimumWidth(400)
        self.setMinimumHeight(300)
        
        layout = QVBoxLayout(self)
        
        self.job_list = QListWidget()
        self.job_list.itemDoubleClicked.connect(self.accept)
        layout.addWidget(self.job_list)
        
        # 添加历史职位到列表
        for job in job_history:
            item = QListWidgetItem(f"{job['name']} - {job['company']}")
            item.setData(Qt.UserRole, job)
            self.job_list.addItem(item)
        
        button_layout = QHBoxLayout()
        self.load_button = QPushButton("加载")
        self.load_button.clicked.connect(self.accept)
        self.cancel_button = QPushButton("取消")
        self.cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(self.load_button)
        button_layout.addWidget(self.cancel_button)
        layout.addLayout(button_layout)
    
    def get_selected_job(self):
        """获取选中的职位"""
        if self.job_list.currentItem():
            return self.job_list.currentItem().data(Qt.UserRole)
        return None

class AnalysisWorker(QThread):
    """分析工作线程"""
    progress_updated = Signal(int)
    analysis_completed = Signal(str)
    analysis_error = Signal(str)
    
    def __init__(self, job_info, resume_info, api_key, model_name):
        super().__init__()
        self.job_info = job_info
        self.resume_info = resume_info
        self.api_key = api_key
        self.model_name = model_name
        self.is_running = True
    
    def run(self):
        try:
            # 构建提示词
            prompt = f"""
            请详细分析以下岗位信息和简历信息的匹配程度，特别注重以下内容：

            1. 核心技术栈匹配度：
               - 重点关注岗位所需的关键技术和工具
               - 只要简历中提及了相关技术即可，不要求详细展开
               - 考虑替代性技术和可迁移技能

            2. 职位方向匹配性：
               - 评估候选人过往工作方向与目标职位的匹配度
               - 区分相似技术栈但不同职位方向（如DevOps vs SRE，自动化运维 vs 云计算平台工程师）
               - 考虑岗位实际工作内容、项目职责与候选人经验的一致性
               - 评分修正规则：如果最近2-3年在知名公司（大厂、行业有影响力的公司、知名的初创企业、公认技术能力强的企业等）具有高匹配工作经验，则对扣分进行60%的衰减。例如：如果原始评分为100-20=80分，修正后为100-(20*0.6)=88分

            3. 相关经验时间线分析：
               - 请分别分析候选人职业生涯中的每一段工作经历，判断每段经历与目标岗位的相关性
               - 对每段经历单独标注为"高度相关"、"部分相关"或"不相关"
               - 计算相关经验（高度相关+部分相关）占总工作经验的百分比
               - 考虑相关经验在时间线上的位置：
                 * 如果最近的经历相关性高，这是有利因素
                 * 如果最近的经历不相关，但早期有相关经历，这是不利因素
                 * 如果早期经历不相关，需要额外减分（支付"不相关经验成本"）
               - 评分修正规则：如果最近2-3年在知名公司具有高匹配工作经验，则对扣分进行60%的衰减。例如：如果原始评分为100-20=80分，修正后为100-(20*0.6)=88分

            4. 项目复杂度和难度：
               - 评估简历中项目的复杂程度
               - 如果使用相同技术，更复杂、难度更高的项目应当获得更高评分
               - 考虑项目规模、挑战性和完成的职责

            5. 专业能力评估：
               - 关注核心专业技能而非次要或辅助技能
               - 对于简历书写不够详细但方向匹配的情况给予适当容忍

            分析输出格式：
            1. 首先列出候选人的工作经历时间线，并对每段经历的相关性进行明确判断
            2. 计算相关经验占比及其在时间线上的分布
            3. 给出核心技术栈匹配度评分(0-100)
            4. 给出职位方向匹配性评分(0-100)
            5. 给出相关经验时间线评分(0-100)
            6. 给出项目复杂度和专业能力匹配评分(0-100)
            7. 根据以上各项计算总体匹配分数(0-100)

            最终推荐：
            1. 明确表明这位候选人是否适合进一步推进（面试/下一轮），使用明确的推荐级别标记：
               - 【强烈推荐】- 95分及以上，非常适合，应立即安排面试
               - 【推荐】- 80-94分，适合，值得进一步考虑
               - 【中性/待定】- 60-79分，存在疑问点，需要更多信息
               - 【不推荐】- 40-59分，不太适合，但可能有部分相关背景
               - 【完全不推荐】- 低于40分，明显不合适，方向错误
            2. 如果不推荐推进或匹配度较低，请用非技术人员(HR/猎头)能理解的语言说明方向偏差
            3. 提供1-2句建议，帮助招聘人员进一步搜寻更合适的候选人

            ==============================================
            推荐给客户的评语（独立部分，且仅在评分80分以上触发）：
            请单独提供一段不超过6点的正面评价，每点评价大于20字避免过于精简，用于向客户推荐候选人。这部分评价应该：
            1. 完全独立于上述分析结果
            2. 以正面信息为主
            3. 包括以下方面（如果适用）：
               a. 学历优势
               b. 知名公司工作经验（如果工作方向高度匹配）
               c. 技术栈匹配性（针对岗位要求的技术栈）
               d. 其他优势
            4. 即使候选人在其他方面存在不足，这部分评价也应聚焦于其优势，除非不足的地方可以自圆其说且很容易被企业方接受，否则不要冒险提出不足之处。

            ==============================================
            岗位信息：
            {self.job_info}
            
            简历信息：
            {self.resume_info}
            """
            
            # 根据选择的模型确定API端点和进度更新速度
            if self.model_name == "DeepSeek R1":
                model = "deepseek-reasoner"
                total_steps = 90  # R1模型大约需要90秒
            else:  # DeepSeek V3
                model = "deepseek-chat"
                total_steps = 60  # V3模型大约需要60秒
            
            # 调用DeepSeek API
            client = OpenAI(
                api_key=self.api_key,
                base_url="https://api.deepseek.com/v1",
                http_client=None  # 显式设置为 None 以避免 proxies 错误
            )
            
            # 发送初始进度
            self.progress_updated.emit(0)
            
            # 启动进度更新定时器
            start_time = time.time()
            last_progress = 0
            api_response_received = False
            api_result = None
            
            # 在单独的线程中调用API
            def call_api():
                nonlocal api_response_received, api_result
                try:
                    response = client.chat.completions.create(
                        model=model,
                        messages=[
                            {"role": "system", "content": "你是一个专业的技术招聘专家，精通各类编程语言和技术栈，擅长评估工程师简历与技术岗位的匹配度。"},
                            {"role": "user", "content": prompt}
                        ],
                        stream=False
                    )
                    
                    # 获取分析结果
                    result = response.choices[0].message.content
                    
                    # 标记已收到API响应
                    api_response_received = True
                    api_result = result
                    
                    # 更新进度到100%并发送结果
                    if self.is_running:
                        self.progress_updated.emit(100)
                        self.analysis_completed.emit(result)
                except Exception as e:
                    # 只有在分析未被停止时才发送错误
                    if self.is_running:
                        self.analysis_error.emit(str(e))
            
            # 启动API调用线程
            api_thread = threading.Thread(target=call_api)
            api_thread.daemon = True
            api_thread.start()
            
            # 更新进度
            while self.is_running and not api_response_received:
                elapsed_time = time.time() - start_time
                if elapsed_time >= total_steps:
                    if not api_response_received:
                        self.progress_updated.emit(95)
                    break
                
                current_progress = min(95, int((elapsed_time / total_steps) * 95))
                if current_progress > last_progress:
                    last_progress = current_progress
                    self.progress_updated.emit(current_progress)
                
                time.sleep(0.05)  # 每50毫秒更新一次
            
            # 等待API线程完成
            api_thread.join(timeout=1)
            
        except Exception as e:
            self.analysis_error.emit(str(e))
    
    def stop(self):
        """停止分析"""
        self.is_running = False
        # 这里可以添加向DeepSeek发送取消请求的代码
        # 但由于API调用是在单独的线程中，我们只能标记停止，无法直接取消请求

class ResumeMatchingApp(QMainWindow):
    """简历匹配应用主窗口"""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("简历匹配分析工具")
        self.setMinimumSize(1000, 700)
        
        # 设置苹果风格
        self.setup_apple_style()
        
        # 初始化变量
        self.job_file_path = ""
        self.resume_file_path = ""
        self.job_info = ""
        self.resume_info = ""
        self.analysis_worker = None
        self.settings = self.load_settings()
        self.job_history = self.load_job_history()
        
        # 创建主布局
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # 创建分割器
        splitter = QSplitter(Qt.Vertical)
        main_layout.addWidget(splitter)
        
        # 上半部分：输入区域
        top_widget = QWidget()
        top_layout = QHBoxLayout(top_widget)
        top_layout.setContentsMargins(0, 0, 0, 0)
        top_layout.setSpacing(15)
        
        # 左侧：岗位信息
        job_group = QGroupBox("岗位信息")
        job_layout = QVBoxLayout(job_group)
        job_layout.setContentsMargins(15, 15, 15, 15)
        job_layout.setSpacing(10)
        
        # 将所有按钮放在同一行
        job_buttons_layout = QHBoxLayout()
        
        # 文件选择部分
        self.job_file_label = QLabel("未选择文件")
        self.job_file_label.setStyleSheet("color: #666;")
        self.job_file_label.setMinimumWidth(150)
        job_file_btn = QPushButton("选择岗位文件")
        job_file_btn.setFixedWidth(100)
        job_file_btn.clicked.connect(self.select_job_file)
        
        # 保存和加载按钮
        self.save_job_btn = QPushButton("保存职位")
        self.save_job_btn.setFixedWidth(80)
        self.save_job_btn.clicked.connect(self.save_job)
        self.save_job_btn.setEnabled(False)  # 初始禁用，当有内容时启用
        
        self.load_job_btn = QPushButton("加载历史职位")
        self.load_job_btn.setFixedWidth(100)
        self.load_job_btn.clicked.connect(self.show_history_dialog)
        
        # 添加所有按钮到布局
        job_buttons_layout.addWidget(self.job_file_label)
        job_buttons_layout.addWidget(job_file_btn)
        job_buttons_layout.addWidget(self.save_job_btn)
        job_buttons_layout.addWidget(self.load_job_btn)
        job_buttons_layout.addStretch(1)  # 添加弹性空间
        
        job_layout.addLayout(job_buttons_layout)
        
        self.job_text = QTextEdit()
        self.job_text.setPlaceholderText("在此输入或粘贴岗位信息...")
        self.job_text.textChanged.connect(self.on_job_text_changed)
        job_layout.addWidget(self.job_text)
        
        top_layout.addWidget(job_group)
        
        # 右侧：简历信息
        resume_group = QGroupBox("简历信息")
        resume_layout = QVBoxLayout(resume_group)
        resume_layout.setContentsMargins(15, 15, 15, 15)
        resume_layout.setSpacing(10)
        
        resume_file_layout = QHBoxLayout()
        self.resume_file_label = QLabel("未选择文件")
        self.resume_file_label.setStyleSheet("color: #666;")
        resume_file_btn = QPushButton("选择简历文件")
        resume_file_btn.setFixedWidth(120)
        resume_file_btn.clicked.connect(self.select_resume_file)
        resume_file_layout.addWidget(self.resume_file_label)
        resume_file_layout.addWidget(resume_file_btn)
        resume_layout.addLayout(resume_file_layout)
        
        self.resume_text = QTextEdit()
        self.resume_text.setPlaceholderText("在此输入或粘贴简历信息...")
        resume_layout.addWidget(self.resume_text)
        
        top_layout.addWidget(resume_group)
        
        # 设置左右两侧的宽度比例
        top_layout.setStretch(0, 1)
        top_layout.setStretch(1, 1)
        
        # 中间部分：控制面板
        control_widget = QWidget()
        control_layout = QHBoxLayout(control_widget)
        control_layout.setContentsMargins(0, 0, 0, 0)
        control_layout.setSpacing(15)
        
        # API设置
        api_group = QGroupBox("API设置")
        api_layout = QGridLayout(api_group)
        api_layout.setContentsMargins(15, 15, 15, 15)
        api_layout.setSpacing(10)
        
        api_layout.addWidget(QLabel("API密钥:"), 0, 0)
        
        # 创建API密钥输入框和切换按钮的容器
        api_key_container = QHBoxLayout()
        api_key_container.setContentsMargins(0, 0, 0, 0)
        api_key_container.setSpacing(5)
        
        self.api_key_input = QLineEdit()
        self.api_key_input.setEchoMode(QLineEdit.Password)
        self.api_key_input.setText(self.settings.get("api_key", ""))
        self.api_key_input.setPlaceholderText("请输入DeepSeek API密钥（在DeepSeek官网申请）")
        api_key_container.addWidget(self.api_key_input)
        
        # 添加显示/隐藏API密钥的按钮
        self.toggle_api_key_btn = QPushButton()
        self.toggle_api_key_btn.setFixedSize(30, 30)  # 增大按钮尺寸
        self.toggle_api_key_btn.setCheckable(True)
        self.toggle_api_key_btn.clicked.connect(self.toggle_api_key_visibility)
        self.toggle_api_key_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                border-radius: 15px;
                font-size: 16px;
                padding: 0;
                margin: 0;
            }
            QPushButton:checked {
                background-color: #e0e0e0;
            }
            QPushButton:hover {
                background-color: #f0f0f0;
            }
        """)
        self.toggle_api_key_btn.setText("👁‍🗨")  # 默认显示闭眼图标
        api_key_container.addWidget(self.toggle_api_key_btn)
        
        api_layout.addLayout(api_key_container, 0, 1)
        
        api_layout.addWidget(QLabel("选择模型:"), 1, 0)
        self.model_combo = QComboBox()
        self.model_combo.addItems(["DeepSeek R1", "DeepSeek V3"])
        self.model_combo.setCurrentText(self.settings.get("model", "DeepSeek R1"))
        
        # 创建并设置列表视图
        list_view = QListView()
        self.model_combo.setView(list_view)
        
        # 设置样式
        self.model_combo.setStyleSheet("""
            QComboBox {
                border: 1px solid #e0e0e0;
                border-radius: 6px;
                padding: 8px;
                background-color: white;
                min-height: 20px;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #333;
                margin-right: 5px;
            }
            QListView {
                border: 1px solid #e0e0e0;
                background-color: white;
                outline: none;
            }
            QListView::item {
                padding: 8px;
                border: none;
                background-color: white;
                color: black;
            }
            QListView::item:hover {
                background-color: #007AFF;
                color: white;
            }
            QListView::item:selected {
                background-color: #007AFF;
                color: white;
            }
        """)
        
        api_layout.addWidget(self.model_combo, 1, 1)
        
        # 确保API设置组在最上层
        api_group.raise_()
        
        control_layout.addWidget(api_group)
        
        # 操作按钮
        button_group = QGroupBox("操作")
        button_layout = QHBoxLayout(button_group)
        button_layout.setContentsMargins(15, 15, 15, 15)
        button_layout.setSpacing(10)
        
        self.analyze_btn = QPushButton("开始分析")
        self.analyze_btn.clicked.connect(self.start_analysis)
        button_layout.addWidget(self.analyze_btn)
        
        self.stop_btn = QPushButton("停止分析")
        self.stop_btn.setEnabled(False)
        self.stop_btn.clicked.connect(self.stop_analysis)
        button_layout.addWidget(self.stop_btn)
        
        self.save_btn = QPushButton("保存结果")
        self.save_btn.setEnabled(False)
        self.save_btn.clicked.connect(self.save_results)
        button_layout.addWidget(self.save_btn)
        
        control_layout.addWidget(button_group)
        
        # 进度条
        progress_group = QGroupBox("进度")
        progress_layout = QVBoxLayout(progress_group)
        progress_layout.setContentsMargins(15, 15, 15, 15)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        progress_layout.addWidget(self.progress_bar)
        
        control_layout.addWidget(progress_group)
        
        # 下半部分：分析结果
        result_group = QGroupBox("分析结果")
        result_layout = QVBoxLayout(result_group)
        result_layout.setContentsMargins(15, 15, 15, 15)
        
        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        result_layout.addWidget(self.result_text)
        
        # 添加所有组件到分割器
        splitter.addWidget(top_widget)
        splitter.addWidget(control_widget)
        splitter.addWidget(result_group)
        
        # 设置分割器的初始大小
        splitter.setSizes([300, 150, 350])
    
    def setup_apple_style(self):
        """设置苹果风格的界面"""
        # 设置应用字体
        app_font = QFont("SF Pro Text", 12)
        QApplication.setFont(app_font)
        
        # 设置窗口样式
        self.setStyleSheet("""
            QMainWindow {
                background-color: #ffffff;
            }
            QGroupBox {
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                margin-top: 1em;
                font-weight: bold;
                background-color: #f9f9f9;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
                color: #333333;
            }
            QPushButton {
                background-color: #007AFF;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 6px 12px;
                font-weight: bold;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #0069D9;
            }
            QPushButton:disabled {
                background-color: #CCCCCC;
            }
            QLineEdit, QTextEdit {
                border: 1px solid #e0e0e0;
                border-radius: 6px;
                padding: 8px;
                background-color: white;
            }
            QProgressBar {
                border: 1px solid #e0e0e0;
                border-radius: 6px;
                text-align: center;
                background-color: #f5f5f5;
            }
            QProgressBar::chunk {
                background-color: #007AFF;
                border-radius: 5px;
            }
            QLabel {
                color: #333333;
            }
            QScrollBar:vertical {
                border: none;
                background: #f0f0f0;
                width: 10px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: #c0c0c0;
                min-height: 20px;
                border-radius: 5px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)
    
    def on_job_text_changed(self):
        """岗位信息文本变化时触发"""
        # 当岗位信息有内容时，启用保存职位按钮
        self.save_job_btn.setEnabled(bool(self.job_text.toPlainText().strip()))
    
    def save_job(self):
        """保存职位信息"""
        job_content = self.job_text.toPlainText().strip()
        if not job_content:
            QMessageBox.warning(self, "警告", "请先输入岗位信息")
            return
        
        dialog = SaveJobDialog(self)
        if dialog.exec() == QDialog.Accepted:
            job_info = dialog.get_job_info()
            job_name = job_info["name"]
            company_name = job_info["company"]
            
            if not job_name or not company_name:
                QMessageBox.warning(self, "警告", "请输入岗位名称和公司名称")
                return
            
            # 添加到历史记录
            self.job_history.append({
                "name": job_name,
                "company": company_name,
                "content": job_content,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
            
            # 保存到文件
            self.save_job_history()
            
            QMessageBox.information(self, "成功", f"职位 '{job_name} - {company_name}' 已保存")
    
    def show_history_dialog(self):
        """显示历史职位列表对话框"""
        dialog = QDialog(self)
        dialog.setWindowTitle("历史职位列表")
        dialog.setMinimumWidth(400)
        
        layout = QVBoxLayout()
        
        # 创建列表控件
        list_widget = QListWidget()
        list_widget.setSelectionMode(QListWidget.SingleSelection)
        
        # 加载历史职位
        try:
            with open("job_history.json", "r", encoding="utf-8") as f:
                history = json.load(f)
                for job in history:
                    # 使用职位名称-公司名称作为显示文本
                    display_text = f"{job.get('name', '未命名职位')} - {job.get('company', '未知公司')}"
                    item = QListWidgetItem(display_text)
                    item.setData(Qt.UserRole, job)  # 存储完整的职位信息
                    list_widget.addItem(item)
        except (FileNotFoundError, json.JSONDecodeError):
            pass
        
        layout.addWidget(list_widget)
        
        # 创建按钮布局
        button_layout = QHBoxLayout()
        
        # 加载按钮
        load_btn = QPushButton("加载选中职位")
        load_btn.clicked.connect(lambda: self.load_history_job(list_widget.currentItem(), dialog))
        button_layout.addWidget(load_btn)
        
        # 删除按钮
        delete_btn = QPushButton("删除选中职位")
        delete_btn.clicked.connect(lambda: self.delete_history_job(list_widget))
        button_layout.addWidget(delete_btn)
        
        # 取消按钮
        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(dialog.reject)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
        dialog.setLayout(layout)
        dialog.exec()
    
    def delete_history_job(self, list_widget):
        """删除选中的历史职位"""
        current_item = list_widget.currentItem()
        if not current_item:
            QMessageBox.warning(self, "提示", "请先选择要删除的职位")
            return
        
        # 从列表控件中移除
        row = list_widget.row(current_item)
        list_widget.takeItem(row)
        
        # 更新历史记录文件
        try:
            with open("job_history.json", "r", encoding="utf-8") as f:
                history = json.load(f)
            
            # 删除对应的职位信息
            if 0 <= row < len(history):
                del history[row]
            
            # 保存更新后的历史记录
            with open("job_history.json", "w", encoding="utf-8") as f:
                json.dump(history, f, ensure_ascii=False, indent=4)
        except Exception as e:
            QMessageBox.warning(self, "错误", f"删除历史记录失败：{str(e)}")
    
    def select_job_file(self):
        """选择岗位文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            "选择岗位文件", 
            "", 
            "所有文件 (*.*);;文本文件 (*.txt);;PDF文件 (*.pdf);;Word文件 (*.docx);;Excel文件 (*.xlsx *.xls)"
        )
        if file_path:
            self.job_file_path = file_path
            self.job_file_label.setText(os.path.basename(file_path))
            self.load_job_file()
    
    def select_resume_file(self):
        """选择简历文件"""
        # 获取上次选择的文件夹路径
        last_dir = os.path.dirname(self.resume_file_path) if self.resume_file_path else ""
        
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            "选择简历文件", 
            last_dir,  # 使用上次的文件夹路径
            "所有文件 (*.*);;文本文件 (*.txt);;PDF文件 (*.pdf);;Word文件 (*.docx);;Excel文件 (*.xlsx *.xls)"
        )
        if file_path:
            self.resume_file_path = file_path
            self.resume_file_label.setText(os.path.basename(file_path))
            self.load_resume_file()
    
    def load_job_file(self):
        """加载岗位文件内容"""
        if not self.job_file_path:
            return
        
        try:
            file_ext = os.path.splitext(self.job_file_path)[1].lower()
            
            if file_ext == '.txt':
                with open(self.job_file_path, 'r', encoding='utf-8') as f:
                    self.job_info = f.read()
            elif file_ext == '.pdf' and PDF_SUPPORT:
                self.job_info = self.read_pdf(self.job_file_path)
            elif file_ext == '.docx' and DOCX_SUPPORT:
                self.job_info = self.read_docx(self.job_file_path)
            elif file_ext in ['.xlsx', '.xls'] and EXCEL_SUPPORT:
                self.job_info = self.read_excel(self.job_file_path)
            else:
                QMessageBox.warning(self, "警告", f"不支持的文件类型: {file_ext}")
                return
            
            self.job_text.setText(self.job_info)
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"加载岗位文件失败: {str(e)}")
    
    def load_resume_file(self):
        """加载简历文件内容"""
        if not self.resume_file_path:
            return
        
        try:
            file_ext = os.path.splitext(self.resume_file_path)[1].lower()
            
            if file_ext == '.txt':
                with open(self.resume_file_path, 'r', encoding='utf-8') as f:
                    self.resume_info = f.read()
            elif file_ext == '.pdf' and PDF_SUPPORT:
                self.resume_info = self.read_pdf(self.resume_file_path)
            elif file_ext == '.docx' and DOCX_SUPPORT:
                self.resume_info = self.read_docx(self.resume_file_path)
            elif file_ext in ['.xlsx', '.xls'] and EXCEL_SUPPORT:
                self.resume_info = self.read_excel(self.resume_file_path)
            else:
                QMessageBox.warning(self, "警告", f"不支持的文件类型: {file_ext}")
                return
            
            self.resume_text.setText(self.resume_info)
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"加载简历文件失败: {str(e)}")
    
    def read_pdf(self, file_path):
        """读取PDF文件内容"""
        text = ""
        with open(file_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                text += page.extract_text() + "\n"
        return text
    
    def read_docx(self, file_path):
        """读取Word文件内容"""
        doc = docx.Document(file_path)
        text = ""
        for para in doc.paragraphs:
            text += para.text + "\n"
        return text
    
    def read_excel(self, file_path):
        """读取Excel文件内容"""
        df = pd.read_excel(file_path)
        return df.to_string()
    
    def start_analysis(self):
        """开始分析"""
        # 获取输入内容
        job_info = self.job_text.toPlainText()
        resume_info = self.resume_text.toPlainText()
        api_key = self.api_key_input.text()
        model_name = self.model_combo.currentText()
        
        # 验证输入
        if not job_info:
            QMessageBox.warning(self, "警告", "请输入岗位信息")
            return
        
        if not resume_info:
            QMessageBox.warning(self, "警告", "请输入简历信息")
            return
        
        if not api_key:
            QMessageBox.warning(self, "警告", "请输入API密钥")
            return
        
        # 验证API密钥
        try:
            client = OpenAI(
                api_key=api_key,
                base_url="https://api.deepseek.com/v1",
                http_client=None  # 显式设置为 None 以避免 proxies 错误
            )
            # 发送一个简单的请求来验证API密钥
            client.chat.completions.create(
                model="deepseek-chat",
                messages=[{"role": "user", "content": "test"}],
                max_tokens=1
            )
        except Exception as e:
            error_msg = str(e).lower()
            if "unauthorized" in error_msg or "invalid" in error_msg:
                QMessageBox.warning(
                    self,
                    "API密钥错误",
                    "您输入的API密钥无效。如果您还没有API密钥，可以前往 DeepSeek 开放平台官网申请。\n\n申请地址：https://platform.deepseek.com/"
                )
            else:
                QMessageBox.warning(
                    self,
                    "连接错误",
                    f"连接DeepSeek服务时出现错误，请检查网络连接或稍后重试。\n\n错误信息：{str(e)}"
                )
            return
        
        # 保存设置
        self.settings["api_key"] = api_key
        self.settings["model"] = model_name
        self.save_settings()
        
        # 禁用开始按钮，启用停止按钮
        self.analyze_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.save_btn.setEnabled(False)
        
        # 清空结果
        self.result_text.clear()
        
        # 创建并启动工作线程
        self.analysis_worker = AnalysisWorker(job_info, resume_info, api_key, model_name)
        self.analysis_worker.progress_updated.connect(self.update_progress)
        self.analysis_worker.analysis_completed.connect(self.analysis_complete)
        self.analysis_worker.analysis_error.connect(self.analysis_error)
        self.analysis_worker.start()
    
    def stop_analysis(self):
        """停止分析"""
        if self.analysis_worker and self.analysis_worker.isRunning():
            self.analysis_worker.stop()
            # 重置进度条
            self.progress_bar.setValue(0)
            # 恢复按钮状态
            self.analyze_btn.setEnabled(True)
            self.stop_btn.setEnabled(False)
    
    def update_progress(self, value):
        """更新进度条"""
        self.progress_bar.setValue(value)
    
    def analysis_complete(self, result):
        """分析完成"""
        # 直接显示API返回的原始结果
        self.result_text.setPlainText(result)
        
        # 恢复按钮状态
        self.analyze_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.save_btn.setEnabled(True)
    
    def analysis_error(self, error_msg):
        """分析错误"""
        QMessageBox.critical(self, "错误", f"分析过程中出错: {error_msg}")
        self.analyze_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
    
    def save_results(self):
        """保存分析结果"""
        if not self.result_text.toPlainText():
            QMessageBox.warning(self, "警告", "没有可保存的结果")
            return
        
        # 获取当前日期缩写
        date_str = datetime.now().strftime("%y%m%d")
        
        # 从岗位信息中提取职位名称
        job_info = self.job_text.toPlainText()
        job_title = "未知职位"
        for line in job_info.split('\n'):
            if "职位" in line or "岗位" in line:
                job_title = line.split('：')[-1].strip()
                break
        
        # 从简历信息中提取候选人姓名
        resume_info = self.resume_text.toPlainText()
        candidate_name = "未知候选人"
        for line in resume_info.split('\n'):
            if "姓名" in line:
                candidate_name = line.split('：')[-1].strip()
                break
        
        # 构建默认文件名
        default_filename = f"{job_title}_{candidate_name}_{date_str}.txt"
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, 
            "保存分析结果", 
            default_filename, 
            "文本文件 (*.txt)"
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(self.result_text.toPlainText())
                QMessageBox.information(self, "成功", "分析结果已保存")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"保存结果失败: {str(e)}")
    
    def load_settings(self):
        """加载设置"""
        try:
            # 获取应用程序包内的路径
            if getattr(sys, 'frozen', False):
                # 如果是打包后的应用
                app_path = os.path.dirname(sys.executable)
                settings_path = os.path.join(app_path, 'settings.json')
            else:
                # 如果是开发环境
                settings_path = 'settings.json'
            
            if os.path.exists(settings_path):
                with open(settings_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"加载设置失败: {str(e)}")
        return {}
    
    def save_settings(self):
        """保存设置"""
        try:
            # 获取应用程序包内的路径
            if getattr(sys, 'frozen', False):
                # 如果是打包后的应用
                app_path = os.path.dirname(sys.executable)
                settings_path = os.path.join(app_path, 'settings.json')
            else:
                # 如果是开发环境
                settings_path = 'settings.json'
            
            with open(settings_path, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, ensure_ascii=False, indent=4)
        except Exception as e:
            QMessageBox.warning(self, "警告", f"保存设置失败: {str(e)}")
            print(f"保存设置失败: {str(e)}")
    
    def load_job_history(self):
        """加载历史岗位记录"""
        try:
            if os.path.exists("job_history.json"):
                with open("job_history.json", "r", encoding="utf-8") as f:
                    return json.load(f)
        except Exception:
            pass
        return []
    
    def save_job_history(self):
        """保存历史岗位记录"""
        try:
            with open("job_history.json", "w", encoding="utf-8") as f:
                json.dump(self.job_history, f, ensure_ascii=False, indent=4)
        except Exception as e:
            QMessageBox.warning(self, "警告", f"保存历史记录失败: {str(e)}")
    
    def toggle_api_key_visibility(self):
        """切换API密钥的可见性"""
        if self.api_key_input.echoMode() == QLineEdit.Password:
            self.api_key_input.setEchoMode(QLineEdit.Normal)
            self.toggle_api_key_btn.setText("👁")  # 显示睁眼图标
        else:
            self.api_key_input.setEchoMode(QLineEdit.Password)
            self.toggle_api_key_btn.setText("👁‍🗨")  # 显示闭眼图标
    
    def load_history_job(self, current_item, dialog):
        """加载选中的历史职位"""
        if not current_item:
            QMessageBox.warning(self, "提示", "请先选择要加载的职位")
            return
        
        # 获取职位信息
        job = current_item.data(Qt.UserRole)
        if job:
            self.job_text.setText(job.get("content", ""))
            dialog.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ResumeMatchingApp()
    window.show()
    sys.exit(app.exec()) 