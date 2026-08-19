
import streamlit as st
import requests
import uuid

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="AI Career Copilot", page_icon="🚀", layout="centered")

# --- PROFESSIONAL STYLING (CSS) ---
st.markdown("""
    <style>
    .stApp { background-color: #0f1117; color: white; }
    .result-box { background-color: #1e1e2e; border-radius: 15px; padding: 25px; box-shadow: 0 4px 10px rgba(0,0,0,0.5); border: 1px solid #3b4252; }
    h1, h2, h3 { color: #58a6ff !important; text-align: center; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
    .stButton>button { border-radius: 25px; width: 100%; height: 50px; font-weight: bold; background: linear-gradient(90deg, #4b6cb7 0%, #182848 100%); color: white; border: none; transition: 0.3s; }
    .stButton>button:hover { background: linear-gradient(90deg, #58a6ff 0%, #4b6cb7 100%); transform: scale(1.02); }
    .whatsapp-btn { background-color: #25D366; color: white !important; padding: 12px 24px; text-decoration: none; border-radius: 25px; font-weight: bold; display: inline-block; text-align: center; width: 100%; transition: 0.3s; }
    .whatsapp-btn:hover { background-color: #1ebd5a; }

    /* 🌟 NAYA: Chat input ko bottom par fix karne ke liye */
    [data-testid="stChatInput"] {
        position: fixed;
        bottom: 20px;
        background-color: #1e1e2e;
        z-index: 100;
    }
    </style>
""", unsafe_allow_html=True)

# --- SESSION STATE SETUP ---
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if "users_db" not in st.session_state:
    st.session_state["users_db"] = {"admin": "1234"}

