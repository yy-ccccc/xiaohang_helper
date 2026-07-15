import streamlit as st
import requests
import os
from pyngrok import ngrok

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
        content += "【文件：{}】\n{}\n\n".format(filename, campus_data[filename])
    
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
        return prompt_template
    
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

【别名词典】
- "学校""航院""ZUA""郑航" = 郑州航空工业管理学院
- "新校区""龙湖""新校" = 龙子湖校区
- "卡""饭卡""校卡" = 校园一卡通
- "保安""门卫""校警" = 保卫处
- "迁户口""落户" = 户籍迁入/迁出
- "调宿舍""换宿舍" = 宿舍调整申请
- "证明""在读证明" = 在校学籍证明""".format(profile["name"])

def ask_xiaohang(question, user_type):
    system_prompt = build_system_prompt(user_type)
    relevant_data = get_relevant_data(question)
    
    user_message = """【学校资料】
{}

用户问题：{}""".format(relevant_data, question)
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_message}
    ]
    
    data = {
        "model": "Qwen/Qwen2.5-7B-Instruct",
        "messages": messages,
        "temperature": 0.1,
        "repetition_penalty": 1.1,
        "max_tokens": 2048
    }
    try:
        response = requests.post(API_URL, headers=headers, json=data, timeout=60)
        if response.status_code != 200:
            return "AI服务暂时不可用，您可以查看电话黄页获取帮助"
        result = response.json()
        answer = result["choices"][0]["message"]["content"]
        return answer
    except requests.exceptions.RequestException:
        return "网络连接异常，AI服务暂时不可用。您可以查看电话黄页获取帮助，或稍后再试"

def main():
    st.set_page_config(
        page_title="小航AI助手",
        page_icon="✈️",
        layout="wide"
    )

    try:
        public_url = ngrok.connect(8501)
        st.sidebar.success(f"🌐 公网访问地址：{public_url}")
    except Exception as e:
        st.sidebar.warning(f"⚠️ 无法创建公网隧道：{str(e)}")
        st.sidebar.info("请使用局域网地址：http://localhost:8501")

    st.title("✈️ 小航AI助手")
    st.subheader("郑州航空工业管理学院校园信息查询助手")

    if "user_type" not in st.session_state:
        st.session_state.user_type = None
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "page" not in st.session_state:
        st.session_state.page = "identity"

    sidebar = st.sidebar
    
    sidebar.title("功能导航")
    if st.session_state.user_type:
        sidebar.button("🏠 返回首页", on_click=lambda: st.session_state.update(page="identity", user_type=None, chat_history=[]))
        sidebar.button("💬 校园问答", on_click=lambda: st.session_state.update(page="chat"))
        sidebar.button("📞 电话黄页", on_click=lambda: st.session_state.update(page="phone"))
    
    if st.session_state.page == "identity":
        st.session_state.user_type = None
        st.session_state.chat_history = []
        
        st.markdown("---")
        st.header("请选择您的身份")
        st.markdown("请根据您的身份选择对应的选项，以便我为您提供更精准的服务")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🎓 大一新生", key="btn_1", use_container_width=True):
                st.session_state.user_type = "1"
                st.session_state.page = "chat"
                st.rerun()
        
        with col2:
            if st.button("📚 在校老生", key="btn_2", use_container_width=True):
                st.session_state.user_type = "2"
                st.session_state.page = "chat"
                st.rerun()
        
        with col3:
            if st.button("👨‍🏫 教师", key="btn_3", use_container_width=True):
                st.session_state.user_type = "3"
                st.session_state.page = "chat"
                st.rerun()
        
        st.markdown("---")
        st.info("""
            **身份说明：**
            - 🎓 **大一新生**：新入学的同学，需要了解报到流程、宿舍、学费、军训等信息
            - 📚 **在校老生**：已在校学习的同学，需要办理各类事务、查询信息
            - 👨‍🏫 **教师**：学校教职工，需要了解办事流程、政策规定等
        """)

    elif st.session_state.page == "chat":
        if not st.session_state.user_type:
            st.session_state.page = "identity"
            st.rerun()
        
        user_type = st.session_state.user_type
        profile = user_profiles[user_type]
        
        st.markdown(f"---")
        st.markdown(f"当前身份：**{profile['name']}**")
        
        st.markdown("### 推荐问题")
        questions = recommended_questions[user_type]
        cols = st.columns(2)
        for i, q in enumerate(questions):
            with cols[i % 2]:
                if st.button(q, key=f"btn_{user_type}_{i}", use_container_width=True):
                    answer = ask_xiaohang(q, user_type)
                    st.session_state.chat_history.append({"question": q, "answer": answer})
                    st.rerun()
        
        st.markdown("---")
        st.markdown("### 问答记录")
        for i, chat in enumerate(st.session_state.chat_history):
            with st.expander(f"Q: {chat['question']}"):
                st.markdown(f"**A:** {chat['answer']}")
        
        st.markdown("---")
        st.markdown("### 输入问题")
        question_input = st.text_input("请输入您的问题：", key="question_input")
        
        if st.button("发送", use_container_width=True):
            if question_input.strip():
                answer = ask_xiaohang(question_input, user_type)
                st.session_state.chat_history.append({"question": question_input, "answer": answer})
                st.rerun()
            else:
                st.warning("请输入有效问题")

    elif st.session_state.page == "phone":
        st.markdown("---")
        st.header("📞 郑州航空工业管理学院 - 电话黄页")
        st.markdown("以下是学校各部门的联系电话，方便您咨询相关事宜")
        
        st.markdown("---")
        
        cols = st.columns(2)
        for i, (dept, phone) in enumerate(phone_directory.items()):
            with cols[i % 2]:
                st.info(f"**{dept}**\n\n📱 {phone}")
        
        st.markdown("---")
        st.warning("""
            **温馨提示：**
            - 如需紧急帮助，请拨打校园110：**0371-61911110**
            - 总值班室电话：**0371-61911000**
        """)

if __name__ == "__main__":
    main()