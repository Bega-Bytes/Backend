from openai import OpenAI
client = OpenAI()  # uses OPENAI_API_KEY
for m in client.models.list().data:
    print(m.id)