# --- 🔐 PAGE 1: LOGIN & SIGN UP PAGE ---
def login_signup_page():
    st.title("🚀 AI Career Copilot")
    st.markdown("<p style='text-align: center; color: #a9b1d6; font-size: 18px;'>Unlock your career potential with AI-driven insights.</p>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["🔑 Secure Login", "📝 Create Account"])
    
    with tab1:
        st.markdown("### Welcome Back!")
        username = st.text_input("Username", key="login_user")
        password = st.text_input("Password", type="password", key="login_pass")
        
        if st.button("Login To Dashboard", key="login_btn"):
            if username in st.session_state["users_db"] and st.session_state["users_db"][username] == password: 
                st.session_state["logged_in"] = True
                st.session_state["user_id"] = username
                st.rerun()
            else:
                st.error("Galat Username ya Password! Kripya dobara try karein.")

    with tab2:
        st.markdown("### Join The AI Revolution")
        new_username = st.text_input("Choose Username", key="signup_user")
        new_password = st.text_input("Create Password", type="password", key="signup_pass")
        
        if st.button("Sign Up Now", key="signup_btn"):
            if new_username in st.session_state["users_db"]:
                st.error("Yeh Username pehle se maujood hai.")
            elif new_username != "" and new_password != "":
                st.session_state["users_db"][new_username] = new_password
                st.success("🎉 Account ban gaya! Ab aap login kar sakte hain.")
            else:
                st.warning("Kripya Username aur Password dono bharein.")

# --- 🚀 PAGE 2: MAIN DASHBOARD ---
def main_app():
    col1, col2 = st.columns([0.85, 0.15])
    with col1:
        st.markdown(f"<h2 style='text-align: left; color: white;'>Welcome, {st.session_state.get('user_id', 'User')} 👋</h2>", unsafe_allow_html=True)
    with col2:
        if st.button("Logout", key="logout_btn"):
            st.session_state["logged_in"] = False
            st.rerun()

    st.markdown("---")
    
    tab_ats, tab_hr, tab_dsa = st.tabs(["📄 ATS Scanner", "🎙️ HR Mock Interview", "🎁 Premium DSA PDF"])

    # --- TAB 1: ATS SCANNER ---
    with tab_ats:
        st.markdown("### 📋 Resume Analysis Workflow")
        uploaded_file = st.file_uploader("Drop your PDF Resume here", type=["pdf"], key="ats_upload")
        jd_text = st.text_area("Job Description (Optional)", height=100, placeholder="Paste target job description...")
        if uploaded_file and st.button("✨ Initialize AI Analysis", key="analyze_btn"):
            with st.spinner("🤖 AI is reading your resume..."):
                files = {"file": (uploaded_file.name, uploaded_file, "application/pdf")}
                data = {"profile_id": str(uuid.uuid4()), "job_description": jd_text}
                try:
                    response = requests.post("https://career-copilot-kqsn.onrender.com/upload-resume", files=files, data=data)
                    if response.status_code == 200:
                        res = response.json()
                        st.balloons()
                        
                        # Resume text ko session mein save kar rahe hain HR bot ke liye
                        st.session_state["saved_resume_text"] = res.get("text_preview", "")
                        
                        st.markdown("### 🎯 Final ATS Assessment")
                        st.markdown(f"<div class='result-box'>{res.get('ai_analysis', 'Error')}</div>", unsafe_allow_html=True)
                    else:
                        st.error(f"Backend Server Error: {response.text}")
                except Exception as e:
                    st.error(f"Connection Error: {e}")

    # --- TAB 2: MOCK HR INTERVIEW ---
    with tab_hr:
        st.markdown("### 🎙️ AI Mock Technical Round")
        st.info("💡 Tip: Upload your resume in the ATS Scanner first so the HR bot can ask personalized questions!")
        
        if "chat_messages" not in st.session_state:
            st.session_state["chat_messages"] = [{"role": "assistant", "content": "Hello! I am your AI Interviewer. Upload your resume in the first tab and say 'Hi' to begin your technical round."}]

        for msg in st.session_state["chat_messages"]:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        if user_msg := st.chat_input("Type your message here..."):
            st.session_state["chat_messages"].append({"role": "user", "content": user_msg})
            with st.chat_message("user"):
                st.markdown(user_msg)
                
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    try:
                        bot_data = {
                            "resume_text": st.session_state.get("saved_resume_text", ""),
                            "user_answer": user_msg
                        }
                        bot_res = requests.post("http://localhost:8000/hr-bot", data=bot_data)
                        
                        if bot_res.status_code == 200:
                            ai_reply = bot_res.json().get("reply", "Error getting response.")
                            st.markdown(ai_reply)
                            st.session_state["chat_messages"].append({"role": "assistant", "content": ai_reply})
                        else:
                            st.error("Backend API Error")
                    except Exception as e:
                        st.error(f"Error connecting to AI: {e}")

    # --- TAB 3: WHATSAPP LEAD GEN ---
    with tab_dsa:
        st.markdown("### 🚀 Master Top Tech Interviews")
        st.write("Top IT companies mein puche gaye actual DSA aur technical questions ka poora collection!")
        
        st.markdown("""
        <div class='result-box' style='text-align:center;'>
            <h3>📘 Company-Wise DSA Cheat Sheet</h3>
            <p>✔️ TCS, Infosys, Wipro, Amazon & More</p>
            <p>✔️ Array, Linked Lists, Trees & Dynamic Programming</p>
            <p>✔️ Core Concepts & Algorithms</p>
            <br>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Yahan apna number daaliye
        my_whatsapp_number = "7357502080"
        message = "Hi! Mujhe aapki Company-wise DSA PDF chahiye."
        whatsapp_link = f"https://wa.me/{7357502080}?text={message}"
        
        st.markdown(f'<a href="{whatsapp_link}" target="_blank" class="whatsapp-btn">🟢 Message Me on WhatsApp to Get PDF</a>', unsafe_allow_html=True)

# --- APP ROUTER ---
if st.session_state["logged_in"]:
    main_app()
else:
    login_signup_page()
