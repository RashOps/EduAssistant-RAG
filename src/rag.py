import os
import glob
from typing import List, Dict, Any
import chromadb
from chromadb.api import Collection
import ollama
from pypdf import PdfReader

# Configuration
OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://127.0.0.1:11434")
if OLLAMA_HOST == "0.0.0.0":
    OLLAMA_HOST = "http://127.0.0.1:11434"
elif "0.0.0.0" in OLLAMA_HOST:
    OLLAMA_HOST = OLLAMA_HOST.replace("0.0.0.0", "127.0.0.1")

EMBED_MODEL = "nomic-embed-text"
LLM_MODEL = "llama3.1:8b"
DB_PATH = "./chroma_db"
COLLECTION_NAME = "documents_ecole"
DOCS_DIR = "./docs"

# Client Ollama
try:
    client_llm = ollama.Client(host=OLLAMA_HOST)
except Exception as e:
    print(f"Erreur d'initialisation du client Ollama: {e}")
    client_llm = None

def get_db_client() -> chromadb.PersistentClient:
    """Initialise et retourne le client persistant de ChromaDB.

    Returns:
        chromadb.PersistentClient: L'instance du client ChromaDB.
    """
    return chromadb.PersistentClient(path=DB_PATH)

def get_or_create_collection() -> Collection:
    """Récupère ou crée la collection ChromaDB pour les documents.

    Returns:
        Collection: La collection ChromaDB.
    """
    client = get_db_client()
    return client.get_or_create_collection(name=COLLECTION_NAME)

def split_text_into_chunks(text: str, chunk_size: int = 700, overlap: int = 100) -> List[str]:
    """Découpe un texte en morceaux de taille fixe avec chevauchement.

    Args:
        text: Le texte à découper.
        chunk_size: La taille maximale de chaque morceau (en caractères).
        overlap: Le nombre de caractères de chevauchement entre deux morceaux.

    Returns:
        List[str]: La liste des morceaux de texte.
    """
    text = text.strip()
    if not text:
        return []
    
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += chunk_size - overlap
    return chunks

