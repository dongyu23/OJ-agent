# AI编程助手 API文档

## API基础信息

- 基础URL: `http://localhost:5001`
- 响应格式: JSON
- 编码方式: UTF-8

## API端点说明

### 1. 分析代码问题（普通模式）

**请求地址**：`/api/analyze`

**请求方式**：POST

**请求参数**：
```json
{
    "query": "这段代码的时间复杂度是多少？",
    "problem_content": "题目描述...",
    "editor_code": "def solution():\n    pass"
}
```

**参数说明**：
- `query`: 用户的问题
- `problem_content`: 题目内容
- `editor_code`: 需要分析的代码

**响应示例**：
```json
{
    "intent": "代码分析",
    "safe": true,
    "action": "分析时间复杂度",
    "need_code": false,
    "response": "这段代码的时间复杂度分析...",
    "task_success": true,
    "task_response": "详细的分析结果...",
    "predicted_questions": [
        {
            "question": "如何优化这段代码？"
        },
        {
            "question": "有什么边界情况需要考虑？"
        }
    ]
}
```

### 2. 分析代码问题（流式模式）

**请求地址**：`/api/analyze/stream`

**请求方式**：POST

**请求参数**：
```json
{
    "query": "这段代码的时间复杂度是多少？",
    "problem_content": "题目描述...",
    "editor_code": "def solution():\n    pass"
}
```

**参数说明**：
- 与普通模式相同

**响应格式**：
Server-Sent Events (SSE)，每个事件包含以下类型：

1. 意图分析结果：
```json
{
    "type": "intent",
    "data": {
        "intent": "代码分析",
        "safe": true,
        "action": "分析时间复杂度",
        "need_code": false,
        "response": "正在分析代码..."
    }
}
```

2. 任务执行结果：
```json
{
    "type": "content",
    "data": "分析结果的部分内容..."
}
```

3. 预测问题：
```json
{
    "type": "predicted_questions",
    "data": [
        {
            "question": "如何优化这段代码？"
        }
    ]
}
```

### 3. 健康检查

**请求地址**：`/api/health`

**请求方式**：GET

**响应示例**：
```json
{
    "status": "ok",
    "version": "1.0.0"
}
```

## 常见问题

### 1. 如何处理流式响应？

```javascript
// 前端示例代码
const eventSource = new EventSource('/api/analyze/stream');

eventSource.onmessage = (event) => {
    const data = JSON.parse(event.data);
    switch(data.type) {
        case 'intent':
            // 处理意图分析结果
            break;
        case 'content':
            // 处理任务执行结果
            break;
        case 'predicted_questions':
            // 处理预测问题
            break;
    }
};
```

### 2. 错误响应格式

当发生错误时，API会返回以下格式的响应：

```json
{
    "error": true,
    "message": "错误描述",
    "code": "ERROR_CODE"
}
```

常见错误码：
- `400`: 请求参数错误
- `401`: 未授权
- `500`: 服务器内部错误

### 3. 注意事项

1. 请求时需要注意代码长度，建议不要超过10000个字符
2. 流式响应需要保持连接稳定
3. 建议使用HTTPS进行安全传输
4. 如遇到连接中断，可以重新发起请求
