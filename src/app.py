import streamlit as st
import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.api import call_ai, build_user_message, trim_history
from src.prompts import build_system_prompt
from src.config import USER_PROFILES, RECOMMENDED_QUESTIONS, PHONE_DIRECTORY

def ask_xiaohang(question, user_type, messages=None):
    if messages is None:
        messages = []
    
    if not messages:
        system_prompt = build_system_prompt(user_type, question)
        messages.append({"role": "system", "content": system_prompt})
    
    user_message = build_user_message(question)
    messages.append({"role": "user", "content": user_message})
    
    messages = trim_history(messages)
    
    answer, error = call_ai(messages)
    if error:
        return f"AI服务暂时不可用，您可以查看电话黄页获取帮助。错误信息：{error}", messages
    messages.append({"role": "assistant", "content": answer})
    return answer, messages

def main():
    st.set_page_config(
        page_title="小航AI助手",
        page_icon="✈️",
        layout="wide"
    )



    st.markdown("""
        <style>
        .stDeployButton {
            display: none;
        }
        header {
            visibility: hidden;
        }
        </style>
    """, unsafe_allow_html=True)

    st.title("✈️ 小航AI助手")
    st.subheader("郑州航空工业管理学院校园信息查询助手")

    if "user_type" not in st.session_state:
        st.session_state.user_type = None
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "page" not in st.session_state:
        st.session_state.page = "identity"

    sidebar = st.sidebar
    
    sidebar.title("功能导航")
    if st.session_state.user_type:
        sidebar.button("🏠 返回首页", on_click=lambda: st.session_state.update(page="identity", user_type=None, chat_history=[], messages=[]))
        sidebar.button("💬 校园问答", on_click=lambda: st.session_state.update(page="chat"))
        sidebar.button("📞 电话黄页", on_click=lambda: st.session_state.update(page="phone"))
    
    if st.session_state.page == "identity":
        st.session_state.user_type = None
        st.session_state.chat_history = []
        st.session_state.messages = []
        
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
        profile = USER_PROFILES[user_type]
        
        st.markdown(f"---")
        st.markdown(f"当前身份：**{profile['name']}**")
        
        st.markdown("### 推荐问题")
        questions = RECOMMENDED_QUESTIONS[user_type]
        cols = st.columns(2)
        for i, q in enumerate(questions):
            with cols[i % 2]:
                if st.button(q, key=f"btn_{user_type}_{i}", use_container_width=True):
                    with st.spinner("小航正在思考..."):
                        answer, messages = ask_xiaohang(q, user_type, st.session_state.messages)
                    st.session_state.messages = messages
                    st.session_state.chat_history.append({
                        "question": q, 
                        "answer": answer,
                        "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        "identity": profile['name']
                    })
                    st.rerun()
        
        st.markdown("---")
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown("### 问答记录")
        with col2:
            if st.button("🗑️ 清空问答记录", key="clear_history", use_container_width=True):
                st.session_state.chat_history = []
                st.session_state.messages = []
                st.rerun()
        
        for i, chat in enumerate(st.session_state.chat_history):
            timestamp = chat.get('timestamp', '')
            with st.expander(f"Q: {chat['question']}"):
                if timestamp:
                    st.markdown(f"⏰ {timestamp}")
                st.markdown(f"**A:** {chat['answer']}")
        
        st.markdown("---")
        st.markdown("### 输入问题")
        question_input = st.text_input("请输入您的问题：", key="question_input")
        
        if st.button("发送", use_container_width=True):
            if question_input.strip():
                with st.spinner("小航正在思考..."):
                    answer, messages = ask_xiaohang(question_input, user_type, st.session_state.messages)
                st.session_state.messages = messages
                st.session_state.chat_history.append({
                    "question": question_input, 
                    "answer": answer,
                    "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    "identity": profile['name']
                })
                st.rerun()
            else:
                st.warning("请输入有效问题")

        st.markdown("---")
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown("### 问答历史")
        with col2:
            if st.button("🗑️ 清空历史", key="clear_history_bottom", use_container_width=True):
                st.session_state.chat_history = []
                st.session_state.messages = []
                st.rerun()
        if st.session_state.chat_history:
            for chat in reversed(st.session_state.chat_history):
                timestamp = chat.get('timestamp', '')
                identity = chat.get('identity', '')
                question = chat.get('question', '')
                if timestamp:
                    time_only = timestamp.split(' ')[1] if ' ' in timestamp else timestamp
                else:
                    time_only = ''
                st.markdown(f"**[{time_only}] {identity} 提问：{question}**")
        else:
            st.info("暂无问答历史")

    elif st.session_state.page == "phone":
        st.markdown("---")
        st.header("📞 郑州航空工业管理学院 - 电话黄页")
        st.markdown("以下是学校各部门的联系电话，方便您咨询相关事宜")
        
        st.markdown("---")
        
        cols = st.columns(2)
        for i, (dept, phone) in enumerate(PHONE_DIRECTORY.items()):
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