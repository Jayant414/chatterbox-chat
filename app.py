import streamlit as st
import random
import time
import requests
import json
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

# --- 1. FREE CLOUD DATABASE CONFIGURATION (ZERO-SETUP NO SLEEP) ---
# This saves your data securely to an online cloud database instead of a local file
CLOUD_DB_URL = "https://kvdb.io/Jc9p8M7b6V5c4X3z2A1q/chatterbox_data"

def load_global_db_from_cloud():
    default_db = {
        "users": {"admin@chat.com": "adminpassword"},
        "group_memberships": {"Global Chat": ["admin@chat.com"]},
        "group_creators": {"Global Chat": "admin@chat.com"},
        "online_status": {},
        "messages": {"Global Chat": [{"id": "sys_start", "sender": "System", "content": "Welcome to ChatterBox!", "timestamp": "", "deleted_for_users": []}]}
    }
    try:
        response = requests.get(CLOUD_DB_URL, timeout=5)
        if response.status_code == 200:
            data = response.json()
            # Ensure essential structures exist
            if "users" not in data: data["users"] = default_db["users"]
            if "group_memberships" not in data: data["group_memberships"] = default_db["group_memberships"]
            if "group_creators" not in data: data["group_creators"] = default_db["group_creators"]
            if "online_status" not in data: data["online_status"] = default_db["online_status"]
            if "messages" not in data: data["messages"] = default_db["messages"]
            return data
        return default_db
    except:
        return default_db

def save_global_db_to_cloud(db_data):
    try:
        requests.post(CLOUD_DB_URL, json=db_data, timeout=5)
    except:
        pass

