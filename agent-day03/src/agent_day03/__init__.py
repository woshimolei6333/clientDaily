from dotenv import load_dotenv
from openai import OpenAI
import os

load_dotenv()

client = OpenAI()

response = client.responses.create(
    model=os.environ["OPENAI_MODEL"],
    instructions="你是一名 AI Agent 开发导师，请用中文回答。",
    input="用100字解释什么是 AI Agent。",
)

print(response.output_text)