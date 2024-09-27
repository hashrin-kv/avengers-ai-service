import os
import fitz
import requests
import json

def extract_text_from_pdf(pdf_path):
    text = ""
    with fitz.open(pdf_path) as doc:
        for page in doc:
            text += page.get_text()
    return text


def download_file(url, file_name):
    response = requests.get(url, stream=True)
    response.raise_for_status()  # Raises an HTTPError for bad responses
    save_path = os.path.join(os.path.join(os.getcwd(), file_name))
    with open(save_path, 'wb') as file:
        for chunk in response.iter_content(chunk_size=8192):
            file.write(chunk)

def download_file_from_google_drive(url, save_path):
    # Extract the file ID from the Google Drive URL
    file_id = url.split('/')[-2]
    
    # Construct the direct download URL
    download_url = f"https://drive.google.com/uc?export=download&id={file_id}"
    
    session = requests.Session()

    # Request the file
    response = session.get(download_url, stream=True)
    
    # Check for redirection and handle cookies if needed
    for key, value in response.cookies.items():
        if key.startswith('download_warning'):
            download_url = f"https://drive.google.com/uc?export=download&id={file_id}&confirm={value}"
            response = session.get(download_url, stream=True)
            break

    # Save the file
    with open(save_path, 'wb') as file:
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:  # Filter out keep-alive new chunks
                file.write(chunk)
    
    print(f"File downloaded successfully: {save_path}")


def convert_to_json(chat_res):
    try:
        result = json.loads(chat_res)
        return result
        
    except json.JSONDecodeError as e:
        print("Invalid JSON response from the model")
        print(e)
        raise