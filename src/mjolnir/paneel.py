import streamlit as st

from mjolnir.register import Register
from mjolnir.sessie import Sessie


def paneel():
    
    if "register" not in st.session_state:
        st.session_state["register"] = Register.openen()
    
    if "sessie" not in st.session_state:
        st.session_state["sessie"] = Sessie.huidig()
    
    st.session_state["sessie"].paneel()