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

@app.post("/check")
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
    newflags = {i:j for i,j in enumerate(flags)}
    skip_for = 0
    for i, flag in enumerate(flags):
        if skip_for > 0:
            skip_for -= 1
            continue
        if flag["status"] == "unknown":
            toks = tokenize_text(flag["message"], form="syllable")
            _ =[]
            prev = flags[i-1]
            prevtok = tokenize_text(prev["message"],form="syllable")
            _.append(prevtok[-1] if len(prevtok)>1 else prevtok[0])
            
            next = flags[i+1]
            nexttok = tokenize_text(next["message"],form="syllable")
            _.append(nexttok[0])
            
            for j in _:
                temp = ""
                for t in toks:
                    temp += t["message"]
                    check = j["message"] + temp
                    status = check_token(check)
                    if status == "known":
                        return None
                
    return flags

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

