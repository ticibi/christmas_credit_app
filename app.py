import streamlit as st
import pandas as pd
import json
import os

TITLE: str = "Christmas Credit Manager"
DATA_FILE: str = "user_data.json"
TRANSACTIONS_FILE: str = "transactions.json"

st.set_page_config(page_title=TITLE, page_icon="❄️", layout="wide")

# Helper function to load user data from JSON
def load_user_data(file):
    if os.path.exists(file):
        with open(file, "r") as f:
            return json.load(f)
    return {}

# Helper function to save user data to JSON
def save_user_data(data, file):
    with open(file, "w") as f:
        json.dump(data, f)

# Initialize `user_data` in session state if it doesn't exist, loading from JSON file
if 'user_data' not in st.session_state:
    st.session_state['user_data'] = load_user_data(DATA_FILE)

if 'transactions' not in st.session_state:
    st.session_state['transactions'] = load_user_data(TRANSACTIONS_FILE)

st.title(f'❄️{TITLE}🎄')

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
                save_user_data(st.session_state['user_data'], DATA_FILE)
                # Success message with updated information
                st.success(f"{cc_amount} CCs {'added to' if cc_amount >= 0 else 'deducted from'} {user_name}'s balance.")
                # Log the transaction
                st.session_state['transactions'].append({
                    "user": user_name,
                    "amount": cc_amount,
                    "balance": st.session_state['user_data'][user_name]['balance']
                })
                # Save the transaction log to the JSON file
                save_user_data(st.session_state['transactions'], TRANSACTIONS_FILE)
            else:
                st.error("User not found.")

    transactions = st.session_state['transactions'] if st.session_state['transactions'] else []
    df = pd.DataFrame(st.session_state['transactions'])
    st.table(df)

# Admin tab to add new users (tab3)
with tab3:
    with st.form("add_user"):
        new_user_name = st.text_input("User Name")
        new_user_balance = st.number_input("Initial CC Balance", min_value=0, step=1)
        add_user_button = st.form_submit_button("Add User")

        if add_user_button:
            # Check if the user name already exists in session state
            if new_user_name not in st.session_state['user_data']:
                # Add the new user
                st.session_state['user_data'][new_user_name] = {
                    "name": new_user_name,
                    "balance": int(new_user_balance),
                }
                # Save the updated data to the JSON file
                save_user_data(st.session_state['user_data'], DATA_FILE)
                st.success(f"User {new_user_name} added with balance {new_user_balance}")
            else:
                st.error("User name already exists. Please choose a different name.")

    with st.form("remove_user"):
        user_name = st.selectbox("Select User", list(st.session_state['user_data'].keys()))
        remove_user_button = st.form_submit_button("Remove User")

        if remove_user_button:
            # Check if the user name already exists in session state
            if user_name not in st.session_state['user_data']:
                st.error("User name not found.")
            else:
                st.success(f"User {user_name} removed.")
                # Remove the user from the session state
                del st.session_state['user_data'][user_name]
                # Save the updated data to the JSON file
                save_user_data(st.session_state['user_data'], DATA_FILE)

    df = pd.DataFrame(st.session_state['user_data']).T
    st.table(df.reset_index(drop=True))
