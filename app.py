import streamlit as st
from datetime import date

from database import (
    insert_workout,
    get_message_history,
    register_user,
    login_user,
    DB_PATH,
)

from calories import calculate_calories
from logic import calculate_streak, detect_inactivity, performance_trend
from messages import get_motivational_message, get_trigger_type
from analytics import (
    plot_weekly_summary,
    plot_daily_summary,
    plot_performance_trend,
    plot_activity_trends,
    export_performance_pdf,
)


def chat_bubble(sender, message, timestamp):

    if sender == "You":
        bubble_color = "#848B7F"
        align = "flex-end"
    else:
        bubble_color = "#CFCBCB"
        align = "flex-start"

    return f"""
<div style="width: 100%; display: flex; justify-content: {align}; margin: 4px 0;">
    <div style="background: {bubble_color}; padding: 8px 10px; border-radius: 11px; max-width: 30%; font-size: 7px; line-height: 1.1; color: #000000; box-shadow: 0px 1px 2px rgba(0,0,0,0.2);">
        <div style="font-size: 12px; font-weight: bold; margin-bottom: 3px;">{sender}</div>
        <div style="font-size: 14px;">{message}</div>
        <div style="font-size: 11px; color:#555; margin-top: 4px; text-align:right;">{timestamp}</div>
    </div>
</div>
"""


import sqlite3

st.set_page_config(page_title="FiTrack", layout="wide")

# ----------------------------------------------------
# CUSTOM UI THEME & STYLING
# ----------------------------------------------------

st.markdown(
    """
<style>

/* MAIN WRAPPER */
.main {
    padding: 0rem 2rem;
}

/* Sidebar styling */
[data-testid="stSidebar"] {
    background-color: #111418;
    padding-top: 2rem;
}

/* Sidebar title */
.sidebar-title {
    font-size: 1.3rem;
    font-weight: 700;
    color: #00C896;
    padding-bottom: 10px;
}

/* Card styling */
.card {
    background: #0B253A;
    padding: 1.5rem;
    border-radius: 12px;
    border: 1px solid #13304B;
    margin-bottom: 20px;
}

.card-title {
    font-size: 1.2rem;
    font-weight: 700;
    margin-bottom: .3rem;
    color: #00E0B8;
}

.card-text {
    font-size: 1rem;
    color: #D0D4D8;
}

/* Improve metric spacing */
[data-testid="stMetricValue"] {
    font-size: 28px;
}


/* ---------------------------------------
   MOBILE RESPONSIVE DESIGN (Phones)
---------------------------------------- */
@media only screen and (max-width: 650px) {

    /* Reduce card padding */
    .card {
        padding: 1rem !important;
        margin-bottom: 15px !important;
    }

    /* Smaller titles on phone */
    .card-title {
        font-size: 1.05rem !important;
    }

    .card-text {
        font-size: 0.85rem !important;
    }

    /* Make Streamlit column layout stack vertically */
    [data-testid="column"] {
        flex-direction: column !important;
        width: 100% !important;
    }

    /* Smaller banner height on phone */
    .mobile-banner {
        height: 120px !important;
    }

    /* Smaller profile avatar */
    .mobile-avatar {
        width: 60px !important;
        height: 60px !important;
    }

    /* Reduce top spacing globally */
    .main {
        padding: 0rem 1rem !important;
    }
}

</style>
""",
    unsafe_allow_html=True,
)

# ----------------------------------------------------
# SESSION STATE FOR LOGIN
# ----------------------------------------------------
if "user_id" not in st.session_state:
    st.session_state["user_id"] = None

if "username" not in st.session_state:
    st.session_state["username"] = None


