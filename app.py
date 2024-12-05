import streamlit as st
import pandas as pd
import random
import json
import os

TITLE: str = "Christmas Credit Manager"
DATA_FILE: str = "users.json"
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

# Initialize `users` in session state if it doesn't exist, loading from JSON file
if 'users' not in st.session_state:
    st.session_state['users'] = load(DATA_FILE)

if 'transactions' not in st.session_state:
    st.session_state['transactions'] = load(TRANSACTIONS_FILE)

if 'tasks' not in st.session_state:
    file = load(TASK_FILE)
    st.session_state['tasks'] = file['tasks']

# Login function
def login(username):
    admin_username = st.secrets["admin"]["username"]
    if username:
        if username not in st.session_state['users'] and username != admin_username:
            st.session_state['users'][username] = {
                "balance": 0
            }
        st.session_state['logged_in'] = True
        st.session_state['username'] = username
        st.session_state['is_admin'] = (username == admin_username)

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
                user_name = st.selectbox("Select User", list(st.session_state['users'].keys()))

                # Input field to add or deduct CCs
                cc_amount = st.number_input("CC Amount", value=1, min_value=-100, max_value=100, step=1)

                # Submit button to apply the transaction
                submit_button = st.form_submit_button("Update CC Balance")

                if submit_button:
                    # Check if the selected user exists in the session state
                    if user_name in st.session_state['users']:
                        # Update the user's balance
                        st.session_state['users'][user_name]['balance'] += cc_amount
                        # Save the updated data to the JSON file
                        save(st.session_state['users'], DATA_FILE)
                        # Success message with updated information
                        st.success(f"{cc_amount} CCs {'added to' if cc_amount >= 0 else 'deducted from'} {user_name}'s balance.")
                        # Log the transaction
                        st.session_state['transactions'].append({
                            "user": user_name,
                            "amount": cc_amount,
                            "balance": st.session_state['users'][user_name]['balance']
                        })
                        save(st.session_state['transactions'], TRANSACTIONS_FILE)
    else:
        task, account = st.tabs([
            "Task",
            "Account",
        ])

        with task:
            current_user = st.session_state['users'][st.session_state['username']]
            if not current_user.get('task'):
                if st.button("Get Task"):
                    current_user['task'] = random.choice(st.session_state['tasks'])
                    save(st.session_state['users'], DATA_FILE)
                    st.write(f"Your task is: \n{current_user['task']['name']}")
                    st.write(f"{current_user['task']['description']}")
                    st.write(f"Reward: {current_user['task']['reward']} Christmas Credits")
            
            if current_user.get('task'):
                if st.button("Re-roll Task"):
                    current_user['task'] = random.choice(st.session_state['tasks'])
                    save(st.session_state['users'], DATA_FILE)
                    st.write(f"Your task is: \n{current_user['task']['name']}")
                    st.write(f"{current_user['task']['description']}")
                    st.write(f"Reward: {current_user['task']['reward']} Christmas Credits")

        with account:
            st.write(f"You have {current_user['balance']} Christmas Credits")
