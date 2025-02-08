from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
import logging
from recognition_server import analyze_intent, ai_assistant
from task_executor import task_executor
import os
from dotenv import load_dotenv
import json

# 配置日志
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 加载环境变量
load_dotenv()
API_KEY = os.getenv('QWEN_API_KEY')

# 创建FastAPI应用
app = FastAPI(
    title="AI编程助手API",
    description="基于camel-ai多智能体框架的智能编程助手API",
    version="1.0.0"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生产环境中应该设置具体的域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 请求模型
class QueryRequest(BaseModel):
    query: str
    problem_content: str = ""
    editor_code: str = ""

# 预测问题模型
class PredictedQuestion(BaseModel):
    question: str

# 响应模型
class QueryResponse(BaseModel):
    intent: str
    safe: bool
    action: str
    need_code: bool
    response: str
    task_success: Optional[bool] = None
    task_response: Optional[str] = None
    predicted_questions: Optional[List[PredictedQuestion]] = None

@app.post("/api/analyze", response_model=QueryResponse)
async def analyze_query(request: QueryRequest):
    """分析用户查询并返回结果"""
    try:
        logger.info(f"收到新的查询请求: {request.query}")
        
        # 设置上下文
        task_executor.set_problem_content(request.problem_content)
        task_executor.set_editor_code(request.editor_code)
        
        # 分析意图
        intent_result = analyze_intent(request.query, ai_assistant)
        if not intent_result:
            raise HTTPException(status_code=500, detail="意图分析失败")
        
        response = {
            'intent': intent_result.get('intent', 'invalid_request'),
            'safe': intent_result.get('safe', False),
            'action': intent_result.get('action', 'block'),
            'need_code': intent_result.get('need_code', False),
            'response': intent_result.get('response', '处理请求时出错'),
        }

        # 如果请求安全且可以处理，则执行任务
        if response['safe'] and response['action'] == 'proceed':
            task_result = task_executor.execute_task(
                intent=response['intent'],
                query=request.query,
                need_code=response['need_code']
            )
            # 更新响应内容
            response.update({
                'task_success': task_result.get('success'),
                'task_response': task_result.get('response'),
                'predicted_questions': [
                    {"question": q.get('question')}
                    for q in task_result.get('predicted_questions', [])
                ]
            })
            logger.info(f"任务执行结果: {task_result}")
        
        return response
        
    except Exception as e:
        logger.error(f"处理请求时出错: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/analyze/stream")
async def analyze_query_stream(request: QueryRequest):
    """流式分析用户查询并返回结果"""
    try:
        logger.info(f"收到新的流式查询请求: {request.query}")
        
        # 设置上下文
        task_executor.set_problem_content(request.problem_content)
        task_executor.set_editor_code(request.editor_code)
        
        async def generate():
            try:
                # 1. 首先进行意图分析
                intent_result = analyze_intent(request.query, ai_assistant)
                if not intent_result:
                    yield f"data: {json.dumps({'type': 'error', 'data': '意图分析失败'})}\n\n"
                    return
                
                # 立即发送意图分析结果
                yield f"data: {json.dumps({'type': 'intent', 'data': intent_result})}\n\n"
                
                # 2. 如果请求安全且可以处理，则流式执行任务
                if intent_result['safe'] and intent_result['action'] == 'proceed':
                    async for chunk in task_executor.execute_task_stream(
                        intent=intent_result['intent'],
                        query=request.query,
                        need_code=intent_result['need_code']
                    ):
                        yield f"data: {json.dumps(chunk)}\n\n"
                
                # 3. 发送结束信号
                yield f"data: {json.dumps({'type': 'end'})}\n\n"
                
            except Exception as e:
                logger.error(f"生成响应时出错: {str(e)}")
                yield f"data: {json.dumps({'type': 'error', 'data': str(e)})}\n\n"
        
        return StreamingResponse(
            generate(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
            }
        )
        
    except Exception as e:
        logger.error(f"处理流式请求时出错: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/health")
async def health_check():
    """健康检查接口"""
    return {"status": "healthy", "version": "1.0.0"}

def start_server():
    """启动服务器"""
    try:
        # 初始化必要的组件
        if not API_KEY:
            raise ValueError("未设置API_KEY环境变量")
            
        # 启动服务器
        uvicorn.run(
            "api_server:app",
            host="0.0.0.0",
            port=5001,
            reload=True,
            log_level="info"
        )
    except Exception as e:
        logger.error(f"启动服务器时出错: {str(e)}")
        raise

if __name__ == "__main__":
    start_server()
