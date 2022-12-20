from sentence_transformers import SentenceTransformer
import pymongo, os, sys
import json
import csv

mongo_uri = "mongodb+srv://username:password@cluster0.xxxxx.mongodb.net/?retryWrites=true&w=majority"
db = "vector_search"
collection = "movies_vector"

# initialize db connection
connection = pymongo.MongoClient(mongo_uri)
movies_vector_collection = connection[db][collection]
movies_vector_collection.delete_many({}) # make sure the target collection is empty

# define transofrmer model (from https://huggingface.co/sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2)
model = SentenceTransformer('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')

# load sample data. We are loading a csv with the following columns: fullplot, title, _id. (from https://www.mongodb.com/docs/atlas/sample-data/)
file = open('/Users/paolopicello/movies_data.csv')
csvreader = csv.reader(file)

rows = []
for row in csvreader:
    rows.append(row)


for row in rows:
    # encode 'fullplot' field
    encode = model.encode(row[0]).tolist()
    new_doc = {
        "fullplot": row[0],
        "title": row[1],
        "_id": row[2],
        "vector": encode
    }
    # insert in new collection
    movies_vector_collection.insert_one(new_doc)
    
print(f"{len(rows)} texts encoded")