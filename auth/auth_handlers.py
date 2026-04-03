# auth/auth_handlers.py
import streamlit as st
import psycopg2
from datetime import datetime
import secrets
import os
from passlib.hash import pbkdf2_sha256
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# -------------------------------
# Database connection
# -------------------------------
@st.cache_resource
def init_connection():
    """Initialize database connection using environment variables."""
    db_config = {
        'host': os.getenv('DB_HOST', 'localhost'),
        'port': os.getenv('DB_PORT', '5432'),
        'database': os.getenv('DB_NAME', 'campus_safety'),
        'user': os.getenv('DB_USER', 'postgres'),
        'password': os.getenv('DB_PASSWORD')
    }
    
    if not db_config['password']:
        st.error("❌ Database password not configured. Check your .env file.")
        st.stop()
    
    try:
        return psycopg2.connect(**db_config)
    except Exception as e:
        st.error(f"❌ Database connection failed: {e}")
        st.stop()

conn = init_connection()

# -------------------------------
# Helper functions
# -------------------------------
def run_query(query, params=None, fetch=True):
    """Run SQL query safely and commit if needed."""
    try:
        with conn.cursor() as cur:
            cur.execute(query, params or ())
            if fetch:
                return cur.fetchall()
            conn.commit()
    except Exception as e:
        conn.rollback()
        st.error(f"Database error: {e}")
        return None


# -------------------------------
# User Management
# -------------------------------
def verify_password(username, password):
    """Verify username and password against database"""
    result = run_query(
        "SELECT user_id, hashed_password, first_name, last_name FROM users WHERE username = %s",
        (username,)
    )
    
    if result and len(result) > 0:
        user_id, hashed_password, first_name, last_name = result[0]
        if pbkdf2_sha256.verify(password, hashed_password):
            return True, user_id, f"{first_name} {last_name}".strip()
    return False, None, None


def add_user(username, email, first_name, last_name, password):
    """Add new user with auto-incremented user_id using pbkdf2_sha256 hash."""
    cur = conn.cursor(cursor_factory=RealDictCursor)

    try:
        # Check if username already exists
        cur.execute("SELECT username FROM users WHERE username = %s", (username,))
        if cur.fetchone():
            cur.close()
            raise Exception(f"Username '{username}' already exists")
        
        # Check if email already exists
        cur.execute("SELECT email FROM users WHERE email = %s", (email,))
        if cur.fetchone():
            cur.close()
            raise Exception(f"Email '{email}' already exists")

        # Find the max user_id
        cur.execute("SELECT MAX(user_id) as max_id FROM users")
        result = cur.fetchone()
        max_id = result["max_id"] or 0

        # New user_id
        new_user_id = max_id + 1

        # Hash the password using pbkdf2_sha256
        hashed_password = pbkdf2_sha256.hash(password)

        # Insert user with correct column name
        cur.execute("""
            INSERT INTO users (user_id, username, email, first_name, last_name, hashed_password, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, NOW())
        """, (new_user_id, username, email, first_name, last_name, hashed_password))
        conn.commit()
        cur.close()
        return new_user_id
        
    except Exception as e:
        conn.rollback()
        cur.close()
        raise e


def update_last_seen(username):
    query = "UPDATE users SET last_seen = NOW() WHERE username = %s"
    run_query(query, (username,), fetch=False)


def update_password(username, new_password):
    """Update user password"""
    hashed_password = pbkdf2_sha256.hash(new_password)
    run_query(
        "UPDATE users SET hashed_password = %s WHERE username = %s",
        (hashed_password, username),
        fetch=False
    )


def get_user_by_username(username):
    """Get user details by username"""
    result = run_query(
        "SELECT user_id, email, first_name, last_name FROM users WHERE username = %s",
        (username,)
    )
    if result:
        return result[0]
    return None


def get_username_by_email(email):
    """Get username by email"""
    result = run_query(
        "SELECT username FROM users WHERE email = %s",
        (email,)
    )
    if result:
        return result[0][0]
    return None


# For backward compatibility - not actually used anymore
authenticator = None
def get_credentials():
    return {}


# -------------------------------
# Authentication Widgets
# -------------------------------
def login_widget():
    """Render login widget and handle authentication"""
    if "authentication_status" not in st.session_state:
        st.session_state["authentication_status"] = None
    if "username" not in st.session_state:
        st.session_state["username"] = None
    if "name" not in st.session_state:
        st.session_state["name"] = None
    if "user_id" not in st.session_state:
        st.session_state["user_id"] = None

    # Don't show login form if already authenticated
    if st.session_state.get("authentication_status"):
        return

    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Login")
        
        if submit:
            if username and password:
                is_valid, user_id, full_name = verify_password(username, password)
                
                if is_valid:
                    st.session_state["authentication_status"] = True
                    st.session_state["username"] = username
                    st.session_state["user_id"] = user_id
                    st.session_state["name"] = full_name
                    update_last_seen(username)
                    st.success(f"✅ Welcome, {full_name}!")
                    st.rerun()
                else:
                    st.session_state["authentication_status"] = False
                    st.error("❌ Username/password is incorrect")
            else:
                st.warning("⚠️ Please enter your username and password")

    # Show navigation buttons only if not authenticated
    if not st.session_state.get("authentication_status"):
        st.markdown("---")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("➕ Create Account", use_container_width=True):
                st.session_state["show_register"] = True
                st.rerun()
        with col2:
            if st.button("🔐 Forgot Password?", use_container_width=True):
                st.session_state["show_forgot_password"] = True
                st.rerun()


