import streamlit as st
import pyrebase
from google.cloud import firestore
from openai import OpenAI
import mappings

ig_version = "3.1.3"
login_form_submitted = False

st.title("IntergalacticPro")
st.write("[Submit a bug report](mailto:contact@aravjain.space)")
st.write("Signup for IntergalacticPro [here](https://intergalacticpro-register.streamlit.app)")

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


def check_password():
    if 'password_correct' not in st.session_state:
        st.session_state['password_correct'] = None

    def login_form():
        st.header("Login Form")
        with st.form("Credentials"):
            st.session_state["email"] = st.text_input("Email")
            st.session_state["password"] = st.text_input("Password", type="password")
            st.form_submit_button("Log in", on_click=password_entered)
            st.caption("⬆️ Press it twice (not rapidly, though)")

    def password_entered():
        form_submitted = True
        try:
            login = auth.sign_in_with_email_and_password(st.session_state["email"], st.session_state["password"])
            print(login)
            st.session_state["password_correct"] = True
            doc_ref = db.collection("users").document(st.session_state["email"])
            doc = doc_ref.get()
            st.session_state["user_name"] = doc.to_dict()["FirstName"] + " " + doc.to_dict()["LastName"]
            st.session_state["user_plan"] = doc.to_dict()["Plan"]
            st.session_state["user_paid"] = doc.to_dict()["Paid"]
        except:
            st.session_state["password_correct"] = False
    # Return True if the username + password is validated.
    if st.session_state.get("password_correct", False):
        return True

    # Show inputs for username + password.
    login_form()
    if login_form_submitted:
        if not st.session_state.get('password_correct'):
            st.error("😕 User not known or password incorrect")
        return False


if not check_password():
    st.stop()

# Main app starts here

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

license_main_content = '''Unauthorized copying, modification, distribution, or use of this project, "IntergalacticPro", 
or any of its parts, via any medium, is strictly prohibited. Proprietary and confidential.'''

with open('IG-ExampleResponse.txt') as file:
    example_response = file.read()

with st.sidebar:
    st.title("IntergalacticPro")
    st.write("[Submit a bug report](mailto:contact@aravjain.space)")

    if st.session_state["user_paid"]:
        if st.session_state["user_plan"] == "Trial" or st.session_state["user_plan"] == "Basic":
            model = st.selectbox("", ["GPT-3.5"])
        elif st.session_state["user_plan"] == "Premium":
            model = st.selectbox("", ["GPT-4", "DALL·E 3"])
        model_id = mappings.models[model]
        plan = mappings.plans[model]
        plan_price = mappings.prices[model]
        requests = mappings.requests[model]
        model_type = mappings.type[model]

    with st.sidebar.expander("ℹ️ Usage & Pricing Disclaimer"):
        st.caption(
            f"""Use of the {model} model in IntergalacticPro requires the {plan} plan. 
            The {plan} plan is ${plan_price}/month, and allocates you a per-session usage quota of {requests} {model} 
            requests."""
        )

    if st.session_state["user_plan"] == "Trial" or st.session_state["user_plan"] == "Basic" and st.session_state[
        "user_paid"
    ]:
        temperature = 0.7
        top_p = 0.6
    elif model_type == "text" and st.session_state["user_plan"] == "Premium" and st.session_state["user_paid"]:
        st.write(f"Advanced {model_type} settings:")
        temperature = st.sidebar.slider('temperature:', min_value=0.0, max_value=2.0, value=0.7, step=0.1)
        top_p = st.sidebar.slider('top_p:', min_value=0.0, max_value=1.0, value=0.6, step=0.1)
    elif model_type == "image" and st.session_state["user_plan"] == "Premium" and st.session_state["user_paid"]:
        st.write(f"Advanced {model_type} settings:")
        image_quality = st.selectbox("Image quality", ["standard", "hd"])
        image_size = st.selectbox("Image size", ["1024x1024", "	1024x1792", "1792x1024"])

    st.write(f"{license_main_content}")
    st.write("Inspired by [ChatGPT](https://chat.openai.com) Plus")
    st.write(f"IntergalacticPro v{ig_version}")

# Ensuring session state for messages
if model_type == "text":
    if "text_messages" not in st.session_state:
        st.session_state["text_messages"] = [{"role": "assistant", "content": f"""Hi {st.session_state["user_name"]}, 
        it's IntergalacticPro again, the highly knowledgeable, clear, concise, and friendly space and rockets expert! 
        What would you like to talk about today?"""}]
