import streamlit as st
import random
import json
import os

TITLE: str = "Christmas Quest Giver"
DATA_FILE: str = "users.json"
TASK_FILE: str = "tasks.json"
CURSES_FILE: str = "curses.json"
TRANSACTIONS_FILE: str = "transactions.json"

st.set_page_config(page_title=TITLE, page_icon="🎄", layout="wide")

# Helper function to load data from JSON
def load(file):
    if os.path.exists(file):
        with open(file, "r") as f:
            return json.load(f)
    return {}

# Helper function to save data to JSON
def save(data, file):
    with open(file, "w") as f:
        json.dump(data, f, indent=4)

# Initialize session state
if "users" not in st.session_state:
    st.session_state["users"] = load(DATA_FILE)

if "transactions" not in st.session_state:
    st.session_state["transactions"] = load(TRANSACTIONS_FILE)

if "tasks" not in st.session_state:
    st.session_state["tasks"] = load(TASK_FILE).get("tasks", [])

if "curses" not in st.session_state:
    st.session_state["curses"] = load(CURSES_FILE)

# Centralized rolling logic
def roll_event(curse_chance=0.2):
    """
    Determines if a curse or a task should be assigned based on the given curse chance.
    Args:
        curse_chance (float): Probability of rolling a curse (0.0 to 1.0).
    Returns:
        dict: A dictionary with the event type ('curse' or 'task') and the selected event.
    """
    if random.random() < curse_chance:
        return {"type": "curse", "event": random.choice(st.session_state["curses"])}
    else:
        return {"type": "task", "event": random.choice(st.session_state["tasks"])}

# Login function
def login(username):
    admin_username = st.secrets.get("admin", {}).get("username", "admin")
    if username:
        if username not in st.session_state["users"]:
            st.session_state["users"][username] = {"balance": 0}
        st.session_state["logged_in"] = True
        st.session_state["username"] = username
        st.session_state["is_admin"] = username == admin_username

# Check if the user is logged in
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if not st.session_state["logged_in"]:
    st.title("Login")
    username = st.text_input("Username")
    if st.button("Login"):
        login(username)
        st.rerun()

else:
    # Sidebar Navigation
    st.sidebar.title("🎅 Navigation")
    selection = st.sidebar.radio("Go to", ["Home", "Task", "Account"])

    if selection == "Home":
        st.title("🎄 Christmas Quest Giver 🎁")
        st.write(f"Welcome, {st.session_state['username']}!")
        st.image("https://via.placeholder.com/800x400?text=Christmas+Quest", use_container_width=True)

    elif selection == "Task":
        st.header("Your Quest")
        current_user = st.session_state["users"][st.session_state["username"]]

        if not current_user.get("task") and not current_user.get("curse"):
            result = roll_event(curse_chance=0.2)
            if result["type"] == "curse":
                current_user["curse"] = result["event"]
                st.error(f"🔮 You've been cursed: {result['event']['name']}")
                with st.expander("Curse Details", expanded=True):
                    st.write(result['event']['curse'])
            else:
                current_user["task"] = result["event"]
                st.success(f"🎯 New Task: {result['event']['name']}")
                with st.expander("Task Details", expanded=True):
                    st.write(result['event']['description'])
                    st.write(f"Reward: {result['event']['reward']} Christmas Credits")
            save(st.session_state["users"], DATA_FILE)
            st.rerun()
            if st.button("Roll for Task or Curse"):
                result = roll_event(curse_chance=0.2)
                if result["type"] == "curse":
                    current_user["curse"] = result["event"]
                    st.error(f"🔮 You've been cursed: {result['event']['name']}")
                    with st.expander("Curse Details", expanded=True):
                        st.write(result['event']['curse'])
                else:
                    current_user["task"] = result["event"]
                    st.success(f"🎯 New Task: {result['event']['name']}")
                    with st.expander("Task Details", expanded=True):
                        st.write(result['event']['description'])
                        st.write(f"Reward: {result['event']['reward']} Christmas Credits")
                save(st.session_state["users"], DATA_FILE)
                st.rerun()

        elif current_user.get("task"):
            st.success(f"🎯 Active Task: {current_user['task']['name']}")
            with st.expander("Task Details", expanded=True):
                st.write(current_user['task']['description'])
                st.write(f"Reward: {current_user['task']['reward']} Christmas Credits")
            if st.button("Complete Task"):
                current_user["balance"] += current_user["task"]["reward"]
                del current_user["task"]
                save(st.session_state["users"], DATA_FILE)
                st.balloons()
                st.success("Task completed! Credits added to your balance.")
                st.rerun()
            elif st.button("Re-roll Task"):
                result = roll_event(curse_chance=0.2)
                if result["type"] == "curse":
                    current_user["curse"] = result["event"]
                    del current_user["task"]
                    st.error(f"🔮 You've been cursed: {result['event']['name']}")
                    with st.expander("Curse Details"):
                        st.write(result['event']['curse'])
                else:
                    current_user["task"] = result["event"]
                    st.success(f"🎯 New Task: {result['event']['name']}")
                    with st.expander("Task Details"):
                        st.write(result["event"]["description"])
                        st.write(f"Reward: {result['event']['reward']} Christmas Credits")
                save(st.session_state["users"], DATA_FILE)
                st.rerun()

        elif current_user.get("curse"):
            st.error(f"🔮 Active Curse: {current_user['curse']['name']}")
            with st.expander("Curse Details", expanded=True):
                st.write(current_user['curse']['curse'])
            if st.button("Break Curse"):
                del current_user["curse"]
                save(st.session_state["users"], DATA_FILE)
                st.success("Curse broken! You can roll again.")
                st.rerun()

    elif selection == "Account":
        st.header("Account Details")
        st.write(f"**Username:** {st.session_state['username']}")
        st.write(f"**Christmas Credits:** {st.session_state['users'][st.session_state['username']]['balance']}")
        if st.button("Logout"):
            st.session_state.clear()
            st.rerun()

    # Admin Panel
    if st.session_state["is_admin"]:
        st.sidebar.title("Admin Panel")
        admin_action = st.sidebar.radio("Admin Actions", ["Transactions", "Manage Tasks"])

        if admin_action == "Transactions":
            st.header("Transactions")
            with st.form("transaction_form"):
                user_name = st.selectbox("User", list(st.session_state["users"].keys()))
                cc_amount = st.number_input("Credits", value=1, min_value=-100, max_value=100, step=1)
                submit_button = st.form_submit_button("Update")
                if submit_button:
                    if user_name in st.session_state["users"]:
                        st.session_state["users"][user_name]["balance"] += cc_amount
                        save(st.session_state["users"], DATA_FILE)
                        st.success(
                            f"{cc_amount} CCs {'added to' if cc_amount >= 0 else 'deducted from'} {user_name}'s balance."
                        )
                        st.session_state["transactions"].append(
                            {
                                "user": user_name,
                                "amount": cc_amount,
                                "balance": st.session_state["users"][user_name]["balance"],
                            }
                        )
                        save(st.session_state["transactions"], TRANSACTIONS_FILE)