# ----------------------------------------------------
# LOGIN / REGISTER PAGE
# ----------------------------------------------------
def login_page():
    st.title("🔐 FiTrack Login")

    tab1, tab2 = st.tabs(["Login", "Register"])

    # LOGIN TAB
    with tab1:
        st.subheader("Login to your account")

        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        login_btn = st.button("Login")

        if login_btn:
            user_id = login_user(username, password)
            if user_id:
                st.session_state["user_id"] = user_id
                st.session_state["username"] = username
                st.success("Login successful!")
                st.rerun()
            else:
                st.error("Invalid username or password")

    # REGISTER TAB
    with tab2:
        st.subheader("Create a new account")

        username = st.text_input("New Username")
        password = st.text_input("New Password", type="password")
        reg_btn = st.button("Create Account")

        if reg_btn:
            ok, msg = register_user(username, password)
            if ok:
                st.success(msg)
            else:
                st.error(msg)


# If no user logged in, show login page
if st.session_state["user_id"] is None:
    login_page()
    st.stop()

# User logged in
USER_ID = st.session_state["user_id"]
USERNAME = st.session_state["username"]

# ----------------------------------------------------
# MAIN APP NAVIGATION
# ----------------------------------------------------
with st.sidebar:
    st.markdown("<div class='sidebar-title'>Navigation</div>", unsafe_allow_html=True)

    menu = st.selectbox(
        "Navigation",
        [
            "🏠 Home",
            "🏋️ Log Workout",
            "📊 Dashboard",
            "💬 Messages",
            "🔥 Streak Partners",
        ],
        label_visibility="collapsed",
    )

st.sidebar.write(f"Logged in as: **{USERNAME}**")
if st.sidebar.button("Logout"):
    st.session_state["user_id"] = None
    st.session_state["username"] = None
    st.rerun()

st.title("FiTrack — Smart Fitness & Wellness Tracker")


# ----------------------------------------------------
# HOME PAGE
# ----------------------------------------------------
if menu == "🏠 Home":

    import base64
    import os

    # Function to convert image to base64
    def img_to_base64(image_path):
        try:
            with open(image_path, "rb") as img_file:
                return base64.b64encode(img_file.read()).decode()
        except Exception as e:
            print(f"Error loading {image_path}: {e}")
            return None

    # Load images as base64
    banner_b64 = img_to_base64("assets/fitness_banner.jpg")
    profile_b64 = img_to_base64("assets/profile_placeholder.png")

    message = get_motivational_message(USER_ID)
    trigger = get_trigger_type(USER_ID)

    # ---------- BANNER ----------
    if banner_b64:
        banner_html = f"""
<div class="mobile-banner" style="position: relative; height: 150px;
    background-image: url('data:image/jpeg;base64,{banner_b64}');
    background-size: cover; background-position: center;
    border-radius: 15px; margin-bottom: 25px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.4);">

<div style="position: absolute; bottom: 0; width: 100%;
    background: linear-gradient(to top, rgba(0,0,0,0.85), transparent);
    padding: 20px; border-radius: 0 0 15px 15px;">

<h1 style="color: #00E0B8; margin:0; font-size:32px; font-weight:900;">
Welcome back, {USERNAME} 👋
</h1>

<p style="color:#E0E0E0; font-size:15px; margin-top:4px;">
Your personalized fitness assistant is ready.
</p>

</div>
</div>
"""
    else:
        banner_html = f"""
<div style="background: linear-gradient(135deg, #0B253A 0%, #13304B 100%);
    padding: 40px 30px; border-radius: 15px; margin-bottom: 25px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.4);">

<h1 class="hero-title" style="color: #00E0B8; margin:0; font-weight:900;">
Welcome back, {USERNAME} 👋
</h1>

<p style="color:#E0E0E0; font-size:15px; margin-top:8px;">
Your personalized fitness assistant is ready.
</p>

</div>
"""
    st.markdown(banner_html, unsafe_allow_html=True)

    # ---------- PROFILE CARD ----------
    if profile_b64:
        profile_html = f"""
<div class="card" style="display:flex; align-items:center; gap:20px;">

<img class="mobile-avatar" src="data:image/png;base64,{profile_b64}" 
     style="width:80px; height:80px; border-radius:50%;
     border:2px solid #00E0B8; object-fit:cover;">

<div>
    <div class="card-title" style="font-size:20px; margin-bottom:4px;">{USERNAME}</div>
    <div class="card-text">FiTrack Member</div>
</div>

</div>
"""
    else:
        # Fallback if image doesn't load
        profile_html = f"""
<div class="card" style="display:flex; align-items:center; gap:20px;">

<div style="width:80px; height:80px; border-radius:50%;
    border:3px solid #00E0B8; background: linear-gradient(135deg, #13304B 0%, #0B253A 100%);
    display:flex; align-items:center; justify-content:center; font-size:36px;">
💪
</div>

<div>
    <div class="card-title" style="font-size:20px; margin-bottom:4px;">{USERNAME}</div>
    <div class="card-text">FiTrack Member</div>
</div>

</div>
"""
    st.markdown(profile_html, unsafe_allow_html=True)

    # ---------- MOTIVATION ----------
    motivation_html = f"""
<div class="card">

<div style="display:flex; align-items:center; gap:12px;">
    <span style="font-size:28px;">💡</span>
    <div class="card-title">Today's Motivation</div>
</div>

<div class="card-text" style="margin-top:10px;">
    {message}
</div>

</div>
"""
    st.markdown(motivation_html, unsafe_allow_html=True)


