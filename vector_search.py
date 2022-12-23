from sentence_transformers import SentenceTransformer
from bson import json_util
import pymongo
import json

mongo_uri = "mongodb+srv://username:password@cluster0.xxxxx.mongodb.net/?retryWrites=true&w=majority"
db = "vector_search"
collection = "movies_vector"

# initialize db connection
connection = pymongo.MongoClient(mongo_uri)
movies_vector_collection = connection[db][collection]

model = SentenceTransformer('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')

query = "Rechtsanwalt"
query_encoding = model.encode(query).tolist()

pipeline = [
    {
        "$search": {
            "index": "vector_search_index",
            "knnBeta": {
                "vector": query_encoding,
                "path": "vector",
                "k": 10
            }
        }
    },
    {
        "$project": {
            "vector": 0,
            "_id": 0,
            'score': {
                '$meta': 'searchScore'
            }
        }
    }
]

# Execute the pipeline
docs = list(movies_vector_collection.aggregate(pipeline))

# Return the results unders the docs array field
json_result = json_util.dumps({'docs': docs}, json_options=json_util.RELAXED_JSON_OPTIONS)
    
print(json_result)