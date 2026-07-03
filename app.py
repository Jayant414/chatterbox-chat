import streamlit as st
import random
import os
import json
import time
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

# --- 1. GLOBAL PERMANENT FILE DATABASE SYSTEM ---
DB_FILE = "global_chat_db.json"

def load_global_db():
    default_db = {
        "users": {"admin@chat.com": {"password": "adminpassword"}},
        "groups": {"Global Chat": [{"id": "sys_start", "sender": "System", "type": "text", "content": "Welcome to ChatterBox!", "timestamp": "", "deleted_for_users": []}]}
    }
    
    # If file doesn't exist, create it clean
    if not os.path.exists(DB_FILE):
        with open(DB_FILE, "w") as f:
            json.dump(default_db, f)
        return default_db
        
    try:
        with open(DB_FILE, "r") as f:
            data = json.load(f)
            
        # CRUCIAL FIX: Automatically scans the database and purges old media entries or backup states
        if "groups" in data and "Global Chat" in data["groups"]:
            cleaned_messages = []
            for msg in data["groups"]["Global Chat"]:
                # Force everything to pure text and drop media blocks
                if msg.get("type", "text") == "text" and "Bones_to_Base-10" not in str(msg.get("content")):
                    msg["deleted_for_users"] = []
                    cleaned_messages.append(msg)
            if not cleaned_messages:
                cleaned_messages = default_db["groups"]["Global Chat"]
            data["groups"]["Global Chat"] = cleaned_messages
            
        if "users" not in data:
            data["users"] = default_db["users"]
            
        # Save the clean database state back to the disk
        with open(DB_FILE, "w") as f:
            json.dump(data, f)
        return data
    except:
        return default_db

def save_global_db(db_data):
    with open(DB_FILE, "w") as f:
        json.dump(db_data, f)

# --- 2. LAYOUT INITIALIZATION & CHATTERBOX SKIN ---
st.set_page_config(page_title="ChatterBox - Internet SMS", layout="wide")

st.markdown("""
    <style>
    /* Clean Global Canvas Background */
    .stApp { background-color: #0b0c0e; color: #dbdee1; font-family: 'Inter', sans-serif; }
    [data-testid="stSidebar"] { background-color: #000000 !important; border-right: 1px solid #1a1c1e; }
    
    .block-container { padding-top: 2rem !important; max-width: 95% !important; }
    
    .chatterbox-title {
        font-size: 2rem;
        font-weight: bold;
        color: #ffffff;
        text-align: center;
        margin-bottom: 5px;
    }
    
    /* Clean Sidebar Layout (Wiped out all backup items) */
    .sb-title { font-size: 1.8rem; font-weight: bold; color: #ffffff; margin-bottom: 20px; }
    .sb-status { color: #22c55e; font-size: 0.9rem; margin-bottom: 2px; }
    .sb-email { color: #ffffff; font-size: 0.95rem; margin-bottom: 25px; word-break: break-all; }
    .sb-section-header { color: #8e9297; font-size: 0.9rem; font-weight: 500; margin-bottom: 15px; }
    .sb-online-user { color: #ffffff; font-size: 0.95rem; display: flex; align-items: center; gap: 8px; margin-bottom: 10px; padding-left: 5px; }
    .status-dot { width: 8px; height: 8px; background-color: #23a55a; border-radius: 50%; display: inline-block; }
    
    .pinned-header-yellow {
        background-color: #0b0c0e;
        padding: 5px 10px 15px 5px;
        font-size: 1.4rem;
        font-weight: bold;
        color: #ffffff;
        border-bottom: 1px solid #1a1c1e;
        margin-bottom: 15px;
    }
    
    /* PERFECT SQUARE LOGIN CARD DESIGN */
    div[data-testid="stForm"] {
        background-color: #16181c !important;
        border: 1px solid #282a30 !important;
        border-radius: 12px !important;
        padding: 40px !important;
        width: 420px !important;
        margin: 60px auto !important;
        box-shadow: 0 10px 30px rgba(0,0,0,0.5) !important;
    }
    
    .login-box-title {
        color: #ffffff;
        font-size: 1.6rem;
        font-weight: bold;
        text-align: center;
        margin-bottom: 25px;
    }
    
    [data-testid="stChatMessage"] { background-color: #16181c !important; border-radius: 8px !important; margin-bottom: 10px !important; }
    [data-testid="stChatInput"] { background-color: #202225 !important; border: 1px solid #2f3136 !important; border-radius: 8px !important; }
    
    /* Blue Button Style */
    div[data-testid="stForm"] button {
        background-color: #5865F2 !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 12px !important;
        font-weight: 600 !important;
        margin-top: 15px !important;
    }
    div[data-testid="stForm"] button:hover {
        background-color: #4752c4 !important;
    }
    
    .toggle-wrapper { text-align: center; margin-top: 5px; }
    </style>
""", unsafe_allow_html=True)

