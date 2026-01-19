# dictionary.py
from datasets import load_dataset

def load_huggingface_dictionary():
    ds = load_dataset("Rickaym/Burmese-Dictionary")
    return set(ds["train"]["word"])

def load_wiktionary_dictionary():
    ds = load_dataset("freococo/myanmar_wikitionary_words")
    return set(ds["train"]["my_word"])

def load_all_dictionaries():
    return load_huggingface_dictionary(),load_wiktionary_dictionary()

import csv
import unicodedata

def add_word(word):
    with open("Dictionary/lookup_dictionary.csv","a",encoding="utf-8") as f:
        word = unicodedata.normalize("NFC", word)
        f.write(word+"\n")


def load_dictionary():
    DICT_PATH = "../Dictionary/dictionary.csv"
    dictionary = set()
    with open(DICT_PATH, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            word = row["word"].strip()
            if not word:
                continue

            # word = unicodedata.normalize("NFC", word)
            dictionary.add(word)

    print(f"[DICT] Loaded {len(dictionary)} words")
    return dictionary


