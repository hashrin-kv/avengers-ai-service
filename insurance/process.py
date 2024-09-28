import shutil
from insurance.records import get_records

from openai import OpenAI
from openai import RateLimitError
import env_loader
import os
from utils import convert_to_json, extract_text_from_all_pdfs, extract_text_from_pdf, html_string_to_pdf

api_key = env_loader.get_environment_variable("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

def build_prompt(text):
    sys_prompt = """
        You are an experienced doctor working for a reputable insurance company, who specializes in medical data summarization. You have a keen eye for detecting anomalies and predicting health risks based on medical records. Your task is to analyze the provided medical records and generate a detailed medical summary for a patient. The summary will be forwarded to an insurance underwriter for risk assessment and policy approval.
        The medical records can be of any type such as CBC, LFT, RFT, ECG, X-Ray, Biopsy, etc. Based on these records, please provide a detailed medical summary.
        Include the following key details:
        Personal Information:
        Full Name (if available)
        Age
        Gender
        Existing Health Conditions:
        List any current illnesses or medical conditions.
        Current Medications:
        Mention any medications the person is currently taking, including dosage and frequency if provided.
        Predicted Risk of Illness:
        Based on the provided medical history, assess the probability of the person developing any serious illness in the next 2 years. Mention the illness and the associated risk level.
        Anomalies or Concerns:
        Identify any observed anomalies or concerns in the medical records.
        Abnormal Values:
        Highlight any test results or values that are outside the normal range (e.g., blood pressure, cholesterol, etc.), and mention the normal reference ranges for comparison.
        File name:
        Provide the name of the file from which the record was extracted.
        Each observation should have the date of the record mentioned along with it. This is very important because the observations from multiple reports will be compared using date later.
        Ensure that the summary is clear and concise while capturing all critical medical details.
        The output should be a valid, well-formed JSON. Do not include any text before or after the JSON output. The JSON output should be parsable by any programming language.
        
    """

    messages = [
        {
            "role": "system",
            "content": sys_prompt
        },
        {
            "role": "user",
            "content": f"Provide a medical summary of the following text: {text}"
        }
    ]

    return messages

def build_prompt_to_combine_medical_record_summaries(medical_record_summaries):
    sys_prompt = """
        You are an experienced doctor working for a reputable insurance company, who specializes in medical data summarization. You have a keen eye for detecting anomalies and predicting health risks based on medical records. Your task is to analyze the provided medical record summaries and combine them for a patient.
        Your input will be an array of JSON which can either have records of a single patient, or have records of multiple patients. You should identify the records of the same patient and combine them into a single record. Use the name to identify the patient.
        While combining, if the same test is present in multiple reports for a patient, retain only the latest one.
        While combining, if there is any abnormality in the values, retain only the abnormal value, no matter how old it is. Also retain its date.
        While combining, along with each observation, mention the date of the record and also the file name from which the record was extracted.
        Your input will be an array of JSON. The output should be of HTML format. The title should be "Medical Record Summary". Each person's name should be given as "Applicant Name". 
        The result will be forwarded to an insurance underwriter for risk assessment and policy approval.
    """
    messages = [
            {
                "role": "system",
                "content": sys_prompt
            },
            {
                "role": "user",
                "content": f"Following are the medical record summaries: {medical_record_summaries}"
            }
        ]

    return messages

def summarize(medical_record_directory):
    # records = get_records()
    # combined_records = "\n".join(records)
    
    current_directory = os.path.dirname(__file__)
    # medical_record_directory = os.path.join(current_directory, "medical_records")
    
    # shutil.rmtree(medical_record_directory) # clear the directory
    # os.makedirs(medical_record_directory) # recreate the directory

    if not os.path.exists(medical_record_directory):
        print(f"The directory '{medical_record_directory}' does not exist.")
        raise FileNotFoundError
    
    # Check if the directory is empty
    if not os.listdir(medical_record_directory):
        print(f"The directory '{medical_record_directory}' is empty.")
        raise FileNotFoundError

    medical_summaries = []
    for filename in os.listdir(medical_record_directory):
        print(filename)
        if filename.endswith(".pdf"):  # Only process PDF files
            pdf_path = os.path.join(medical_record_directory, filename)
            medical_record_data = extract_text_from_pdf(pdf_path)
            medical_record_data = "file name: " + filename + "\n" + medical_record_data
            prompt = build_prompt(medical_record_data)
            llm_response = call_llm(prompt)
            llm_response = llm_response.strip()
            if(llm_response.startswith("```json")):
                llm_response = llm_response[7:].strip()
            if(llm_response.endswith("```")):
                llm_response = llm_response[:-3].strip()
            convert_to_json(llm_response, medical_summaries)
            # print("LLM response:\n", llm_response)

    # medical_record_data = extract_text_from_all_pdfs(medical_record_directory)
    combined_summary_prompt = build_prompt_to_combine_medical_record_summaries(medical_summaries)
    final_llm_response = call_llm(combined_summary_prompt)
    final_llm_response = final_llm_response.strip()
    if(final_llm_response.startswith("```html")):
        final_llm_response = final_llm_response[7:].strip()
    if(final_llm_response.endswith("```")):
        final_llm_response = final_llm_response[:-3].strip()
    
    output_pdf_directory = os.path.join(current_directory, "medical_records_output")
    if os.path.exists(output_pdf_directory):
        shutil.rmtree(output_pdf_directory)
    os.makedirs(output_pdf_directory) # recreate the directory

    output_pdf_path = output_pdf_directory + "/medical_record_summary.pdf"
    html_string_to_pdf(final_llm_response, output_pdf_path)

    return "PFA medical record summary", output_pdf_directory

def call_llm(messages, model="gpt-4o-mini"):
    try:
        is_demo = (env_loader.get_environment_variable("AGENT_LIVE_MODE_ENABLED") == "True".lower())

        if is_demo:
            return {
                "text": "This is a demo response.",
            }

        response = client.chat.completions.create(
            model=model,
            messages=messages
        )
        chat_res = response.choices[0].message.content
        print("LLM response:", chat_res)
        return chat_res

    except RateLimitError as e:
        msg = "Rate limit error. Please try again after some time. " + str(e)
        print(msg)
        raise