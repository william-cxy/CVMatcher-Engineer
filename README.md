# 工程师岗位智能匹配工具

基于OpenAI的简历与岗位智能匹配工具，支持批量导入简历，自动分析匹配度。

## 功能特点

- 支持PDF、Word格式简历导入
- 智能分析简历内容与岗位要求的匹配程度
- 批量处理多份简历
- 可视化展示匹配结果
- 支持自定义岗位要求
- 历史记录查看

## 系统要求

- macOS 10.13 或更高版本
- 无需安装Python环境，已打包为独立应用

## 安装说明

1. 下载最新版本的应用程序
2. 将 `Resume Matching App.app` 拖拽到应用程序文件夹
3. 首次运行时，如果提示安全警告，请在"系统偏好设置 > 安全性与隐私"中允许运行

## 使用方法

1. 启动应用程序
2. 导入简历文件（支持单个或批量导入）
3. 设置岗位要求
4. 点击分析按钮开始匹配
5. 查看分析结果

## 开发说明

本项目使用以下技术栈：

- Python
- PySide6 (Qt for Python)
- OpenAI API
- pandas
- PyPDF2
- python-docx

### 开发环境配置

```bash
# 安装依赖
pip install -r requirements.txt

# 运行开发版本
python resume_matching_app_pyside6.py
```

### 打包说明

使用py2app打包Mac应用：

```bash
# 安装py2app
pip install py2app

# 打包应用
python setup.py py2app --semi-standalone
```

## 注意事项

- 使用前请确保配置了有效的OpenAI API Key
- 请勿删除settings.json和job_history.json文件
- 建议定期备份历史数据

## 常见问题

### macOS 常见问题
Q: 提示"无法打开，因为来自身份不明的开发者"？
A: 这是 macOS 的安全机制。首次运行时，请按住 Control 键点击应用图标，选择"打开"。

## 技术支持

如果您在使用过程中遇到任何问题，请：
1. 查看上述常见问题
2. 在 GitHub Issues 中提交问题
3. 通过 Email 联系开发者

## 更新日志

### v1.0.0
- 首次发布
- 支持简历与职位匹配度分析
- 支持多种文件格式
- 支持历史职位管理 
