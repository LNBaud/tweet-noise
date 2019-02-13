# -*- coding: utf-8 -*-
"""
Created on Wed Oct 31 14:28 2018

@author: dshi, hbaud, vlefranc
"""

import pandas as pd
import datetime
from config import FILEDIR
import os

from sklearn.preprocessing import LabelEncoder

pd.set_option('display.width', None)


class Classification:

    def __init__(self):
        self.current_file = FILEDIR + "tweets_2018-11-23T09:17:21.577598.csv"
        self.columns = ['nb_follower', 'nb_following', 'verified', 'reputation', 'age', 'nb_tweets', 'posted_at',
                        'proportion_spamwords', 'proportion_whitewords', 'orthographe', 'nb_hashtag', 'guillemets',
                        'nb_emoji', 'spam']
        self.df_tweets = None
        self.df_tweets_categorized = None

    def create_dataframe(self, categorize=True):
        df = pd.read_csv(self.current_file, encoding="utf-8")
        # print(df.head())
        # print(df.describe())
        self.df_tweets = df[self.columns]
        # print(self.df_tweets)
        self.df_tweets_categorized = self.df_tweets.copy(deep=True)
        self.categorize_columns(['posted_at'], self.categorize_time)
        if categorize:
            self.categorize_columns(['reputation'], self.categorize_proportion)
            self.categorize_columns(['orthographe'], self.categorize_orth)
            self.categorize_columns(['proportion_spamwords'], self.categorize_spamword)
            self.categorize_columns(['proportion_whitewords'], self.categorize_whiteword)
            self.categorize_columns(['verified'], self.categorize_bool)
            self.categorize_columns(['nb_emoji'], self.categorize_emoji)
            self.categorize_columns(['spam'], self.categorize_bool)
            self.categorize_columns(['nb_follower', 'nb_following'], self.categorize_follower_following)
            self.categorize_columns(['age'], self.categorize_age)
            self.categorize_columns(['nb_tweets'], self.categorize_nb_tweets)
        # print(self.df_tweets_categorized.head())
        # print(type(df_tweets_categorized))
        return self.df_tweets_categorized

    def categorize_proportion(self, x):
        if x > 0.5:
            return 1
        else:
            return 0

    def categorize_orth(self, x):
        if x > 0.4:
            return 1
        else:
            return 0

    def categorize_spamword(self, x):
        if x < 0.15:
            return 0
        else:
            return 1

    def categorize_bool(self, x):
        if x:
            return 1
        else:
            return 0

    def categorize_time(self, x):
        now = datetime.datetime.now()
        today8am = now.replace(hour=8, minute=0, second=0, microsecond=0)
        todaynoon = now.replace(hour=12, minute=0, second=0, microsecond=0)
        today2pm = now.replace(hour=14, minute=0, second=0, microsecond=0)
        today6pm = now.replace(hour=18, minute=0, second=0, microsecond=0)
        today10pm = now.replace(hour=22, minute=0, second=0, microsecond=0)
        t = x.split(':')
        time = now.replace(hour=int(t[0]), minute=int(t[1]), second=int(t[2]), microsecond=0)
        if today8am <= time < todaynoon:
            return 0
        elif todaynoon <= time < today2pm:
            return 1
        elif today2pm <= time < today6pm:
            return 2
        elif today6pm <= time < today10pm:
            return 3
        else:
            return 4

    def categorize_follower_following(self, x):
        if x < 100:
            return 0
        elif x < 300:
            return 1
        elif x < 6000:
            return 2
        else:
            return 3

    def categorize_age(self, x):
        if x < 180:
            return 0
        if x < 730:
            return 1
        if x < 2190:
            return 2
        else:
            return 3

    def categorize_nb_tweets(self, x):
        if x < 40000:
            return 0
        if x < 80000:
            return 1
        else:
            return 2

    def categorize_whiteword(self, x):
        if x > 0:
            return 1
        else:
            return 0

    def categorize_emoji(self, x):
        if x > 0:
            return 1
        else:
            return 0

    def categorize_columns(self, cols, func):
        # print(cols)
        for col in cols:
            self.df_tweets_categorized[col] = self.df_tweets[col].apply(func)
            # print(self.df_tweets[col])


if __name__ == "__main__":

    classification = Classification()
    classification.create_dataframe()


# for col in df_tweets_categorized.columns.values:
# print(col, df_tweets_categorized[col].unique())

"""
def label_encode(data_frame, cols):
    for col in cols:
        le = LabelEncoder()
        col_values_unique = list(data_frame[col].unique())
        le_fitted = le.fit(col_values_unique)

        col_values = list(data_frame[col].values)
        le.classes_
        col_values_transformed = le.transform(col_values)
        data_frame[col] = col_values_transformed


# df_tweets_ohe = df_tweets.copy(deep=True)
# to_be_encoded_cols = df_tweets_ohe.columns.values
# label_encode(df_tweets_ohe, to_be_encoded_cols)
# print(df_tweets_ohe.head())"""
