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
List only 2 recommended skincare products (by name) with a short explanation for each. Output nothing else."""

        def stream_response():
            for chunk in client.chat.completions.create(
                model="gpt-35-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=300,
                stream=True,
            ):
                if not chunk.choices:
                    continue
                choice = chunk.choices[0]
                content = getattr(getattr(choice, "delta", None), "content", None) or getattr(getattr(choice, "message", None), "content", None)
                if content:
                    content = content.replace('\\', '\\\\').replace('"', '\\"')
                    yield content

        return func.HttpResponse(
            ''.join(stream_response()),
            mimetype="application/json"
        )

    except Exception as e:
        return func.HttpResponse(json.dumps({"error": str(e)}), mimetype="application/json", status_code=500)