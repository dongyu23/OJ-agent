import requests
import json

def test_recognition_server(query: str, problem_content: str = "", editor_code: str = ""):
    """测试识别服务器"""
    url = "http://localhost:5001/recognition_server"
    data = {
        "query": query,
        "problem_content": problem_content,
        "editor_code": editor_code
    }
    
    try:
        print("\n" + "="*50)
        print("发送请求...")
        print(f"问题: {query}")
        
        response = requests.post(url, json=data)
        response.raise_for_status()
        result = response.json()
        
        print("\n1. 意图识别结果:")
        print(f"识别的意图: {result.get('intent')}")
        print(f"是否安全: {result.get('safe')}")
        print(f"处理动作: {result.get('action')}")
        print(f"需要代码: {result.get('need_code')}")
        print(f"意图识别响应: {result.get('response')}")
        
        if result.get('task_success') is not None:
            print("\n2. 任务执行结果:")
            print(f"执行是否成功: {result.get('task_success')}")
            print(f"执行器响应: {result.get('task_response', '')}")
            
            predicted_questions = result.get('predicted_questions', [])
            print(f"\n3. 预测的后续问题 (共 {len(predicted_questions)} 个):")
            if predicted_questions:
                for i, pred in enumerate(predicted_questions, 1):
                    print(f"\n预测 {i}:")
                    print(f"问题: {pred.get('question', '')}")
            else:
                print("没有预测到后续问题")
        
        print("\n" + "="*50)
        return result
    except requests.exceptions.RequestException as e:
        print(f"请求错误: {e}")
        return None

if __name__ == "__main__":
    # 测试用例
    problem_content = """
题目：两数之和

给定一个整数数组 nums 和一个整数目标值 target，请你在该数组中找出和为目标值 target 的那两个整数，并返回它们的数组下标。

你可以假设每种输入只会对应一个答案。但是，数组中同一个元素在答案里不能重复出现。

你可以按任意顺序返回答案。

示例 1：
输入：nums = [2,7,11,15], target = 9
输出：[0,1]
解释：因为 nums[0] + nums[1] == 9 ，返回 [0, 1] 。

示例 2：
输入：nums = [3,2,4], target = 6
输出：[1,2]
"""
    
    editor_code = """
def twoSum(nums, target):
    n = len(nums)
    for i in range(n):
        for j in range(i + 1, n):
            if nums[i] + nums[j] == target:
                return [i, j]
    return []
"""
    
    # 一个具有代表性的测试用例：请求代码分析
    print("开始测试完整流程...")
    test_recognition_server(
        query="这段代码的时间复杂度是多少？有什么可以优化的地方吗？",
        problem_content=problem_content,
        editor_code=editor_code
    )
