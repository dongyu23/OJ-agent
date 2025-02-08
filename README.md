# AI编程助手

基于camel-ai多智能体框架的智能编程助手系统，提供实时代码分析、问题解答和智能推荐功能。

## 功能特点

- 🔍 **智能意图识别**：准确识别用户意图，提供针对性服务
- 💡 **实时代码分析**：分析代码复杂度、性能瓶颈和优化建议
- 🤖 **多轮对话**：支持上下文理解和多轮交互
- 🔮 **智能问题预测**：预测用户可能的后续问题
- 📊 **流式响应**：实时展示分析结果
- 🛡️ **安全防护**：内置安全检查机制

## 系统架构

```
├── Pipeline/              # 核心实现目录
│   ├── api_server.py     # FastAPI服务器
│   ├── task_executor.py  # 任务执行器
│   ├── recognition_server.py  # 意图识别服务
│   ├── next_question_predictor.py  # 问题预测器
│   └── ui.py            # Streamlit UI界面
├── requirements.txt      # 项目依赖
└── README.md            # 项目文档
```

## 快速开始

### 1. 环境要求

- Python 3.8+
- 安装依赖：
```bash
pip install -r requirements.txt
```

### 2. 配置

1. 创建 `.env` 文件并设置：
```env
QWEN_API_KEY=你的API密钥
```

### 3. 启动服务

1. 启动API服务器：
```bash
python Pipeline/api_server.py
```

2. 启动UI界面：
```bash
streamlit run Pipeline/ui.py
```

## 使用说明

1. 访问 `http://localhost:8501` 打开UI界面
2. 在左侧输入区域：
   - 填写题目内容
   - 输入或粘贴代码
   - 提出你的问题
3. 点击"发送请求"获取AI助手的实时分析和建议

## 技术栈

- **后端框架**：FastAPI
- **UI框架**：Streamlit
- **AI模型**：Qwen2.5-72B-Instruct
- **多智能体框架**：camel-ai
- **API集成**：ModelScope API

## 主要特性

### 1. 流式输出
- 实时展示分析进度
- 分步显示不同类型的结果
- 支持长文本生成

### 2. 意图识别
- 智能分析用户意图
- 安全性检查
- 精准的任务分发

### 3. 代码分析
- 复杂度分析
- 性能优化建议
- 代码质量检查

### 4. 智能推荐
- 上下文感知
- 预测后续问题
- 个性化建议

## 开发指南

### 添加新功能

1. 在 `Pipeline/` 目录下创建新的功能模块
2. 在 `api_server.py` 中添加新的API端点
3. 在 `ui.py` 中添加对应的UI组件
4. 更新 `requirements.txt` 添加新依赖

### 代码规范

- 使用类型注解
- 添加详细的文档字符串
- 遵循PEP 8编码规范
- 添加适当的日志记录

## 常见问题

1. **API连接失败**
   - 检查API密钥是否正确
   - 确认网络连接正常
   - 查看服务器日志

2. **流式输出问题**
   - 检查浏览器兼容性
   - 确认网络稳定性
   - 查看服务器负载

## 贡献指南

1. Fork 项目
2. 创建功能分支
3. 提交变更
4. 发起 Pull Request

## 许可证

MIT License
