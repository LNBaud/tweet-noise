# -*- coding: utf-8 -*-
"""
Created on Mon Oct 29 09:35 2018

@author: dshi, hbaud, vlefranc
"""

import logging
from datetime import datetime, timezone
from config import FILEDIR, FILEBREAK, MONGODB
from pymongo import MongoClient
from Emojilist import emojilist
import spacy
import fr_core_news_md
nlp = fr_core_news_md.load()
spell = SpellChecker(language='fr')

logging.basicConfig(format='%(asctime)s - %(levelname)s : %(message)s', level=logging.INFO)


class VectorBuilder:
    """
    Retrieve data from the MongoDB database.

    """
    def __init__(self):

        self.do_continue = True
        self.count = 0
        self.line_count = 0
        self.current_file = FILEDIR + "tweets_" + datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f") + ".csv"
        # connect to MongoDB
        client = MongoClient("mongodb+srv://" + MONGODB["USER"] + ":" + MONGODB["PASSWORD"] + "@" + MONGODB["HOST"] + "/" + MONGODB["DATABASE"] + "?retryWrites=true")
        self.db = client[MONGODB["DATABASE"]]

    def retrieve(self):
        start = time.time()
        logging.info("Retrieving data...")
        tweets = self.db.tweets.find({"spam": {"$exists": True}})
        logging.info("Building features file...")
        for obj in tweets:
            self.count += 1
            self.write(obj)
            if self.count % 100 == 0:
                logging.info("{} elements retrieved".format(self.count))
        end = time.time()
        logging.info("Total of {0} elements retrieved in {1} seconds".format(self.count, end - start))

    def write(self, data):
        with open(self.current_file, "a+", encoding='utf-8') as f:
            if self.line_count == 0:
                f.write("\"id\",\"vectorize\",\"spam\",\n")
            f.write(
                data["id_str"] + self.vectorize(data)  + ("\"true\"" if data["spam"] else "\"false\"") +
                "\n")
        self.line_count += 1

        if self.line_count > FILEBREAK:
            logging.info("Closing file {}".format(self.current_file))
            self.current_file = FILEDIR + "tweets_" + datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f") + ".csv"
            self.line_count = 0

    @staticmethod
    def vectorize(data):
        message = data['text']
        doc = nlp(correct_words(message))
        vect = 0
        for token in doc:
            vect += token.vector/(len(doc))
        return vect

    @staticmethod
    def correct_words(message, spellchecker = spell):
        # find those words that may be misspelled
        doc = nlp (message)
        hashtag = False
        list = [str(token) for token in doc]
        corrected = ''
        for elt in list :
            for i in range(len(elt)-1,1, -1):
                if elt[i] == elt [i-1] and elt[i] == elt [i-2] :
                    elt = elt[:i]+elt[i+1:]
            #On coupe le mot si il s'agit du terme après un hastag
            if hashtag == True :
                decoup = re.findall('[A-Z][^A-Z]*',elt)
                for word in decoup :
                    corrected += word + ' '
                hashtag = False
            elif elt == '#' :
                hashtag = True
            elif elt in emojilist :
                pass
            else :
                corrected += elt + ' '
        return corrected




if __name__ == "__main__":
    vect = VectorBuilder()
    vect.retrieve()
