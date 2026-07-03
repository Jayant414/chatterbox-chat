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
        "groups": {"Global Chat": [{"id": "sys_start", "sender": "System", "type": "text", "content": "Welcome to ChatterBox!", "timestamp": "", "deleted_for_users": []}]},
        "group_memberships": {"Global Chat": ["admin@chat.com"]},  # Whitelist pool for Global Chat
        "group_creators": {"Global Chat": "admin@chat.com"},        # Admin set as the absolute creator/owner of Global Chat
        "online_status": {}
    }
    
    if not os.path.exists(DB_FILE):
        with open(DB_FILE, "w") as f:
            json.dump(default_db, f)
        return default_db
        
    try:
        with open(DB_FILE, "r") as f:
            data = json.load(f)
            
        if "groups" in data and "Global Chat" in data["groups"]:
            cleaned_messages = []
            for msg in data["groups"]["Global Chat"]:
                if msg.get("type", "text") == "text" and "Bones_to_Base-10" not in str(msg.get("content")):
                    msg["deleted_for_users"] = []
                    cleaned_messages.append(msg)
            if not cleaned_messages:
                cleaned_messages = default_db["groups"]["Global Chat"]
            data["groups"]["Global Chat"] = cleaned_messages
            
        if "users" not in data:
            data["users"] = default_db["users"]
        if "group_memberships" not in data:
            data["group_memberships"] = {"Global Chat": ["admin@chat.com"]}
        if "Global Chat" not in data["group_memberships"]:
            data["group_memberships"]["Global Chat"] = ["admin@chat.com"]
        if "group_creators" not in data:
            data["group_creators"] = {"Global Chat": "admin@chat.com"}
        if "Global Chat" not in data["group_creators"]:
            data["group_creators"]["Global Chat"] = "admin@chat.com"
        if "online_status" not in data:
            data["online_status"] = {}
            
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
    
    /* Clean Sidebar Layout */
    .sb-title { font-size: 1.8rem; font-weight: bold; color: #ffffff; margin-bottom: 20px; }
    .sb-status { color: #22c55e; font-size: 0.9rem; margin-bottom: 2px; }
    .sb-email { color: #ffffff; font-size: 0.95rem; margin-bottom: 25px; word-break: break-all; }
    .sb-section-header { color: #8e9297; font-size: 0.9rem; font-weight: 500; margin-bottom: 15px; margin-top: 15px; }
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
    
    /* Utility spacing for lists */
    .member-row { display: flex; align-items: center; justify-content: space-between; margin-bottom: 8px; }
    .member-name { color: #ffffff; font-size: 0.95rem; word-break: break-all; }
    </style>
""", unsafe_allow_html=True)

db = load_global_db()

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

# --- 3. PASSWORD-BASED AUTHENTICATION ---
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
    
    db["online_status"][current_user] = time.time()
    save_global_db(db)

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
        
        # --- GROUP CREATION & SELECTION MANAGEMENT SYSTEM ---
        st.markdown('<div class="sb-section-header">📁 Chat Channels / Groups</div>', unsafe_allow_html=True)
        
        # Only show Global Chat if the user is explicitly added to its whitelist pool
        available_groups = []
        if current_user in db.get("group_memberships", {}).get("Global Chat", []):
            available_groups.append("Global Chat")
            
        for group_name, info in db.get("group_memberships", {}).items():
            if group_name != "Global Chat" and current_user in info:
                if group_name not in available_groups:
                    available_groups.append(group_name)
                    
        if st.session_state.active_group not in available_groups:
            if available_groups:
                st.session_state.active_group = available_groups[0]
            else:
                st.session_state.active_group = None
            
        for group_name in available_groups:
            group_creator = db.get("group_creators", {}).get(group_name, None)
            button_label = f"🌐 {group_name}" if group_name == "Global Chat" else f"🔒 {group_name}"
            
            # Creator gets a layout option to delete custom groups directly here
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
                    if st.button("🗑️", key=f"del_grp_{group_name}", help=f"Delete entire {group_name} group", use_container_width=True):
                        if st.session_state.dont_remind_group_delete:
                            if group_name in db.get("group_memberships", {}):
                                del db["group_memberships"][group_name]
                            if group_name in db.get("groups", {}):
                                del db["groups"][group_name]
                            if group_name in db.get("group_creators", {}):
                                del db["group_creators"][group_name]
                            save_global_db(db)
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

        # Popover Form Module to safely create custom chat channels
        with st.popover("➕ Create Custom Group", use_container_width=True):
            with st.form("create_group_form_block", clear_on_submit=True):
                new_group_title = st.text_input("Group Name", placeholder="e.g., Squad Goals").strip()
                member_emails_raw = st.text_area("Invite Members (Enter Gmails separated by commas)", placeholder="friend1@gmail.com, friend2@gmail.com")
                submit_new_group = st.form_submit_button("Form Group Channel", use_container_width=True)
                
                if submit_new_group:
                    if new_group_title:
                        if new_group_title == "Global Chat":
                            st.error("That channel label is reserved.")
                        elif new_group_title in db.get("group_memberships", {}):
                            st.error("This group name already exists.")
                        else:
                            parsed_members = [email.strip() for email in member_emails_raw.split(",") if email.strip()]
                            if current_user not in parsed_members:
                                parsed_members.append(current_user)
                                
                            if "group_memberships" not in db:
                                db["group_memberships"] = {}
                            if "groups" not in db:
                                db["groups"] = {}
                            if "group_creators" not in db:
                                db["group_creators"] = {}
                                
                            db["group_creators"][new_group_title] = current_user
                            db["group_memberships"][new_group_title] = parsed_members
                            db["groups"][new_group_title] = [{
                                "id": f"sys_{str(random.randint(100000, 999999))}", 
                                "sender": "System", 
                                "type": "text", 
                                "content": f"Group '{new_group_title}' generated by creator.", 
                                "timestamp": "",
                                "deleted_for_users": []
                            }]
                            
                            save_global_db(db)
                            st.session_state.active_group = new_group_title
                            st.toast(f"🔒 Channel '{new_group_title}' successfully created!")
                            st.rerun()
                    else:
                        st.error("Group name cannot be left blank.")

        # --- SIMPLIFIED MEMBER MANAGEMENT PANEL (CREATOR/ADMIN-ONLY) ---
        current_group = st.session_state.active_group
        group_creator = db.get("group_creators", {}).get(current_group, None)
        
        if current_group and group_creator == current_user:
            st.markdown('<div class="sb-section-header">⚙️ Group Settings (Owner)</div>', unsafe_allow_html=True)
            
            with st.popover("👥 Manage Group Members", use_container_width=True):
                st.write(f"**Members in {current_group}:**")
                
                with st.form("quick_add_form", clear_on_submit=True):
                    quick_email = st.text_input("Add Member by Email", placeholder="user@gmail.com").strip()
                    if st.form_submit_button("Add", use_container_width=True):
                        if quick_email and quick_email not in db["group_memberships"].get(current_group, []):
                            if current_group not in db["group_memberships"]:
                                db["group_memberships"][current_group] = []
                            db["group_memberships"][current_group].append(quick_email)
                            db["groups"][current_group].append({
                                "id": f"sys_{str(random.randint(100000, 999999))}", "sender": "System", "type": "text",
                                "content": f"{quick_email} was added to the group.", "timestamp": "", "deleted_for_users": []
                            })
                            save_global_db(db)
                            st.rerun()

                st.write("---")
                for member_email in db["group_memberships"].get(current_group, []):
                    m_col1, m_col2 = st.columns([0.75, 0.25])
                    with m_col1:
                        st.markdown(f'<div class="member-name">👤 {member_email}</div>', unsafe_allow_html=True)
                    with m_col2:
                        if member_email != current_user:
                            if st.button("🗑️", key=f"del_mem_{member_email}"):
                                if st.session_state.dont_remind_user_delete:
                                    db["group_memberships"][current_group].remove(member_email)
                                    db["groups"][current_group].append({
                                        "id": f"sys_{str(random.randint(100000, 999999))}", "sender": "System", "type": "text",
                                        "content": f"{member_email} was removed from the group.", "timestamp": "", "deleted_for_users": []
                                    })
                                    save_global_db(db)
                                    st.rerun()
                                else:
                                    st.session_state.pending_user_delete = member_email
                                    st.session_state.pending_group_delete = None

        # --- DYNAMIC INTERNET ONLINE FEED ENGINE ---
        st.markdown('<div class="sb-section-header">👥 Online Status Feed</div>', unsafe_allow_html=True)
        
        current_time_marker = time.time()
        active_online_count = 0
        
        for user_email, last_active_time in db.get("online_status", {}).items():
            if current_time_marker - last_active_time < 15:
                display_clean_name = user_email.split("@")[0]
                st.markdown(f'<div class="sb-online-user"><span class="status-dot"></span> {display_clean_name}</div>', unsafe_allow_html=True)
                active_online_count += 1
                
        if active_online_count == 0:
            st.markdown(f'<div class="sb-online-user"><span class="status-dot"></span> {current_user.split("@")[0]}</div>', unsafe_allow_html=True)
        
        st.write("---")
        if st.session_state.active_group and st.button("🗑️ Clear Chat History", use_container_width=True):
            db["groups"][st.session_state.active_group] = [{"id": "sys_start", "sender": "System", "type": "text", "content": "Chat database reset.", "timestamp": "", "deleted_for_users": []}]
            save_global_db(db)
            st.rerun()
            
        st.write("")
        if st.button("🚪 Disconnect Session", use_container_width=True, type="secondary"):
            st.session_state.logged_in_user = None
            st.rerun()

    # --- INLINE WARNING MODAL HOOKS ---
    if st.session_state.pending_user_delete and st.session_state.active_group:
        target_user = st.session_state.pending_user_delete
        with st.warning(f"⚠️ Warning: Clicking this button will remove the user ({target_user}) from the group."):
            chk_user = st.checkbox("Don't remind me again", key="chk_dont_rem_user")
            w_c1, w_c2 = st.columns(2)
            with w_c1:
                if st.button("Confirm Removal", type="primary", use_container_width=True):
                    if chk_user:
                        st.session_state.dont_remind_user_delete = True
                    if target_user in db["group_memberships"].get(st.session_state.active_group, []):
                        db["group_memberships"][st.session_state.active_group].remove(target_user)
                        db["groups"][st.session_state.active_group].append({
                            "id": f"sys_{str(random.randint(100000, 999999))}", "sender": "System", "type": "text",
                            "content": f"{target_user} was removed from the group.", "timestamp": "", "deleted_for_users": []
                        })
                        save_global_db(db)
                    st.session_state.pending_user_delete = None
                    st.rerun()
            with w_c2:
                if st.button("Cancel", use_container_width=True):
                    st.session_state.pending_user_delete = None
                    st.rerun()

    if st.session_state.pending_group_delete:
        target_group = st.session_state.pending_group_delete
        with st.warning(f"⚠️ Warning: Clicking this button will remove the group ({target_group})."):
            chk_group = st.checkbox("Don't remind me again", key="chk_dont_rem_grp")
            wg_c1, wg_c2 = st.columns(2)
            with wg_c1:
                if st.button("Confirm Deletion", type="primary", use_container_width=True):
                    if chk_group:
                        st.session_state.dont_remind_group_delete = True
                    if target_group in db.get("group_memberships", {}):
                        del db["group_memberships"][target_group]
                    if target_group in db.get("groups", {}):
                        del db["groups"][target_group]
                    if target_group in db.get("group_creators", {}):
                        del db["group_creators"][target_group]
                    save_global_db(db)
                    st.session_state.active_group = "Global Chat" if "Global Chat" in available_groups else None
                    st.session_state.pending_group_delete = None
                    st.rerun()
            with wg_c2:
                if st.button("Cancel", use_container_width=True):
                    st.session_state.pending_group_delete = None
                    st.rerun()

    # --- MAIN INTERFACE PANEL ---
    if st.session_state.active_group:
        st.markdown(f'<div class="pinned-header-yellow">🌐 {st.session_state.active_group}</div>', unsafe_allow_html=True)
        
        if st.session_state.active_group not in db["groups"]:
            db["groups"][st.session_state.active_group] = []
            
        current_messages = db["groups"][st.session_state.active_group]
        
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
            
            # India Standard Time offset math
            ist_timestamp = datetime.fromtimestamp(time.time() + 19800).strftime("%I:%M %p")
            
            db["groups"][st.session_state.active_group].append({
                "id": msg_id, 
                "sender": current_user, 
                "type": "text", 
                "content": user_text, 
                "timestamp": ist_timestamp, 
                "deleted_for_users": []
            })
            save_global_db(db)
            st.rerun()
    else:
        st.markdown('<div class="pinned-header-yellow">🌐 No Channel Selected</div>', unsafe_allow_html=True)
        st.info("You don't have access to any channels yet. Ask the admin (`admin@chat.com`) to add your Gmail to the Global Chat list!")
