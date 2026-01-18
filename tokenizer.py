from pyidaungsu import tokenize

def tokenize_text(text,form="word"):
    tokens = tokenize(text, form=form)
    result = []
    cursor = 0

    for tok in tokens:
        error = False
        start = text.find(tok, cursor)
        if start == -1:
            start = cursor
            error = True
        end = start + len(tok)
        result.append({
            "token": tok,
            "start": start,
            "end": end,
            "error": error
        })
        cursor = end

    return result
