# 简历匹配分析工具

这是一个基于 DeepSeek API 的简历匹配分析工具，可以帮助您快速分析简历与职位的匹配程度。

## 下载和安装

### Windows 用户
1. 从 [Releases](../../releases) 页面下载最新的 `简历匹配分析.exe` 文件
2. 双击运行下载的文件
3. 如果出现 Windows 安全提示，点击"更多信息"，然后点击"仍要运行"

### macOS 用户
1. 从 [Releases](../../releases) 页面下载对应您芯片的版本：
   - Intel 芯片 Mac：下载 `简历匹配分析.dmg`
   - Apple Silicon (M1/M2) Mac：下载 `简历匹配分析工具-arm64.dmg`
2. 双击打开下载的 DMG 文件
3. 将应用程序拖入"应用程序"文件夹
4. 首次运行时，按住 Control 键点击应用图标，选择"打开"
5. 在弹出的对话框中点击"打开"

#### Apple Silicon (M1/M2) Mac 用户特别说明
如果您使用的是 Apple Silicon Mac（M1/M2 芯片），有两种方式运行本应用：

1. 使用 Rosetta 2（推荐）：
   - 在"应用程序"文件夹中找到"简历匹配分析工具"
   - 右键点击应用图标，选择"显示简介"
   - 勾选"使用 Rosetta 打开"
   - 关闭简介窗口，正常运行应用

2. 从源码编译（适合开发者）：
   - 克隆项目代码
   - 使用 ARM64 版本的 Python 环境
   - 安装依赖：`pip install -r requirements.txt`
   - 运行 `build_mac_arm64.sh` 脚本构建

## 使用说明

### 获取 API 密钥
1. 访问 [DeepSeek 开放平台](https://platform.deepseek.com/)
2. 注册并登录账号
3. 在平台中申请 API 密钥

### 基本使用步骤
1. 启动应用程序
2. 在 API 设置中输入您的 DeepSeek API 密钥
3. 选择要使用的模型（R1 或 V3）
4. 输入或粘贴职位描述
5. 输入或粘贴简历内容
6. 点击"开始分析"按钮

### 功能特点
- 支持多种文件格式（文本、PDF、Word、Excel）
- 可保存和加载历史职位信息
- 打分逻辑基于核心技术栈匹配度、职位方向匹配度、相关经验时间线分析、项目复杂度和难度、专业能力评估等，打分逻辑和过程会展示在分析报告中。
- 如果不推荐推进或匹配度较低，会用非技术人员(HR/猎头)能理解的语言说明方向偏差，并给出招聘人员进一步搜寻合适人选的建议。
- for猎头，单独生成一个推荐给客户的推荐评语。

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
