import json

import os
import re
# from nltk.tokenize import word_tokenize
from PyPDF2 import PdfReader
from docx import Document

from dbmanager import PostgreSQLWrapper

def read_dict_from_json(file_path):
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
            return data
    except FileNotFoundError:
        print(f"Error: The file {file_path} was not found.")
        return None
    except json.JSONDecodeError:
        print(f"Error: The file {file_path} contains invalid JSON.")
        return None
    



def get_keywords(db: PostgreSQLWrapper, jobOfferId ):

    Skills = []

    select_joboffer_query = """
    SELECT "Skills".*
    FROM "Skills"
    LEFT JOIN "JobOfferSkills" ON "Skills"."SkillId" = "JobOfferSkills"."skillId"
    WHERE "JobOfferSkills"."jobOfferId" = %s
    """

    res = db.fetch_all(select_joboffer_query, (jobOfferId,))
    print(res)

    for element in res:
        Skills.append(element[1])

    print(Skills)

    return Skills

    with open(file_path, 'r', encoding='utf-8') as file:
        return [line.strip().lower() for line in file.readlines() if line.strip()]

def get_joboffer(db: PostgreSQLWrapper, jobOfferId ):


    select_joboffer = """
    SELECT "JobOfferId", "jobName", description, "educationNeeded", "createdAt", "updatedAt"
    FROM "JobOffer"
    WHERE "JobOfferId" = %s
    """

    res = db.fetch_one(select_joboffer, (jobOfferId,))

    print(res[2])

    return res[2]


def get_resumes(db: PostgreSQLWrapper, jobOfferId):


    select_resumes_query = """
    SELECT  "cvId"
    FROM public."User"
    LEFT JOIN public."JobApplication" ON  "User"."UserId" = "JobApplication"."userId"
    WHERE "User"."role" = 'user'
    AND "JobApplication"."jobOfferId" = %s
    """

    res = db.fetch_all(select_resumes_query, (jobOfferId,))

    return res

def read_formated_file(file_path):

    try:
        file_ext = os.path.splitext(file_path)[1].lower()
        text = ""
    
        # Extract text based on file type
        if file_ext == ".pdf":
            text = read_pdf(file_path)
        elif file_ext == ".docx":
            text = read_docx(file_path)
        elif file_ext == ".txt":
            text = read_text_file(file_path)

        return text
    except:
        print("Error while reading the file")

def read_text_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

def read_pdf(file_path):
    # text = ""
    # reader = PdfReader(file_path)
    # for page in reader.pages:
    #     text += page.extract_text()
    # return text

    import pdfplumber

    with pdfplumber.open(file_path) as pdf:
        # Extract all text from the PDF
        all_text = ""
        for page in pdf.pages:
            all_text += page.extract_text()
        
        print(all_text)
        return all_text

def read_docx(file_path):
    doc = Document(file_path)
    return "\n".join([para.text for para in doc.paragraphs])

# def process_resume(model, file_path):
#     if file_path.endswith('.pdf'):
#         text = read_pdf(file_path)
#     elif file_path.endswith('.docx'):
#         text = read_docx(file_path)
#     else:
#         return [], ""
    
#     # Clean text
#     text = re.sub(r'\s+', ' ', text).strip().lower()
#     full_text = text
#     #words = word_tokenize(text)
#     words = model.encode(text, convert_to_tensor=True)
    
#     # Split into chunks if needed
#     chunks = []
#     if len(words) > 200:
#         for i in range(0, len(words), 200):
#             chunk = ' '.join(words[i:i+200])
#             chunks.append(chunk)
#     else:
#         chunks.append(' '.join(words))
    
#     return chunks, full_text


# def process_resume(model , file_path):
#     if file_path.endswith('.pdf'):
#         text = read_pdf(file_path)
#     elif file_path.endswith('.docx'):
#         text = read_docx(file_path)
#     else:
#         return [], ""
    
#     # Clean text
#     text = re.sub(r'\s+', ' ', text).strip().lower()
#     full_text = text
    
#     # Split into sentences or meaningful chunks (better for sentence transformers)
#     sentences = [text]
    
#     # Alternatively, you could use sentence splitting:
#     # from nltk.tokenize import sent_tokenize
#     # sentences = sent_tokenize(text)
    
#     # Split into chunks if needed (better to split by sentences than arbitrary word counts)
#     chunks = []
#     current_chunk = []
#     current_length = 0
    