# ----------------------------------------------------
# LOG WORKOUT PAGE
# ----------------------------------------------------
elif menu == "🏋️ Log Workout":

    # Header card — tighter layout
    st.markdown(
        """
    <div class="card" style="padding: 1rem; margin-bottom: 15px;">
        <div class="card-title" style="font-size: 20px;">Log a New Workout</div>
        <div class="card-text" style="font-size: 14px;">Record your exercise for today.</div>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # Form card — tighter layout
    st.markdown(
        "<div class='card' style='padding: 1rem; margin-bottom: 15px;'>",
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns(2)

    with col1:
        workout_date = st.date_input("📅 Date", value=date.today())
        activity = st.selectbox(
            "🏃 Activity", ["Running", "Walking", "Gym", "Cycling", "Yoga"]
        )

    with col2:
        duration = st.number_input("⏱ Minutes", min_value=1)
        intensity = st.selectbox("🔥 Intensity", ["Low", "Medium", "High"])

    st.markdown("</div>", unsafe_allow_html=True)

    # Save button card
    st.markdown("<div class='card' style='padding: 1rem;'>", unsafe_allow_html=True)

    if st.button("💾 Save Workout", use_container_width=True):
        calculated_calories = calculate_calories(
            activity_type=activity, duration=duration, intensity=intensity
        )

        insert_workout(
            user_id=USER_ID,
            date=str(workout_date),
            activity_type=activity,
            duration=duration,
            intensity=intensity,
            calories=calculated_calories,
        )

        st.success(
            f"Workout saved for **{workout_date}**! "
            f"Calories burned: **{calculated_calories:.0f} kcal** 🔥"
        )

    st.markdown("</div>", unsafe_allow_html=True)


# ----------------------------------------------------
# DASHBOARD PAGE
# ----------------------------------------------------
elif menu == "📊 Dashboard":

    st.markdown(
        """
    <div class="card">
        <div class="card-title">Your Fitness Dashboard</div>
        <div class="card-text">Overview of your activity, performance, and progress.</div>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # ---------- STAT CARDS ----------
    st.markdown("<div class='card'>", unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)

    # Workout Streak
    with c1:
        streak = calculate_streak(USER_ID)
        st.markdown(
            f"""
        <div style="
            background:#0E2137;
            padding:20px;
            border-radius:12px;
            text-align:center;
            border:1px solid #13304B;">
            <h3 style="color:#00E0B8; margin-bottom:8px;">Workout Streak</h3>
            <div style="font-size:32px; font-weight:800; color:white;">
                {streak} Days
            </div>
        </div>
        """,
            unsafe_allow_html=True,
        )

    # Inactivity
    with c2:
        inactive = detect_inactivity(USER_ID)
        status_color = "#FF4B4B" if inactive else "#00E0B8"
        status_text = "Yes" if inactive else "No"

        st.markdown(
            f"""
        <div style="
            background:#0E2137;
            padding:20px;
            border-radius:12px;
            text-align:center;
            border:1px solid #13304B;">
            <h3 style="color:#00E0B8; margin-bottom:8px;">Inactive?</h3>
            <div style="font-size:32px; font-weight:800; color:{status_color};">
                {status_text}
            </div>
        </div>
        """,
            unsafe_allow_html=True,
        )

    # Duration Trend
    with c3:
        trend = performance_trend(USER_ID)
        st.markdown(
            f"""
        <div style="
            background:#0E2137;
            padding:20px;
            border-radius:12px;
            text-align:center;
            border:1px solid #13304B;">
            <h3 style="color:#00E0B8; margin-bottom:8px;">Avg Duration Trend</h3>
            <div style="font-size:28px; font-weight:800; color:white;">
                {trend['previous']:.1f} → {trend['current']:.1f}
            </div>
        </div>
        """,
            unsafe_allow_html=True,
        )

    st.markdown("</div>", unsafe_allow_html=True)
    st.divider()

    # ---------- MOTIVATION ----------
    today_msg = get_motivational_message(USER_ID)
    st.markdown(
        f"""
    <div class="card">
        <div class="card-title">💡 Motivation Boost</div>
        <div class="card-text">{today_msg}</div>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # ---------- CHARTS ----------
    st.markdown(
        """
    <div class="card">
        <div class="card-title">📈 Performance & Activity Charts</div>
        <div class="card-text">Visual snapshots of your weekly and daily trends.</div>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # Weekly Summary
    weekly_fig = plot_weekly_summary(USER_ID)
    if weekly_fig:
        st.plotly_chart(weekly_fig, use_container_width=True)

    # Daily Summary
    daily_fig = plot_daily_summary(USER_ID)
    if daily_fig:
        st.plotly_chart(daily_fig, use_container_width=True)

    # Performance Trend
    performance_fig = plot_performance_trend(USER_ID)
    if performance_fig:
        st.plotly_chart(performance_fig, use_container_width=True)
    else:
        st.info("Log more data to see your performance trend.")

    # Activity Trends
    activity_fig = plot_activity_trends(USER_ID)
    if activity_fig:
        st.plotly_chart(activity_fig, use_container_width=True)
    else:
        st.info("Log different activities to see activity trends.")

    st.divider()

    # ---------- EXPORT REPORT ----------
    st.markdown(
        """
    <div class="card">
        <div class="card-title">📄 Export Report</div>
        <div class="card-text">Download a detailed PDF summary of your performance.</div>
    </div>
    """,
        unsafe_allow_html=True,
    )

    pdf_filename = export_performance_pdf(USER_ID)

    if pdf_filename:
        with open(pdf_filename, "rb") as pdf_file:
            st.download_button(
                label="📥 Download Performance Report (PDF)",
                data=pdf_file,
                file_name="FiTrack_Report.pdf",
                mime="application/pdf",
            )
    else:
        st.warning("Cannot generate PDF: Not enough workout data yet.")


# ----------------------------------------------------
# MESSAGES PAGE
# ----------------------------------------------------
elif menu == "💬 Messages":

    # ---------- Today's Message ----------
    today_msg = get_motivational_message(USER_ID)
    today_trigger = get_trigger_type(USER_ID)

    st.markdown(
        f"""
    <div class="card">
        <div class="card-title">💬 Today's Motivation</div>
        <div class="card-text">{today_msg}</div>
        <div style="color:#00E0B8; font-size:14px; margin-top:10px;">
            Trigger: <span style="font-style:italic; color:#7BD8FF;">{today_trigger}</span>
        </div>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # ---------- History Header ----------
    st.markdown(
        """
    <div class="card">
        <div class="card-title">📜 Message History</div>
        <div class="card-text">Your previous motivational messages appear below.</div>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # ---------- Message History ----------
    history = get_message_history(USER_ID)

    if len(history) == 0:
        st.warning("No messages yet. Keep working out to receive more messages!")
    else:

        st.markdown("<div class='card'>", unsafe_allow_html=True)

        formatted = [{"Date": h[0], "Message": h[1], "Trigger": h[2]} for h in history]

        st.dataframe(
            formatted,
            use_container_width=True,
            hide_index=True,
        )

        st.markdown("</div>", unsafe_allow_html=True)


# ----------------------------------------------------
# STREAK PARTNERS PAGE
# ----------------------------------------------------
elif menu == "🔥 Streak Partners":

    from database import (
        add_streak_partner,
        get_streak_partners,
        add_partner_message,
        get_partner_messages,
        delete_partner_and_messages,
    )
    from datetime import datetime

    # ---------- PAGE HEADER ----------
    st.markdown(
        """
    <div class="card">
        <div class="card-title">🤝 Streak Partners</div>
        <div class="card-text">Stay accountable by tracking your streak with friends!</div>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # =====================================================
    # ADD PARTNER
    # =====================================================
    st.markdown("<div class='card'>", unsafe_allow_html=True)

    st.markdown(
        """
    <div class="card-title">Add a Partner</div>
    <div class="card-text">Invite someone to keep each other motivated.</div>
    """,
        unsafe_allow_html=True,
    )

    new_partner = st.text_input("👤 Partner name")

    if st.button("➕ Add Partner"):
        if not new_partner.strip():
            st.warning("Please enter a valid name.")
        else:
            add_streak_partner(USER_ID, new_partner.strip())
            st.success(f"{new_partner.strip()} added!")
            st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

    # =====================================================
    # LIST PARTNERS
    # =====================================================
    partners = get_streak_partners(USER_ID)
    partner_names = [p[1] for p in partners] if partners else []

    st.markdown("<div class='card'>", unsafe_allow_html=True)

    st.markdown(
        """
    <div class="card-title">Your Partners</div>
    <div class="card-text">View your current streak partners below.</div>
    """,
        unsafe_allow_html=True,
    )

    if not partners:
        st.info("No partners yet. Add one above.")
        st.markdown("</div>", unsafe_allow_html=True)
        st.stop()
    else:
        for _, pname in partners:
            st.markdown(
                f"<div style='color:white; font-size:16px; margin-bottom:6px;'>👤 {pname}</div>",
                unsafe_allow_html=True,
            )

    st.markdown("</div>", unsafe_allow_html=True)

    # =====================================================
    # CHAT SECTION
    # =====================================================
    st.markdown("<div class='card'>", unsafe_allow_html=True)

    st.markdown(
        """
    <div class="card-title">💬 Chat</div>
    <div class="card-text">Select a partner to chat with.</div>
    """,
        unsafe_allow_html=True,
    )

    selected = (
        st.selectbox("Choose partner to chat with", partner_names)
        if partner_names
        else None
    )

    if selected:

        chat_history = get_partner_messages(USER_ID, partner_name=selected)

        chat_container = st.container()
        with chat_container:
            if not chat_history:
                st.info("No messages yet. Say hello!")
            else:
                # Render chat bubbles in reverse chronological order (oldest first)
                for sender, msg, timestamp in chat_history:
                    st.markdown(
                        chat_bubble(sender, msg, timestamp), unsafe_allow_html=True
                    )

        new_msg = st.text_input("Type your message...", key="chat_input")

        if st.button("📨 Send Message"):
            if new_msg.strip():
                add_partner_message(USER_ID, selected, new_msg.strip(), sender="You")
                st.rerun()
            else:
                st.warning("Message cannot be empty.")

    else:
        st.info("Add a partner above to start chatting.")

    st.markdown("</div>", unsafe_allow_html=True)

    # =====================================================
    # REMOVE PARTNER
    # =====================================================
    st.markdown("<div class='card'>", unsafe_allow_html=True)

    st.markdown(
        """
    <div class="card-title">🗑 Remove a Partner</div>
    <div class="card-text">Removing a partner will delete the full chat history.</div>
    """,
        unsafe_allow_html=True,
    )

    if partner_names:
        remove_name = st.selectbox(
            "Select partner to remove", partner_names, key="remove_select"
        )

        if st.button("❌ Delete Partner and Messages"):
            delete_partner_and_messages(USER_ID, remove_name)
            st.success(f"Removed {remove_name} and deleted all chat history.")
            st.rerun()
    else:
        st.info("No partners to remove.")

    st.markdown("</div>", unsafe_allow_html=True)

