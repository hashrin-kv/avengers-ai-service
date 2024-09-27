from insurance.records import get_records

from openai import OpenAI
from openai import RateLimitError
import env_loader
from utils import convert_to_json

api_key = env_loader.get_environment_variable("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

def build_prompt(text):
    sys_prompt = """
        You are an experienced doctor working for a reputable insurance company, who specializes in medical data summarization. You have a keen eye for detecting anomalies and predicting health risks based on medical records. Your task is to analyze the provided medical records and generate a detailed medical summary for a patient. The summary will be forwarded to an insurance underwriter for risk assessment and policy approval.
        The medical records can be of any type such as CBC, LFT, RFT, ECG, X-Ray, Biopsy, etc. Based on these records, please provide a detailed medical summary. Include the following key details:
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

def summarize():
    result = []
    records = get_records()
    combined_records = "\n".join(records)
    prompt = build_prompt(combined_records)

    llm_response = call_llm(prompt)

    #convert_to_json(llm_response, result)

    #print("Final result:\n", result)
    return llm_response

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