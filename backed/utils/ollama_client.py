import re
import requests
import json
from typing import Generator, List, Dict, Optional

def ask_ai(prompt: str, history: Optional[List[Dict[str, str]]] = None) -> Generator[str, None, None]:
    """
    调用本地Ollama API进行对话。

    :param prompt: 用户输入的问题
    :param history: 对话历史，格式为 [{"role": "user", "content": "问题"}, {"role": "assistant", "content": "回答"}]
    :return: 生成器，返回逐字的回答
    """
    if history is None:
        history = []

    messages = history + [{
        "role": "user",
        "content": (
            "请严格按以下格式回答：\n"
            "<think>\n"
            "这里是你的思考过程（分析问题、推理步骤等）\n"
            "</think>\n"
            "<answer>\n"
            "这里是面向用户的最终答案\n"
            "</answer>"
            f"\n\n问题：{prompt}"
        )
    }]

    try:
        response = requests.post(
            "http://localhost:11434/api/chat",
            json={
                "model": "deepseek-r1:7b",
                "messages": messages,
                "stream": True,
                "options": {
                    "temperature": 0.7,
                    "num_ctx": 4096
                }
            },
            stream=True,
            timeout=120  # 延长超时时间
        )
        response.raise_for_status()

        buffer = ""
        in_think = False
        in_answer = False
        pending_content = []

        for line in response.iter_lines():
            if not line:
                continue

            try:
                chunk = json.loads(line.decode('utf-8')).get('message', {}).get('content', '')
                if not chunk:
                    continue

                buffer += chunk
                
                # 处理标签和内容
                while True:
                    # 查找最近的标签
                    tag_match = re.search(r'<(/?)(think|answer)>', buffer)
                    if not tag_match:
                        break
                    
                    tag_pos = tag_match.start()
                    tag_type = tag_match.group(2)
                    is_closing = bool(tag_match.group(1))
                    
                    # 处理标签前的内容
                    content_before = buffer[:tag_pos]
                    if content_before:
                        if in_think:
                            pending_content.append(f"<think>{content_before}</think>")
                        elif in_answer:
                            pending_content.append(content_before)
                        else:
                            pending_content.append(content_before)
                    
                    # 更新状态
                    if is_closing:
                        if tag_type == 'think' and in_think:
                            in_think = False
                        elif tag_type == 'answer' and in_answer:
                            in_answer = False
                    else:
                        if tag_type == 'think':
                            in_think = True
                        elif tag_type == 'answer':
                            in_answer = True
                    
                    # 移除已处理的部分
                    buffer = buffer[tag_match.end():]
                
                # 如果有待处理内容，优先返回
                while pending_content:
                    yield pending_content.pop(0)
                
            except (json.JSONDecodeError, KeyError) as e:
                yield f"<think>解析错误: {str(e)}</think>"
                continue

        # 处理剩余内容
        if buffer:
            if in_think:
                yield f"<think>{buffer}</think>"
            elif in_answer:
                yield buffer
            else:
                yield buffer

    except requests.exceptions.Timeout:
        yield "<think>错误：请求超时，请稍后再试</think>"
    except requests.exceptions.RequestException as e:
        yield f"<think>网络错误：{str(e)}</think>"
    except Exception as e:
        yield f"<think>系统错误：{str(e)}</think>"