elif model_type == "image":
    if "image_urls" not in st.session_state:
        st.session_state["image_urls"] = []

# Displaying messages
if model_type == "text":
    for message in st.session_state["text_messages"]:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
elif model_type == "image":
    with st.chat_message("assistant"):
        st.markdown(f"""Hi {st.session_state["user_name"]}, it's IntergalacticPro again! What would you like to create 
        today?""")
    for message in st.session_state["image_urls"]:
        with st.chat_message(message["role"]):
            st.image(message["content"])

# Maximum allowed messages
max_text_messages = 101  # includes sent+received messages; extra 1 added due to welcome message
max_image_messages = 6  # includes received images; extra 1 added due to welcome message

if model_type == "text":
    if len(st.session_state["text_messages"]) >= max_text_messages:
        st.info(
            f"""Your session limit for the {model_type} models has been reached. Please start a new conversation later. 
            Thank you for your understanding, and for using IntergalacticPro today."""
        )
    else:
        text_prompt = st.chat_input(f"Message IntergalacticPro ({model})...")
        if text_prompt:
            # Append the user's message to the session state
            st.session_state["text_messages"].append({"role": "user", "content": text_prompt})
            with st.chat_message("user"):
                st.markdown(text_prompt)

            with st.chat_message("assistant"):
                message_placeholder = st.empty()
                full_response = ""
                for response in client.chat.completions.create(
                    model=model_id,
                    messages=[{"role": "system", "content": f"""You are IntergalacticPro, a space and rockets expert who 
                    is highly knowledgeable, clear, concise, and friendly. The current user's name is 
                    {st.session_state["user_name"]} You are based on the {model} model created by OpenAI, but the 
                    IntergalacticPro bot and interface were created/designed by Arav Jain (https://github.com/aravhawk), 
                    using Python. Arav Jain is a 13-year-old programmer and space enthusiast who lives in the United 
                    States. The Streamlit library is used for the interface, along with the OpenAI Python library. Also,
                    IntergalacticPro is only accessible via a paid, monthly subscription. The $5/month {plan} plan gives 
                    access to GPT-3.5, and the $15/month {plan} plan gives access to GPT-4 & DALL·E 3, along with some 
                    advanced developer settings (i.e. temperature, top_p, etc.). If someone would like to upgrade (or 
                    submit a bug report), tell them to email me. My email is contact@aravjain.space. The current version of 
                    IntergalacticPro is v{ig_version} A good response to a user could be: '{example_response}' Also, the 
                    license's main content verbatim states: '{license_main_content}'"""}] +
                             [{"role": m["role"], "content": m["content"]} for m in st.session_state["text_messages"]],
                    stream=True,
                    temperature=temperature,
                    top_p=top_p,
                ):
                    incremental_content = response.choices[0].delta.content or ""
                    full_response += incremental_content
                    message_placeholder.markdown(full_response + "▌")

                # Remove the typewriter effect cursor for the final message
                message_placeholder.markdown(full_response)

            # Append the assistant's response to the session state
            st.session_state["text_messages"].append({"role": "assistant", "content": full_response})
elif model_type == "image":
    if len(st.session_state["image_urls"]) >= max_image_messages:
        st.info(
            f"""Your session limit for the {model_type} models has been reached. Please continue your conversation 
            tomorrow. Thank you for your understanding, and for using IntergalacticPro today."""
        )
    else:
        image_prompt = st.chat_input(f"Message IntergalacticPro ({model})...")
        if image_prompt is not None:
            with st.chat_message("assistant"):
                message_placeholder = st.markdown("Creating image...")
                if image_prompt:
                    response = client.images.generate(
                        model=model_id,
                        prompt=image_prompt,
                        size=image_size,
                        quality=image_quality,
                        n=1,
                    )
                    image_url = response.data[0].url
                    message_placeholder.image(image_url, caption=f'"{image_prompt}"')
                    st.session_state["image_urls"].append({"role": "assistant", "content": image_url})

st.markdown(f"""
<footer style='text-align: center; color: grey; position: fixed;'>
    <p style='margin: 20px; padding: 10px;'>
        IntergalacticPro {ig_version} — AI can make mistakes. Consider checking important information.
    </p>
</footer>
""", unsafe_allow_html=True)
