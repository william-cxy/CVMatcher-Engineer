# 工程师岗位智能匹配工具

基于OpenAI的简历智能匹配工具，帮助HR和招聘人员快速筛选合适的工程师简历。

## 主要功能

- 支持PDF和Word格式简历批量导入
- 基于OpenAI的智能匹配算法
- 可视化展示匹配结果
- 支持自定义岗位要求
- 历史记录管理

## Mac版本使用说明

1. 下载`Resume Matching App.app`
2. 将应用拖入Applications文件夹
3. 首次运行时在系统偏好设置中允许运行
4. 配置OpenAI API Key
5. 开始使用

## 开发环境

- Python 3.13
- PySide6
- OpenAI API
- pandas
- PyPDF2
- python-docx

## 本地开发

```bash
# 安装依赖
pip install -r requirements.txt

# 运行
python resume_matching_app_pyside6.py
```

## 打包发布

```bash
# 安装py2app
pip install py2app

# 打包Mac应用
python setup.py py2app --semi-standalone
```

## 注意事项

- 请确保配置了有效的OpenAI API Key
- 建议定期备份job_history.json
- 首次运行可能需要在系统偏好设置中允许运行

## 常见问题

### Windows 常见问题
Q: 运行时提示"Windows 已保护你的电脑"？
A: 这是因为应用没有数字签名。点击"更多信息"，然后点击"仍要运行"即可。

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
