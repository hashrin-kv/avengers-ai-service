from insurance.records import get_records

from openai import OpenAI
from openai import RateLimitError
import env_loader
import os
from utils import convert_to_json, extract_text_from_all_pdfs, extract_text_from_pdf

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
        Doctor's Notes:
        Summarize any important comments or recommendations from doctors that are crucial for understanding the person's health.
        Ensure that the summary is clear and concise while capturing all critical medical details.
        The output should be a JSON string containing the medical summary. If a property consists of multiple words, separate them by spaces instead of combining them into a single word.
        Each non-empty sub-JSON property in the JSON should also have the date of the test mentioned.
        The output should strictly be a JSON. There should not be anything written before or after the JSON string. The JSON should be parsable by any code. Otherwise, whole programs will break due to syntax errors.
        
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
        Your input will be an array of JSON.
        While combining, if there are multiple properties having the same name, retain only the latest one.
        While combining, if there is any abnormality in the values, retain only the abnormal value, no matter how old it is. Also retain its date.
        Your input will be an array of JSON. The output should also strictly be an array of JSON. There should not be anything written before or after the JSON string. This JSON string should be parsable by the insurance underwriter for further processing.
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

def summarize():
    # records = get_records()
    # combined_records = "\n".join(records)
    current_directory = os.path.dirname(__file__)
    medical_record_directory = os.path.join(current_directory, "medical_records/hashrin")
    medical_summaries = []
    for filename in os.listdir(medical_record_directory):
        print(filename)
        if filename.endswith(".pdf"):  # Only process PDF files
            pdf_path = os.path.join(medical_record_directory, filename)
            medical_record_data = extract_text_from_pdf(pdf_path)
            prompt = build_prompt(medical_record_data)
            llm_response = call_llm(prompt)
            convert_to_json(llm_response, medical_summaries)
            # print("LLM response:\n", llm_response)

    # medical_record_data = extract_text_from_all_pdfs(medical_record_directory)
    combined_summary_prompt = build_prompt_to_combine_medical_record_summaries(medical_summaries)
    llm_response = call_llm(combined_summary_prompt)
    result = []
    convert_to_json(llm_response, result)

    print("Final result:\n", result)
    return result

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