def register_widget():
    """Render registration widget and save user to DB"""
    st.subheader("📝 Create New Account")
    
    with st.form("register_form"):
        email = st.text_input("Email", placeholder="your.email@example.com")
        username = st.text_input("Username", placeholder="Choose a username")
        first_name = st.text_input("First Name")
        last_name = st.text_input("Last Name")
        password = st.text_input("Password", type="password", placeholder="Min. 6 characters")
        password_confirm = st.text_input("Confirm Password", type="password")
        
        col1, col2 = st.columns(2)
        with col1:
            submit = st.form_submit_button("✅ Register", use_container_width=True)
        with col2:
            cancel = st.form_submit_button("❌ Cancel", use_container_width=True)
        
        if cancel:
            st.session_state["show_register"] = False
            st.rerun()
        
        if submit:
            if not all([email, username, first_name, password]):
                st.error("❌ Please fill in all required fields")
            elif password != password_confirm:
                st.error("❌ Passwords do not match")
            elif len(password) < 6:
                st.error("❌ Password must be at least 6 characters long")
            else:
                try:
                    user_id = add_user(username, email, first_name, last_name, password)
                    if isinstance(user_id, (int, float)):
                        st.success(f"✅ Account created successfully! Please log in.")
                        st.session_state["show_register"] = False
                        st.balloons()
                        st.rerun()
                    else:
                        st.error("❌ Failed to create account")
                except Exception as e:
                    st.error(f"Registration error: {e}")
    
    # Back to login button outside the form
    st.markdown("---")
    if st.button("⬅️ Back to Login", use_container_width=True):
        st.session_state["show_register"] = False
        st.rerun()


def reset_password_widget():
    """Reset password for authenticated user"""
    if not st.session_state.get("authentication_status"):
        st.warning("Please log in first")
        return
    
    st.subheader("🔑 Reset Password")
    
    with st.form("reset_password_form"):
        current_password = st.text_input("Current Password", type="password")
        new_password = st.text_input("New Password", type="password")
        confirm_password = st.text_input("Confirm New Password", type="password")
        
        submit = st.form_submit_button("Update Password")
        
        if submit:
            username = st.session_state.get("username")
            
            # Verify current password
            is_valid, _, _ = verify_password(username, current_password)
            
            if not is_valid:
                st.error("❌ Current password is incorrect")
            elif new_password != confirm_password:
                st.error("❌ New passwords do not match")
            elif len(new_password) < 6:
                st.error("❌ New password must be at least 6 characters long")
            else:
                try:
                    update_password(username, new_password)
                    st.success("✅ Password updated successfully!")
                except Exception as e:
                    st.error(f"Error updating password: {e}")


def forgot_password_widget():
    """Render forgot password widget"""
    st.subheader("🔐 Forgot Password")
    
    with st.form("forgot_password_form"):
        username = st.text_input("Username")
        email = st.text_input("Email")
        
        submit = st.form_submit_button("Generate New Password")
        
        if submit:
            if not username or not email:
                st.error("❌ Please enter both username and email")
            else:
                # Verify username and email match
                user = get_user_by_username(username)
                if user and user[1] == email:  # user[1] is email
                    # Generate new password
                    new_password = secrets.token_urlsafe(12)
                    try:
                        update_password(username, new_password)
                        st.success("✅ New password generated")
                        st.info(f"Username: {username}\nNew Password: {new_password}\n\n⚠️ Please save this password and change it after logging in.")
                    except Exception as e:
                        st.error(f"Error generating new password: {e}")
                else:
                    st.error("❌ Username and email do not match")
    
    # Back to login button
    st.markdown("---")
    if st.button("⬅️ Back to Login", use_container_width=True):
        if "show_forgot_password" in st.session_state:
            del st.session_state["show_forgot_password"]
        st.rerun()


def forgot_username_widget():
    """Retrieve username by email"""
    st.subheader("❓ Forgot Username")
    
    with st.form("forgot_username_form"):
        email = st.text_input("Email")
        submit = st.form_submit_button("Retrieve Username")
        
        if submit:
            if not email:
                st.error("❌ Please enter your email")
            else:
                username = get_username_by_email(email)
                if username:
                    st.success("✅ Username retrieved")
                    st.info(f"Username: {username}\nEmail: {email}")
                else:
                    st.error("❌ Email not found")


def update_user_details_widget():
    """Update user details for authenticated user"""
    if not st.session_state.get("authentication_status"):
        st.warning("Please log in first")
        return
    
    st.subheader("✏️ Update Account Details")
    
    username = st.session_state.get("username")
    user = get_user_by_username(username)
    
    if user:
        user_id, current_email, first_name, last_name = user
        
        with st.form("update_details_form"):
            new_email = st.text_input("Email", value=current_email)
            new_first_name = st.text_input("First Name", value=first_name)
            new_last_name = st.text_input("Last Name", value=last_name or "")
            
            submit = st.form_submit_button("Update Details")
            
            if submit:
                try:
                    run_query(
                        "UPDATE users SET email = %s, first_name = %s, last_name = %s WHERE username = %s",
                        (new_email, new_first_name, new_last_name, username),
                        fetch=False
                    )
                    
                    # Update session state
                    st.session_state["name"] = f"{new_first_name} {new_last_name}".strip()
                    
                    st.success("✅ Details updated successfully!")
                except Exception as e:
                    st.error(f"Error updating details: {e}")


def logout_widget():
    """Handle user logout"""
    if st.session_state.get('authentication_status'):
        if st.sidebar.button("🚪 Logout", use_container_width=True):
            # Clear all session state
            for key in ["authentication_status", "username", "name", "user_id"]:
                if key in st.session_state:
                    del st.session_state[key]
            st.success("✅ Logged out successfully!")
            st.rerun()
    else:
        st.info("You are not logged in.")