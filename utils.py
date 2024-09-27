import os
import fitz
import requests
import json
import pdfkit

def extract_text_from_all_pdfs(directory):
    """Extract and append text from all PDF files in a directory."""
    combined_text = ""
    for filename in os.listdir(directory):
        print(filename)
        if filename.endswith(".pdf"):  # Only process PDF files
            pdf_path = os.path.join(directory, filename)
            print(f"Extracting text from: {pdf_path}")
            pdf_text = extract_text_from_pdf(pdf_path)
            combined_text += pdf_text + "\n"  # Append text with a newline
    return combined_text

def extract_text_from_pdf(pdf_path):
    text = ""
    if pdf_path.endswith(".pdf"):
        print(f"Extracting text from: {pdf_path}")
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


def convert_to_json(chat_res, combined_data = []):
    try:
        result = json.loads(chat_res)
        combined_data.append(result)
        return result
        
    except json.JSONDecodeError as e:
        print("Invalid JSON response from the model")
        print(e)
        raise

def html_string_to_pdf(html_string, output_pdf_path):
    try:
        pdfkit.from_string(html_string, output_pdf_path)
        print(f"Successfully converted HTML string to {output_pdf_path}")
    except Exception as e:
        print(f"Error occurred: {e}")