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

query = "The Driver and The Mechanic are two car freaks driving a 1955 Chevy throughout the southwestern U.S. looking for other cars to race. They are totally dedicated to The Car and converse with each other only when necessary. At a gas station, The Driver and The Mechanic, along with a girl who has ingratiated herself into their world, meet G.T.O., a middle-aged man who fabricates stories about his exploits. It is decided to have a race to Washington, D.C., where the winner will get the loser's car. Along the way, the race and the highway metaphorically depict the lives of these contestants as they struggle to their destination."
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