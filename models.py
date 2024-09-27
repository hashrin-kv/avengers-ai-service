from pydantic import BaseModel

class ResumeParserBody(BaseModel):
    url: str

class EmailClassifierBody(BaseModel):
    text: str

class ContextBuilderBody(BaseModel):
    name: str
    urls: list[str]