from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

from tokenizer import tokenize_text
from dictionary import *
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # allow all for now
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# app.mount("/static", StaticFiles(directory="static"), name="static")

class TextInput(BaseModel):
    text: str

@app.get("/", response_class=HTMLResponse)
def home():
    with open("static/index.html", "r", encoding="utf-8") as f:
        return f.read()
# DictA,DictB = load_all_dictionaries()
dictionary = load_dictionary()

@app.post("/checkfromtrainer")
def check_text(data: TextInput):
    tokens = tokenize_text(data.text, form="word")

    flags = []
    for t in tokens:
        status = check_token(t['message'].strip())
    
        if status == "unknown":
            color = "red"
        elif status == "non-burmese":
            color = "gray"
        else:
            color = "green"

        flags.append({
            "start": t["start"],
            "end": t["end"],
            "message": t['message'],
            "status": status,
            "color": color
        })
    # flags = extra_check_for_syllable(flags)
    flags = extra_check_for_word(flags)
    return { "flags": flags }

@app.post("/checkfromuser")
def check_text(data: TextInput):
    tokens = tokenize_text(data.text, form="word")

    flags = []
    for t in tokens:
        status = check_token(t['message'].strip())
    
        if status == "unknown":
            color = "red"
        elif status == "non-burmese":
            color = "gray"
        else:
            color = "green"

        flags.append({
            "start": t["start"],
            "end": t["end"],
            "message": t['message'],
            "status": status,
            "color": color
        })
    # flags = extra_check_for_syllable(flags)
    # flags = extra_check_for_word(flags)
    return { "flags": flags }

def extra_check_for_syllable(flags):
    newflags = {i:j for i,j in enumerate(flags)}
    skip_for = 0
    for i, flag in enumerate(flags):
        if skip_for > 0:
            skip_for -= 1
            continue
        if flag["status"] == "unknown":
            correction, j , k = check_uncertain(flags[i-3:i+4])
            if correction is not None:
                # newflags[i]["correction"] = correction
                start = flags[i-j+k]["start"]
                end = flags[i+k]["end"]
                message = ""
                for x in range(i-j+k, i+k+1):
                    message += flags[x]["message"]
                status = check_token(message)
                color = "green"
                _ = {"start": start, "end": end, "message": message, "status": status, "color": color}
                for a in range(i-j+k, i+k+1):
                    newflags.pop(a)
                newflags[i] = _
                newflags[i]["correction"] = correction
                skip_for = k
            
    flags = [newflags[i] for i in sorted(newflags.keys())]   
    return flags

def check_uncertain(tokens):
    for i in range(1,4):
        grams = tokens[3-i:3+i+1]
        for j in range(i+1):
            _ = ""
            # _ = grams[j]["message"]+grams[j+1]["message"]
            for k in range(i+1):
                _ =_ + grams[k+j]["message"]
            status = check_token(_)
            if status == "known":
                return _,i,j
    return None,None,None

def extra_check_for_word(flags):
    print("Starting extra check for words...")
    i = 0
    while i < len(flags):

        if flags[i]["status"] != "unknown":
            i += 1
            continue
        print(f"Checking token at index {i}: {flags[i]['message']}")
        # 1. Extract window
        window, w_start, w_end = get_window(flags, i, radius=1)
        window_text = "".join(tok["message"] for tok in window)

        # 2. Syllable tokenize window
        syllables = tokenize_text(
            window_text,
            form="syllable",
            return_type="tokens"
        )
        print(f"Syllables in window: {syllables}")
        # 3. Generate candidates
        candidates = generate_candidates(syllables, max_n=4)
        if not candidates:
            i += 1
            continue
        print(f"Generated {len(candidates)} candidates: {[w for _,_,w,_ in candidates]},{candidates}")
        # 4. Segment syllables
        results = segment(syllables, candidates)
        if not results:
            i += 1
            continue
        print(f"Generated {len(results)} segmentations.{results}")
        # 5. Choose best segmentation
        # best = max(
        #     results,
        #     key=lambda seg: (
        #         coverage_ratio(seg, syllables),      # maximize coverage
        #         -len(seg)                             # prefer fewer tokens
        #     )
        # )

        # if coverage_ratio(best, syllables) < 0.7:
        #     i += 1
        #     continue
        best = min(results, key=score)

        print(f"Best segmentation: {best}")
        # 6. Build new tokens
        new_tokens = []
        cursor = window[0]["start"]

        for word,typ in best:
            if typ == "dict":
                color = "green"
            else:
                color = "red"
            length = len(word)
            new_tokens.append({
                "start": cursor,
                "end": cursor + length - 1,
                "message": word,
                "status": "corrected",
                "color": color
            })
            cursor += length
        print(f"Replacing window {w_start}-{w_end} with tokens: {[t['message'] for t in new_tokens]}")
        # 7. Replace window
        flags = flags[:w_start] + new_tokens + flags[w_end:]

        # 8. Re-check from start of replacement
        i = w_start

    return flags

