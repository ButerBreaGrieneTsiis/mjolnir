import streamlit as st

from .kern import Sessie

def sessie_paneel():
    
    sessie = Sessie.open()
    sessie.start()
    
    
#     start_time = st.slider(
#     "When do you start?",
#     value=datetime(2020, 1, 1, 9, 30),
#     format="MM/DD/YY - hh:mm",
# )
# st.write("Start time:", start_time)