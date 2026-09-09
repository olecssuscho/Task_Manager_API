from anthropic import Anthropic
from config import settings
from schemas.models import TaskMODELS

client = Anthropic(api_key=settings.API_KEY)

def generate_task_data_from_text(text:str):
    response = client.messages.parse(
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
            Return the deadline as an ISO 8601 datetime."""
        }
        ],
        output_format=TaskMODELS
    )
    return response.parsed_output