def ingest_pdf(file_path: str) -> int:
    """Extrait le texte d'un PDF, le découpe en morceaux, calcule les embeddings et les stocke.

    Args:
        file_path: Le chemin absolu ou relatif vers le fichier PDF.

    Returns:
        int: Le nombre de morceaux insérés dans la base de données.
    
    Raises:
        FileNotFoundError: Si le fichier PDF n'existe pas.
        Exception: En cas d'erreur de lecture du PDF ou d'appel à l'API d'embedding.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Le fichier {file_path} est introuvable.")
    
    collection = get_or_create_collection()
    file_name = os.path.basename(file_path)
    
    try:
        reader = PdfReader(file_path)
    except Exception as e:
        raise Exception(f"Impossible de lire le fichier PDF {file_name} : {e}")
        
    chunks_added = 0
    
    for page_num, page in enumerate(reader.pages, start=1):
        try:
            page_text = page.extract_text()
            if not page_text or not page_text.strip():
                continue
        except Exception as e:
            print(f"Erreur d'extraction de texte sur la page {page_num} de {file_name} : {e}")
            continue
            
        page_chunks = split_text_into_chunks(page_text)
        
        for chunk_idx, chunk in enumerate(page_chunks):
            # Créer un identifiant unique pour le chunk
            chunk_id = f"{file_name}_p{page_num}_c{chunk_idx}"
            
            try:
                # Calcul de l'embedding via Ollama
                if client_llm is None:
                    raise Exception("Le client Ollama n'est pas configuré ou est inaccessible.")
                    
                response = client_llm.embeddings(model=EMBED_MODEL, prompt=f"search_document: {chunk}")
                embedding = response.get("embedding")
                
                if not embedding:
                    print(f"Embedding vide généré pour {chunk_id}")
                    continue
                
                # Ajout dans ChromaDB
                metadata = {
                    "source": file_name,
                    "page": page_num,
                }
                
                collection.add(
                    ids=[chunk_id],
                    documents=[chunk],
                    embeddings=[embedding],
                    metadatas=[metadata]
                )
                chunks_added += 1
            except Exception as e:
                print(f"Erreur lors de l'indexation du morceau {chunk_id} : {e}")
                
    return chunks_added

def list_pdf_files() -> List[str]:
    """Liste tous les fichiers PDF présents dans le dossier docs/.

    Returns:
        List[str]: Les chemins des fichiers PDF trouvés.
    """
    if not os.path.exists(DOCS_DIR):
        return []
    return glob.glob(os.path.join(DOCS_DIR, "*.pdf"))

def check_and_ingest_all(force_reset: bool = False) -> Dict[str, Any]:
    """Vérifie le dossier docs/ et indexe tous les fichiers PDF dans ChromaDB.

    Args:
        force_reset: Si True, réinitialise la collection avant de réindexer.

    Returns:
        Dict[str, Any]: Un résumé de l'opération d'ingestion.
    """
    client = get_db_client()
    
    if force_reset:
        try:
            client.delete_collection(name=COLLECTION_NAME)
        except Exception:
            pass # Si la collection n'existait pas, ce n'est pas grave
            
    collection = get_or_create_collection()
    existing_count = collection.count()
    
    # Si la collection contient déjà des données et qu'on ne force pas le reset, on ne fait rien
    if existing_count > 0 and not force_reset:
        return {
            "status": "skipped",
            "message": f"La base de données contient déjà {existing_count} morceaux de documents.",
            "count": existing_count
        }
        
    pdf_files = list_pdf_files()
    if not pdf_files:
        return {
            "status": "error",
            "message": f"Aucun fichier PDF trouvé dans le dossier '{DOCS_DIR}'. Veuillez d'abord y ajouter des documents.",
            "count": 0
        }
        
    total_added = 0
    errors = []
    
    for pdf_file in pdf_files:
        try:
            added = ingest_pdf(pdf_file)
            total_added += added
        except Exception as e:
            errors.append(f"Erreur sur {os.path.basename(pdf_file)}: {str(e)}")
            
    if errors:
        return {
            "status": "partial_success",
            "message": f"Indexation terminée avec des erreurs. {total_added} morceaux ajoutés.",
            "count": total_added,
            "errors": errors
        }
        
    return {
        "status": "success",
        "message": f"Indexation réussie ! {total_added} morceaux de texte ont été stockés dans la base de données vectorielle.",
        "count": total_added
    }

def repondre(query: str, n_results: int = 4) -> Dict[str, Any]:
    """Recherche les informations pertinentes et génère une réponse avec les sources.

    Args:
        query: La question de l'étudiant.
        n_results: Nombre de morceaux pertinents à récupérer dans la base de données.

    Returns:
        Dict[str, Any]: Un dictionnaire contenant la réponse générée et les sources utilisées.
    """
    result = {
        "answer": "Une erreur interne s'est produite lors de la génération de la réponse.",
        "sources": []
    }
    
    if not query.strip():
        result["answer"] = "Veuillez poser une question valide."
        return result
        
    if client_llm is None:
        result["answer"] = "L'assistant IA est actuellement indisponible (Ollama n'est pas accessible)."
        return result
        
    try:
        collection = get_or_create_collection()
        
        # Vérifier si la base de données contient des documents
        if collection.count() == 0:
            result["answer"] = "La base de données documentaire est vide. Veuillez indexer des documents PDF d'abord."
            return result
            
        # 1. Calculer l'embedding de la question de l'utilisateur
        q_emb_response = client_llm.embeddings(model=EMBED_MODEL, prompt=f"search_query: {query}")
        q_emb = q_emb_response.get("embedding")
        
        if not q_emb:
            result["answer"] = "Impossible de calculer l'empreinte sémantique de votre question."
            return result
            
        # 2. Rechercher les morceaux les plus proches dans ChromaDB
        search_results = collection.query(query_embeddings=[q_emb], n_results=n_results)
        
        # Extraire les morceaux de texte et métadonnées
        documents = search_results.get("documents", [[]])[0]
        metadatas = search_results.get("metadatas", [[]])[0]
        
        if not documents:
            result["answer"] = "Je n'ai trouvé aucune information pertinente dans les documents de l'école pour répondre à votre question."
            return result
            
        # Formater le contexte pour le LLM
        contexte_parts = []
        sources_list = []
        
        for idx, (doc_text, meta) in enumerate(zip(documents, metadatas)):
            source_name = meta.get("source", "Document inconnu")
            page_num = meta.get("page", "?")
            
            contexte_parts.append(f"--- MORCEAU {idx+1} (Source: {source_name}, Page: {page_num}) ---\n{doc_text}")
            
            sources_list.append({
                "source": source_name,
                "page": page_num,
                "text": doc_text
            })
            
        contexte = "\n\n".join(contexte_parts)
        
        # 3. Construire le prompt système et utilisateur
        messages = [
            {
                "role": "system",
                "content": (
                    "Tu es un assistant IA d'aide aux étudiants d'une école. "
                    "Réponds à la question posée de manière claire, concise et en français. "
                    "Règle absolue : Réponds uniquement en utilisant les informations fournies dans le CONTEXTE ci-dessous.\n"
                    "Si le CONTEXTE ne contient pas l'information nécessaire pour répondre à la question ou si tu as un doute, "
                    "réponds exactement et uniquement par : 'Je ne sais pas.' sans ajouter d'autres commentaires ou explications.\n"
                    "Ne fais aucune supposition et n'invente rien."
                )
            },
            {
                "role": "user",
                "content": f"CONTEXTE :\n{contexte}\n\nQUESTION : {query}"
            }
        ]
        
        # 4. Appeler le LLM pour générer la réponse
        llm_response = client_llm.chat(
            model=LLM_MODEL,
            messages=messages,
            options={"temperature": 0.0} # Température à 0 pour éviter les hallucinations
        )
        
        answer = llm_response["message"]["content"].strip()
        
        # Remplir le résultat
        result["answer"] = answer
        result["sources"] = sources_list
        
    except Exception as e:
        result["answer"] = f"Une erreur technique est survenue : {str(e)}"
        
    return result

if __name__ == "__main__":
    # Test simple en console
    print("Vérification et indexation automatique des documents...")
    res = check_and_ingest_all(force_reset=False)
    print(res["message"])
    
    print("\nTest de question 1 (présente dans les documents) :")
    q1 = "Quelles sont les règles pour justifier une absence ?"
    rep1 = repondre(q1)
    print(f"Q: {q1}")
    print(f"R: {rep1['answer']}")
    print("Sources :", [f"{s['source']} (p. {s['page']})" for s in rep1['sources']])
    
    print("\nTest de question 2 (absente des documents) :")
    q2 = "Comment s'appelle le président de la République ?"
    rep2 = repondre(q2)
    print(f"Q: {q2}")
    print(f"R: {rep2['answer']}")
