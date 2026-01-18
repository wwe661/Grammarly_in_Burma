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


