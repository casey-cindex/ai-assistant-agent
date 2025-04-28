import os
import json
from openai import OpenAI

MODEL_NAME = "qwen-max"
client = OpenAI(
    api_key = os.environ.get("OPENAI_API_KEY"),
    base_url = "https://dashscope.aliyuncs.com/compatible-mode/v1",
)

def exec_python_code(code: str):
    try:
        exec_env = {}
        exec(code, exec_env, exec_env)
        return {"result": exec_env, "error": None}
    except Exception as e:
        print("失败了 %s" % str(e))
        return {"result": None, "error": str(e)}

from googlesearch import search

def google_search(query: str, num_results: int = 5):
    results = []
    for url in search(query, num_results=num_results, lang='zh-CN'):
        results.append(url)
    return results


import logging
logging.disable(logging.CRITICAL)
from newspaper import Article
def fetch_webpage_content(url: str, max_total_length: int = 4500):
    try:
        article = Article(url, language='zh')
        article.download()
        article.parse()
    except Exception as e:
        return f"请求失败，错误信息：{e}"

    # 提取主体文本并截断
    text_content = article.text.strip()
    if len(text_content) > max_total_length:
        text_content = text_content[:max_total_length] + '...'

    # 提取图片链接（主体图片+其他图片）
    images = list(article.images)

    # 主图优先
    if article.top_image:
        images = [article.top_image] + [img for img in images if img != article.top_image]

    images_content = "\n".join(f"[IMAGE:{img}]" for img in images[:5])  # 限制前5张

    final_content = f"[TEXT:{text_content}]\n\n{images_content}" if images else f"[TEXT:{text_content}]"

    return final_content if final_content else "未能提取到有效内容。"

def parse_pdf(file_path: str) -> str:
    try:
        import PyPDF2
        text = ""
        with open(file_path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        return text
    except Exception as e:
        return f"解析 PDF 文件失败: {str(e)}"


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
    },
    {
        "type": "function",
        "function": {
            "name": "google_search",
            "description": "使用Google搜索获取关键词对应的前几个搜索结果的链接。",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "搜索关键词"},
                    "num_results": {"type": "integer", "description": "需要返回的结果数量，默认5"}
                },
                "required": ["query"]
            }
        },
        "strict": True
    },
    {
        "type": "function",
        "function": {
            "name": "fetch_webpage_content",
            "description": "抓取指定URL的网页内容，自动提取网页主体文本和图片链接，保持原始顺序并明确标识文本与图片位置，内容长度自动受限以适合模型的上下文。",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "需要抓取内容的网页URL"
                    }
                },
                "required": ["url"]
            }
        },
        "strict": True
    },
    {
        "type": "function",
        "function": {
            "name": "parse_pdf",
            "description": "解析本地 PDF 文件，并返回其中的文本内容。",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {"type": "string", "description": "本地PDF文件的路径"}
                },
                "required": ["file_path"]
            }
        },
        "strict": True
    }
]

messages = [
    {
        "role": "system",
        "content": (
            "你是一个高效、灵活且坚持不懈的智能助手，能够自主分析并拆解用户提出的任务，始终通过现有工具或生成代码的方式给出有效的解决方案。\n\n"
            "你当前拥有且必须优先调用的工具如下：\n"
            "1. exec_python_code：执行Python代码并返回执行结果或错误信息。\n"
            "2. google_search：根据关键词返回相关网页链接。\n"
            "3. fetch_webpage_content：抓取URL页面的主要文本内容。\n"
            "4. parse_pdf：解析本地PDF文件并返回其中的文本内容。\n\n"
            "处理任何任务时，必须严格遵循以下执行原则：\n"
            "A. 在调用工具前，始终先完整地拆分任务，给出明确的步骤计划（每一步含简短标题与目的说明）。\n"
            "B. 优先尝试使用已有工具组合来完成任务，不轻易请求额外工具。\n"
            "C. 当某个工具调用失败或工具无法满足需求时，必须：\n"
            "   1) 更换关键词或方法，继续尝试其他可用工具或来源，而非在同一来源反复尝试。\n"
            "   2) 若所有工具尝试均失败，主动生成完整且可执行的Python代码以实现任务，决不能提前终止任务。\n"
            "特别注意：\n"
            "- 在执行任何任务时，必须严格确保提供的结果与用户提出的任务或请求高度相关，不允许使用无关或不准确的信息敷衍任务。\n"
            "- 当任务涉及的信息无法直接从前几个来源获得时，必须主动深入搜索并分析更多相关来源（至少尝试分析3-5个不同页面或来源），不得轻易放弃。\n"
            "- 如果某个页面或方法未能提供明确答案，务必主动切换到其他页面或尝试不同搜索关键词，不得停留于单一来源反复尝试。\n"
            "- 严禁泛泛而谈或过于笼统地告知无法找到答案，必须体现出主动、深入的解决态度。\n\n"
            "确保每次任务最终均给出完整有效的解决方案，直至用户需求被彻底满足为止。\n\n"
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
                elif name == "google_search":
                    result = google_search(args["query"], args["num_results"])
                elif name == "fetch_webpage_content":
                    result = fetch_webpage_content(args["url"])
                elif name == "parse_pdf":
                    result = parse_pdf(args["file_path"])
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