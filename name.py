# import spacy

# nlp_model = spacy.load("en_core_web_trf")
# text = "Dr. Jane Doe and Elon Musk attended the event with Marie Curie and Faycal Bouchefra"



 
def extract_names(nlp_model, text):

    doc = nlp_model(text)

    for ent in doc.ents:
        if ent.label_ == "PERSON":
            parts = ent.text.split()
            if len(parts) >= 2:
                first = parts[0]
                last = parts[1]
                
                return parts
    
    return []