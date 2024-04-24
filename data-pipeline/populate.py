import os
import csv
import weaviate
import time
import json

from dotenv import load_dotenv

load_dotenv()

WEAVIATE_URL = os.getenv('WEAVIATE_URL')
WEAVIATE_API_KEY = os.getenv('WEAVIATE_API_KEY')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

def get_book_details(book) -> dict:
	return {
		"isbn13": book[0],
		"isbn10": book[1],
		"title": book[2],
		"subtitle": book[3],
		"authors": book[4],
		"categories": book[5],
		"thumbnail": book[6],
		"description": book[7],
		"published_year": book[8],
		"average_rating": book[9],
		"num_pages": book[10],
		"ratings_count": book[11],
	}

def main():
	client = weaviate.Client(
		url=WEAVIATE_URL,
		auth_client_secret=weaviate.AuthApiKey(api_key=WEAVIATE_API_KEY), 
		additional_headers={"X-OpenAI-Api-Key": OPENAI_API_KEY})
	
	if client.schema.exists("Book"):
		client.schema.delete_class("Book")

	reader = open("./data-pipeline/weaviate_schema.json", "r", encoding='utf8')
	class_obj = json.load(reader)
	client.schema.create_class(class_obj)
	reader.close()

	f = open("./data-pipeline/7k-books-kaggle.csv", "r", encoding='utf8')
	reader = csv.reader(f)
	current_book = None
	try:
		with client.batch as batch:
			batch.batch_size = 100
			for book in reader:
				current_book = book
				properties = get_book_details(book)
				batch.add_data_object(data_object=properties, class_name="Book")
	except Exception as e:
		print(f"something happened {e}. Failure at {current_book}")

	f.close()

if __name__ == "__main__":
	main()