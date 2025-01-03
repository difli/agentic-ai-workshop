import requests
import streamlit as st
from datetime import datetime

BASE_API_URL = "https://api.langflow.astra.datastax.com"
LANGFLOW_ID = st.secrets['LANGFLOW_ID']
ENDPOINT = st.secrets['ENDPOINT']
APPLICATION_TOKEN = st.secrets['APP_TOKEN']


def run_flow(message: str) -> dict:
    api_url = f"{BASE_API_URL}/lf/{LANGFLOW_ID}/api/v1/run/{ENDPOINT}"

    payload = {
        "input_value": message,
        "output_type": "chat",
        "input_type": "chat",
    }

    headers = {"Authorization": "Bearer " + APPLICATION_TOKEN, "Content-Type": "application/json"}
    response = requests.post(api_url, json=payload, headers=headers)
    return response.json()


def main():
    # Apply custom styles
    st.markdown(
        """
        <style>
            .chat-bubble {
                background-color: #007bff;
                color: white;
                padding: 10px;
                border-radius: 15px;
                max-width: 80%;
                margin-bottom: 10px;
                font-size: 16px;
                line-height: 1.5;
            }
            .chat-bubble-user {
                background-color: #f1f1f1;
                color: black;
                padding: 10px;
                border-radius: 15px;
                max-width: 80%;
                margin-bottom: 10px;
                align-self: flex-end;
                font-size: 16px;
                line-height: 1.5;
            }
            .timestamp {
                font-size: 12px;
                color: gray;
                margin-bottom: 5px;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.title("📞 Customer Support Assistant")
    st.subheader("Get instant answers to your questions!")

    # Initialize session state for messages
    if "messages" not in st.session_state:
        st.session_state["messages"] = []
    if "current_input" not in st.session_state:
        st.session_state["current_input"] = ""

    # Clear chat button
    if st.button("Clear Chat"):
        st.session_state["messages"] = []
        st.session_state["current_input"] = ""

    # Sample questions
    st.markdown("### Try asking:")
    col1, col2, col3 = st.columns(3)

    if col1.button("How can I track my order?"):
        st.session_state["current_input"] = "How can I track my order?"
    if col2.button("What is your return policy?"):
        st.session_state["current_input"] = "What is your return policy?"
    if col3.button("Can I cancel order #1004?"):
        st.session_state["current_input"] = "Can I cancel order #1004?"

    # Input form for question submission
    with st.form(key="chat_form", clear_on_submit=False):
        user_input = st.text_input(
            "Type your question here",
            placeholder="How can we help you today?",
            value=st.session_state["current_input"],
        )
        submit_button = st.form_submit_button("Submit")

    if submit_button:
        if not user_input.strip():
            st.error("Please enter a question.")
        else:
            try:
                response = run_flow(user_input)

                # Extract and store bot response
                bot_response = response["outputs"][0]["outputs"][0]["results"]["message"]["text"]
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                # Add the latest interaction to the chat history
                st.session_state["messages"].insert(0, {"user": user_input, "bot": bot_response, "timestamp": timestamp})
                # Clear the current input
                st.session_state["current_input"] = ""

            except Exception as e:
                st.error("Oops! Something went wrong. Please try again.")

    # Display chat history (latest at the top)
    for message in st.session_state["messages"]:
        # Timestamp
        st.markdown(f'<div class="timestamp">{message["timestamp"]}</div>', unsafe_allow_html=True)
        # User's message
        st.markdown(
            f'<div class="chat-bubble-user">{message["user"]}</div>',
            unsafe_allow_html=True,
        )
        # Bot's response
        st.markdown(
            f'<div class="chat-bubble">{message["bot"]}</div>',
            unsafe_allow_html=True,
        )


if __name__ == "__main__":
    main()