#     for sentence in sentences:
#         sentence_length = len(sentence.split())
#         if current_length + sentence_length > 200 and current_chunk:
#             chunks.append(' '.join(current_chunk))
#             current_chunk = []
#             current_length = 0
#         current_chunk.append(sentence)
#         current_length += sentence_length
    
#     if current_chunk:
#         chunks.append(' '.join(current_chunk))
    
#     # Generate embeddings for each chunk
#     chunk_embeddings = model.encode(chunks)
    
#     return chunk_embeddings, full_text



def process_resume(model, file_path):
    if file_path.endswith('.pdf'):
        text = read_pdf(file_path)
    elif file_path.endswith('.docx'):
        text = read_docx(file_path)
    else:
        return [], ""
    
    # Clean text
    text = re.sub(r'\s+', ' ', text).strip().lower()
    full_text = text
    words = text.split()  # Simple whitespace tokenization
    
    # Split into chunks
    chunks = []
    for i in range(0, len(words), 200):
        chunk = ' '.join(words[i:i+200])
        chunks.append(chunk)
    
    # Generate embeddings for each chunk
    chunk_embeddings = model.encode(chunks)
    
    return chunk_embeddings, full_text

def calculate_keyword_score(text, keywords):
    text = text.lower()
    found_keywords = [kw for kw in keywords if kw in text]
    return len(found_keywords) / len(keywords) if keywords else 0


def extract_contact_info(text):
    
    # Regular expression for phone numbers (improved pattern)
    phone_regex = re.compile(
        r'(?:\+?(\d{1,3}))?[-. (]*(\d{3})[-. )]*(\d{3})[-. ]*(\d{4})'  # Common formats
        r'|\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'  # US-style numbers
        r'|\b\d{10}\b'  # 10-digit numbers
    )
    
    # Regular expression for email addresses
    email_regex = re.compile(
        r'\b[A-Za-z0-9][A-Za-z0-9_.%+-]{0,63}@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b'
    )


    
    # Find matches and deduplicate
    phone_numbers = list(set(phone_regex.findall(text)))
    emails = list(set(email_regex.findall(text)))
    
    # Clean phone numbers (join tuple matches from regex groups)
    cleaned_phones = []
    for number in phone_numbers:
        if isinstance(number, tuple):
            # Join non-empty groups and remove non-numeric characters
            cleaned = ''.join(number).replace('(', '').replace(')', '')
            cleaned_phones.append(cleaned)
        else:
            cleaned_phones.append(number)
    
    return {
        'phone_numbers': cleaned_phones,
        'emails': emails
    }

def insert_resumes_db(db: PostgreSQLWrapper, cvId, cvUrl, sha256_hash, phone_numbers, emails, name, jobOfferId=None):

    email = ""
    phoneNumber = ""
    fullname = ""

    if phone_numbers:
        phoneNumber = phone_numbers[0]
    if emails:
        email = emails[0]
    for element in name:
        fullname = fullname + " " + element  

        # First insert the user
    insert_user_query = """
    INSERT INTO "User" (
        "firstName",
        "email", 
        "phoneNumber", 
        "role", 
        "cvId",
        "cvUrl",
        "cvhash"
    ) VALUES (
        %s, %s, %s, %s, %s, %s, %s
    ) RETURNING "UserId";
    """
    result = db.execute_query(insert_user_query, (
            fullname,
            email,
            phoneNumber,
            "user",
            cvId,
            cvUrl,
            sha256_hash
    ))

    user_id = result[0]
    print(user_id)
    print(jobOfferId)

    # If jobOfferId is provided, create a job application
    if jobOfferId:
        insert_application_query = """
        INSERT INTO "JobApplication" (
            "userId",
            "jobOfferId",
            "createdAt",
            "updatedAt"
        ) VALUES (
            %s, %s, NOW(), NOW()
        );
        """

        JobOffer = db.fetch_one(""" SELECT * FROM "JobOffer" WHERE "JobOfferId" = %s """, (jobOfferId,))


        if JobOffer:
            db.execute_query(insert_application_query, (user_id,jobOfferId))





def file_hash_esxist(db: PostgreSQLWrapper, file_hash, jobOfferId) -> bool:


    select_file_hash_query = """
    SELECT  "cvhash"
    FROM public."User"
    LEFT JOIN public."JobApplication" ON  "User"."UserId" = "JobApplication"."userId"
    WHERE "User"."role" = 'user'
    AND "User"."cvhash" = %s
    AND "JobApplication"."jobOfferId" = %s
    """

    res = db.fetch_all(select_file_hash_query, (file_hash, jobOfferId))

    for row in res:
        if file_hash == row[0]:
            return True

    return False