# Bookstore Chatbot

This bookstore chatbot is a web-based chatbot with an interactive user interface built with `Streamlit`. It utilizes OpenAI's `GPT-3.5-turbo` as its language model and `text-embedding-ada-002` as its text embedding model, and `Weaviate` for its database.

This chatbot can handle users' questions about book recommendations and store policies. In addition, the chatbot can also help users add books to their shopping carts or remove books from their shopping carts.

A demo video of this chatbot can be found [here](https://drive.google.com/file/d/1pDyz7azMONYpG6_NbnggbBoyU6MUS2qh/view?usp=sharing).

## Features

- Book search by title, author, genre
- Book recommendation by genre and/or popularity
- General inquries about store return policies, shipping, and customer support service
- Conversational-based shopping cart management
- Ability to handle follow-up questions
- Error handling

## Instructions

To run this chatbot on your machine, follow the instructions below:

1. Create a conda environment with the following command: `conda create --name bookstore-chatbot --file requirements.txt`
2. Create a `.env` file that contains the following variables: `WEAVIATE_URL = ""`, `WEAVIATE_API_KEY = ""`, and `OPENAI_API_KEY = ""`.
3. Push data to `Weaviate` by running `python data-pipeline/populate.py`
4. Run the following command to start the chatbot: `streamlit run app/main.py` (The chatbot will pop up in your browser. If not, open [http://localhost:8501/](http://localhost:8501/) in your browser.)
