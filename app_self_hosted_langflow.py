import requests
import streamlit as st
from datetime import datetime

# Retrieve the HTTP endpoint and token from secrets
LANGFLOW_API_URL = st.secrets['LANGFLOW_API_URL']  # Example: "http://127.0.0.1:7860/api/v1/run/customer_support2?stream=false"
APPLICATION_TOKEN = st.secrets['LANGFLOW_API_KEY']

def run_flow(message: str) -> dict:
    """
    Sends a request to the Langflow API using x-api-key authentication.
    """
    api_url = LANGFLOW_API_URL  # Ensure the full API URL is in secrets (including query params if needed)

    payload = {
        "input_value": message,
        "output_type": "chat",
        "input_type": "chat",
    }

    headers = {
        "x-api-key": APPLICATION_TOKEN,  # Using x-api-key for authentication
        "Content-Type": "application/json"
    }

    response = requests.post(api_url, json=payload, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        return {"error": f"Request failed with status {response.status_code}: {response.text}"}

def main():
    # Apply custom styles for chat bubbles
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

    # Initialize session state for messages and current input
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

                if "error" in response:
                    st.error(response["error"])
                else:
                    bot_response = response["outputs"][0]["outputs"][0]["results"]["message"]["text"]
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    # Store the interaction in the session state
                    st.session_state["messages"].insert(0, {
                        "user": user_input,
                        "bot": bot_response,
                        "timestamp": timestamp
                    })
                    st.session_state["current_input"] = ""
            except Exception as e:
                st.error(f"Oops! Something went wrong. {str(e)}")

    # Display chat history (latest at the top)
    for message in st.session_state["messages"]:
        st.markdown(f'<div class="timestamp">{message["timestamp"]}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="chat-bubble-user">{message["user"]}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="chat-bubble">{message["bot"]}</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
