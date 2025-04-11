
# File_server



### 1-python -m venv env 


### 2-.\env\Scripts\activate


### 3-pip install fastapi uvicorn python-multipart psycopg2 nltk PyPDF2 python-docx sentence-transformers spacy

### 4-python -m spacy download en_core_web_trf


### 5-create file db.json with the format:


```
{
    "dbname": "dbname",  
    "user": "user",         
    "password": "password",     
    "host": "localhost",             
    "port": "5432"                   
}
```


### 6-create folder "static" and "resumes"  to get  static/resumes
