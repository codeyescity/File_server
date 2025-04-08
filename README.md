# File_server



### python -m venv env 


.\env\Scripts\activate


pip install fastapi uvicorn python-multipart psycopg2 nltk PyPDF2 python-docx sentence-transformers spacy

python -m spacy download en_core_web_sm


## create file db.json with the format:

`
{
    "dbname": "dbname",  
    "user": "user",         
    "password": "password",     
    "host": "localhost",             
    "port": "5432"                   
}
`


## create folder "static" and "resumes"   ./static/resumes



