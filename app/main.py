from st_weaviate_connection import WeaviateConnection
import streamlit as st
import time
import sys
import os
import numpy as np
from openai import OpenAI
from utils import parse_completion, generative_gql, vector_gql

from dotenv import load_dotenv

load_dotenv()

WEAVIATE_URL = os.getenv('WEAVIATE_URL')
WEAVIATE_API_KEY = os.getenv('WEAVIATE_API_KEY')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# Check keys
if WEAVIATE_URL is None or WEAVIATE_API_KEY is None or OPENAI_API_KEY is None:
    print(f"Environment variables not set")
    sys.exit("Environment variables not set")

def display_chat_messages() -> None:
    """Print message history
    @returns None
    """
    for message in st.session_state.messages:
        if message["role"] == "system":
            continue
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

def display_shopping_cart() -> None:
    """Print shopping cart
    @returns None
    """
    st.sidebar.header("Shopping Cart")
    for key, value in st.session_state.shopping_cart.items():
        st.sidebar.write(f"{key}: {value}")

# Title
st.title("📚 Welcome to the Bookstore Chat!")

# Connection to Weaviate thorugh Connector
conn = st.connection(
    "weaviate",
    type=WeaviateConnection,
    url=WEAVIATE_URL,
    api_key=WEAVIATE_API_KEY,
    additional_headers={"X-OpenAI-Api-Key": OPENAI_API_KEY},
)

# OpenAI client
openai_client = OpenAI(
    api_key=OPENAI_API_KEY,
)

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.greetings = False
    st.session_state.shopping_cart = {}

# Display chat messages from history on app rerun
display_chat_messages()

# display shopping cart on app rerun
display_shopping_cart()


# Greet user
if not st.session_state.greetings:
    with st.chat_message("assistant"):
        intro = "Hey! I am Bookworm, your assistant for finding the best next book. Let's get started!"
        st.markdown(intro)
        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": intro})
        st.session_state.greetings = True
        # Add prompt to chat history
        with open('./app/prompt.txt', 'r') as file:
            # Read the contents of the file
            system_message = file.read()
            st.session_state.messages.append({"role": "system", "content": system_message})

if prompt := (st.chat_input("What can I help you with today?")):
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)

    prompt = prompt.replace('"', "").replace("'", "")

    if prompt != "":
        query = prompt.strip().lower()
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": query})
        completion = openai_client.chat.completions.create(model="gpt-3.5-turbo",
                                                  messages=st.session_state.messages,
                                                  temperature=0.7)
    
        action, book_title, author, genre, text = parse_completion(completion.choices[0].message.content)

        # print(f"Action: {action}, Book Title: {book_title}, Author: {author}, Genre: {genre}")

        if action not in ["Add_to_Cart", "Remove_from_Cart", "Clear_Cart", "Search", "Return_Policy", "Shipping_Information", "Support_Contact"]:
            # tell the user you cannot respond to the request
            respond = "I'm sorry. I can only answer questions related to books. Please ask me about books."
            st.session_state.messages.append({"role": "assistant", "content": respond})
        elif action == "Add_to_Cart":
            if book_title in st.session_state.shopping_cart:
                st.session_state.shopping_cart[book_title] += 1
                respond = f"I have added {book_title} to your cart! Is there anything else I can help you with?"
                st.session_state.messages.append({"role": "assistant", "content": respond})
            else:
                gql = vector_gql.format(input=book_title, limit=1)
                df = conn.query(gql, ttl=None)
                row = df.iloc[0]
                if row["_additional.distance"] >= 0.15 or df.empty:
                    respond = f"Sorry, we don't have {book_title} in our store. Is there another book you would like to purchase?"
                    st.session_state.messages.append({"role": "assistant", "content": respond})
                else:
                    st.session_state.shopping_cart[book_title] = 1
                    respond = f"I have added {book_title} to your cart! Is there anything else I can help you with?"
                    st.session_state.messages.append({"role": "assistant", "content": respond})
        elif action == "Remove_from_Cart":
            if book_title in st.session_state.shopping_cart:
                st.session_state.shopping_cart[book_title] -= 1
                if st.session_state.shopping_cart[book_title] > 0:
                    respond = f"I have removed a copy of {book_title} from your cart! There is still {st.session_state.shopping_cart[book_title]} copy of this book in your cart. Is there anything else I can help you with?"
                else:
                    respond = f"I have removed {book_title} from your cart! Is there anything else I can help you with?"
                st.session_state.messages.append({"role": "assistant", "content": respond})
                if st.session_state.shopping_cart[book_title] == 0:
                    st.session_state.shopping_cart.pop(book_title)
            else:
                respond = f"Sorry, {book_title} is not in your cart. Is there anything else I can help you with?"
                st.session_state.messages.append({"role": "assistant", "content": respond})
        elif action == "Clear_Cart":
            st.session_state.shopping_cart.clear()
            respond = "I have cleared your cart! Is there anything else I can help you with?"
            st.session_state.messages.append({"role": "assistant", "content": respond})
        elif action == "Return_Policy":
            respond = "Our return policy is simple. Any merchandise that is unopened and in original condition can be returned within 30 days of purchase. Is there anything else I can help you with?"
            st.session_state.messages.append({"role": "assistant", "content": respond})
        elif action == "Shipping_Information":
            respond = "We offer free shipping on all orders. You can expect your order to arrive within 5-7 business days. Is there anything else I can help you with?"
            st.session_state.messages.append({"role": "assistant", "content": respond})
        elif action == "Support_Contact":
            respond = "You can reach our customer support team at contact@bookstore.com. Is there anything else I can help you with?"
            st.session_state.messages.append({"role": "assistant", "content": respond})
        elif action == "Search":
            gql = generative_gql.format(input=query, limit=1, task_prompt=f"Based on the bookstore database, which one would you recommend and why. Use the context of the user query: {query}. Don't include images or thumbnails.")
            df = conn.query(gql, ttl=None)
            with st.chat_message("assistant"):
                for index, row in df.iterrows():
                    if index == 0:
                        distance = row["_additional.distance"]
                        if distance >= 0.2:
                            response = "I'm sorry. I couldn't find any books matching your criteria. Please try again with different details."
                        else:
                            response = row['_additional.generate.groupedResult']
                        st.session_state.messages.append({"role": "assistant", "content": response})
        st.rerun()