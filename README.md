<p align="center">
  <img src="https://img.shields.io/badge/Python-3.8%2B-blue?logo=python&logoColor=white" alt="Python 3.8+">
  <img src="https://img.shields.io/badge/Streamlit-1.31-FF4B4B?logo=streamlit&logoColor=white" alt="Streamlit 1.31">
  <img src="https://img.shields.io/badge/框架-camel--ai-7B3FE4" alt="camel-ai">
  <img src="https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-lightgrey" alt="License CC BY-NC-SA 4.0">
</p>

<h1 align="center">OJ-agent</h1>

<p align="center">
  把算法题和你的代码贴进去，问「这段的时间复杂度是多少」「怎么优化」——<br>
  它当导师，不当枪手：引导你自己想，顺手画张流程图，还会猜你下一个想问什么。
</p>

---

**目录**：[这是什么](#这是什么) · [能做什么](#能做什么) · [快速开始](#快速开始) · [它是怎么跑的](#它是怎么跑的) · [项目结构](#项目结构) · [开发与测试](#开发与测试) · [注意事项](#注意事项) · [许可证](#许可证)

## 这是什么

刷题时卡住，把题面和代码丢给通用大模型，它往往直接甩一份能 AC 的完整答案——你看懂了，但下次还是不会。

OJ-agent 是一个跑在浏览器里的算法学习助手：左边贴题目内容和你的代码，右边直接用自然语言提问。它基于 [camel-ai](https://github.com/camel-ai/camel) 多智能体框架作答，而内置的系统提示词写得很明确——「避免直接给出完整答案」，要「培养能够独立思考和解决问题的程序员，而不是简单地提供答案」。

## 快速开始

### 前置条件

- Python 3.8 及以上（开发环境为 3.10）
- 一个通义千问系列的 API Key（兼容 OpenAI 接口格式，走 `QWEN_API_KEY`）

### 1. 装依赖

```bash
git clone https://github.com/dongyu23/OJ-agent.git
cd OJ-agent
pip install -r requirements.txt
```

### 2. 配 Key

在项目根目录建一个 `.env` 文件：

```
QWEN_API_KEY=你的API密钥
```

### 3. 启动

```bash
python -m streamlit run Pipeline/ui.py
```

Streamlit 会把地址打印到终端（默认 `http://localhost:8501`），浏览器打开就能用。左栏已经预填了一道示例题和代码模板，直接点「发送请求」即可看到效果。

## 能做什么

| 你能问 | 它怎么答 |
|---|---|
| 这段代码的时间复杂度是多少？ | 不直接报答案，而是引导你自己分析循环层数和数据规模 |
| 这个算法怎么优化？ | 指出性能瓶颈，引导你想更合适的数据结构，而不是给一份重写稿 |
| 边界情况有哪些？ | 提示你去想空输入、极值、溢出，并说明为什么这些情况会出错 |
| 看不懂这段思路 | 用生活里的比喻把算法讲明白（可视化解释 agent 的专职） |
| 接下来该问什么？ | 回答末尾附三个预测问题，每个都说明推荐追问的理由 |

另有一层意图识别：每次提问先过一遍安全和「是否需要带上代码」的判断，识别为不安全或无关的请求会被拦下，不会传到模型。

## 快速开始

### 前置条件

- Python 3.8 及以上（开发环境为 3.10）
- 一个通义千问系列的 API Key（兼容 OpenAI 接口格式，走 `QWEN_API_KEY`）

### 1. 装依赖

```bash
git clone https://github.com/dongyu23/OJ-agent.git
cd OJ-agent
pip install -r requirements.txt
```

### 2. 配 Key

在项目根目录建一个 `.env` 文件：

```
QWEN_API_KEY=你的API密钥
```

### 3. 启动

```bash
python -m streamlit run Pipeline/ui.py
```

Streamlit 会把地址打印到终端（默认 `http://localhost:8501`），浏览器打开就能用。左栏已经预填了一道示例题和代码模板，直接点「发送请求」即可看到效果。

## 它是怎么跑的

一次提问在内部要走完这条流水线：

```
你的提问
   │
   ▼
意图识别 ── 安全性判断 + 要不要带上代码 ──→ 不通过：直接拦下，不进模型
   │ 通过
   ▼
任务执行（导师式回答，流式输出）
   │
   ├─→ 流程图生成：把算法步骤画成 Mermaid 流程图
   ├─→ 可视化解释：用比喻把思路讲通俗
   └─→ 后续问题预测：给出三个值得追问的问题及理由
```

各环节在 `Pipeline/` 下各自独立成一个 agent，互不依赖，可以单独替换或停用。

## 项目结构

```
Pipeline/
├── ui.py                              # Streamlit 界面（左右两栏）
├── recognition_server.py              # 意图识别：安全性 + 是否需要代码
├── task_executor.py                   # 任务执行：导师式流式回答
├── mermaid_agent.py                   # 算法流程图生成
├── visualization_agent.py             # 比喻式可视化解释
└── next_question_predictor.py         # 后续问题预测
```

## 开发与测试

```bash
# 跑测试
pytest Pipeline/pipeline_test.py

# 代码规范（项目已配 pre-commit）
black Pipeline/
isort Pipeline/
flake8 Pipeline/
mypy Pipeline/
```

## 注意事项

- **Key 只放在 `.env`**，不要提交到仓库；`.gitignore` 已忽略该文件
- 回答质量取决于所选的 Qwen 模型，复杂题目的引导轮数会变长
- 跑的是大模型，注意 API 用量；需要稳定复现实验时建议先用小题目验证

## 许可证

[CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/deed.zh)——可以复制、分享、修改，用于个人学习和研究；**不可用于商业目的**，衍生作品须以相同许可证分发并保留署名。
