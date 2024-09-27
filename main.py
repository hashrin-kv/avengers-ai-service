import random
from fastapi import FastAPI, HTTPException
from knowledge_base import builder
from email_classifier import classifier
from models import ContextBuilderBody, EmailClassifierBody, ResumeParserBody
from resume_parser import parser
import os
from utils import download_file_from_google_drive

app = FastAPI()

@app.post("/parse-resume")
def parse_resume(body: ResumeParserBody):

    file_name = "resume_"
    random_number = random.randint(1, 1000)
    file_name = file_name + str(random_number) + ".pdf"
    path = os.path.join(os.getcwd(), file_name)
    download_file_from_google_drive(body.url, path)
    result = parser.extract(path)
    # print(result)
    return result

@app.post("/classify-email")
def classify_text(body: EmailClassifierBody):
    result = classifier.classify(body.text)
    return result

@app.post("/knowledge-base")
def create_knowledge_base(body: ContextBuilderBody):
    result = builder.build_knowledge_base(body.name, body.urls)
    return result