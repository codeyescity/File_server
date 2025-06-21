# import spacy

# nlp_model = spacy.load("en_core_web_trf")
# text = "Dr. Jane Doe and Elon Musk attended the event with Marie Curie and Faycal Bouchefra"



 
# def extract_names(nlp_model, text):

#     doc = nlp_model(text)

#     for ent in doc.ents:
#         if ent.label_ == "PERSON":
#             parts = ent.text.split()
#             if len(parts) >= 2:
#                 first = parts[0]
#                 last = parts[1]
                
#                 return parts
    
#     return []




import spacy
import re

def extract_names(nlp_model, text):
    """
    Extract person names from text, prioritizing names that appear early in the document
    (typically where the resume owner's name appears)
    """
    
    # Don't lowercase the text for NER - proper names need capitalization
    # Take first 500 characters where the person's name usually appears
    header_text = text[:500]
    
    # Process the header text (keep original case)
    doc = nlp_model(header_text)
    
    names = []
    
    # Collect all person entities
    for ent in doc.ents:
        if ent.label_ == "PERSON":
            # Clean the name (remove extra whitespace, etc.)
            clean_name = re.sub(r'\s+', ' ', ent.text.strip())
            parts = clean_name.split()
            
            # Only consider names with 2+ parts and reasonable length
            if len(parts) >= 2 and len(clean_name) <= 50:
                names.append(parts)
    
    # Return the first valid name found (usually the resume owner)
    if names:
        return names[0]
    
    # Fallback: try to find name patterns in the first few lines
    lines = header_text.split('\n')[:3]  # Check first 3 lines
    
    for line in lines:
        line = line.strip()
        # Skip lines that are clearly not names (contain email, phone, etc.)
        if any(indicator in line.lower() for indicator in ['@', 'phone', 'email', 'linkedin', 'github', '•']):
            continue
            
        # Process individual lines for names
        doc = nlp_model(line)
        for ent in doc.ents:
            if ent.label_ == "PERSON":
                clean_name = re.sub(r'\s+', ' ', ent.text.strip())
                parts = clean_name.split()
                if len(parts) >= 2 and len(clean_name) <= 50:
                    return parts
    
    return []

def extract_names_advanced(nlp_model, text):
    """
    More advanced name extraction with multiple strategies
    """
    
    # Strategy 1: Look in the first 200 characters (header area)
    header = text[:200]
    doc = nlp_model(header)
    
    for ent in doc.ents:
        if ent.label_ == "PERSON":
            parts = ent.text.split()
            if len(parts) >= 2:
                return parts
    
    # Strategy 2: Look for name patterns (capitalized words at start)
    lines = text.split('\n')[:5]  # First 5 lines
    for line in lines:
        line = line.strip()
        
        # Skip lines with contact info indicators
        if any(x in line.lower() for x in ['@', 'phone', 'email', '•', 'linkedin']):
            continue
            
        # Look for 2-3 capitalized words pattern
        words = line.split()
        if len(words) >= 2:
            # Check if first 2-3 words are capitalized (potential name)
            if all(word[0].isupper() for word in words[:2] if word.isalpha()):
                return words[:2]
    
    return []