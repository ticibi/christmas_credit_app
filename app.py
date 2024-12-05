import streamlit as st
import random
import time
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
    if random.random() < curse_chance:
        return {"type": "curse", "event": random.choice(st.session_state["curses"])}
    else:
        return {"type": "task", "event": random.choice(st.session_state["tasks"])}

# Login function
def login(username):
    admin_username = st.secrets.get("admin", {}).get("username", "admin")
    if username:
        if username not in st.session_state["users"]:
            st.session_state["users"][username] = {"balance": 0, "stats": {}}
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
    st.title("🎄 Christmas Quest Giver 🎁")
    current_user = st.session_state["users"][st.session_state["username"]]

    # Display User Info
    st.subheader(f"Welcome, {st.session_state['username']}!")
    st.write(f"**Christmas Credits:** {current_user['balance']}")

    # Task and Curse Section
    st.subheader("Your Quest")
    if not current_user.get("task") and not current_user.get("curse"):
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
            current_user["balance"] += int(current_user["task"]["reward"])
            del current_user["task"]
            save(st.session_state["users"], DATA_FILE)
            st.balloons()
            st.success("Task completed! Credits added to your balance.")
            time.sleep(2)
            st.rerun()
        elif st.button("Re-roll Task"):
            result = roll_event(curse_chance=0.2)
            if result["type"] == "curse":
                current_user["curse"] = result["event"]
                del current_user["task"]
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

    elif current_user.get("curse"):
        st.error(f"🔮 Active Curse: {current_user['curse']['name']}")
        with st.expander("Curse Details", expanded=True):
            st.write(current_user['curse']['curse'])
        if st.button("Break Curse"):
            del current_user["curse"]
            save(st.session_state["users"], DATA_FILE)
            st.success("Curse broken! You can roll again.")
            st.rerun()

    # Admin Panel
    if st.session_state["is_admin"]:
        st.sidebar.title("Admin Panel")
        admin_action = st.sidebar.radio("Admin Actions", ["Transactions", "Manage Tasks"])

        # Transactions Management
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

        # Task Management
        elif admin_action == "Manage Tasks":
            st.header("Manage Tasks")
            
            # Display current tasks
            st.subheader("Existing Tasks")
            if st.session_state["tasks"]:
                for idx, task in enumerate(st.session_state["tasks"]):
                    with st.expander(f"Task {idx + 1}: {task['name']}"):
                        st.write(f"**Description:** {task['description']}")
                        st.write(f"**Reward:** {task['reward']} Christmas Credits")
                        if st.button(f"Delete Task {idx + 1}", key=f"delete_task_{idx}"):
                            st.session_state["tasks"].pop(idx)
                            save({"tasks": st.session_state["tasks"]}, TASK_FILE)
                            st.warning(f"Task {idx + 1} deleted.")
                            st.rerun()

            # Add a new task
            st.subheader("Add a New Task")
            with st.form("add_task_form"):
                new_task_name = st.text_input("Task Name")
                new_task_description = st.text_area("Task Description")
                new_task_reward = st.number_input(
                    "Reward (Christmas Credits)", 
                    value=10, 
                    step=1, 
                    min_value=0
                )
                add_task_button = st.form_submit_button("Add Task")

                if add_task_button:
                    if new_task_name and new_task_description and new_task_reward > 0:
                        new_task = {
                            "name": new_task_name,
                            "description": new_task_description,
                            "reward": int(new_task_reward),
                        }
                        st.session_state["tasks"].append(new_task)
                        save({"tasks": st.session_state["tasks"]}, TASK_FILE)
                        st.success(f"Task '{new_task_name}' added successfully!")
                    else:
                        st.error("Please fill out all fields to add a task.")

            # Edit existing tasks
            st.subheader("Edit Existing Tasks")
            if st.session_state["tasks"]:
                task_to_edit = st.selectbox(
                    "Select Task to Edit", 
                    range(len(st.session_state["tasks"])), 
                    format_func=lambda x: st.session_state["tasks"][x]["name"]
                )
                if task_to_edit is not None:
                    selected_task = st.session_state["tasks"][task_to_edit]
                    with st.form("edit_task_form"):
                        updated_task_name = st.text_input("Task Name", value=selected_task["name"])
                        updated_task_description = st.text_area("Task Description", value=selected_task["description"])
                        updated_task_reward = st.number_input(
                            "Reward (Christmas Credits)", 
                            value=int(selected_task["reward"]), 
                            step=1, 
                            min_value=0
                        )
                        update_task_button = st.form_submit_button("Update Task")

                        if update_task_button:
                            if updated_task_name and updated_task_description and updated_task_reward > 0:
                                selected_task["name"] = updated_task_name
                                selected_task["description"] = updated_task_description
                                selected_task["reward"] = int(updated_task_reward)
                                save({"tasks": st.session_state["tasks"]}, TASK_FILE)
                                st.success(f"Task '{updated_task_name}' updated successfully!")
                            else:
                                st.error("Please fill out all fields to update the task.")
