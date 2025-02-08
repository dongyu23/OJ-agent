# AI智能编程助手

基于camel-ai多智能体框架实现的智能编程助手系统，采用Pipeline架构设计。

## 项目特点

- 🤖 **多智能体协作**：使用camel-ai框架实现多个专业化AI智能体的协同工作
- 🔍 **智能意图识别**：准确识别用户意图，并进行安全性评估
- 💡 **智能问题预测**：基于上下文预测用户可能的后续问题
- 🛠️ **专业任务执行**：针对不同类型的编程任务提供专业解答
- 🔒 **安全性保障**：内置完整的安全检查机制

## 系统架构

项目采用Pipeline架构，主要包含三个核心组件：

1. **意图识别服务器** (recognition_server.py)
   - 接收用户输入
   - 分析用户意图
   - 评估请求安全性
   - 确定处理策略

2. **任务执行器** (task_executor.py)
   - 处理具体编程任务
   - 代码分析与优化
   - 解题思路指导
   - 代码检查与建议

3. **问题预测器** (next_question_predictor.py)
   - 基于上下文预测后续问题
   - 智能交互引导

## 技术栈

- Python 3.8+
- camel-ai框架
- Qwen2.5-72B-Instruct大模型
- Flask Web框架

## 快速开始

1. 安装依赖：
```bash
pip install -r requirements.txt
```

2. 配置环境变量：
```bash
QWEN_API_KEY=your_api_key
```

3. 启动服务：
```bash
python recognition_server.py
```

4. 运行测试：
```bash
python test_client.py
```

## 功能特性

- 智能代码分析
- 解题思路指导
- 代码优化建议
- 算法复杂度分析
- 测试用例建议
- 智能问题预测

## 项目结构

```
demo_ojagent/
├── Pipeline/
│   ├── recognition_server.py    # 意图识别服务器
│   ├── task_executor.py        # 任务执行器
│   ├── next_question_predictor.py  # 问题预测器
│   └── test_client.py          # 测试客户端
└── README.md
```

## 开发说明

- 遵循Pipeline架构设计
- 使用camel-ai框架实现多智能体系统
- 保持代码模块化和可扩展性
- 完善的错误处理和日志机制

## 注意事项

1. 确保正确配置API密钥
2. 遵循安全编码规范
3. 保持代码可维护性
4. 定期更新依赖包