# def extra_check_for_word(flags):
#     newflags = {i:j for i,j in enumerate(flags)}
#     skip_for = 0
#     for i, flag in enumerate(flags):
#         if skip_for > 0:
#             skip_for -= 1
#             continue
#         if flag["status"] == "unknown":
#             window, start, end = get_window(flags, i, radius=1)
#             window_text = "".join(tok["message"] for tok in window)
#             syllables = tokenize_text(window_text, form="syllable",return_type="tokens")
#             canditates = generate_candidates(syllables, max_n=4)
#             results = segment(syllables, canditates)
#             best = min(
#                 results,
#                 key=lambda seg: (len(seg), -sum(len(w) for w in seg))
#             )
#             new_token = {
#                 "start": window[0]["start"],
#                 "end": window[-1]["end"],
#                 "message": corrected_word,
#                 "status": "corrected",
#                 "source": "ngram"
#             }

#             # toks = tokenize_text(flag["message"], form="syllable")
#             # _ =[]
#             # prev = flags[i-1]
#             # prevtok = tokenize_text(prev["message"],form="syllable")
#             # _.append(prevtok[-1] if len(prevtok)>1 else prevtok[0])
            
#             # next = flags[i+1]
#             # nexttok = tokenize_text(next["message"],form="syllable")
#             # _.append(nexttok[0])
            
#             # for j in _:
#             #     temp = ""
#             #     for t in toks:
#             #         temp += t["message"]
#             #         check = j["message"] + temp
#             #         status = check_token(check)
#             #         if status == "known":
#             #             return None
                
#     return flags

def check_token(token):
    if not is_burmese_token(token):
        return "non-burmese"
    elif token in dictionary:
        return "known"
    else:
        return "unknown"
    
def is_burmese_char(ch):
    code = ord(ch)
    return (
        0x1000 <= code <= 0x109F or
        0xAA60 <= code <= 0xAA7F
    )

def is_burmese_token(token):
    burmese_chars = 0
    total_chars = 0

    for ch in token:
        if ch.isalpha():
            total_chars += 1
            if is_burmese_char(ch):
                burmese_chars += 1

    if total_chars == 0:
        return False

    return burmese_chars / total_chars > 0.6

def get_window(flags, i, radius=1):
    start = max(0, i - radius)
    end = min(len(flags), i + radius + 1)
    return flags[start:end], start, end
def generate_candidates(syllables, max_n=4):
    candidates = []
    n = len(syllables)

    for i in range(n):
        for j in range(i+1, min(i+max_n+1, n+1)):
            word = "".join(syllables[i:j])

            if word in dictionary:
                candidates.append((i, j, word, "dict"))

            elif j == i + 1:  # single syllable fallback
                candidates.append((i, j, word, "error"))

    return candidates
def segment(syllables, candidates):
    index_map = {}
    for i, j, w, t in candidates:
        index_map.setdefault(i, []).append((j, w, t))

    results = []

    def dfs(pos, path):
        if pos == len(syllables):
            results.append(path)
            return
        if pos not in index_map:
            return
        for next_pos, word, typ in index_map[pos]:
            dfs(next_pos, path + [(word, typ)])

    dfs(0, [])
    return results

def score_segmentation(segmentation, total_syllables):
    covered = sum(len(word) for word in segmentation)
    coverage_ratio = covered / total_syllables
    return coverage_ratio, -len(segmentation)

def coverage_ratio(segmentation, syllables):
    covered = sum(len(word) for word in segmentation)
    return covered / len(syllables)

def score(seg):
    dict_words = sum(1 for _, t in seg if t == "dict")
    errors = sum(1 for _, t in seg if t == "error")
    length = len(seg)

    return (
        -dict_words * 10,  # prefer dictionary
        errors * 20,       # penalize errors
        length             # prefer fewer tokens
    )
