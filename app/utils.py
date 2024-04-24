import re

def parse_completion(text):
    print(text)
    action = ""
    book_title = ""
    author = ""
    genre = ""
    pattern = r"\[USER_ACTION: (.*?); BOOK_TITLE: (.*?); AUTHOR: (.*?); GENRE: (.*?)\]"
    matches = re.findall(pattern, text)

    if matches:
        for match in matches:
            action, book_title, author, genre = match
            text = text.replace(
                "[USER_ACTION: " + action + "; BOOK_TITLE: " + book_title + "; AUTHOR: " + author + "; GENRE: " + genre + "]",
                "")

    return action, book_title, author, genre, text

vector_gql = """
        {{
            Get {{
                Book(limit: {limit}, nearText: {{ concepts: ["{input}"] }})
                {{
                    isbn13
                    isbn10
                    title
                    subtitle
                    authors
                    categories
                    thumbnail
                    description
                    published_year
                    average_rating
                    num_pages
                    ratings_count
                    _additional {{
                        id
                        distance
                        vector
                    }}
                }}
            }}
        }}"""

generative_gql = """
        {{
            Get {{
                Book(limit: {limit}, nearText: {{ concepts: ["{input}"] }})
                {{
                    isbn13
                    isbn10
                    title
                    subtitle
                    authors
                    categories
                    thumbnail
                    description
                    published_year
                    average_rating
                    num_pages
                    ratings_count
                    _additional {{
                        generate(
                            groupedResult: {{
                                task: "{task_prompt}"
                            }}
                        ) {{
                        groupedResult
                        error
                        }}
                        id
                        distance
                        vector
                    }}
                }}
            }}
        }}"""