import random
import string
import os
import env_loader
from utils import download_file_from_google_drive
import shutil
from langchain_community.document_loaders import DirectoryLoader # type: ignore
from langchain.schema import Document # type: ignore
from langchain.text_splitter import RecursiveCharacterTextSplitter # type: ignore
from langchain_openai import OpenAIEmbeddings # type: ignore
from langchain_community.vectorstores import Chroma
openai_api_key = env_loader.get_environment_variable("OPENAI_API_KEY")


def download_context_files(directory_name: str, urls: list[str]):
    directory_path = os.path.join(os.getcwd(), "knowledge_base/" + directory_name)
    for url in urls:
        print(f"Downloading content from {url}")
        if not os.path.exists(directory_path):
            os.makedirs(directory_path)
        random_file_name = ''.join(random.choices(string.ascii_letters + string.digits, k=5))
        file_path = directory_path + "/" + random_file_name + ".pdf"
        download_file_from_google_drive(url, file_path)
    return directory_path

def build_knowledge_base(name: str, urls: list[str]):
    file_directory_name = name + "_files"
    db_directory_name = name + "_db"
    download_path = download_context_files(file_directory_name, urls)
    create_vector_store(db_directory_name, download_path)

def create_vector_store(db_directory_name: str, file_directory: str):
    documents = load_documents(file_directory)
    chunks = split_text(documents)
    db_path = os.path.join(os.getcwd(), "knowledge_base/" + db_directory_name)
    save_to_chroma(db_path, chunks)

def load_documents(path: str):
    loader = DirectoryLoader(path)
    documents = loader.load()
    return documents

def split_text(documents: list[Document]):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=400,
        length_function=len,
        add_start_index=True,
    )
    chunks = text_splitter.split_documents(documents)

    print(f"Split {len(documents)} documents into {len(chunks)} chunks.")

    # document = chunks[10]
    # print(document.page_content)
    # print(document.metadata)

    return chunks

def save_to_chroma(path: str, chunks: list[Document]):
    # Clear out the database first.
    if os.path.exists(path):
        shutil.rmtree(path)

    # Create a new DB from the documents.
    db = Chroma.from_documents(
        chunks, OpenAIEmbeddings(openai_api_key = openai_api_key), persist_directory=path
    )
    print(f"Saved {len(chunks)} chunks to {path}.")