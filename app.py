import streamlit as st
import pandas as pd
import random
import json
import os

TITLE: str = "Christmas Credit Manager"
DATA_FILE: str = "user_data.json"
TASK_FILE: str = "tasks.json"
TRANSACTIONS_FILE: str = "transactions.json"

st.set_page_config(page_title=TITLE, page_icon="❄️", layout="wide")

# Helper function to load user data from JSON
def load(file):
    if os.path.exists(file):
        with open(file, "r") as f:
            return json.load(f)
    return {}

# Helper function to save user data to JSON
def save(data, file):
    with open(file, "w") as f:
        json.dump(data, f)

# Initialize `user_data` in session state if it doesn't exist, loading from JSON file
if 'user_data' not in st.session_state:
    st.session_state['user_data'] = load(DATA_FILE)

if 'transactions' not in st.session_state:
    st.session_state['transactions'] = load(TRANSACTIONS_FILE)

if 'tasks' not in st.session_state:
    file = load(TASK_FILE)
    st.session_state['tasks'] = file['tasks']

# Login function
def login(username):
    admin_username = st.secrets["admin"]["username"]
    if username:
        st.session_state['logged_in'] = True
        st.session_state['username'] = username
        st.session_state['is_admin'] = (username == admin_username)
    else:
        st.error("Please enter a username")

# Check if the user is logged in
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

if not st.session_state['logged_in']:
    st.title("Login")
    username = st.text_input("Username")
    if st.button("Login"):
        login(username)
else:
    st.title(f'❄️{TITLE}🎄')
    welcome_message = f"Welcome, {st.session_state['username']}!" if not st.session_state['is_admin'] else "Welcome, Admin!"
    st.subheader(welcome_message)

    if st.session_state['is_admin']:
        tab2, tab3 = st.tabs([
            "Transactions",
            "Actions"
        ])

        # Transactions tab (tab2)
        with tab2:
            with st.form("transaction_form"):
                # Dropdown to select a user by their name
                user_name = st.selectbox("Select User", list(st.session_state['user_data'].keys()))

                # Input field to add or deduct CCs
                cc_amount = st.number_input("CC Amount", value=1, min_value=-100, max_value=100, step=1)

                # Submit button to apply the transaction
                submit_button = st.form_submit_button("Update CC Balance")

                if submit_button:
                    # Check if the selected user exists in the session state
                    if user_name in st.session_state['user_data']:
                        # Update the user's balance
                        st.session_state['user_data'][user_name]['balance'] += cc_amount
                        # Save the updated data to the JSON file
                        save(st.session_state['user_data'], DATA_FILE)
                        # Success message with updated information
                        st.success(f"{cc_amount} CCs {'added to' if cc_amount >= 0 else 'deducted from'} {user_name}'s balance.")
                        # Log the transaction
                        st.session_state['transactions'].append({
                            "user": user_name,
                            "amount": cc_amount,
                            "balance": st.session_state['user_data'][user_name]['balance']
                        })
                        save(st.session_state['transactions'], TRANSACTIONS_FILE)
    else:
        task, account = st.tabs([
            "Task",
            "Account",
        ])

        with task:
            if 'task' not in st.session_state['user_data']:
                if st.button("Get Task"):
                    st.session_state['user_data']['task'] = random.choice(st.session_state['tasks'])
                    save(st.session_state['user_data'], DATA_FILE)
                    st.write(f"Your task is: \n{st.session_state['user_data']['task']['name']}")
                    st.write(f"{st.session_state['user_data']['task']['description']}")
                    st.write(f"Reward: {st.session_state['user_data']['task']['reward']} CCs")
            else:    
                st.write(f"Your task is: {st.session_state['user_data']['task']['name']}")
                st.write(f"{st.session_state['user_data']['task']['description']}")
                st.write(f"Reward: {st.session_state['user_data']['task']['reward']}")
