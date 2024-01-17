import streamlit as st
from openai import OpenAI
import mappings

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

st.title("IntergalacticPro")

model = st.selectbox("", ["GPT-3.5", "GPT-4"])
model_id = mappings.models[model]
plan = mappings.plans[model]
plan_price = mappings.prices[model]

with st.expander("ℹ️ Usage & Pricing Disclaimer"):
    st.caption(
        f"""Usage of the {model} model in IntergalacticPro requires the {plan} plan. 
        The {plan} plan is ${plan_price}, and allocates you a daily usage quota of 50 requests."""
    )

# Ensuring session state for messages
if "messages" not in st.session_state:
    st.session_state["messages"] = []

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
                messages=[{"role": "system", "content": "You are IntergalacticPro, a space and rockets expert who is highly knowledgeable, clear, and concise."}] +
                         [{"role": m["role"], "content": m["content"]} for m in st.session_state["messages"]],
                stream=True,
            ):
                incremental_content = response.choices[0].delta.content or ""
                full_response += incremental_content
                message_placeholder.markdown(full_response + "▌")

            # Remove the typewriter effect cursor for the final message
            message_placeholder.markdown(full_response)

        # Append the assistant's response to the session state
        st.session_state["messages"].append({"role": "assistant", "content": full_response})