# --- 2. LAYOUT INITIALIZATION & CHATTERBOX SKIN ---
st.set_page_config(page_title="ChatterBox - Internet SMS", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #0b0c0e; color: #dbdee1; font-family: 'Inter', sans-serif; }
    [data-testid="stSidebar"] { background-color: #000000 !important; border-right: 1px solid #1a1c1e; }
    .block-container { padding-top: 2rem !important; max-width: 95% !important; }
    .chatterbox-title { font-size: 2rem; font-weight: bold; color: #ffffff; text-align: center; margin-bottom: 5px; }
    .sb-title { font-size: 1.8rem; font-weight: bold; color: #ffffff; margin-bottom: 20px; }
    .sb-status { color: #22c55e; font-size: 0.9rem; margin-bottom: 2px; }
    .sb-email { color: #ffffff; font-size: 0.95rem; margin-bottom: 25px; word-break: break-all; }
    .sb-section-header { color: #8e9297; font-size: 0.9rem; font-weight: 500; margin-bottom: 15px; margin-top: 15px; }
    .sb-online-user { color: #ffffff; font-size: 0.95rem; display: flex; align-items: center; gap: 8px; margin-bottom: 10px; padding-left: 5px; }
    .status-dot { width: 8px; height: 8px; background-color: #23a55a; border-radius: 50%; display: inline-block; }
    .pinned-header-yellow { background-color: #0b0c0e; padding: 5px 10px 15px 5px; font-size: 1.4rem; font-weight: bold; color: #ffffff; border-bottom: 1px solid #1a1c1e; margin-bottom: 15px; }
    div[data-testid="stForm"] { background-color: #16181c !important; border: 1px solid #282a30 !important; border-radius: 12px !important; padding: 40px !important; width: 420px !important; margin: 60px auto !important; box-shadow: 0 10px 30px rgba(0,0,0,0.5) !important; }
    .login-box-title { color: #ffffff; font-size: 1.6rem; font-weight: bold; text-align: center; margin-bottom: 25px; }
    [data-testid="stChatMessage"] { background-color: #16181c !important; border-radius: 8px !important; margin-bottom: 10px !important; }
    [data-testid="stChatInput"] { background-color: #202225 !important; border: 1px solid #2f3136 !important; border-radius: 8px !important; }
    div[data-testid="stForm"] button { background-color: #5865F2 !important; color: #ffffff !important; border: none !important; border-radius: 8px !important; padding: 12px !important; font-weight: 600 !important; margin-top: 15px !important; }
    div[data-testid="stForm"] button:hover { background-color: #4752c4 !important; }
    .toggle-wrapper { text-align: center; margin-top: 5px; }
    .member-name { color: #ffffff; font-size: 0.95rem; word-break: break-all; }
    </style>
""", unsafe_allow_html=True)

db = load_global_db_from_cloud()

if "logged_in_user" not in st.session_state:
    st.session_state.logged_in_user = None
if "auth_page_mode" not in st.session_state:
    st.session_state.auth_page_mode = "Login"
if "active_group" not in st.session_state:
    st.session_state.active_group = "Global Chat"
if "dont_remind_user_delete" not in st.session_state:
    st.session_state.dont_remind_user_delete = False
if "dont_remind_group_delete" not in st.session_state:
    st.session_state.dont_remind_group_delete = False
if "pending_user_delete" not in st.session_state:
    st.session_state.pending_user_delete = None
if "pending_group_delete" not in st.session_state:
    st.session_state.pending_group_delete = None

# --- 3. LOGIN SCREEN ---
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
                    if user_email in db["users"] and db["users"][user_email] == user_pass:
                        st.session_state.logged_in_user = user_email
                        st.rerun()
                    else:
                        st.error("Invalid credentials provided.")
                else:
                    db["users"][user_email] = user_pass
                    save_global_db_to_cloud(db)
                    st.session_state.logged_in_user = user_email
                    st.rerun()
            else:
                st.error("All fields are required.")
                
    st.markdown('<div class="toggle-wrapper">', unsafe_allow_html=True)
    if st.session_state.auth_page_mode == "Login":
        if st.button("Don't have an account? Sign up"):
            st.session_state.auth_page_mode = "Sign Up"
            st.rerun()
    else:
        if st.button("Already have an account? Login"):
            st.session_state.auth_page_mode = "Login"
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# --- 4. RUNTIME APPLICATION INTERFACE ---
else:
    current_user = st.session_state.logged_in_user
    db = load_global_db_from_cloud()

    st_autorefresh(interval=1000, limit=None, key="chatterbox_live_refresh")
    
    db["online_status"][current_user] = time.time()
    save_global_db_to_cloud(db)

    with st.sidebar:
        st.markdown(f'<div class="sb-title">💬 ChatterBox</div>', unsafe_allow_html=True)
        st.markdown('<div class="sb-status">Logged in as</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="sb-email">{current_user}</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="sb-section-header">📁 Chat Channels / Groups</div>', unsafe_allow_html=True)
        
        available_groups = []
        if current_user in db.get("group_memberships", {}).get("Global Chat", []):
            available_groups.append("Global Chat")
            
        for group_name, info in db.get("group_memberships", {}).items():
            if group_name != "Global Chat" and current_user in info:
                if group_name not in available_groups:
                    available_groups.append(group_name)
                    
        if st.session_state.active_group not in available_groups:
            st.session_state.active_group = available_groups[0] if available_groups else None
            
        for group_name in available_groups:
            group_creator = db.get("group_creators", {}).get(group_name, None)
            button_label = f"🌐 {group_name}" if group_name == "Global Chat" else f"🔒 {group_name}"
            
            if group_name != "Global Chat" and group_creator == current_user:
                g_col1, g_col2 = st.columns([0.75, 0.25])
                with g_col1:
                    if group_name == st.session_state.active_group:
                        st.button(f"👉 {group_name}", key=f"chan_{group_name}", use_container_width=True, type="primary")
                    else:
                        if st.button(button_label, key=f"chan_{group_name}", use_container_width=True):
                            st.session_state.active_group = group_name
                            st.rerun()
                with g_col2:
                    if st.button("🗑️", key=f"del_grp_{group_name}", use_container_width=True):
                        if st.session_state.dont_remind_group_delete:
                            if group_name in db["group_memberships"]: del db["group_memberships"][group_name]
                            if group_name in db["group_creators"]: del db["group_creators"][group_name]
                            if group_name in db["messages"]: del db["messages"][group_name]
                            save_global_db_to_cloud(db)
                            st.session_state.active_group = "Global Chat" if "Global Chat" in available_groups else None
                            st.rerun()
                        else:
                            st.session_state.pending_group_delete = group_name
                            st.session_state.pending_user_delete = None
            else:
                if group_name == st.session_state.active_group:
                    st.button(f"👉 {group_name}", key=f"chan_{group_name}", use_container_width=True, type="primary")
                else:
                    if st.button(button_label, key=f"chan_{group_name}", use_container_width=True):
                        st.session_state.active_group = group_name
                        st.rerun()

        with st.popover("➕ Create Custom Group", use_container_width=True):
            with st.form("create_group_form_block", clear_on_submit=True):
                new_group_title = st.text_input("Group Name").strip()
                member_emails_raw = st.text_area("Invite Members (Separated by commas)")
                if st.form_submit_button("Form Group Channel", use_container_width=True) and new_group_title:
                    if new_group_title != "Global Chat" and new_group_title not in db["group_memberships"]:
                        parsed_members = [email.strip() for email in member_emails_raw.split(",") if email.strip()]
                        if current_user not in parsed_members: parsed_members.append(current_user)
                        
                        db["group_creators"][new_group_title] = current_user
                        db["group_memberships"][new_group_title] = parsed_members
                        db["messages"][new_group_title] = [{"id": "sys_init", "sender": "System", "content": f"Group '{new_group_title}' created.", "timestamp": "", "deleted_for_users": []}]
                        save_global_db_to_cloud(db)
                        st.session_state.active_group = new_group_title
                        st.rerun()

        current_group = st.session_state.active_group
        group_creator = db.get("group_creators", {}).get(current_group, None)
        
        if current_group and group_creator == current_user:
            st.markdown('<div class="sb-section-header">⚙️ Group Settings (Owner)</div>', unsafe_allow_html=True)
            with st.popover("👥 Manage Group Members", use_container_width=True):
                with st.form("quick_add_form", clear_on_submit=True):
                    quick_email = st.text_input("Add Member by Email").strip()
                    if st.form_submit_button("Add") and quick_email:
                        if quick_email not in db["group_memberships"].get(current_group, []):
                            db["group_memberships"][current_group].append(quick_email)
                            save_global_db_to_cloud(db)
                            st.rerun()

                st.write("---")
                for member_email in db["group_memberships"].get(current_group, []):
                    m_col1, m_col2 = st.columns([0.75, 0.25])
                    with m_col1: st.markdown(f'<div class="member-name">👤 {member_email}</div>', unsafe_allow_html=True)
                    with m_col2:
                        if member_email != current_user:
                            if st.button("🗑️", key=f"del_mem_{member_email}"):
                                if st.session_state.dont_remind_user_delete:
                                    db["group_memberships"][current_group].remove(member_email)
                                    save_global_db_to_cloud(db)
                                    st.rerun()
                                else:
                                    st.session_state.pending_user_delete = member_email
                                    st.session_state.pending_group_delete = None

        st.markdown('<div class="sb-section-header">👥 Online Status Feed</div>', unsafe_allow_html=True)
        current_time_marker = time.time()
        for user_email, last_active_time in db.get("online_status", {}).items():
            if current_time_marker - last_active_time < 15:
                st.markdown(f'<div class="sb-online-user"><span class="status-dot"></span> {user_email.split("@")[0]}</div>', unsafe_allow_html=True)
        
        st.write("---")
        if st.button("🚪 Disconnect Session", use_container_width=True):
            st.session_state.logged_in_user = None
            st.rerun()

    # --- INLINE WARNING MODAL HOOKS ---
    if st.session_state.pending_user_delete and st.session_state.active_group:
        target_user = st.session_state.pending_user_delete
        with st.warning(f"⚠️ Remove {target_user} from group?"):
            chk_user = st.checkbox("Don't remind me again")
            w_c1, w_c2 = st.columns(2)
            with w_c1:
                if st.button("Confirm Removal", type="primary"):
                    if chk_user: st.session_state.dont_remind_user_delete = True
                    if target_user in db["group_memberships"].get(st.session_state.active_group, []):
                        db["group_memberships"][st.session_state.active_group].remove(target_user)
                        save_global_db_to_cloud(db)
                    st.session_state.pending_user_delete = None
                    st.rerun()
            with w_c2:
                if st.button("Cancel"):
                    st.session_state.pending_user_delete = None
                    st.rerun()

    if st.session_state.pending_group_delete:
        target_group = st.session_state.pending_group_delete
        with st.warning(f"⚠️ Delete entire group {target_group}?"):
            chk_group = st.checkbox("Don't remind me again")
            wg_c1, wg_c2 = st.columns(2)
            with wg_c1:
                if st.button("Confirm Deletion", type="primary"):
                    if chk_group: st.session_state.dont_remind_group_delete = True
                    if target_group in db["group_memberships"]: del db["group_memberships"][target_group]
                    if target_group in db["group_creators"]: del db["group_creators"][target_group]
                    if target_group in db["messages"]: del db["messages"][target_group]
                    save_global_db_to_cloud(db)
                    st.session_state.active_group = "Global Chat" if "Global Chat" in available_groups else None
                    st.session_state.pending_group_delete = None
                    st.rerun()
            with wg_c2:
                if st.button("Cancel"):
                    st.session_state.pending_group_delete = None
                    st.rerun()

    # --- MAIN CHAT CONTAINER HOOK ---
    if st.session_state.active_group:
        st.markdown(f'<div class="pinned-header-yellow">🌐 {st.session_state.active_group}</div>', unsafe_allow_html=True)
        if st.session_state.active_group not in db["messages"]:
            db["messages"][st.session_state.active_group] = []
        current_messages = db["messages"][st.session_state.active_group]
        
        chat_box = st.container(height=580)
        with chat_box:
            for msg in current_messages:
                if current_user in msg.get("deleted_for_users", []): continue
                if msg["sender"] == "System":
                    st.markdown(f"*{msg['content']}*")
                else:
                    with st.chat_message(name="user", avatar="💬"):
                        st.markdown(f"**@{msg['sender'].split('@')[0]} ({msg.get('timestamp', '')})**")
                        st.write(msg["content"])

        user_text = st.chat_input("Type a message...")
        if user_text:
            ist_timestamp = datetime.fromtimestamp(time.time() + 19800).strftime("%I:%M %p")
            current_messages.append({
                "id": str(random.randint(100000, 999999)),
                "sender": current_user,
                "content": user_text,
                "timestamp": ist_timestamp,
                "deleted_for_users": []
            })
            db["messages"][st.session_state.active_group] = current_messages
            save_global_db_to_cloud(db)
            st.rerun()
    else:
        st.markdown('<div class="pinned-header-yellow">🌐 No Channel Selected</div>', unsafe_allow_html=True)
        st.info("Ask the admin to whitelist your Gmail for access!")
