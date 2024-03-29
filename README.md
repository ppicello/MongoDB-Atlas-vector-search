# Atlas Search & Hugging Face transformers

![header](/docs/header.png?raw=true "header")

This repo wants to be an easy way to showcase how to leverage [Hugging Face](https://huggingface.co/) transformers in [Atlas Search](https://www.mongodb.com/docs/atlas/atlas-search/). In this example we show how to build multi dimensional vectors starting from text using the Hugging face library and the [sentence-transformers models](https://www.sbert.net/), how to build Atlas Search indexes for vector search and then how to leverage those vectors to get more relevant results. In particular we will show how to use those vectors for implementing recommendation systems (similar to the the `moreLikeThis` operator) and for increasing the effectiveness of the search system without having to manually define synonyms.

1. [Test 1: Similarity Search](#test1)
2. [Test 2: Relevant results without manually defining synonyms](#test2)
3. [Test 3: Multi-Lingual Search](#test3)

<a id="AtlasCluster"></a>

## Load sample data

To follow along with the example, you will need to create a MongoDB Atlas cluster and load the sample data set into your cluster. We assume you have a csv file with the data you want to use. For this example we wil leverage the sample_mflix.movies collection part of the sample dataset available in MongoDB Atlas. For simplicity we have defined a csv file with just the `fullplot`, `title` and `_id` fields. You can find an example of the csv document as part of this project.

![csv](/docs/csv.png?raw=true "csv")

Once you have your csv file ready you need to update the MongoDB Atlas uri in `encoder.py`. Once you have updated the file with your MongoDB Atlas uri you are ready to execute `encoder.py`. This file will leverage the Hugging Face [sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2](https://huggingface.co/sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2) model for generating a 384 dimensional vector starting from the `fullplot` field for each movie. The document will be then loaded in MongoDB Atlas in the `vector_search.movies_vector` collection.

```console
python3 encoder.py
```

You will end up with a collection that looks like this.

![collection](/docs/collection2.png?raw=true "collection")

## Define Atlas Search Index

Create the following search index on the `vector_search.movies_vector` collection:

```json
{
  "mappings": {
    "fields": {
      "vector": [
        {
          "dimensions": 384,
          "similarity": "cosine",
          "type": "knnVector"
        }
      ]
    }
  }
}
```

Your index should look like this: 

![index](/docs/vector_search_index.png?raw=true "index")

<a id="test1"></a>
## Test 1: Similarity Search


The first capability we want to showcase is the ability to leverage these vectors for similarity search. In this example we want to find movies "similar" to others starting from the description contained in the `fullplot` field. This capability could be leveraged for example in a movie catalog app  to provide the end user with "related" movies.

To do so we need to paste the fullplot field of the movie we are interested in the `vector_search.py` file. 

The pipeline used to compute the results looks like: 

```json
[{
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
        "score": {
            "$meta": "searchScore"
        }
    }
}]
```

We can then run `vector_search.py` with:

```console
python3 vector_search.py
```

And if we look at the results we can see that the first result is exactly the same document, and we have a score of 1.0, and then we have other "related" movies, ranked by their score.

![results1](/docs/results1.png?raw=true "results1")

<a id="test2"></a>
## Test 2: Relevant results without manually defining synonyms

The second capability we want to showcase here is the ability of the model of detecting synonyms. Words with the same "meaning" will in fact be encoded closer in the vector space. In a search engine like Atlas Search we can use this feature to increase the effectiveness of our search results.

For this second example we are going to issue a query for the word `automobile`. Again, the only thing we have to do is to employ the same model sued for encoding our documents, to encode our query. In this example this will simply be:

```python
query_encoding = model.encode("automobile").tolist()
```
```console
python3 vector_search.py
```

And if we look at the results we can see that we got results with the words `cars` or `auto` or `camper` but no documents actually contain the word `automobile` and we did not perform any explicit synonyms definition.

![results2](/docs/results2.png?raw=true "results2")

<a id="test3"></a>
## Test 3: Multi-Lingual Search

One of the coolest things of the model we are using for this example is that it is a multi-lingual model, meaning that similar inputs in different languages are mapped close in vector space. This model in particular is trained with more than 50 languages. So what this means for your application is that you could be able to support multi language search without configuring anything. 

Let's for example search for lawyers related movies 

```python
query = "lawyer"
```

As we can expect we get back movies related to lawyers. 

But let's try with different languages.

```python
# italian
query = "avvocato"
```
```python
# french
query = "juriste"
```
```python
# german
query = "Rechtsanwalt"
```
```python
# spanish
query = "abogado"
```

As you can see from the image below, we get relevant results even if all this words never appear in our data and we only have english data. You can play around with different languages and you will get similar results.

![lawyer](/docs/lawyer.png?raw=true "lawyer")

> **Note**
> In this case this multi-language capability is part of the model used and not really related to Atlas Search, Atlas Search is used to perform the multidimensional search once the encodings are computed by the model. In a real case scenario you could choose between using a pre-trained model (like in this example), fine-tune an existing model, or train and bring your own models. 