
from openai import OpenAI
from openai import RateLimitError
import env_loader
from utils import convert_to_json

api_key = env_loader.get_environment_variable("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

sample_response = """
{
    "text": "Hello, I am writing to inquire about your software services. Can you provide me with more information?",
    "category": "Enquiry"
}
"""

def build_prompt(text):

    sys_prompt = """
        You are an experienced customer support assistant at a technology company which specializes at building software for startups. Your job is to classify emails you receive into the following categories:
        1. Enquiry
        2. Complaint
        3. Others
        If the mail is neither an enquiry nor a complaint, you should classify it as 'Others'.

        Return the result in a JSON format with the following structure:

        {{
            "text": "",
            "category": ""
        }}

        "text" corresponds to your input email text, and "category" is the category you assign to the text. Return only the JSON. No need for any other output or markdown.
    """

    messages = [
        {
            "role": "system",
            "content": sys_prompt
        },
        {
            "role": "user",
            "content": f"Categorize the following text: {text}"
        }
    ]

    return messages

def classify(text):
    result = []
    prompt = build_prompt(text)

    llm_response = call_llm(prompt)

    convert_to_json(llm_response, result)

    print("Final result:\n", result)
    return result

def call_llm(messages, model="gpt-4o-mini"):
    try:
        is_demo = (env_loader.get_environment_variable("AGENT_LIVE_MODE_ENABLED") == "True".lower())

        if is_demo:
            return sample_response

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