import streamlit as st
from openai import OpenAI

st.set_page_config(page_title="Creative Role Studio", page_icon="🎭", layout="centered")
st.title("🎭 Creative Role Studio")
st.caption("Arts and Advanced Big Data | Assignment 07: Role-Based Chatbot")

# 프리셋 역할 정의 (바다 탐험, 시나리오 작가, 아트 큐레이터 등 다채로운 구성)
PRESETS = {
    "Ocean Explorer": "You are a passionate marine biologist and deep-sea explorer. You love the mysteries of the abyss, ocean currents, and marine life. Speak enthusiastically and use poetic, vivid ocean metaphors.",
    "Noir Screenwriter": "You are a seasoned noir film screenwriter and story consultant. You give sharp, atmosphere-focused advice on lighting, plot tension, character depth, and dark cinematic aesthetics.",
    "Creative Art Director": "You are an avant-garde visual art director. You advise on graphic balance, generative forms, color harmony, and visual storytelling with clear, inspiring feedback.",
    "Story Worldbuilder": "You are an imaginative narrative worldbuilder. Help users construct rich sci-fi and fantasy settings, mythologies, environments, and faction conflicts.",
    "Custom Role": ""
}

# ---------- 사이드바 설정 ----------
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # API 키 입력창 (secrets가 있으면 자동 로드, 없으면 직접 입력 가능)
    api_key = st.text_input(
        "OpenAI API Key",
        type="password",
        value=st.secrets.get("OPENAI_API_KEY", "") if hasattr(st, "secrets") else "",
        help="Enter your OpenAI API key to start chatting."
    )
    
    model = st.selectbox("Model", ["gpt-4o-mini", "gpt-4o"])
    temperature = st.slider("Creativity (Temperature)", min_value=0.0, max_value=1.5, value=0.8, step=0.1)
    
    st.divider()
    st.subheader("🎭 Select Persona")
    preset_choice = st.selectbox("Preset Roles", list(PRESETS.keys()))
    
    role_prompt = st.text_area(
        "System Prompt (Role Description)",
        value=PRESETS[preset_choice],
        height=140,
        placeholder="Define how the AI should behave and speak..."
    )
    
    if st.button("Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# ---------- 대화 세션 관리 ----------
if "messages" not in st.session_state:
    st.session_state.messages = []

# 역할이 변경되면 대화 초기화
if st.session_state.get("current_role") != role_prompt:
    st.session_state.current_role = role_prompt
    st.session_state.messages = []

if role_prompt:
    st.info(f"**Active Persona:** {preset_choice}")
else:
    st.warning("Please select or define a persona in the sidebar.")

# 기존 대화 출력
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ---------- 사용자 입력 및 OpenAI API 호출 ----------
if user_input := st.chat_input("Talk to your AI character..."):
    if not api_key:
        st.error("Please provide an OpenAI API key in the sidebar.")
        st.stop()
        
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)
        
    client = OpenAI(api_key=api_key)
    system_instruction = role_prompt if role_prompt.strip() else "You are a helpful and creative AI assistant."
    
    conversation = [{"role": "system", "content": system_instruction}] + st.session_state.messages
    
    with st.chat_message("assistant"):
        try:
            stream = client.chat.completions.create(
                model=model,
                messages=conversation,
                temperature=temperature,
                stream=True
            )
            reply = st.write_stream(
                chunk.choices[0].delta.content or ""
                for chunk in stream
                if chunk.choices
            )
        except Exception as err:
            st.error(f"Error communicating with OpenAI: {err}")
            st.stop()
            
    st.session_state.messages.append({"role": "assistant", "content": reply})
