from typing import List

import streamlit as st


class Two:
    
    def __init__(
        self,
        id,
        ) -> "Two":
        
        self.id = id
    
    @property
    def aantal(self):
        return self._aantal
    
    @aantal.setter
    def aantal(self, waarde: int):
        self._aantal = waarde
    
    def dashboard(self):
        
        waarde = st.slider(
            label = "number",
            key = self.id,
            min_value = 0,
            max_value = 10,
            )
        
        self.aantal = waarde
        
class One:
    
    def __init__(
        self,
        name: str,
        twos: List[Two] = None,
        ) -> "One":
        
        self.name = name
        self.twos = list() if twos is None else twos
    
    def dashboard(self):
        
        for two in self.twos:
            if two.id not in st.session_state:
                st.session_state[two.id] = 5
        
        for two in self.twos:
            two.dashboard()
        
@st.cache_data
def initialise():
    two_1 = Two(1)
    two_2 = Two(2)
    two_3 = Two(3)
    one = One("", [two_1, two_2, two_3])
    
    return one

def dashboard():
    one = initialise()
    one.dashboard()

if __name__ == "__main__":
    dashboard()