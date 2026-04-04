import json
import logging
from typing import Optional
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import os

from recognition_server import recognition_server
from task_executor import task_executor

# 配置日志
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = FastAPI(title="AI Programming Assistant API")

# 允许跨域
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AnalyzeRequest(BaseModel):
    query: str
    problem_content: str = ""
    editor_code: str = ""

@app.post("/api/analyze/stream")
async def analyze_stream(req: AnalyzeRequest):
    """
    处理请求并流式返回结果。
    首先通过意图识别判断action，然后根据action处理。
    如果action是proceed，则调用流式任务执行器。
    """
    async def generate():
        print(f"generate() called for query: {req.query}")
        print(f"req: {req.dict()}")
        try:
            import asyncio
            # 1. 更新题目和代码
            task_executor.set_problem_content(req.problem_content)
            print("set_problem_content done")
            
            # 2. 意图识别
            intent_result = await asyncio.to_thread(recognition_server._analyze_intent, req.query)
            print(f"intent_result: {intent_result}")
            
            # 发送意图分析结果
            yield f"data: {json.dumps({'type': 'intent', 'data': {'intent': req.query, 'safe': intent_result.get('safe', False), 'action': intent_result.get('action', 'block'), 'need_code': intent_result.get('need_code', False), 'response': '分析完成'}})}\n\n"
            
            if intent_result.get('need_code', False):
                task_executor.set_editor_code(req.editor_code)
                
            if intent_result.get('safe', False):
                action = intent_result.get('action')
                if action == 'generate_diagram':
                    # 同步生成，然后发送结果
                    mermaid_code = recognition_server.mermaid_agent.generate_diagram(req.query)
                    if mermaid_code and recognition_server.mermaid_agent.validate_code(mermaid_code):
                        response_text = f"已生成流程图代码：\n```mermaid\n{mermaid_code}\n```"
                    else:
                        response_text = "生成流程图失败，请重试"
                    yield f"data: {json.dumps({'type': 'content', 'data': response_text})}\n\n"
                    
                elif action == 'visualize':
                    # 同步生成可视化解释
                    result = recognition_server.visualization_agent.visualize(req.query)
                    yield f"data: {json.dumps({'type': 'content', 'data': result.get('response', '生成失败')})}\n\n"
                    if result.get('predicted_questions'):
                        yield f"data: {json.dumps({'type': 'predicted_questions', 'data': result.get('predicted_questions')})}\n\n"
                        
                elif action == 'proceed':
                    # 异步流式执行任务，增加心跳机制防代理超时
                    import asyncio
                    task_gen = task_executor.execute_task_stream(req.query, intent_result.get('need_code', False))
                    next_task = None
                    while True:
                        if next_task is None:
                            next_task = asyncio.create_task(task_gen.__anext__())
                        done, pending = await asyncio.wait([next_task], timeout=5.0)
                        if next_task in done:
                            try:
                                chunk = next_task.result()
                                yield f"data: {json.dumps(chunk, ensure_ascii=False)}\n\n"
                                next_task = None
                            except StopAsyncIteration:
                                break
                            except Exception as inner_e:
                                yield f"data: {json.dumps({'type': 'error', 'data': str(inner_e)})}\n\n"
                                break
                        else:
                            # 超时则发送心跳注释（不影响客户端解析，防代理掐断）
                            yield ": ping\n\n"
                else:
                    yield f"data: {json.dumps({'type': 'content', 'data': '请求被阻止：可能存在安全风险'})}\n\n"
            else:
                yield f"data: {json.dumps({'type': 'content', 'data': '请求被阻止：可能存在安全风险'})}\n\n"
                
        except Exception as e:
            logger.error(f"处理请求时出错: {str(e)}")
            yield f"data: {json.dumps({'type': 'error', 'data': str(e)})}\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")

# 挂载静态文件，用于前端页面
static_dir = os.path.join(os.path.dirname(__file__), "static")
if not os.path.exists(static_dir):
    os.makedirs(static_dir)

app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
