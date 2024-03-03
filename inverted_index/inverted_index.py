from os import listdir, path
from bs4 import BeautifulSoup


STORAGE_PATH = path.dirname('C:/Users/Repositories/itis/information-searching/crawler/storage/')
LEMMAS_PATH = 'C:/Users/Repositories/itis/information-searching/tokenizer/lemmas.txt'
INVERTED_INDEX_PATH = 'C:/Users/Repositories/itis/information-searching/inverted_index/inverted_index.txt'


def get_texts():
    texts = dict()
    for file_name in listdir(STORAGE_PATH):
        html = open(STORAGE_PATH + '/' + file_name, 'r', encoding='utf-8', errors='ignore')
        text = BeautifulSoup(html, features='html.parser').get_text().lower()
        html.close()
        texts[file_name] = text
    return texts


def get_lemmas():
    lemmas = dict()
    lines = open(LEMMAS_PATH, encoding='windows-1251', errors='ignore').read().splitlines()
    for l in lines:
        lemmas[l.split(": ")[0]] = l.split(": ")[1].split(' ')
    return lemmas


def build_index():
    inverted_index = dict()
    lemmas = get_lemmas()
    texts = get_texts()

    for key, lemmas in lemmas.items():
        for file_name, text in texts.items():
            if any([l in text for l in lemmas]):
                if key not in inverted_index:
                    inverted_index[key] = set()
                inverted_index[key].add(file_name)

    for key in inverted_index.keys():
        inverted_index[key] = list(inverted_index[key])

    with open(INVERTED_INDEX_PATH, 'w+', encoding='utf-8') as index:
        for key, files in inverted_index.items():
            index.write(key + ' ' + str(files) + '\n')


if __name__ == "__main__":
    build_index()