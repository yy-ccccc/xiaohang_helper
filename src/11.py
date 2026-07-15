import requests
import os

API_URL = "https://api.siliconflow.cn/v1/chat/completions"
API_KEY = "sk-npnovafjuixqniobduslqkqybtkqruzahjybpvonldetxmqm"
headers = {
    "Authorization": "Bearer {}".format(API_KEY),
    "Content-Type": "application/json"
}

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

def load_file(filename):
    filepath = os.path.join(DATA_DIR, filename)
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        print("文件未找到：{}".format(filepath))
        return ""

campus_data = {
    "01_新生入学.md": load_file("01_新生入学.md"),
    "02_办事流程.md": load_file("02_办事流程.md"),
    "03_电话黄页.md": load_file("03_电话黄页.md"),
    "04_应急防骗.md": load_file("04_应急防骗.md")
}

def get_relevant_data(question):
    keywords = ["报到", "宿舍", "学费", "军训", "食堂", "图书馆", "补卡", "证明", "转专业", "报销", "调课", "报修", "科研", "电话", "黄页", "防骗", "心理", "应急"]
    relevant_files = []
    
    for keyword in keywords:
        if keyword in question:
            if keyword in ["报到", "宿舍", "学费", "军训"] and "01_新生入学.md" not in relevant_files:
                relevant_files.append("01_新生入学.md")
            if keyword in ["补卡", "证明", "转专业", "报销", "调课", "报修", "科研"] and "02_办事流程.md" not in relevant_files:
                relevant_files.append("02_办事流程.md")
            if keyword in ["电话", "黄页"] and "03_电话黄页.md" not in relevant_files:
                relevant_files.append("03_电话黄页.md")
            if keyword in ["防骗", "心理", "应急"] and "04_应急防骗.md" not in relevant_files:
                relevant_files.append("04_应急防骗.md")
    
    if not relevant_files:
        relevant_files = ["01_新生入学.md", "02_办事流程.md"]
    
    content = ""
    for filename in relevant_files:
        lines = campus_data[filename].split('\n')
        key_lines = []
        for line in lines:
            if line.strip() and not line.startswith('#') and len(line) > 5:
                key_lines.append(line)
        content += "[文件: {}]\n{}\n\n".format(filename, '\n'.join(key_lines))
    
    return content

user_profiles = {
    "1": {
        "name": "大一新生",
        "features": "对校园完全不熟悉、信息焦虑、容易受骗",
        "concerns": "报到流程、宿舍分配、学费缴纳、军训安排、防骗知识",
        "response_style": "耐心详细、步骤清晰、强调重点、提醒注意事项、语气亲切",
        "prompt_file": "05_Prompt模板.md"
    },
    "2": {
        "name": "在校老生",
        "features": "办事多、追求效率、不想听废话",
        "concerns": "开证明、补卡、转专业、图书馆时间、课程安排",
        "response_style": "简洁高效、直奔主题、提供关键信息、减少冗余描述",
        "prompt_file": "05_Prompt模板.md"
    },
    "3": {
        "name": "教师",
        "features": "专业场景、需要政策依据",
        "concerns": "差旅报销、调课申请、设备报修、科研申报、会议安排",
        "response_style": "专业准确、引用政策依据、提供流程规范、正式严谨",
        "prompt_file": "05_Prompt模板.md"
    }
}

recommended_questions = {
    "1": [
        "报到需要带什么东西",
        "宿舍怎么分配的",
        "军训什么时候开始",
        "学费怎么缴纳"
    ],
    "2": [
        "图书馆开放时间",
        "补卡去哪里办理",
        "转专业流程",
        "如何开在读证明"
    ],
    "3": [
        "科研申报流程",
        "调课怎么申请",
        "差旅报销需要什么材料",
        "设备报修流程"
    ]
}

phone_directory = {
    "教务处": "0371-61912001",
    "学生处": "0371-61912002",
    "保卫处": "0371-61912003",
    "校医院": "0371-61912004",
    "图书馆": "0371-61912005",
    "宿管中心": "0371-61912006",
    "后勤服务": "0371-61912007",
    "财务处": "0371-61912008",
    "招生办": "0371-61912009",
    "就业指导中心": "0371-61912010"
}

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
    start_marker = prompts[user_type]
    end_markers = end_markers_by_type[user_type]
    
    start_idx = template_content.find(start_marker)
    if start_idx == -1:
        return ""
    
    content = template_content[start_idx:]
    
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

