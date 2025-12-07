import keyboard
import os
import psutil

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
    
    st.session_state["sessie"].paneel()
    
    # opslaan toets enkel zichtbaar bij afronden alle sets
    if st.button("opslaan", key = "opslaan"):
        st.session_state["sessie"].opslaan()
        st.session_state["register"].opslaan()
        # time.sleep(5)
        keyboard.press_and_release("ctrl+w")
        pid = os.getpid()
        p = psutil.Process(pid)
        p.terminate()