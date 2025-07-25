import os
import azure.functions as func
import json
from openai import AzureOpenAI  # ✅ Use AzureOpenAI

app = func.FunctionApp()

# ✅ Use AzureOpenAI client
client = AzureOpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    api_version=os.getenv("OPENAI_API_VERSION", "2024-02-15-preview"),
    azure_endpoint=os.getenv("OPENAI_API_BASE")  # ✅ Must include https:// prefix
)

@app.route(route="recommend", auth_level=func.AuthLevel.ANONYMOUS)
def recommend(req: func.HttpRequest) -> func.HttpResponse:
    try:
        data = req.get_json()
        skin_type = data.get("skin_type")
        age = data.get("age")
        concern = data.get("concern")

        prompt = f"""You are a Japanese skincare expert.
User is {age} years old with {skin_type} skin, concerned about {concern}.
Recommend 2 products suitable for them and explain why."""

        def stream_response():
            yield '{"recommendation":"'
            first = True
            for chunk in client.chat.completions.create(
                model="gpt-35-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=300,
                stream=True,
            ):
                content = chunk.choices[0].delta.content if hasattr(chunk.choices[0], "delta") else chunk.choices[0].message.content
                if content:
                    # Escape double quotes and backslashes for JSON
                    content = content.replace('\\', '\\\\').replace('"', '\\"')
                    yield content
            yield '"}'

        return func.HttpResponse(
            stream_response(),
            mimetype="application/json"
        )

    except Exception as e:
        return func.HttpResponse(json.dumps({"error": str(e)}), mimetype="application/json", status_code=500)