import streamlit as st
import pyrebase
from google.cloud import firestore

signup_form_submitted = False

st.title("IntergalacticPro Signup Page")
st.write("[Submit a bug report](mailto:contact@aravjain.space)")

firebaseConfig = {
    'apiKey': st.secrets.firebaseConfig['apiKey'],
    'authDomain': st.secrets.firebaseConfig['authDomain'],
    'databaseURL': st.secrets.firebaseConfig['databaseURL'],
    'projectId': st.secrets.firebaseConfig['projectId'],
    'storageBucket': st.secrets.firebaseConfig['storageBucket'],
    'messagingSenderId': st.secrets.firebaseConfig['messagingSenderId'],
    'appId': st.secrets.firebaseConfig['appId'],
    'measurementId': st.secrets.firebaseConfig['measurementId']
}

firebase = pyrebase.initialize_app(firebaseConfig)
auth = firebase.auth()
db = firestore.Client.from_service_account_json("intergalacticpro-firebase-key.json")


def sign_up():
    """Returns `True` if the user had a correct password."""

    def signup_form():
        st.header("Signup Form")
        with st.form("Credentials"):
            st.session_state["first_name"] = st.text_input("First Name")
            st.session_state["last_name"] = st.text_input("Last Name")
            st.session_state["email"] = st.text_input("Email")
            st.session_state["password"] = st.text_input("Password", type="password")
            st.session_state["user_plan"] = st.selectbox("Choose a Plan", ["Trial", "Basic", "Premium", "BetaTester"])
            st.session_state["user_paid"] = st.selectbox("Already Paid?", ["Trial", "Yes", "No", "BetaTester"])
            st.form_submit_button("Sign up", on_click=password_entered)
            st.caption("⬆️ Press it twice (not rapidly, though)")
        with st.expander("ℹ️ Pricing"):
            st.write("""Free Trial - Includes 50 GPT-3.5 Requests Per Session: 3 days, automatic account deactivation 
            afterward""")
            st.write("Basic Plan - Includes 50 GPT-3.5 Requests Per Session: $5/month")
            st.write("""Premium Plan - Includes 50 GPT-4 and 5 DALL·E 3 Requests Per Session (also includes dev tools): 
            $15/month""")
        st.write("""Note: Beta Testers are those people who have received an email on or after February 10, 2024 which 
                is similar to the following: """)
        with st.expander("ℹ️ Beta Tester Sample Email"):
            st.image('IG-beta-sample-email.png')

    def password_entered():
        form_submitted = True
        try:
            signup = auth.create_user_with_email_and_password(st.session_state["email"], st.session_state["password"])
            print(signup)
            st.session_state["password_correct"] = True
            doc_ref = db.collection("users").document(st.session_state["email"])
            doc = doc_ref.get()
            if (st.session_state["user_paid"] == "Trial" or st.session_state["user_paid"] == "Yes" or
                    st.session_state["user_paid"] == "BetaTester"):
                paid_status = True
            elif st.session_state["user_paid"] == "No":
                paid_status = False
            if st.session_state["user_plan"] == "Trial":
                plan_selection = "Trial"
            elif st.session_state["user_plan"] == "Basic":
                plan_selection = "Basic"
            elif st.session_state["user_plan"] == "Premium" or st.session_state["user_plan"] == "BetaTester":
                plan_selection = "Premium"
            doc_ref.set({
                "FirstName": st.session_state["first_name"],
                "LastName": st.session_state["last_name"],
                "Paid": paid_status,
                "Plan": plan_selection
            })
            del st.session_state["first_name"]
            del st.session_state["last_name"]
            st.session_state["user_name"] = doc.to_dict()["FirstName"] + " " + doc.to_dict()["LastName"]
            st.session_state["user_plan"] = doc.to_dict()["Plan"]
            st.session_state["user_paid"] = doc.to_dict()["Paid"]
        except Exception as e:
            st.error(f"Failed to create user: {e}")
            return
    # Show inputs for username + password.
    signup_form()
    if not signup_form_submitted:
        return False

if not sign_up():
    st.stop()

st.success("""Signup was successful! You may now begin using IntergalacticPro 
[here](https://intergalacticpro.aravjain.space)""")
