"""mjolnir.sessie.functies"""
from __future__ import annotations
from contextlib import contextmanager
from typing import Literal

import streamlit as st


@contextmanager
def st_horizontaal(uitlijning: Literal["rechts", "links"] = "links"):
    
    if uitlijning == "rechts":
        uitlijning_tekst = "justify-content: flex-end;"
    else:
        uitlijning_tekst = "justify-content: flex-start;"
    
    HORIZONTAL_STYLE = f"""
        <style class = "hide-element">
            .element-container:has(.hide-element) {{
                display: none;
                }}
            div[data-testid = "stVerticalBlock"]:has(> .element-container .horizontal-marker-{uitlijning}) {{
                display: flex;
                flex-direction: row !important;
                flex-wrap: wrap;
                gap: 0.5rem;
                align-items: baseline;
                {uitlijning_tekst}
                }}
            div[data-testid = "stVerticalBlock"]:has(> .element-container .horizontal-marker-{uitlijning}) div {{
                width: max-content !important;
                }}
        </style>
        """
    
    st.markdown(HORIZONTAL_STYLE, unsafe_allow_html=True)
    with st.container():
        st.markdown(f"""<span class = "hide-element horizontal-marker-{uitlijning}"></span>""", unsafe_allow_html = True)
        yield