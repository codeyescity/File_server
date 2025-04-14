from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.staticfiles import StaticFiles
from typing import List
from pathlib import Path
import uuid
from datetime import datetime

import hashlib

import os
from sentence_transformers import SentenceTransformer, util

from fastapi.middleware.cors import CORSMiddleware
import spacy

from datetime import datetime

from helper import read_dict_from_json
from helper import get_keywords, get_joboffer,insert_resumes_db, file_hash_esxist ,read_formated_file, extract_contact_info, get_resumes
from helper import process_resume, calculate_keyword_score
from name import extract_names

from dbmanager import PostgreSQLWrapper

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SUPORTED_FORMATS = ("pdf", "docx")
SERVER_URL = "http://localhost:8000"
# Configuration
SEMANTIC_WEIGHT = 0.7 
KEYWORD_WEIGHT = 0.3

model = SentenceTransformer('all-MiniLM-L6-v2')
nlp_model = spacy.load("en_core_web_trf")


db_config = read_dict_from_json("db.json")
db = PostgreSQLWrapper(dbname=db_config["dbname"], user= db_config["user"] , password=db_config["password"], host=db_config["host"] , port=db_config["port"])

# Mount static files directory
app.mount("/static", StaticFiles(directory="static"), name="static")




@app.post("/upload-resume")
async def upload_resume(job_offer_id: int, file: UploadFile = File(...)):
    # Validate PDF file
    if not file.filename.lower().endswith(SUPORTED_FORMATS):
        raise HTTPException(400, "File must be a PDF or DOCX")
    
    # Generate Path Name
    year = datetime.now().year
    unique_id = uuid.uuid4().hex
    dir_path = Path(f"static/resumes/{year}-{unique_id}")
    
    # Create directory and save file
    dir_path.mkdir(parents=True, exist_ok=True)
    file_path = dir_path / file.filename

    sha256_hash = ""
    
    try:
        contents = await file.read()
        sha256_hash = hashlib.sha256(contents).hexdigest()

        if file_hash_esxist(db, sha256_hash, job_offer_id):
            raise HTTPException(500, f"Error saving file: {str(e)}")

        with open(file_path, "wb") as f:
            f.write(contents)
    except Exception as e:
        raise HTTPException(500, f"Error saving file: {str(e)}")
    
    try:

        resume_id = f"{year}-{unique_id}"
        resume_url = f"{SERVER_URL}/static/resumes/{year}-{unique_id}/{file.filename}"

        resume_txt = read_formated_file(file_path)
        contact_info = extract_contact_info(resume_txt)

        phone_numbers = contact_info["phone_numbers"]
        emails = contact_info["emails"]
        name = extract_names(nlp_model, resume_txt)

        # print(phone_numbers)
        # print(emails)
        # print(name)

        insert_resumes_db(db, resume_id, resume_url ,sha256_hash , phone_numbers, emails, name, job_offer_id)

        # rows = db.fetch_all("""SELECT * FROM "User" """)
        # for row in rows:
        #     print(row)

        # res = db.fetch_all("""SELECT * FROM "JobApplication" """)
        # print(res)
        # for row in res:
        #     print(row)

    except Exception as e:
        print(f"Error: {e}")
    
    return {"url": f"{SERVER_URL}/static/resumes/{year}-{unique_id}/{file.filename}"}

@app.post("/upload-resumes-hr/{job_offer_id}")
async def upload_resumes_hr(job_offer_id: int, files: List[UploadFile] = File(...)):
    # Validate all files first
    invalid_files = []
    
    for file in files:
        if not file.filename.lower().endswith(SUPORTED_FORMATS):
            invalid_files.append(file.filename)

    if invalid_files:
        raise HTTPException(400, 
            f"Invalid files: {', '.join(invalid_files)}. All files must be PDFs")

    # Create directory and save file
    urls = []

    # Generate Path Name
    for file in files:
        year = datetime.now().year
        unique_id = uuid.uuid4().hex
        dir_path = Path(f"static/resumes/{year}-{unique_id}")
    

        sha256_hash = ""

        try:


            contents = await file.read()
            sha256_hash = hashlib.sha256(contents).hexdigest()


            if file_hash_esxist(db, sha256_hash, job_offer_id):
                print("file ", file , "is duplicated")
                continue

            dir_path.mkdir(parents=True, exist_ok=True)
            file_path = dir_path / file.filename


            with open(file_path, "wb") as f:
                f.write(contents)
            urls.append(f"{SERVER_URL}/static/resumes/{year}-{unique_id}/{file.filename}")

            try:
                resume_id = f"{year}-{unique_id}"
                resume_url = f"{SERVER_URL}/static/resumes/{year}-{unique_id}/{file.filename}"
                #insert_resumes_db(file_path, resume_id, resume_url, job_offer_id)

                resume_txt = read_formated_file(file_path)
                contact_info = extract_contact_info(resume_txt)

                phone_numbers = contact_info["phone_numbers"]
                emails = contact_info["emails"]
                name = extract_names(nlp_model, resume_txt)

                insert_resumes_db(db, resume_id, resume_url , sha256_hash, phone_numbers, emails, name, job_offer_id)
                print("saved :", resume_url)

                
            except Exception as e:
                print(f"Error: {e}")

        except Exception as e:
            raise HTTPException(500, f"Error saving {file.filename}: {str(e)}")

    return {"urls": urls}


@app.get("/recommendation/{job_offer_id}")
async def get_recommendation(job_offer_id: int):

    RESUMES_PATH = "static/resumes"
    # Read inputs
    #job_description = read_text_file('job_offer.txt')
    job_description = get_joboffer(db, job_offer_id)
    keywords = get_keywords(db, job_offer_id)
    
    # Get job embedding
    job_embedding = model.encode(job_description, convert_to_tensor=True)

    resume_directories = get_resumes(db, job_offer_id)

    resume_scores = {}

    for dir in resume_directories:
        print(RESUMES_PATH + '/' + str(dir[0]))

    # Process resumes
    for dir in resume_directories:
        for filename in os.listdir( RESUMES_PATH + '/' + str(dir[0])):

            filename = RESUMES_PATH + '/' + str(dir[0]) + "/" + filename
            if filename.endswith(('.pdf', '.docx')):
                file_path = filename
                chunks, full_text = process_resume(model ,file_path)
                # if not chunks:
                #     continue
                
                # Semantic similarity score
                # chunk_embeddings = model.encode(chunks, convert_to_tensor=True)
                chunk_embeddings = chunks
                similarities = util.cos_sim(job_embedding, chunk_embeddings)[0]
                semantic_score = max(similarities).item()
                
                # Keyword matching score
                keyword_score = calculate_keyword_score(full_text, keywords)
                
                # Combined score
                combined_score = (SEMANTIC_WEIGHT * semantic_score) + (KEYWORD_WEIGHT * keyword_score)
                
                resume_scores[str(dir[0])] = {
                    'combined': combined_score,
                    'semantic': semantic_score,
                    'keywords': keyword_score
                }

    # Rank resumes
    ranked_resumes = sorted(resume_scores.items(), 
                          key=lambda x: x[1]['combined'], 
                          reverse=True)

    # Print results
    print("Ranked Resumes:")
    for rank, (filename, scores) in enumerate(ranked_resumes, 1):
        print(f"{rank}. {filename}")
        print(f"   Combined Score: {scores['combined']:.4f}")
        print(f"   Semantic Score: {scores['semantic']:.4f}")
        print(f"   Keyword Score:  {scores['keywords']:.4f}\n")


    return ranked_resumes


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)