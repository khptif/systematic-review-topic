import re
import os
import json

import joblib
from langdetect import detect, DetectorFactory

DetectorFactory.seed = 0
from tqdm import tqdm
from gensim.utils import simple_preprocess

# import contextlib
import spacy

nlp = spacy.load("en_core_web_sm", disable=["parser", "ner"])
nlp.max_length = 10000000

import nltk
import ssl

try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
   pass
else :
   ssl._create_default_https_context = _create_unverified_https_context

nltk.download("stopwords")
nltk.download("names")

from nltk.corpus import stopwords
from nltk.corpus import names

from stop_words import get_stop_words
import unidecode
from spellchecker import SpellChecker
from gensim.models import phrases
from sklearn.feature_extraction.text import TfidfVectorizer
import pandas as pd


def pre_processing(df_to_list):

    # Remove Emails
    list_emails = [re.sub("\S*@\S*\s?", "", doc) for doc in df_to_list]
    # Remove new line characters
    list_new_line = [re.sub("\s+", " ", doc) for doc in list_emails]
    # Remove distracting single quotes
    list_quotes = [re.sub("'", "", doc) for doc in list_new_line]
    # Remove http remnants in the text
    list_http = [re.sub(r"^http?.*[\r\n]*", "", doc) for doc in list_quotes]
    # Remove www remnants in the text
    list_www = [re.sub(r"^www?.*[\r\n]*", "", doc) for doc in list_http]
    # change aaa into aa (or any other letter)
    list_aaa = [re.sub(r"(.)\1{2,}", r"\1\1", doc) for doc in list_www]
    # remove zero characters words
    list_zero = [re.sub(r"\b\w{0}\b", "", doc) for doc in list_aaa]

    
    return list_zero


def define_languages(list_pre_processing):

    languages = ["en"]
    list_languages = list_pre_processing[:]
    
    no_lang = {}

    for paper in tqdm(list_pre_processing, desc="Removing non-specified languages"):
        try:
            if detect(paper) not in languages:
                no_lang[list_pre_processing.index(paper)] = paper
                list_languages.remove(paper)
                
        except:
            no_lang[list_pre_processing.index(paper)] = paper
            list_languages.remove(paper)

    return list_languages


def sent_to_words(list_languages):

    for sentence in tqdm(list_languages, desc="Sentences to words"):
        yield (simple_preprocess(str(sentence), deacc=True))


def lemmatization(
    list_words, allowed_postags=["NOUN", "ADJ", "VERB", "ADV"]
):

    list_lemmatized = []

    for sent in tqdm(list_words, desc="Lemmatization"):
        doc = nlp(" ".join(sent))
        list_lemmatized.append(
            [token.lemma_ for token in doc if token.pos_ in allowed_postags]
        )

    return list_lemmatized


def create_stopwords():

    languages = ["en"]
    nltk_stopwords = stopwords.words("english")
    nltk_stopnames = names.words("male.txt") + names.words("female.txt")
    nltk_stopnames_unidecode = [
        unidecode.unidecode(name.lower()) for name in nltk_stopnames
    ]
    stop_words_stopwords = []

    for language in languages:
        stop_words_stopwords.extend(list(get_stop_words(language)))

    custom_stopwords = [
        "study",
        "volume",
        "issue",
        "magazine",
        "article",
        "doi",
        "preprint",
        "introduction",
        "background",
        "method",
        "methods",
        "result",
        "results",
        "conclusion",
        "conclusions",
        "limitations",
        "acknowledgements",
        "biorxiv",
        "peer",
        "review",
        "fig",
        "figure",
        "image",
        "copyright",
        "publication",
        "author",
        "authors",
        "publish",
        "editor",
        "from",
        "subject",
        "re",
        "edu",
        "use",
    ]

    list_stopwords = set(
        nltk_stopwords
        + nltk_stopnames_unidecode
        + stop_words_stopwords
        + custom_stopwords
    )

    return list_stopwords


def remove_words(list_lemmatized, list_stopwords):

    list_stopped = [
        [word for word in doc if word not in list_stopwords] for doc in list_lemmatized
    ]

    list_one_two = [
        re.sub(r"\b\w{1,2}\b", "", doc) for doc in [" ".join(x) for x in list_stopped]
    ]

    return list_one_two


def remove_misspelled(list_one_two, save, path_data_folder):

    f = open(f"{os.getcwd()}/BackEnd/files/dictionary_compact.json")
    dictionary = json.load(f)
    f.close()

    spell = SpellChecker()
    spell.word_frequency.load_words(list(dictionary.keys()))

    misspelled_words = spell.unknown(set(" ".join(list_one_two).split()))
    list_misspelled = [
        [word for word in doc.split() if word not in misspelled_words]
        for doc in list_one_two
    ]

    return list_misspelled


def create_ngrams(list_misspelled, save, path_data_folder):

    bigram = phrases.Phrases(
        list_misspelled, min_count=2, threshold=0.8, scoring="npmi"
    )

    trigram = phrases.Phrases(
        bigram[list_misspelled], min_count=2, threshold=0.8, scoring="npmi"
    )

    bigram_frozen = phrases.FrozenPhrases(bigram)
    trigram_frozen = phrases.FrozenPhrases(trigram)

    dict_bigram = {}
    dict_trigram = {}

    for phrase, score in bigram_frozen.find_phrases(list_misspelled).items():
        dict_bigram[phrase] = score

    list_bigrams = [
        bigram_frozen[doc] for doc in tqdm(list_misspelled, desc="Creating bigrams")
    ]

    for phrase, score in trigram_frozen.find_phrases(
        bigram_frozen[list_misspelled]
    ).items():
        dict_trigram[phrase] = score

    list_trigrams = [
        trigram_frozen[bigram_frozen[doc]]
        for doc in tqdm(list_misspelled, desc="Creating trigrams")
    ]

    return list_trigrams


def remove_common_and_unique(list_trigrams, save, path_data_folder):

    common_words = TfidfVectorizer(min_df=1, max_df=0.50).fit(
        " ".join(doc) for doc in list_trigrams
    )
    unique_words = TfidfVectorizer(min_df=2, max_df=1.00).fit(
        " ".join(doc) for doc in list_trigrams
    )

    if save:
        pd.DataFrame(common_words.stop_words_).to_csv(
            f"{path_data_folder}/common_words.csv", index=False
        )
        pd.DataFrame(unique_words.stop_words_).to_csv(
            f"{path_data_folder}/unique_words.csv", index=False
        )

    common_and_unique_words = TfidfVectorizer(min_df=2, max_df=0.50).fit(
        " ".join(doc) for doc in list_trigrams
    )
    list_temporary = [
        [word for word in doc if word not in common_and_unique_words.stop_words_]
        for doc in list_trigrams
    ]
    list_final = [" ".join(doc) for doc in list_temporary]

    print("Number of unique words removed:", len(unique_words.stop_words_))
    print("Number of common words removed:", len(common_words.stop_words_))
    print(
        "Total number of remaining words:",
        len(set(" ".join(doc for doc in list_final).split())),
    )

    return list_final


def remove_empty(id_list, list_final):

    for i in range(len(list_final)):
        if list_final[i] == "":
            id_list[i] = -1
    
    return id_list,list_final
