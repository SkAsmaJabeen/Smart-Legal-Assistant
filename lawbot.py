import streamlit as st
import requests

st.set_page_config(page_title="LawBot", layout="wide")
st.title("⚖️ Smart Legal Assistant")

def olakrutrim_chat(messages):
    url = "https://cloud.olakrutrim.com/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {st.secrets['OLAKRUTRIM_API_KEY']}"
    }
    payload = {
        "model": "gpt-oss-20b",
        "messages": messages
    }

    response = requests.post(url, headers=headers, json=payload, timeout=30)
    response.raise_for_status()
    return response.json()

def generate_chat_title(text, max_words=5):
    words = text.strip().split()
    return " ".join(words[:max_words])

def export_chat(messages):
    chat_text = ""
    for msg in messages:
        role = "You" if msg["role"] == "user" else "LawBot"
        chat_text += f"{role}: {msg['content']}\n\n"
    return chat_text

if "chats" not in st.session_state:
    st.session_state.chats = {
        "New Chat": [
            {
                "role": "assistant",
                "content": "Hey hi 👋 Welcome to LawBot ⚖️\n\nHow can I help you today?"
            }
        ]
    }

if "current_chat" not in st.session_state:
    st.session_state.current_chat = "New Chat"

st.sidebar.title("Chat History")

for chat_name in list(st.session_state.chats.keys()):
    if st.sidebar.button(chat_name, use_container_width=True):
        st.session_state.current_chat = chat_name

st.sidebar.divider()

if st.sidebar.button("➕New Chat", use_container_width=True):
    base_name = "New Chat"
    count = 1
    new_chat_name = base_name

    while new_chat_name in st.session_state.chats:
        count += 1
        new_chat_name = f"{base_name} {count}"

    st.session_state.chats[new_chat_name] = [
        {
            "role": "assistant",
            "content": "Hey hi 👋 Welcome to LawBot ⚖️\n\nHow can I help you today?"
        }
    ]
    st.session_state.current_chat = new_chat_name

st.sidebar.subheader("Rename Chat")

rename_input = st.sidebar.text_input(
    "New name",
    value=st.session_state.current_chat
)

if st.sidebar.button("Rename"):
    if (
        rename_input
        and rename_input not in st.session_state.chats
    ):
        st.session_state.chats[rename_input] = st.session_state.chats[
            st.session_state.current_chat
        ]
        del st.session_state.chats[st.session_state.current_chat]
        st.session_state.current_chat = rename_input
        st.sidebar.success("Chat renamed")
    else:
        st.sidebar.warning("Invalid or duplicate name")

st.sidebar.subheader("Delete Chat")

if st.sidebar.button("Delete Current Chat"):
    if len(st.session_state.chats) > 1:
        del st.session_state.chats[st.session_state.current_chat]
        st.session_state.current_chat = list(st.session_state.chats.keys())[0]
        st.sidebar.success("Chat deleted")
    else:
        st.sidebar.warning("At least one chat must exist")

st.sidebar.subheader("Export Chat")

chat_data = export_chat(
    st.session_state.chats[st.session_state.current_chat]
)

st.sidebar.download_button(
    label="Download Chat",
    data=chat_data,
    file_name=f"{st.session_state.current_chat}.txt",
    mime="text/plain"
)

messages = st.session_state.chats[st.session_state.current_chat]

for msg in messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Ask your legal question..."):
    messages.append({"role": "user", "content": prompt})

    if (
        st.session_state.current_chat.startswith("New Chat")
        and len(messages) == 2
    ):
        new_title = generate_chat_title(prompt)
        st.session_state.chats[new_title] = messages
        del st.session_state.chats[st.session_state.current_chat]
        st.session_state.current_chat = new_title

    with st.chat_message("user"):
        st.markdown(prompt)

    if len(messages) > 20:
        st.warning("⚠️ Message limit reached")
        st.stop()

    with st.chat_message("assistant"):
        try:
            result = olakrutrim_chat(messages)
            reply = result["choices"][0]["message"]["content"]
            st.markdown(reply)
            messages.append(
                {"role": "assistant", "content": reply}
            )
        except requests.exceptions.RequestException:
            st.error("🚫 API error or quota exceeded. Try again later.")
