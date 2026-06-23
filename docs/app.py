import streamlit as st
from docs.rag import repondre 

st.title("Assistant documentaire")
question = st.text_input("Posez votre question :")

if st.button("Demander") and question:
    reponse = repondre(question)
    st.write(reponse)
    st.snow()
    st.write(reponse)
    with st.expander("Sources utilisées"):
        for morceau in reponse["documents"][0]:
            st.markdown(f"- {morceau}")