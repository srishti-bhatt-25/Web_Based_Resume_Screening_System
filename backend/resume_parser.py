import PyPDF2

def extract_text(path):
    text = ""
    try:
        with open(path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            for p in reader.pages:
                text += p.extract_text()
    except:
        pass

    return text.lower()