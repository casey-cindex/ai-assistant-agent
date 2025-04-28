import os
import json
from openai import OpenAI

MODEL_NAME = "qwen-plus"
client = OpenAI(
    api_key = os.environ.get("OPENAI_API_KEY"),
    base_url = "https://dashscope.aliyuncs.com/compatible-mode/v1",
)

def exec_python_code(code: str):
    print(code)
    try:
        exec_env = {}
        exec(code, exec_env, exec_env)
        return {"result": exec_env, "error": None}
    except Exception as e:
        print("失败了 %s" % str(e))
        return {"result": None, "error": str(e)}

# 定义可用工具列表（函数描述）
tools = [
    {
        "type": "function",
        "function": {
            "name": "exec_python_code",
            "description": "执行任意Python代码，并返回执行结果或报错信息。",
            "parameters": {
                "type": "object",
                "properties": {
                    "code": {
                        "type": "string",
                        "description": "要执行的Python代码片段。"
                    }
                },
                "required": ["code"]
            }
        },
        "strict": True
    }
]

messages = [
    {
        "role": "system",
        "content": (
            "你是一个高效、灵活且坚持不懈的智能助手，能够自主分析并拆解用户提出的任务，"
            "始终通过执行Python代码的方式给出有效的解决方案。\n\n"
            "你拥有并必须调用的工具如下：\n"
            "1. exec_python_code：执行Python代码并返回执行结果或错误信息。\n\n"
            "执行任务时，必须严格遵循以下原则：\n"
            "A. 每次调用工具前，都先给出明确的分步执行计划（步骤标题和目的）。\n"
            "B. Python代码功能强大，能访问系统信息、网络资源、文件系统，"
            "优先使用标准库完成任务，尽量避免依赖第三方库。\n"
            "C. 若需访问特定网页或信息，必须首先执行Python代码调用搜索引擎（如百度或谷歌）搜索并确定目标页面的真实URL，"
            "禁止自行猜测URL。\n"
            "D. 若环境缺乏特定库或方法失败，必须主动尝试其他替代方法，而非中断任务。\n"
            "特别注意：\n"
            "- 必须确保返回结果与用户任务高度相关，绝不允许使用未经验证的URL或无关信息。\n"
            "- 必须主动且深入地解决问题，不得泛泛而谈或笼统告知任务无法完成。\n\n"
            "现在，请开始执行用户提出的任务。"
        )
    }
]

while True:
    # 用户提出问题
    user_question = input("$ ")
    messages.append({"role": "user", "content": user_question})

    # 调用模型，自动判断是否需要函数调用
    completion = client.chat.completions.create(
        model=MODEL_NAME, messages=messages, tools=tools
    )

    while True:
        messages.append(completion.choices[0].message)
        if completion.choices[0].message.content:
            print(completion.choices[0].message.content)
        if completion.choices[0].finish_reason == "stop":
            break
        for tool_call in completion.choices[0].message.tool_calls:
            name = tool_call.function.name
            try:
                args = json.loads(tool_call.function.arguments)
                if name == "exec_python_code":
                    result = exec_python_code(args["code"])
            except Exception as e:
                result = f"错误信息：{e}"
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": str(result)
            })
        completion = client.chat.completions.create(
            model=MODEL_NAME, messages=messages, tools=tools
        )