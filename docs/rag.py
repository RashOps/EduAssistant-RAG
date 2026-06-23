import chromadb
import ollama

client_db = chromadb.Client()
client_llm = ollama.Client(host="http://localhost:11434")
collection = client_db.create_collection("mes_docs")

def repondre(query: str) -> str :
    morceaux = [
        "Les cours commencent à 9h et se terminent à 17h.",
        "Le règlement interdit de manger dans les salles informatiques.",
        "Les absences doivent être justifiées sous 48 heures.",
        ]

    for i, texte in enumerate(morceaux):
        emb = client_llm.embeddings(model="llama3.1:8b", prompt=texte)["embedding"]
        collection.add(ids=[str(i)], documents=[texte], embeddings=[emb])

    q_emb = client_llm.embeddings(model="llama3.1:8b", prompt=query)["embedding"]
    resultats = collection.query(query_embeddings=[q_emb], n_results=2)
    contexte = "\n".join(resultats["documents"][0])

    messages = [
        {"role": "system", "content":
            "Réponds uniquement à partir du CONTEXTE ci-dessous. "
            "Si la réponse n'y est pas, dis : Je ne sais pas."},
        {"role": "user", "content": f"CONTEXTE:\n{contexte}\n\nQUESTION: {query}"},
    ]
    
    return client_llm.chat(model="gemma4:e2b", messages=messages)["message"]["content"]

if __name__ == "__main__":
    question = "C'est quand la prochaine coupe du monde ?"
    print(repondre(question))