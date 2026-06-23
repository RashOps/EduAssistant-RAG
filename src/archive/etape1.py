import ollama
import os

# os.environ["OLLAMA_HOST"] = "http://localhost:11434"

client = ollama.Client(host="http://localhost:11434")
reponse = client.chat(
    model="llama3.1:8b",
    messages=[
        {"role": "user", "content": "Donne 3 idées de noms d'app."}
    ],
    options={"temperature": 0.9},
)

print(reponse["message"]["content"])