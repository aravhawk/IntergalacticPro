import streamlit as st
from openai import OpenAI

st.title("IntergalacticPro")

with st.expander("ℹ️ Disclaimer"):
    st.caption(
        """Usage of the GPT-3.5 model in IntergalacticPro requires the basic plan. 
        The basic plan is $5, and allocates you a usage quota of 50 requests per day."""
    )

client = OpenAI()

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
    prompt = st.chat_input("Message IntergalacticPro (GPT-3.5)...")
    if prompt:
        # Append the user's message to the session state
        st.session_state["messages"].append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""
            for response in client.chat.completions.create(
                model="gpt-3.5-turbo-1106",
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
