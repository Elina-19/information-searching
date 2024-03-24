import math
import os
import pymorphy2
from nltk import word_tokenize


TF_IDF_LEMMAS_PATH = 'C:/Users/Repositories/itis/information-searching/tf-idf/lemmas_tf_idf'
LEMMAS_PATH = 'C:/Users/Repositories/itis/information-searching/tokenizer/lemmas.txt'
INVERTED_INDEX_PATH = 'C:/Users/Repositories/itis/information-searching/inverted_index/inverted_index.txt'


class SearchSystem:

    def __init__(self):
        self.morph = pymorphy2.MorphAnalyzer()
        self.lemmas = self.get_lemmas()
        self.inverted_index = self.get_inverted_index()
        self.documents_lemmas_tf_idf = dict()
        self.lemmas_documents_tf_idf = dict()
        self.document_lengths = dict()
        self.get_lemmas_tf_idf()
        self.calc_document_vector_length()

    def get_inverted_index(self):
        inverted_index = dict()
        with open(INVERTED_INDEX_PATH, 'r', encoding='utf-8') as file:
            lines = file.read().splitlines()
            for line in lines:
                inverted_index[line.split(" ", 1)[0]] = set(eval(line.split(" ", 1)[1]))
        return inverted_index

    def get_lemmas(self):
        lemmas = dict()
        with open(LEMMAS_PATH, encoding='windows-1251', errors='ignore') as file:
            lines = file.readlines()
            for line in lines:
                lemmas[line.split(": ")[0]] = line.rstrip('\n').split(": ")[1].split(' ')
        return lemmas

    def get_lemmas_tf_idf(self):
        for file_name in os.listdir(TF_IDF_LEMMAS_PATH):
            with open(f'{TF_IDF_LEMMAS_PATH}/{file_name}', encoding='utf-8') as tf_idf_file:
                lines = tf_idf_file.readlines()
                for line in lines:
                    data = line.rstrip('\n').split(' ')
                    lemma_to_documents_tf_idf = self.lemmas_documents_tf_idf.get(data[0], {})
                    lemma_to_documents_tf_idf[file_name] = float(data[2])
                    self.lemmas_documents_tf_idf[data[0]] = lemma_to_documents_tf_idf
                    documents_to_lemma_tf_idf = self.documents_lemmas_tf_idf.get(file_name, {})
                    documents_to_lemma_tf_idf[data[0]] = float(data[2])
                    self.documents_lemmas_tf_idf[file_name] = documents_to_lemma_tf_idf

    def calc_document_vector_length(self):
        for doc in os.listdir(TF_IDF_LEMMAS_PATH):
            self.document_lengths[doc] = math.sqrt(sum(i ** 2 for i in self.documents_lemmas_tf_idf[doc].values()))

    def multiply_vectors(self, query_vector, document_vector, document_vector_length):
        return sum(document_vector.get(token, 0) for token in query_vector) / len(query_vector) / document_vector_length

    def process_query(self, query):
        query_vector = [self.morph.parse(token)[0].normal_form for token in word_tokenize(query, language='russian')]
        documents = set()
        for lemma in query_vector:
            documents = documents.union(self.inverted_index.get(lemma, set()))
        result = dict()
        for doc in documents:
            tf_idf_doc = doc.split('.')[0] + '.txt'
            result[doc] = self.multiply_vectors(query_vector, self.documents_lemmas_tf_idf[tf_idf_doc], self.document_lengths[tf_idf_doc])
        return sorted(result.items(), key=lambda r: r[1], reverse=True)


def run(query, system):
    result = system.process_query(query.lower())
    return [i[0] for i in result]


if __name__ == '__main__':
    search_system = SearchSystem()
    while True:
        user_input = input("Введите запрос: ")
        if user_input.lower() == 'exit':
            exit()
        try:
            print(search_system.process_query(user_input.lower()))
        except Exception as e:
            print(f"Error: {e}")
