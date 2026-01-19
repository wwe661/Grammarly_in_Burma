from learningmode.dictionary import load_all_dictionaries
import csv

a,b = load_all_dictionaries()
import unicodedata
with open("Dictionary/dictionary.csv","w",encoding="utf-8") as f:
    f.write("word\n")
    for word in sorted(a):
        word = unicodedata.normalize("NFC", word)  
        f.write(word+"\n")
    for word in sorted(b):
        word = unicodedata.normalize("NFC", word)  
        f.write(word+"\n")

print(len(a))
print(len(b))

def load_dictionary():
    DICT_PATH = "Dictionary/dictionary.csv"
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

dictionary = load_dictionary()
print(len(dictionary))
print(type(dictionary))