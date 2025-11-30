import streamlit as st

from mjolnir.register import Register
from mjolnir.sessie import Sessie


@st.cache_data
def laden():
    Register.openen()
    sessie = Sessie.huidig()
    return sessie

def opslaan(sessie):
    Register().opslaan()
    sessie.opslaan()

def paneel():
    
    sessie = laden()
    
    for oefening in sessie.oefeningen:
        st.write(oefening.oefening.value[0])
        for setgroep, sets in oefening.sets.items():
            st.write(setgroep)
            for set in sets:
                set.paneel
    
    # if button:
    # opslaan()