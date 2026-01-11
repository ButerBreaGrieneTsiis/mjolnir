import streamlit as st

from mjolnir.basis import Register
from mjolnir.sessie.sessie import Sessie


st.set_page_config(layout = "wide")

def paneel():
    
    st.markdown(
        f"""
        <style>
            .block-container {{
                padding-top: 0.0rem;
                padding-bottom: 0rem;
                padding-left: 2rem;
                padding-right: 2rem;
                }}
            
            header {{visibility: hidden;}}
            
            .main {{overflow: hidden}}
        </style>
        """,
        unsafe_allow_html = True,
        )
    
    if "register" not in st.session_state:
        st.session_state["register"] = Register.openen()
    
    if "sessie" not in st.session_state:
        st.session_state["sessie"] = Sessie.huidig()
    
    st.session_state["sessie"].paneel()