db = load_global_db()

if "logged_in_user" not in st.session_state:
    st.session_state.logged_in_user = None
if "auth_page_mode" not in st.session_state:
    st.session_state.auth_page_mode = "Login"

active_group = "Global Chat"

# --- 3. CORE INSTANT-RESPONSE LOGIN SCREEN ---
if st.session_state.logged_in_user is None:
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown('<div class="chatterbox-title">💬 ChatterBox</div>', unsafe_allow_html=True)
    
    with st.form("auth_form_block"):
        st.markdown(f'<div class="login-box-title">{st.session_state.auth_page_mode}</div>', unsafe_allow_html=True)
        
        user_email = st.text_input("Username / Email", placeholder="kini.jayanth@gmail.com", label_visibility="collapsed").strip()
        user_pass = st.text_input("Password", type="password", placeholder="Password", label_visibility="collapsed")
        
        submit_auth = st.form_submit_button(st.session_state.auth_page_mode, use_container_width=True)
        
        if submit_auth:
            if user_email and user_pass:
                if st.session_state.auth_page_mode == "Login":
                    if user_email in db["users"] and db["users"][user_email]["password"] == user_pass:
                        st.session_state.logged_in_user = user_email
                        st.rerun()
                    else:
                        st.error("Invalid credentials provided.")
                else:
                    db["users"][user_email] = {"password": user_pass}
                    save_global_db(db)
                    st.session_state.logged_in_user = user_email
                    st.rerun()
            else:
                st.error("All fields are required.")
                
    st.markdown('<div class="toggle-wrapper">', unsafe_allow_html=True)
    if st.session_state.auth_page_mode == "Login":
        if st.button("Don't have an account? Sign up", type="secondary"):
            st.session_state.auth_page_mode = "Sign Up"
            st.rerun()
    else:
        if st.button("Already have an account? Login", type="secondary"):
            st.session_state.auth_page_mode = "Login"
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# --- 4. THE CHATTERBOX APPLICATION RUNTIME INTERFACE ---
else:
    current_user = st.session_state.logged_in_user
    db = load_global_db()

    # --- 5. HIGH-SPEED BACKGROUND AUTO-REFRESH ENGINE ---
    st_autorefresh(interval=1000, limit=None, key="chatterbox_live_refresh")

    # --- LEFT SIDEBAR PANEL ---
    with st.sidebar:
        st.markdown(f'<div class="sb-title">💬 ChatterBox</div>', unsafe_allow_html=True)
        
        if st.button("📥 Install ChatterBox App", type="primary", use_container_width=True):
            st.components.v1.html("""
                <script>
                alert("Click the three dots button in your browser address bar top right corner and select 'Install ChatterBox' to use it as a desktop software!");
                </script>
            """, height=0)
        
        st.write("")
        st.markdown('<div class="sb-status">Logged in as</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="sb-email">{current_user}</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="sb-section-header">👥 Online Status Feed</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="sb-online-user"><span class="status-dot"></span> {current_user.split("@")[0]}</div>', unsafe_allow_html=True)
        
        st.write("---")
        if st.button("🗑️ Clear Chat History", use_container_width=True):
            db["groups"][active_group] = [{"id": "sys_start", "sender": "System", "type": "text", "content": "Chat database reset.", "timestamp": "", "deleted_for_users": []}]
            save_global_db(db)
            st.rerun()
            
        st.write("")
        if st.button("🚪 Disconnect Session", use_container_width=True, type="secondary"):
            st.session_state.logged_in_user = None
            st.rerun()

    # --- MAIN INTERFACE PANEL ---
    st.markdown(f'<div class="pinned-header-yellow">🌐 {active_group}</div>', unsafe_allow_html=True)
    
    current_messages = db["groups"][active_group]
    
    chat_box = st.container(height=580)
    with chat_box:
        for msg in current_messages:
            if "deleted_for_users" not in msg:
                msg["deleted_for_users"] = []
                
            if current_user in msg["deleted_for_users"]:
                continue
                
            if msg["sender"] == "System":
                st.markdown(f"*{msg['content']}*")
            else:
                display_name = f"{msg['sender'].split('@')[0]} ({msg.get('timestamp', '')})"
                
                with st.chat_message(name="user", avatar="💬"):
                    st.markdown(f"**@{display_name}**")
                    if msg.get("type", "text") == "text":
                        st.write(msg["content"])

    # --- TEXT INPUT CONTROLS ---
    st.write("---")
    user_text = st.chat_input("Type a message or use Win + . for emojis...")
    if user_text:
        msg_id = str(random.randint(100000, 999999))
        db["groups"][active_group].append({
            "id": msg_id, 
            "sender": current_user, 
            "type": "text", 
            "content": user_text, 
            "timestamp": datetime.now().strftime("%I:%M %p"), 
            "deleted_for_users": []
        })
        save_global_db(db)
        st.rerun()