def build_system_prompt(user_type):
    profile = user_profiles[user_type]
    template_content = load_file(profile["prompt_file"])
    prompt_template = extract_prompt(template_content, user_type)
    
    if prompt_template:
        all_data_content = ""
        for filename, content in campus_data.items():
            if content:
                lines = content.split('\n')
                key_lines = []
                for line in lines:
                    if line.strip() and not line.startswith('#') and len(line) > 5:
                        key_lines.append(line)
                all_data_content += "[文件: {}]\n{}\n\n".format(filename, '\n'.join(key_lines))
        
        prompt_template = prompt_template.replace("{学校资料内容}", all_data_content)
        return prompt_template
    
    all_data_content = ""
    for filename, content in campus_data.items():
        if content:
            lines = content.split('\n')
            key_lines = []
            for line in lines:
                if line.strip() and not line.startswith('#') and len(line) > 5:
                    key_lines.append(line)
            all_data_content += "[文件: {}]\n{}\n\n".format(filename, '\n'.join(key_lines))
    
    return """你是"小航"，郑州航空工业管理学院的校园信息查询AI助手。

当前用户身份：{}

【你的角色】
你像一位热心的学长，语气详细、口语化、多给鼓励。

【回答重点】
1. 根据用户身份提供差异化的回答风格
2. 涉及金钱/转账，无条件提示"先联系辅导员核实，任何要求转账的都是诈骗"

【防幻觉硬规则】
1. 只能根据【学校资料】回答，资料里没有的明说"这个我没收录，建议拨打0371-61911000总值班室问一下"
2. 严禁编造电话号码、地址、办公时间、学费金额、人名
3. 涉及金钱/转账，无条件提示"先联系辅导员核实，任何要求转账的都是诈骗"
4. 涉及心理危机（自杀、不想活、活不下去等），立即给：12320-5心理援助 + 学校心理咨询中心 + 告诉辅导员
5. 不接入学校系统（教务/一卡通/财务），被问"查我的成绩/课表/卡余额"礼貌拒绝
6. 回答末尾标注【来源：郑州航院官网、校园资料】
7. 数字必须绝对准确！所有数字（人数、金额、时间、电话号码等）都不能重复或增加数字：
   - 人数类："4人间"不能说成"444人间"，"6人间"不能说成"666人间"
   - 金额类："1200元"不能说成"12000元"或"11200元"
   - 时间类："14天"不能说成"114天"或"144天"
   - 电话号码："0371-61912001"不能说成"0371-619112001"或"0371-661912001"
8. 回答时先直接给出答案，再简要说明依据，不要添加任何猜测内容

【学校资料】
{}

【别名词典】
- "学校""航院""ZUA""郑航" = 郑州航空工业管理学院
- "新校区""龙湖""新校" = 龙子湖校区
- "卡""饭卡""校卡" = 校园一卡通
- "保安""门卫""校警" = 保卫处
- "迁户口""落户" = 户籍迁入/迁出
- "调宿舍""换宿舍" = 宿舍调整申请
- "证明""在读证明" = 在校学籍证明""".format(
        profile["name"],
        all_data_content
    )

messages = []

def ask_xiaohang(question):
    global messages
    user_message = "用户问题：{}".format(question)
    messages.append({"role": "user", "content": user_message})
    
    if len(messages) > 11:
        messages = [messages[0]] + messages[-10:]
    
    data = {
        "model": "Qwen/Qwen2.5-7B-Instruct",
        "messages": messages
    }
    try:
        response = requests.post(API_URL, headers=headers, json=data, timeout=60)
        if response.status_code != 200:
            print("AI服务暂时不可用，您可以查看电话黄页获取帮助")
            return None
        result = response.json()
        answer = result["choices"][0]["message"]["content"]
        messages.append({"role": "assistant", "content": answer})
        return answer
    except requests.exceptions.RequestException:
        print("网络连接异常，AI服务暂时不可用")
        print("您可以查看电话黄页获取帮助，或稍后再试")
        return None

def show_phone_directory():
    print("=" * 60)
    print("郑州航空工业管理学院 - 电话黄页")
    print("=" * 60)
    for dept, phone in phone_directory.items():
        print("{:<12} {}".format(dept, phone))
    print("=" * 60)

def chat_mode():
    global messages
    print()
    print("请选择您的身份：")
    for key in sorted(user_profiles.keys()):
        profile = user_profiles[key]
        print("{} - {}".format(key, profile["name"]))
    print()

    while True:
        try:
            user_choice = input("请输入选择（1/2/3）：")
            if user_choice in user_profiles:
                break
            print("请输入有效选择（1/2/3）")
        except EOFError:
            print()
            print("提示：在交互式环境中运行可输入身份选择")
            return

    print("-" * 60)

    messages = [{"role": "system", "content": build_system_prompt(user_choice)}]

    print("【推荐问题】")
    questions = recommended_questions[user_choice]
    for i, q in enumerate(questions, 1):
        print("{} - {}".format(i, q))
    print("输入问题编号快速提问，或直接输入自定义问题")
    print("输入'黄页'查看电话簿，输入'quit'退出")
    print("-" * 60)

    while True:
        try:
            user_input = input("请输入您的问题：")
            if user_input.lower() == 'quit':
                print("感谢使用小航AI助手，再见！")
                break
            if user_input.lower() == '黄页':
                show_phone_directory()
                continue
            if not user_input.strip():
                print("请输入有效问题")
                continue
            
            if user_input.isdigit() and 1 <= int(user_input) <= len(questions):
                question = questions[int(user_input) - 1]
                print("快速提问：{}".format(question))
            else:
                question = user_input
            
            answer = ask_xiaohang(question)
            if answer:
                print("小航：", answer)
                print("-" * 60)
        except EOFError:
            print()
            print("提示：在交互式环境中运行可输入问题进行对话")
            break

def main():
    print("=" * 60)
    print("欢迎使用小航AI助手")
    print("=" * 60)
    print()

    while True:
        print("请选择功能：")
        print("1 - 校园问答")
        print("2 - 电话黄页")
        print("3 - 退出")
        print()

        try:
            choice = input("请输入选择（1/2/3）：")
            if choice == "1":
                chat_mode()
            elif choice == "2":
                show_phone_directory()
            elif choice == "3":
                print("感谢使用小航AI助手，再见！")
                break
            else:
                print("请输入有效选择（1/2/3）")
            print()
        except EOFError:
            print()
            choice = "1"
            print("默认进入校园问答")
            chat_mode()
            break

if __name__ == "__main__":
    main()