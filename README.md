# AI编程助手

基于camel-ai多智能体框架的智能编程助手系统，提供代码分析、算法可视化和交互式学习功能。

## 功能特点

- **智能意图识别**：自动分析用户意图，提供针对性服务
- **代码分析**：分析代码质量、复杂度和优化建议
- **算法可视化**：生成算法流程图，帮助理解算法原理
- **生动解释**：通过生动形象的比喻解释编程概念
- **问题预测**：智能预测用户可能的后续问题
- **安全防护**：内置安全检查机制，防止恶意请求

## 系统架构

### Pipeline模式
- `recognition_server.py`: 意图识别服务
- `task_executor.py`: 任务执行器
- `mermaid_agent.py`: 流程图生成代理
- `visualization_agent.py`: 可视化解释代理
- `next_question_predictor.py`: 问题预测器
- `ui.py`: Web界面实现

## 快速开始

1. 安装依赖：
```bash
pip install -r requirements.txt
```

2. 配置环境变量：
创建`.env`文件并设置：
```
QWEN_API_KEY=你的API密钥
```

3. 启动服务：
```bash
python -m streamlit run Pipeline/ui.py
```

## 开发指南

### 代码规范
- 使用black进行代码格式化
- 使用isort进行导入排序
- 使用flake8进行代码检查
- 使用mypy进行类型检查

### 测试
```bash
pytest Pipeline/pipeline_test.py
```

## 技术栈

- **框架**: camel-ai, streamlit
- **AI模型**: Qwen2.5-72B
- **开发工具**: pytest, black, isort, flake8, mypy
- **其他**: python-dotenv, requests, typing-extensions, loguru

## 注意事项

1. 请确保有足够的系统资源运行大型语言模型
2. API密钥请妥善保管，不要泄露
3. 建议使用Python 3.8+版本

## 许可证

本项目采用 [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/deed.zh) 许可证。

这意味着您可以：
- 复制、分享和修改本项目
- 将本项目用于个人学习和研究

但您必须：
- 禁止用于商业目的
- 保留原作者署名
- 使用相同的许可证分发衍生作品
