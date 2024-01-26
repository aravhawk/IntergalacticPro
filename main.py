import streamlit as st
from openai import OpenAI
import mappings

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

license_main_content = '''Unauthorized copying, modification, distribution, or use of this project, "IntergalacticPro", 
or any of its parts, via any medium, is strictly prohibited. Proprietary and confidential.'''

with st.sidebar:
    st.title("IntergalacticPro")

    model = st.selectbox("", ["GPT-3.5", "GPT-4"])
    model_id = mappings.models[model]
    plan = mappings.plans[model]
    plan_price = mappings.prices[model]

    with st.sidebar.expander("ℹ️ Usage & Pricing Disclaimer"):
        st.caption(
            f"""Use of the {model} model in IntergalacticPro requires the {plan} plan. 
            The {plan} plan is ${plan_price}/month, and allocates you a daily usage quota of 50 requests."""
        )

    st.write("Advanced settings:")
    with st.sidebar.expander("ℹ️ Advanced Settings Disclaimer"):
        st.caption(
            f"""Use of advanced settings in IntergalacticPro requires the premium plan. 
            The premium plan is $15/month, and allocates you a daily usage quota of 50 requests. If you don't have the 
            premium plan, the settings will still show up, but they will be overriden (in the background) by system 
            defaults."""
        )

    temperature = st.sidebar.slider('temperature:', min_value=0.0, max_value=2.0, value=0.7, step=0.1)
    top_p = st.sidebar.slider('top_p:', min_value=0.0, max_value=1.0, value=0.6, step=0.1)
    if model == "GPT-3.5":
        temperature = 0.7
        top_p = 0.6

    st.write(license_main_content)

# Ensuring session state for messages
if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": """Hi, it's IntergalacticPro again, the highly 
        knowledgeable, clear, and concise space and rockets expert! What would you like to talk about today?"""}]

# Displaying messages
for message in st.session_state["messages"]:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Maximum allowed messages
max_messages = 100

if len(st.session_state["messages"]) >= max_messages:
    st.info(
        """Your limit for this model has been reached. Please continue your conversation tomorrow. 
        Thank you for your understanding, and for using IntergalacticPro today."""
    )
else:
    prompt = st.chat_input(f"Message IntergalacticPro ({model})...")
    if prompt:
        # Append the user's message to the session state
        st.session_state["messages"].append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""
            for response in client.chat.completions.create(
                model=model_id,
                messages=[{"role": "system", "content": f"""You are IntergalacticPro, a space and rockets expert who is 
                highly knowledgeable, clear, and concise. You are based on the {model} model created by OpenAI, but the 
                IntergalacticPro bot and interface were created/designed by Arav Jain (https://github.com/aravhawk), 
                using Python. The Streamlit library is used for the interface, along with the OpenAI Python library. 
                Also, IntergalacticPro is only accessible via a paid, month subscription. The $5/month plan gives access 
                to GPT-3.5, and the $15/month plan gives access to GPT-4, along with some advanced developer settings 
                (i.e. temperature, top_p). The license's main content verbatim states: {license_main_content}"""}] +
                         [{"role": m["role"], "content": m["content"]} for m in st.session_state["messages"]],
                stream=True,
                temperature=0.7,
                top_p=0.6
            ):
                incremental_content = response.choices[0].delta.content or ""
                full_response += incremental_content
                message_placeholder.markdown(full_response + "▌")

            # Remove the typewriter effect cursor for the final message
            message_placeholder.markdown(full_response)

        # Append the assistant's response to the session state
        st.session_state["messages"].append({"role": "assistant", "content": full_response})

