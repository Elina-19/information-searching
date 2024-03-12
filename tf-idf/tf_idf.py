import pymorphy2
from os import listdir
from bs4 import BeautifulSoup
from nltk.tokenize import wordpunct_tokenize
from collections import Counter
import math


STORAGE_PATH = 'C:/Users/Repositories/itis/information-searching/crawler/storage'
TOKENS_PATH = 'C:/Users/Repositories/itis/information-searching/tokenizer/tokens.txt'
LEMMAS_PATH = 'C:/Users/Repositories/itis/information-searching/tokenizer/lemmas.txt'
RESULT_PATH = 'C:/Users/Repositories/itis/information-searching/tf-idf/'


def get_tokens():
    tokens = set()
    with open(TOKENS_PATH, 'r') as file:
        lines = file.readlines()
        for line in lines:
            tokens.add(line.strip())
    return tokens


def get_lemmas():
    lemmas = set()
    with open(LEMMAS_PATH, 'r') as file:
        lines = file.readlines()
        for line in lines:
            lemmas.add(line.split(':')[0])
    return lemmas


class TfIdfCounter:

    def __init__(self):
        self.morph = pymorphy2.MorphAnalyzer()
        self.tokens = get_tokens()
        self.lemmas = get_lemmas()
        self.documents = []
        self.counters = []
        self.file_names = []

    def get_data(self, with_normal_form):
        self.documents = []
        self.counters = []
        self.file_names = []
        for file_name in listdir(STORAGE_PATH):
            with open(STORAGE_PATH + '/' + file_name, 'r', encoding='utf-8') as file:
                self.file_names.append(file_name.split('.')[0])
                text_words = wordpunct_tokenize(BeautifulSoup(file, features='html.parser').get_text().lower())
                data = []
                for word in text_words:
                    if with_normal_form:
                        parsed_word = self.morph.parse(word)[0]
                        lemma = parsed_word.normal_form if parsed_word.normalized.is_known else word
                        if lemma in self.lemmas:
                            data.append(lemma)
                    else:
                        if word in self.tokens:
                            data.append(word)
                self.documents.append(data)
                self.counters.append(Counter(data))

    def get_tf(self, word_in):
        documents_tf = []
        for document, counter in zip(self.documents, self.counters):
            tf = dict()
            for word in word_in:
                tf[word] = counter[word] / len(document)
            documents_tf.append(tf)
        return documents_tf

    def get_idf(self, count_of_documents, word_in):
        counters = dict.fromkeys(word_in, 0)
        for counter in self.counters:
            for word in word_in:
                counters[word] = counters[word] + 1 if counter[word] != 0 else counters[word]
        idf = dict()
        for word in word_in:
            idf[word] = math.log10(count_of_documents/counters[word]) if counters[word] != 0 else 0
        return idf

    def get_tf_idf(self, tf, idf, word_in):
        idf_tf = []
        for tf_count in tf:
            idf_tf_dict = dict()
            for word in word_in:
                idf_tf_dict[word] = tf_count[word] * idf[word]
            idf_tf.append(idf_tf_dict)
        return idf_tf

    def calculate_tf_idf(self, dir_name, with_normal_form, words):
        self.get_data(with_normal_form)
        tf = self.get_tf(words)
        idf = self.get_idf(len(self.documents), words)
        tf_idf = self.get_tf_idf(tf, idf, words)
        for document_tf_idf, file_name in zip(tf_idf, self.file_names):
            with open(f'{RESULT_PATH}/{dir_name}/{file_name}.txt', 'w', encoding='utf-8') as file:
                for word in words:
                    file.write(f'{word} {idf[word]} {document_tf_idf[word]}\n')


if __name__ == '__main__':
    tf_idf_counter = TfIdfCounter()
    tf_idf_counter.calculate_tf_idf('tokens_tf_idf', False, tf_idf_counter.tokens)
    tf_idf_counter.calculate_tf_idf('lemmas_tf_idf', True, tf_idf_counter.lemmas)
