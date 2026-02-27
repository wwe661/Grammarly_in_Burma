from pyidaungsu import tokenize

def tokenize_text(text,form="word",return_type="flags"):
    # print(text)
    tokens = tokenize(text, form=form)
    result = []
    cursor = 0

    if return_type == "flags":
        for tok in tokens:
            error = False
            start = text.find(tok, cursor)
            if start == -1:
                start = cursor
                error = True
            end = start + len(tok)
            
            result.append({
                "message": tok,
                "start": start,
                "end": end,
                "error": error
            })
            cursor = end
    elif return_type == "tokens":
        result = tokens
    return result

res = tokenize_text("ဆရာ စာသင်သောအခါကျွန်တော်နှင့်မောင်မောင်တို့သည်ဂရုတစိုက်နားထောင်မှတ်သားကြသည်။")
print(res)