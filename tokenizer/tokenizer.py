import nltk
import re
import pymorphy2
from os import listdir, path
from bs4 import BeautifulSoup
from nltk.corpus import stopwords
from nltk.tokenize import wordpunct_tokenize


STORAGE_PATH = path.dirname('C:/Users/Repositories/itis/information-searching/crawler/storage/')
RESULT_PATH = path.dirname('C:/Users/Repositories/itis/information-searching/tokenizer/')

morph = pymorphy2.MorphAnalyzer()
# nltk.download('stopwords')
stop_words = set(stopwords.words('russian'))
functors_pos = {'INTJ', 'PRCL', 'CONJ', 'PREP'}


def is_valid(token):
    is_stop_word = token.lower() in stop_words
    is_russian_word = re.compile(r'^[а-яА-Я]+$').match(token)
    parsed_token = morph.parse(token)[0]
    is_valid_word = parsed_token.tag.POS not in functors_pos and parsed_token.score >= 0.8
    return not is_stop_word and is_russian_word and is_valid_word


def get_tokens():
    tokens = set()
    for i, file_name in enumerate(listdir(STORAGE_PATH), start=1):
        print(f'Process: {i}')
        html = open(STORAGE_PATH + '/' + file_name, 'r', encoding='utf-8', errors='ignore')
        text = BeautifulSoup(html, features='html.parser').get_text()
        html.close()
        tokens.update(set(filter(is_valid, wordpunct_tokenize(text.lower()))))
    return tokens


def get_lemmas(tokens):
    lemmas = dict()
    for token in tokens:
        normal_form = morph.parse(token)[0].normal_form
        if normal_form not in lemmas:
            lemmas[normal_form] = set()
        lemmas[normal_form].add(token)
    return lemmas


def write_tokens(tokens):
    tokens_file = open(RESULT_PATH + '/tokens.txt', 'w')
    for token in tokens:
        tokens_file.write(token + '\n')
    tokens_file.close()


def write_lemmas(lemmas):
    lemmas_file = open(RESULT_PATH + '/lemmas.txt', 'w')
    for lemma, tokens in lemmas.items():
        lemmas_file.write(lemma + ': ' + ' '.join(map(str, tokens)) + '\n')
    lemmas_file.close()


if __name__ == '__main__':
    tokens_result = get_tokens()
    write_tokens(tokens_result)
    lemmas_result = get_lemmas(tokens_result)
    write_lemmas(lemmas_result)
