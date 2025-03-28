import requests
from typing import Optional

OLLAMA_BASE_URL = "http://localhost:11434/api"

def ask_ai(prompt: str, 
          model: str = "deepseek-chat",
          max_tokens: Optional[int] = 2000) -> str:
    """
    调用Ollama本地API生成文本
    参数：
        prompt: 中文提示词
        model: 使用的模型名称
        max_tokens: 最大输出长度
    返回：
        str: AI生成的文本内容
    """
    try:
        response = requests.post(
            f"{OLLAMA_BASE_URL}/generate",
            json={
                "model": model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "max_tokens": max_tokens,
                    "temperature": 0.7
                }
            },
            timeout=30
        )
        
        if response.status_code == 200:
            return response.json().get("response", "").strip()
        else:
            return f"请求失败，错误码：{response.status_code}"
            
    except Exception as e:
        return f"连接Ollama服务失败：{str(e)}"