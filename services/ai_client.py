from datetime import datetime,timezone
from anthropic import Anthropic
from config import settings
from schemas.models import TaskMODELS
from voyageai.client import Client

voyage_client = Client(api_key=settings.VOYAGE_API_KEY)

cluaud_client = Anthropic(api_key=settings.CLAUDE_API_KEY)

def generate_task_data_from_text(text:str):
    response = cluaud_client.messages.parse(
        model="claude-opus-5",
        max_tokens=200,
        messages=[
        {
            "role": "user",
            "content": f"""Convert the following text into a task: {text}
            Extract:
            - title
            - description
            - priority
            - deadline
            If priority is not explicitly specified, infer it.
            Return the deadline as an ISO 8601 datetime.
            Important rules:
            - Interpret relative dates such as "today", "tomorrow", "next week",
              and "next month" relative to the Current date{datetime.now(timezone.utc)}.
            - Do not invent a different current year.
            - "next month" means the first day of the next calendar month."""
        }
        ],
        output_format=TaskMODELS
    )
    return response.parsed_output

def generate_embedding(text:str):
    responce = voyage_client.embed(texts=text,model="voyage-3.5",input_type="document")
    return responce.embeddings[0]