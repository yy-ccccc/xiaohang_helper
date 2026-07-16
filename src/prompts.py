import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config import SYSTEM_PROMPT_TEMPLATE, USER_PROFILES, KEYWORD_MAP
from src.api import campus_data, get_relevant_data

PROMPT_TEMPLATE_FILE = "05_Prompt模板.md"

def load_prompt_template():
    from .config import DATA_DIR
    filepath = os.path.join(DATA_DIR, PROMPT_TEMPLATE_FILE)
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return ""

def extract_prompt(template_content, user_type):
    prompts = {
        "1": "## 一、大一新生模板",
        "2": "## 二、在校老生模板",
        "3": "## 三、教师模板"
    }
    end_markers_by_type = {
        "1": ["## 二、在校老生模板", "## 三、教师模板", "## 四、通用规则"],
        "2": ["## 三、教师模板", "## 四、通用规则"],
        "3": ["## 四、通用规则"]
    }
    
    start_marker = prompts.get(user_type)
    if not start_marker:
        return ""
    
    start_idx = template_content.find(start_marker)
    if start_idx == -1:
        return ""
    
    content = template_content[start_idx:]
    
    end_markers = end_markers_by_type.get(user_type, [])
    for marker in end_markers:
        end_idx = content.find(marker)
        if end_idx != -1:
            content = content[:end_idx]
            break
    
    start_code = content.find("```")
    end_code = content.rfind("```")
    if start_code != -1 and end_code != -1 and start_code < end_code:
        return content[start_code+3:end_code].strip()
    
    return ""

def build_system_prompt(user_type, question=None):
    profile = USER_PROFILES.get(user_type)
    if not profile:
        return SYSTEM_PROMPT_TEMPLATE.format(
            user_name="未知用户",
            response_style="你是一位热心的校园助手。",
            school_data=""
        )
    
    template_content = load_prompt_template()
    if template_content:
        prompt_template = extract_prompt(template_content, user_type)
        if prompt_template:
            if question:
                school_data = get_relevant_data(question)
            else:
                all_data_content = ""
                for filename, content in campus_data.items():
                    if content:
                        lines = content.split('\n')
                        key_lines = []
                        for line in lines:
                            if line.strip() and not line.startswith('#') and len(line) > 5:
                                key_lines.append(line)
                        joined_lines = '\n'.join(key_lines)
                        all_data_content += f"【文件：{filename}】\n{joined_lines}\n\n"
                school_data = all_data_content
            
            prompt_template = prompt_template.replace("{学校资料内容}", school_data)
            prompt_template = prompt_template.replace("{user_name}", profile["name"])
            return prompt_template
    
    if question:
        school_data = get_relevant_data(question)
    else:
        school_data = ""
    
    return SYSTEM_PROMPT_TEMPLATE.format(
        user_name=profile["name"],
        response_style=profile["response_style"],
        school_data=school_data
    )