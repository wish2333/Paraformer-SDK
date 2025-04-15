# Paraformer 语音识别SDK

一个基于阿里云DashScope的语音识别SDK，支持多种音频格式的语音转文字功能。

## 功能特点

- 支持多种音频格式：wav, mp3, m4a, flac, acc
- 提供两种语音识别模型：paraformer-v2, paraformer-v1
- 支持热词识别（v1和v2版本）
- 支持多音轨选择
- 提供语气词过滤功能
- 支持时间戳校准
- 提供敏感词过滤功能（过滤或替换）
- 支持说话人分离
- 可自定义说话人数量
- 支持中文、英语、日语三种语言
- 提供文件上传和URL输入两种方式
- 自动保存识别结果，包括JSON、文本和SRT字幕文件

## 安装与运行

### 系统要求

- Python 3.10+
- pip

### 安装步骤

1. 克隆仓库：

2. 安装依赖：

```bash
pip install -r requirements.txt
```

或者用UV管理项目：

```bash
uv init
uv sync
```

3. 运行应用：

```bash
streamlit run main.py
```

或使用uv管理

```bash
.venv\Scripts\streamlit.exe run main.py
```

在浏览器中打开：http://localhost:8501

## 使用说明

1. 在"基本设置"中输入API Key并选择模型
2. 在"高级设置"中配置热词、音轨、语气词过滤等选项
3. 在"说话人分离"中启用说话人分离并设置说话人数量
4. 选择识别语言（中文、英语、日语）
5. 选择输入方式（上传文件或输入URL）
6. 点击"开始识别"按钮进行语音识别
7. 查看识别结果，结果会自动保存到output目录

## 开发指南

### 项目结构

```
paraformer-sdk/
├── output/            # 识别结果输出目录
├── main.py            # 主程序
├── config.json        # 配置文件
├── requirements.txt   # Python依赖
└── README.md          # 项目文档
```

### 配置文件说明

配置文件`config.json`包含以下字段：

- api_key: 阿里云DashScope API Key
- model: 使用的语音识别模型（paraformer-v2或paraformer-v1）
- vocabulary_id: 热词ID（v2版本）
- phrase_id: 热词ID（v1版本）
- channel_id: 音轨索引列表
- disfluency_removal_enabled: 是否启用语气词过滤
- timestamp_alignment_enabled: 是否启用时间戳校准
- special_word_filter: 敏感词过滤方式（"", "filter", "replace"）
- diarization_enabled: 是否启用说话人分离
- speaker_count: 说话人数量

### 贡献流程

欢迎提交Issue和Pull Request！

1. Fork本项目
2. 创建特性分支 (git checkout -b feature/your-feature)
3. 提交更改 (git commit -am 'Add some feature')
4. 推送到分支 (git push origin feature/your-feature)
5. 创建Pull Request

## 许可证

MIT License - 详见 LICENSE 文件