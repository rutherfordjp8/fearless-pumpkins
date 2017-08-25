from pymongo import MongoClient
import re
import nltk
# nltk.download_shell()
from nltk.corpus import stopwords
from nltk.stem.porter import *
stemmer = PorterStemmer()
from nltk.stem.snowball import SnowballStemmer
from multiprocessing import Pool
pool =  Pool()
import asyncio


client = MongoClient('localhost', 27017)
db = client['dataSet']

#training
collection = db.trainings
#democrat
# results = collection.find()
# print(results)
# print(collection.distinct('Text'))
patrick = []
jasper = []

# You need to get the ids as well as the text so you can update afterwards.
# You can use collection.find({}, {text: 1})
# It gives all the ids and text.
async def patrick_populater():
    for tweet in collection.distinct('Text', {'Classification': 1}):
        meaningful_words = []
        nonum = re.sub("[\d*]",
            "number ",
            tweet)
        letters_only = re.sub("[^a-zA-Z]",
            " ",
            nonum)
        nourlwords = re.sub(r'^https?:\/\/.*[\r\n]*', 'http ', letters_only, flags=re.MULTILINE)
        words =  nourlwords.lower().split()
        stops = set(stopwords.words("english"))
        meaningful_words = [w for w in words if not w in stops]
        clean = []
        for word in meaningful_words:
            clean.append(SnowballStemmer("english").stem(word))
        patrick.append(clean)
        jasper.append(1)

    for tweet in collection.distinct('Text', {'Classification': 0}):
        meaningful_words = []
        nonum = re.sub("[\d*]",
            "number ",
            tweet)
        letters_only = re.sub("[^a-zA-Z]",
            " ",
            nonum)
        nourlwords = re.sub(r'^https?:\/\/.*[\r\n]*', 'http ', letters_only, flags=re.MULTILINE)
        words =  nourlwords.lower().split()
        stops = set(stopwords.words("english"))
        meaningful_words = [w for w in words if not w in stops]
        clean = []
        for word in meaningful_words:
            clean.append(SnowballStemmer("english").stem(word))
        patrick.append(clean)
        jasper.append(0)

    return jasper, patrick;


async def test():
    jasper, patrick = await patrick_populater()
    seralizeTweets()

loop = asyncio.get_event_loop()
loop.run_until_complete(test())
loop.close()


# compares words in trainingModel to each word in every tweet
# creates a new array with a 1 where each word matched and a 0 otherwise
# returns [[0,1,0,0], [1,1,0,0], [0,0,1,1]]
eachTweet = []
def seralizeTweets(tweets, trainingModel):
    for tweet in tweets:
        temp = []
        for word in trainingModel:
            if word in tweet:
                temp.append(1)
            else:
                temp.append(0)
        eachTweet.append(temp)
