from datetime import datetime

import env_loader
import json
from openai import OpenAI
from openai import RateLimitError
from utils import convert_to_json, extract_text_from_pdf


api_key = env_loader.get_environment_variable("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

sample_llm_message_content = """
{
    "name": "James Anderson",
    "current_company": "Qburst",
    "current_designation": "Software Engineer",
    "applied_role": "Senior Software Engineer",
    "total_experience_yr": "2",
    "linked_in": "https://www.linkedin.com/in/hashrin/",
    "github": "github.com/ja",
    "location": "Kochi, Kerala",
    "behance": "",
    "skills": "Rust, Kotlin, Swift, Go, Scala, TypeScript, R, Perl, Haskell, Groovy, Julia, Dart, React.js, Angular, Vue.js, Django, Flask, Ruby on Rails, Spring Boot, Express.js, TensorFlow, PyTorch, jQuery, Bootstrap, Laravel, Flask, ASP.NET, Node.js, Electron, Android SDK, iOS SDK, Symfony",
    "is_gap_between_college_and_first_job": "No",
    "is_gap_between_jobs": "Yes",
    "gap_between_jobs": "12",
    "is_current_company_match": "Yes",
    "num_job_changes": "1",
    "is_graduated_from_top_colleges": "No",
    "summary": "James Anderson is a Software Engineer with 2 years of experience in developing microservices architecture, optimizing databases, and leading cross-functional teams. He is proficient in a wide range of technologies including Rust, Kotlin, Django, React.js, TensorFlow, and more. James has strong technical skills and has made significant contributions in improving application performance and user engagement. He is from Kochi, Kerala and has one job change in his career. He has a gap of 12 months between his previous and current job."
}
"""

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "find_experience_duration",
            "description": "Find the experience duration for each company and the total year of experience",
            "parameters": {
                "type": "object",
                "properties": {
                    "experiences": {
                        "type": "array",
                        "description": "List of experiences with company name, start date and end date. For example: [('Company 1', 'May 2018', 'May 2020'), ('Company 2', 'May 2021', 'Present')]",
                        "items": {
                            "type": "array",
                            "items": {
                                "type": "string"
                            }
                        }
                    }
                },
                "required": ["experiences"]
            }
        }
    }
]


def find_experience_duration(experiences):
    total_years = 0
    experience_duration = []
    for experience in experiences:
        company, start_date, end_date = experience
        start_year = int(start_date.split()[-1])
        end_year = datetime.now().year if end_date.lower() == "present" else int(end_date.split()[-1])
        years = end_year - start_year
        total_years += years
        experience_duration.append(f"{company} - {years} years")
    return json.dumps({
        "experience_duration": experience_duration,
        "total_years_of_experience": total_years
    })


def extract(resume_file_path):
    print(api_key)
    extracted_content = []

    resume_text = extract_text_from_pdf(resume_file_path)

    messages = build_resume_extraction_prompt(resume_text)

    chat_res = call_llm(messages)

    convert_to_json(chat_res, extracted_content)
        

    print("Final result:\n", extracted_content)
    return extracted_content

