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

sample_response = """
{
    "text": "We have built several e-commerce projects",
}
"""

def build_prompt(text: str):
    sys_prompt = """
        You are an experienced research assistant at a software company that builds products for startups. Your role is to generate the content for a response mail.
        You will be provided with details regarding case studies your software company has done for other clients, which are similar to the potential client's need.
        You will be provided with the client's requirements and the case studies.
        Your task is to generate a response mail that includes the case studies and how they are relevant to the client's requirements.
        The response mail should be professional and should include the case studies in a way that is easy for the client to understand.
        The response mail should also include a call to action for the client to schedule a meeting with your company.
        The response mail should be concise and should not exceed 500 words.
    """

    messages = [
        {
            "role": "system",
            "content": sys_prompt
        }
    ]

    context = get_context_from_knowledge_base(text, os.path.join(os.getcwd(), "knowledge_base/case_studies_db"))
    if context:
        messages.insert(
            {
            "role": "system",
            "content": f"The following context may be relevant:\n{context}"
            }
        )
        messages.insert(
            {
                "role": "user",
                "content": f"Generate an email response for the following client enquiry mail: {text}"
            }
        )

    else:
        return "No relevant context found in the knowledge base. Aborting workflow"


def get_context_from_knowledge_base(text: str, kb_path: str):
    embedding_function = OpenAIEmbeddings()
    db = Chroma(persist_directory=kb_path, embedding_function=embedding_function)
    results = db.similarity_search_with_relevance_scores(text, k=3)
    if len(results) != 0 and results[0][1] > 0.5:
        context = "\n\n---\n\n".join([doc.page_content for doc, _score in results]) 
        return context
    return None  


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
    
