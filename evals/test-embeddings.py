from google import genai

client = genai.Client()

for m in client.models.list():
    if "embed" in m.name.lower():
        print(m.name)