def build_resume_extraction_prompt(resume_text):
    year = datetime.now().year
    preferred_companies = ["KeyValue Software Systems", "Apple", "Oracle"]
    top_colleges = ["Indian Institute of Management (IIM)",
                    "National Institute of Design (NID)",
                    "National Institute of Fashion technology (NIFT)",
                    "Indian Institute of Technology (IIT)"]

    job_gap_example = """
            Example: If user has two experiences in the resume and the duration of each experience is as follows:
            Experience 1: May 2018 - May 2020
            Experience 2: May 2021 - May 2023
            The answer should be "Yes", as there is a gap between May 2020 and May 2021.
        """

    experience_example = """
            Company A: May 2018 - May 2020
            Company B: May 2021 - Present
            
            Then return 'Company A - 2 years, Company B - 3 years'
        """

    total_yrs_exp = """
            If the current year is 2024 and candidate has two experiences in the resume with the duration of each experience as follows:
            Experience 1: May 2018 - May 2020 (2 years)
            Experience 2: May 2021 - Present  (3 years)
            The total years of experience should be 2 + 3 = 5 years.
    """

    sys_prompt = """
            You are a helpful assistant who can filter out resumes for the roles in a technical company.
            Current year is {year}.
            Extract the following information from the resume file. If any of the following information is not available in the email content or resume, please add an empty string. 
            Please use the available tools to extract the information.
            - Name
            - Candidate's email
            - Current company
            - Current designation
            - Total years of experience. Example: {total_yrs_exp}
            - List of companies the candidates has worked with and the duration of each experience in years. Do not include the education period. {experience_example}
            - LinkedIn profile
            - GitHub profile
            - Location
            - Behance profile
            - Skills
            - Is there any gap between college graduation and first job? (Answer should be Yes or No.)
            - Is there any gap between each job? (Answer should be Yes or No. {job_gap_example})
            - If there is a gap between jobs, how many months or years of gap?
            - Does the current company match with any of the company in this list {preferred_companies}
            - Number of job changes (This should be a string number)
            - If the candidate is applying for Product manager or Designer role, check if the candidate graduated from
            {top_colleges}. (Answer should be Yes or No)
            - Summary of the candidate in 5-6 lines

            Return the result in the following json format. Return  only this json. No need for markdown.

            {{
                "name": "Name of the candidate",
                "email": "Email of the candidate",
                "current_company": "Current company of the candidate",
                "current_designation": "Current designation of the candidate",
                "applied_role": "Role applied",
                "total_experience_yr": "Total years of experience",
                "previous_employers": "List of companies the candidate has worked",
                "linked_in": "Link to the LinkedIn profile",
                "github": "Link to GitHub profile",
                "location": "Location of the candidate",
                "behance": "Link to the Behance profile of candidate",
                "skills": "Technical skills of the candidate, should be comma separated string",
                "from_kerala": "Yes or No",
                "gap_between_college_and_first_job": "Yes or No"
                "gap_between_jobs": "Yes or No",
                "gap_between_jobs": "Number of months or years of gap",
                "is_current_company_match": "Yes or No",
                "num_job_changes": "Number of job changes",
                "graduated_from_top_colleges": "Yes or No",
                "summary": "Summary of the candidate."
            }} 
        """

    messages = [
        {
            "role": "system",
            "content": sys_prompt.format(year=year,
                                         total_yrs_exp=total_yrs_exp,
                                         job_gap_example=job_gap_example,
                                         preferred_companies=preferred_companies,
                                         top_colleges=top_colleges,
                                         experience_example=experience_example)
        },
        {
            "role": "user",
            "content": f"Use this resume to extract relevant information: {resume_text}"
        },
    ]

    return messages


def invoke_llm(messages, model="gpt-4o-mini"):
    is_demo = (env_loader.get_environment_variable("AGENT_LIVE_MODE_ENABLED") == "True".lower())

    if is_demo:
        return sample_llm_message_content

    response = client.chat.completions.create(
        model=model,
        messages=messages
    )
    chat_res = response.choices[0].message.content
    return chat_res


def invoke_llm_with_tool(messages, model="gpt-4o-mini"):
    is_demo = (env_loader.get_environment_variable("AGENT_LIVE_MODE_ENABLED") == "True".lower())

    if is_demo:
        return sample_llm_message_content

    response = client.chat.completions.create(
        model=model,
        messages=messages,
        tools=TOOLS,
    )
    chat_res = response.choices[0].message

    if chat_res.tool_calls:

        available_functions = {
            "find_experience_duration": find_experience_duration,
        }

        messages.append(chat_res)

        for tool_call in chat_res.tool_calls:
            function_name = tool_call.function.name
            function_to_call = available_functions[function_name]
            function_args = json.loads(tool_call.function.arguments)
            function_response = function_to_call(
                experiences=function_args.get("experiences")
            )

            messages.append(
                {
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": function_name,
                    "content": function_response,
                }
            )

        second_response = client.chat.completions.create(
            model=model,
            messages=messages,
        )
        chat_res = second_response.choices[0].message

    return chat_res.content


def call_llm(messages, model="gpt-4o-mini"):
    try:
        chat_res = invoke_llm_with_tool(messages, model=model)
        print("LLM response:", chat_res)
        return chat_res

    except RateLimitError as e:
        print("Rate limit error. Please try again after some time.", e)
        return ""
