import ollama
import os

client = ollama.Client(host="http://localhost:11434")
reponse = client.chat(
    model="llama3.1:8b",
    messages=[
        {"role": "system", "content":
            "Tu es un assistant qui répond en français, de façon claire et brève. "
            "Si tu ne sais pas, dis-le honnêtement."},
        {"role": "user", "content": "Qu'est-ce qu'une base de données ?"}
    ],
    options={"temperature": 0.2},
)

print(reponse["message"]["content"])