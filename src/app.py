import streamlit as st
from langchain_core.messages import AIMessage, HumanMessage
from rag import get_response


# Steeamlit page configuration
st.set_page_config(page_title="DeepChat", page_icon="🧠", layout="wide")
st.title("DeepChat - chat with any website")
# Initialize chat history only if it doesn't exist, so only once in a session it will be initialized
# This is a way to counter the fact that Streamlit reruns the whole script on every user interaction


# sidebar
with st.sidebar:
    st.header(body="Settings")
    website_url = st.text_input(label="Website URL")

if website_url is None or website_url == "":
    st.info("Please enter a website URL to get started.")
else:
    # session state
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = [
            AIMessage("Hello! I'm DeepChat. Paste a website URL in the sidebar to get started.")]

    # chat info
    st.info(f"Chatting with the website: {website_url}")

    # user input
    user_query = st.chat_input(placeholder="Type your message here...")
    if user_query is not None and user_query != "":
        st.session_state.chat_history.append(HumanMessage(user_query))
        # response = get_response(user_query)
        response = get_response(website_url=website_url, user_query=user_query)
        st.session_state.chat_history.append(AIMessage(response))
        st.write(st.session_state.chat_history)
        # docs = retriever_chain.invoke(
        #     {'input': user_query})
        # st.write(docs)

    # chat
    for message in st.session_state.chat_history:
        if isinstance(message, AIMessage):
            with st.chat_message(name="AI"):
                st.write(message.content)
        elif isinstance(message, HumanMessage):
            with st.chat_message(name="Human"):
                st.write(message.content)

    # debug
    # with st.expander(label="Debug"):
    #     st.write(st.session_state.chat_history)
    #     st.write(website_url)
    #     st.write(user_query)

    # with st.chat_message(name="AI"):
    #     st.write("Hello! I'm DeepChat. Paste a website URL in the sidebar to get started.")

    # with st.chat_message(name="Human"):
    #     st.write("Hi! I'm excited to chat with you.")
