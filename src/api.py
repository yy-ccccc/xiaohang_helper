import requests
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config import API_URL, API_KEY, MODEL_NAME, DATA_DIR, MAX_TOKENS, TEMPERATURE, REPETITION_PENALTY, TIMEOUT, MAX_HISTORY_LENGTH, KEYWORD_MAP

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

def load_file(filename):
    filepath = os.path.join(DATA_DIR, filename)
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        print(f"文件未找到：{filepath}")
        return ""

campus_data = {
    filename: load_file(filename)
    for filename in ["01_新生入学.md", "02_办事流程.md", "03_电话黄页.md", "04_应急防骗.md"]
}

def get_relevant_data(question):
    relevant_files = []
    
    for filename, keywords in KEYWORD_MAP.items():
        for keyword in keywords:
            if keyword in question:
                if filename not in relevant_files:
                    relevant_files.append(filename)
                    break
    
    if not relevant_files:
        relevant_files = ["01_新生入学.md", "02_办事流程.md"]
    
    content = ""
    for filename in relevant_files:
        file_content = campus_data.get(filename, "")
        if file_content:
            lines = file_content.split('\n')
            key_lines = []
            for line in lines:
                if line.strip() and not line.startswith('#') and len(line) > 5:
                    key_lines.append(line)
            joined_lines = '\n'.join(key_lines)
            content += f"【文件：{filename}】\n{joined_lines}\n\n"
    
    return content

def build_user_message(question):
    relevant_data = get_relevant_data(question)
    return f"""【学校资料】
{relevant_data}

用户问题：{question}"""

def call_ai(messages):
    data = {
        "model": MODEL_NAME,
        "messages": messages,
        "temperature": TEMPERATURE,
        "repetition_penalty": REPETITION_PENALTY,
        "max_tokens": MAX_TOKENS
    }
    try:
        response = requests.post(API_URL, headers=headers, json=data, timeout=TIMEOUT)
        if response.status_code != 200:
            result = response.json() if response.content else {}
            error_msg = result.get("message", f"AI服务返回错误状态码：{response.status_code}")
            return None, error_msg
        result = response.json()
        if "choices" in result and len(result["choices"]) > 0:
            answer = result["choices"][0]["message"]["content"]
            return answer, None
        return None, "AI服务返回格式异常"
    except requests.exceptions.RequestException as e:
        return None, f"网络连接异常：{str(e)}"

def trim_history(messages):
    if len(messages) > MAX_HISTORY_LENGTH + 1:
        return [messages[0]] + messages[-(MAX_HISTORY_LENGTH):]
    return messages