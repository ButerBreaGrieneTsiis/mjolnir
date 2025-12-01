import streamlit as st

from mjolnir.register import Register
from mjolnir.sessie import Sessie

def opslaan(sessie):
    sessie.opslaan()
    Register().opslaan()

def paneel():
    
    if "register" not in st.session_state:
        st.session_state["register"] = Register.openen()
    
    if "sessie" not in st.session_state:
        st.session_state["sessie"] = Sessie.huidig()
    
    for oefening in st.session_state["sessie"].oefeningen:
        oefening.paneel()
    
    if st.button("opslaan", key = "opslaan"):
        st.session_state["sessie"].opslaan()
        st.session_state["register"].opslaan()