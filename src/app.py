import os
import streamlit as st
import rag

# Configuration de la page Streamlit
st.set_page_config(
    page_title="EduAssistant RAG - PSTB",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Injection de CSS personnalisé pour une esthétique premium et moderne
st.markdown("""
<style>
    /* Import de la police Google Inter */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Application de la police globale */
    html, body, [class*="css"], .stApp {
        font-family: 'Inter', sans-serif;
        background-color: #f7fafc;
        color: #2d3748;
    }
    
    /* En-tête principal stylisé */
    .main-header {
        background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
        padding: 2.5rem;
        border-radius: 16px;
        color: white;
        margin-bottom: 2rem;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
        text-align: center;
        position: relative;
        overflow: hidden;
    }
    
    .main-header::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0) 80%);
        pointer-events: none;
    }
    
    .main-header h1 {
        font-size: 2.5rem;
        font-weight: 700;
        margin: 0;
        letter-spacing: -0.025em;
    }
    
    .main-header p {
        font-size: 1.1rem;
        opacity: 0.9;
        margin-top: 0.5rem;
        font-weight: 300;
    }

    /* Cartes de réponse */
    .response-card {
        background-color: white;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
        border-left: 5px solid #3b82f6;
        margin-bottom: 1.5rem;
        font-size: 1rem;
        line-height: 1.5;
    }
    
    .response-card.no-info {
        border-left: 5px solid #e53e3e;
        background-color: #fff5f5;
    }

    /* Cartes de sources */
    .source-card {
        background-color: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 1rem;
        margin-bottom: 0.75rem;
        transition: all 0.2s ease-in-out;
    }
    
    .source-card:hover {
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        border-color: #cbd5e1;
    }

    .source-badge {
        background-color: #3b82f6;
        color: white;
        padding: 0.2rem 0.6rem;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 600;
        display: inline-block;
        margin-bottom: 0.5rem;
    }
    
    .page-badge {
        background-color: #64748b;
        color: white;
        padding: 0.2rem 0.6rem;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 600;
        display: inline-block;
        margin-bottom: 0.5rem;
        margin-left: 0.25rem;
    }

    /* Sidebar Styling */
    .sidebar .sidebar-content {
        background-color: #0f172a;
        color: #f8fafc;
    }
    
    .doc-item {
        display: flex;
        align-items: center;
        padding: 0.5rem;
        background-color: #edf2f7;
        border-radius: 6px;
        margin-bottom: 0.5rem;
        font-size: 0.9rem;
        color: #4a5568;
        font-weight: 500;
    }
    
    .doc-icon {
        margin-right: 0.5rem;
        color: #e53e3e;
        font-size: 1.1rem;
    }

    /* Styles de la Charte d'utilisation */
    .charter-card {
        background-color: white;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        border: 1px solid #e2e8f0;
        margin-bottom: 1.5rem;
    }
    
    .charter-title {
        font-size: 1.1rem;
        font-weight: 700;
        color: #1e3a8a;
        margin-top: 0;
        margin-bottom: 0.75rem;
        border-bottom: 2px solid #3b82f6;
        padding-bottom: 0.5rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .charter-section-title {
        font-weight: 600;
        margin-top: 1rem;
        margin-bottom: 0.5rem;
        font-size: 0.9rem;
        display: flex;
        align-items: center;
        gap: 0.25rem;
    }
    
    .charter-section-title.allowed {
        color: #15803d;
    }
    
    .charter-section-title.forbidden {
        color: #b91c1c;
    }
    
    .charter-list {
        margin: 0;
        padding-left: 1.25rem;
        font-size: 0.85rem;
        color: #4b5563;
    }
    
    .charter-list li {
        margin-bottom: 0.4rem;
        line-height: 1.4;
    }
    
    .charter-warning-box {
        background-color: #fff7ed;
        border: 1px solid #ffedd5;
        border-left: 4px solid #f97316;
        color: #9a3412;
        padding: 0.75rem;
        border-radius: 8px;
        font-size: 0.8rem;
        font-weight: 500;
        line-height: 1.4;
        margin-top: 1.25rem;
    }
</style>
""", unsafe_allow_html=True)

# En-tête principal de la page (Barre bleue)
st.markdown("""<div class="main-header">
<h1>🎓 Assistant Documentaire Étudiant</h1>
<p>Votre compagnon IA local pour trouver rapidement les informations sur votre formation (Syllabus, Règlements, Contacts)</p>
</div>""", unsafe_allow_html=True)

# Initialisation de l'état de la charte dans session_state
if "show_charter" not in st.session_state:
    st.session_state.show_charter = True

# Barre latérale (Sidebar)
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # Statut d'Ollama
    if rag.client_llm is not None:
        st.success("🤖 Ollama : Connecté")
        st.info(f"Modèles :\n- LLM : `{rag.LLM_MODEL}`\n- Embed : `{rag.EMBED_MODEL}`")
    else:
        st.error("❌ Ollama : Déconnecté")
        st.warning("Assurez-vous qu'Ollama tourne en local sur http://localhost:11434.")
        
    st.markdown("---")
    
    # Liste des PDF indexés
    st.subheader("📁 Documents indexés")
    pdf_files = rag.list_pdf_files()
    if pdf_files:
        for pdf_path in pdf_files:
            file_name = os.path.basename(pdf_path)
            st.markdown(f"""
<div class="doc-item">
<span class="doc-icon">📄</span>
<span>{file_name}</span>
</div>""", unsafe_allow_html=True)
    else:
        st.warning("Aucun document PDF trouvé dans 'docs/'.")
        
    st.markdown("---")
    
    # Contrôle de la base ChromaDB
    st.subheader("🔄 Base de données")
    if st.button("Réindexer les documents 📂", key="btn_reindex", use_container_width=True):
        with st.spinner("Indexation des fichiers PDF en cours..."):
            try:
                res = rag.check_and_ingest_all(force_reset=True)
                if res["status"] in ["success", "partial_success"]:
                    st.success(res["message"])
                    st.rerun()
                else:
                    st.error(res["message"])
            except Exception as e:
                st.error(f"Erreur d'indexation : {e}")

    try:
        collection = rag.get_or_create_collection()
        count = collection.count()
        st.caption(f"Nombre de fragments en base : **{count}**")
    except Exception:
        st.caption("Erreur de connexion à ChromaDB.")

    st.markdown("---")
    
    # Bascule d'affichage de la charte d'utilisation
    st.subheader("⚖️ Affichage")
    show_charter = st.toggle("Afficher la charte", value=st.session_state.show_charter)
    st.session_state.show_charter = show_charter

# Vérifier si la base de données est vide
try:
    collection = rag.get_or_create_collection()
    db_empty = (collection.count() == 0)
except Exception:
    db_empty = True

if db_empty:
    st.info("👋 Bienvenue ! Pour commencer, veuillez indexer les documents d'exemple fournis.")
    if st.button("Lancer l'indexation initiale 🚀", key="btn_initial_index", type="primary"):
        with st.spinner("Création de la base vectorielle et indexation des PDF..."):
            try:
                res = rag.check_and_ingest_all(force_reset=False)
                if res["status"] in ["success", "partial_success"]:
                    st.success(res["message"])
                    st.rerun()
                else:
                    st.error(res["message"])
            except Exception as e:
                st.error(f"Une erreur est survenue lors de l'indexation : {e}")
else:
    # Structure de mise en page avec colonnes
    if st.session_state.show_charter:
        col_main, col_charter = st.columns([3.2, 1.2])
    else:
        col_main = st.container()
        col_charter = None

    # Partie Assistant (colonne principale)
    with col_main:
        st.subheader("💡 Posez votre question à l'assistant")
        
        # Utilisation d'un formulaire pour regrouper la saisie et le bouton
        with st.form("question_form", clear_on_submit=False):
            question = st.text_input(
                "Saisissez votre question ici (ex: 'Quels sont les objectifs du module IA ?', 'Quel est le règlement de retard ?') :",
                placeholder="Comment contacter le secrétariat ?...",
                key="student_question"
            )
            submit_btn = st.form_submit_button("Poser la question 💬", type="primary")

        # Détection de soumission de question pour masquer automatiquement la charte
        if submit_btn and question.strip():
            if st.session_state.show_charter:
                st.session_state.show_charter = False
                st.rerun()

        # Affichage de la réponse si une question a été posée
        if question.strip():
            with st.spinner("Recherche d'informations et formulation de la réponse..."):
                try:
                    response = rag.repondre(question)
                    answer = response.get("answer", "")
                    sources = response.get("sources", [])
                    
                    # Formatage de la réponse selon le fait qu'il sache ou non
                    if answer == "Je ne sais pas.":
                        st.markdown(f"""
<div class="response-card no-info">
<h3>🔍 Réponse de l'assistant</h3>
<p><b>{answer}</b></p>
<p style="font-size: 0.9rem; color: #718096; margin-top: 0.5rem;">
<i>Désolé, les documents officiels de l'école ne contiennent pas d'informations suffisantes pour répondre à cette question.</i>
</p>
</div>""", unsafe_allow_html=True)
                    else:
                        st.markdown(f"""
<div class="response-card">
<h3>🤖 Réponse de l'assistant</h3>
<div>{answer}</div>
</div>""", unsafe_allow_html=True)
                        if submit_btn:
                            st.balloons()
                        
                    # Affichage des sources
                    if sources and answer != "Je ne sais pas.":
                        st.subheader("📚 Sources utilisées")
                        cols = st.columns(min(len(sources), 3))
                        for idx, src in enumerate(sources):
                            col_idx = idx % len(cols)
                            with cols[col_idx]:
                                st.markdown(f"""
<div class="source-card">
<span class="source-badge">📄 {src['source']}</span>
<span class="page-badge">Page {src['page']}</span>
<p style="font-size: 0.85rem; color: #4a5568; line-height: 1.3; font-style: italic;">
"{src['text'][:250]}..."
</p>
</div>""", unsafe_allow_html=True)
                                
                except Exception as e:
                    st.error(f"Une erreur technique est survenue lors de la génération : {e}")

    # Partie Charte d'utilisation (colonne de droite)
    if st.session_state.show_charter and col_charter:
        with col_charter:
            st.markdown("""<div class="charter-card">
<div class="charter-title">⚖️ Charte & Conditions</div>

<div style="font-size: 0.8rem; color: #6b7280; font-style: italic; margin-bottom: 0.75rem;">
Cet outil est mis à disposition pour faciliter l'accès aux règlements et syllabus. Veuillez lire attentivement les limites de son périmètre d'action.
</div>

<div class="charter-section-title allowed">✅ Ce que l'assistant peut faire :</div>
<ul class="charter-list">
<li>Présenter le <b>contenu des cours</b>.</li>
<li>Décrire les <b>objectifs d'un module</b>.</li>
<li>Détailler les <b>modalités d'évaluation</b>.</li>
<li>Expliquer les <b>règles d'absence et de retard</b>.</li>
<li>Retrouver des dates ou des consignes importantes.</li>
<li>Citer le <b>règlement intérieur</b> de l'école.</li>
<li>Expliquer l'<b>organisation de la formation</b>.</li>
</ul>

<div class="charter-section-title forbidden">❌ Ce que l'assistant ne peut pas faire :</div>
<ul class="charter-list">
<li><b>Modifier une note</b> ou un relevé officiel.</li>
<li><b>Justifier une absence</b> (contacter le secrétariat).</li>
<li>Remplacer un professeur ou un responsable.</li>
<li>Prendre des décisions officielles pour l'établissement.</li>
<li>Consulter votre dossier scolaire personnel.</li>
<li>Accéder à des informations privées d'autres élèves.</li>
<li>Inventer des réponses (sécurité anti-hallucination active).</li>
</ul>

<div class="charter-warning-box">
⚠️ <b>Avertissement de Sécurité :</b><br>
Toute tentative d'utilisation abusive, d'attaques par injection de requêtes (prompt injection) ou de contournement des consignes de sécurité sera consignée et signalée à la direction de l'école. Les contrevenants feront l'objet de sanctions disciplinaires.
</div>
</div>""", unsafe_allow_html=True)
