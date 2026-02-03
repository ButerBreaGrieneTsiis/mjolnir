"""mjolnir.sessie.sessie_set"""
from __future__ import annotations
from copy import copy
from dataclasses import dataclass
from typing import TYPE_CHECKING

import streamlit as st

from mjolnir.kern import CONFIG, Setcode
from mjolnir.kern.enums import Oefening, GewichtType, HalterType, RepetitieType, SetType, Status
from mjolnir.sessie.halter import Halter
from mjolnir.sessie.functies import st_horizontaal

if TYPE_CHECKING:
    from mjolnir.sessie.sessie import SessieOefening


@dataclass
class SessieSet:
    
    setcode: Setcode
    
    set_nummer: int
    oefening: Oefening
    
    sessie_oefening: SessieOefening = None
    setgroep: str = None
    
    trainingsgewicht: float | None = None
    halter: Halter | None = None
    
    status: Status = Status.GEPLAND
    repetitie_gedaan: int = 0
    repetitie_links_gedaan: int = 0
    gewicht_gedaan: float = 0.0
    
    @property
    def set_type(self) -> SetType:
        return self.setcode.set_type
    
    @property
    def set_aantal(self) -> int:
        return self.setcode.set_aantal
    
    @property
    def repetitie_type(self) -> RepetitieType:
        return self.setcode.repetitie_type
    
    @property
    def repetitie_aantal(self) -> int:
        return self.setcode.repetitie_aantal
    
    @property
    def repetitie_maximaal(self) -> int:
        return self.setcode.repetitie_maximaal
    
    @property
    def gewicht_type(self) -> GewichtType:
        return self.setcode.gewicht_type
    
    @property
    def gewicht_aantal(self) -> int | None:
        if self.gewicht_type == GewichtType.PERCENTAGE:
            return self.setcode.gewicht_aantal / 100 * self.trainingsgewicht
        return self.setcode.gewicht_aantal
    
    @property
    def set_tekst(self) -> str:
        return self.setcode.set_tekst
    
    @property
    def repetitie_tekst(self) -> str:
        return self.setcode.repetitie_tekst
    
    @property
    def gewicht_tekst(self) -> str:
        return self.setcode.gewicht_tekst
    
    @property
    def volume(self) -> float | None:
        if self.oefening.gewichtloos:
            return None
        return self.gewicht_gedaan * self.repetitie_gedaan
    
    @property
    def e1rm(self) -> float | None:
        if self.oefening.gewichtloos:
            return None
        return self.gewicht_gedaan * (1 + self.repetitie_gedaan/30)
    
    def paneel(
        self,
        kolom,
        ):
        
        # verwijderen van deze set
        if st.session_state.get(f"knop_verwijderen_{self.oefening.naam_underscore}_{self.set_nummer}", False):
            self.verwijderen_set()
            return
        
        if self.repetitie_type == RepetitieType.AANTAL:
            max_repetities = self.repetitie_aantal
            aantal_repetities = self.repetitie_aantal
        elif self.repetitie_type == RepetitieType.BEREIK:
            max_repetities = self.repetitie_aantal[1]
            aantal_repetities = self.repetitie_aantal[1]
        else:
            max_repetities = CONFIG["REPETITIE_AANTAL_MAX"]
            if self.repetitie_type == RepetitieType.BEREIK_AMRAP:
                aantal_repetities = self.repetitie_aantal[1]
            else:
                aantal_repetities = self.repetitie_aantal
        
        if self.gewicht_type == GewichtType.PERCENTAGE:
            hoeveelheid_gewicht = self.halter.massa
        elif self.gewicht_type in (GewichtType.GEWICHT, GewichtType.VRIJ):
            hoeveelheid_gewicht = self.gewicht_aantal
        else:
            hoeveelheid_gewicht = 0.0
        
        # status expander van deze set
        if f"expander_{self.oefening.naam_underscore}_{self.set_nummer}" not in st.session_state:
            st.session_state[f"expander_{self.oefening.naam_underscore}_{self.set_nummer}"] = True
        
        # status expander van de volgende set
        if f"expander_{self.oefening.naam_underscore}_{self.set_nummer + 1}" not in st.session_state:
            st.session_state[f"expander_{self.oefening.naam_underscore}_{self.set_nummer + 1}"] = False
        
        # aantal repetities van deze set
        if f"repetities_{self.oefening.naam_underscore}_{self.set_nummer}" not in st.session_state:
            st.session_state[f"repetities_{self.oefening.naam_underscore}_{self.set_nummer}"] = aantal_repetities
            
            if self.oefening.dextraal:
                st.session_state[f"repetities_links_{self.oefening.naam_underscore}_{self.set_nummer}"] = aantal_repetities
        
        # hoeveelheid gewicht van deze set
        if f"gewicht_{self.oefening.naam_underscore}_{self.set_nummer}" not in st.session_state:
            st.session_state[f"gewicht_{self.oefening.naam_underscore}_{self.set_nummer}"] = hoeveelheid_gewicht
        
        # instellen van het gewicht van deze set, indien aanwezig
        if st.session_state.get(f"knop_gewicht_{self.oefening.naam_underscore}_{self.set_nummer}", False):
            
            if self.oefening.halter_type is not None:
                self.halter = self.halter.halterstang.laden(
                    gewicht = st.session_state[f"gewicht_ingevuld_{self.oefening.naam_underscore}_{self.set_nummer}"],
                    halterschijven = st.session_state["register"].halterschijven.filter(diameter = self.halter.halterstang.diameter).lijst,
                    )
                st.session_state[f"gewicht_{self.oefening.naam_underscore}_{self.set_nummer}"] = self.halter.massa
            else:
                st.session_state[f"gewicht_{self.oefening.naam_underscore}_{self.set_nummer}"] = st.session_state[f"gewicht_ingevuld_{self.oefening.naam_underscore}_{self.set_nummer}"]
        
        # afronden van deze set
        if st.session_state.get(f"knop_afronden_{self.oefening.naam_underscore}_{self.set_nummer}", False):
            
            self.repetitie_gedaan = st.session_state[f"repetities_{self.oefening.naam_underscore}_{self.set_nummer}"]
            if self.oefening.dextraal:
                self.repetitie_links_gedaan = st.session_state[f"repetities_links_{self.oefening.naam_underscore}_{self.set_nummer}"]
            self.gewicht_gedaan = st.session_state[f"gewicht_{self.oefening.naam_underscore}_{self.set_nummer}"]
            
            if self.set_type in (SetType.AMSAP, SetType.VRIJ) and self.status == Status.GEPLAND:
                self.toevoegen_set()
            
            self.status = Status.AFGEROND
            
            st.session_state[f"expander_{self.oefening.naam_underscore}_{self.set_nummer}"] = False
            st.session_state[f"expander_{self.oefening.naam_underscore}_{self.set_nummer + 1}"] = True
            
        # afbreken van deze set
        if st.session_state.get(f"knop_afbreken_{self.oefening.naam_underscore}_{self.set_nummer}", False):
            
            if self.set_type in (SetType.AMSAP, SetType.VRIJ):
                self.status = Status.AFGEROND
            else:
                self.status = Status.AFGEBROKEN
            
            st.session_state[f"expander_{self.oefening.naam_underscore}_{self.set_nummer}"] = False
            st.session_state[f"expander_{self.oefening.naam_underscore}_{self.set_nummer + 1}"] = True
        
        # naam van deze set
        if f"label_{self.oefening.naam_underscore}_{self.set_nummer}" not in st.session_state:
            if self.oefening.gewichtloos:
                st.session_state[f"label_{self.oefening.naam_underscore}_{self.set_nummer}"] = f"set {self.set_nummer}: {self.repetitie_tekst}"
            else:
                st.session_state[f"label_{self.oefening.naam_underscore}_{self.set_nummer}"] = f"set {self.set_nummer}: {self.repetitie_tekst}@{self.gewicht_tekst}"
        else:
            if self.status == Status.AFGEROND:
                if self.oefening.gewichtloos:
                    st.session_state[f"label_{self.oefening.naam_underscore}_{self.set_nummer}"] = f":white_check_mark: set {self.set_nummer}: {self.repetitie_gedaan} ({self.repetitie_tekst})"
                else:
                    st.session_state[f"label_{self.oefening.naam_underscore}_{self.set_nummer}"] = f":white_check_mark: set {self.set_nummer}: {self.repetitie_gedaan}@{self.gewicht_gedaan} ({self.repetitie_tekst}@{self.gewicht_tekst})"
            if self.status == Status.AFGEBROKEN:
                if self.oefening.gewichtloos:
                    st.session_state[f"label_{self.oefening.naam_underscore}_{self.set_nummer}"] = f":heavy_multiplication_x: set {self.set_nummer}: {self.repetitie_tekst}"
                else:
                    st.session_state[f"label_{self.oefening.naam_underscore}_{self.set_nummer}"] = f":heavy_multiplication_x: set {self.set_nummer}: {self.repetitie_tekst}@{self.gewicht_tekst}"
        
        expander = kolom.expander(
            label = st.session_state[f"label_{self.oefening.naam_underscore}_{self.set_nummer}"],
            expanded = st.session_state[f"expander_{self.oefening.naam_underscore}_{self.set_nummer}"],
            )
        
        kolom_repetities, kolom_gewicht, kolom_halter = expander.columns([0.2, 0.2, 0.6])
        
        kolom_repetities.markdown("**repetities**")
        kolom_repetities.markdown(f"{self.repetitie_tekst} ({self.repetitie_type.value})")
        
        if not self.oefening.gewichtloos:
            kolom_gewicht.markdown("**gewicht**")
            if self.oefening.halter_type is not None:
                kolom_gewicht.markdown(f"{f"{self.halter.massa}".replace(".", ",")} kg")
            else:
                kolom_gewicht.markdown(f"{f"{st.session_state[f"gewicht_{self.oefening.naam_underscore}_{self.set_nummer}"]}".replace(".", ",")} kg")
        
        if self.oefening.halter_type is not None:
            kolom_halter.markdown("**halter**")
            kolom_halter.markdown(self.halter)
        
        if self.gewicht_type == GewichtType.VRIJ:
            
            formulier_gewicht = expander.form(
                key = f"formulier_gewicht_{self.oefening.naam_underscore}_{self.set_nummer}",
                border = False,
                )
            
            max_value = int(CONFIG["GEWICHT_AANTAL_MAX"]) if self.oefening.halter_type == HalterType.BARBELL else 50
            
            formulier_gewicht.slider(
                label = "gewicht",
                min_value = 0,
                max_value = max_value,
                key = f"gewicht_ingevuld_{self.oefening.naam_underscore}_{self.set_nummer}",
                )
            
            formulier_gewicht.form_submit_button(
                label = "gewicht instellen",
                key = f"knop_gewicht_{self.oefening.naam_underscore}_{self.set_nummer}",
                )
        
        formulier = expander.form(
            key = f"formulier_{self.oefening.naam_underscore}_{self.set_nummer}",
            border = False,
            )
        
        if self.oefening.dextraal:
            
            formulier.slider(
                label = "rechts",
                min_value = 0,
                max_value = max_repetities,
                key = f"repetities_{self.oefening.naam_underscore}_{self.set_nummer}",
                )
            
            formulier.slider(
                label = "links",
                min_value = 0,
                max_value = max_repetities,
                key = f"repetities_links_{self.oefening.naam_underscore}_{self.set_nummer}",
                )
        else:
            
            formulier.slider(
                label = "repetities",
                min_value = 0,
                max_value = max_repetities,
                key = f"repetities_{self.oefening.naam_underscore}_{self.set_nummer}",
                )
        
        knoppen, _ = formulier.columns([0.9, 0.1], vertical_alignment = "bottom")
        
        with knoppen:
            with st_horizontaal():
                formulier_knop_afronden = st.empty()
                formulier_knop_afbreken = st.empty()
                formulier_knop_verwijderen = st.empty()
        
        if self.set_type in (SetType.AMSAP, SetType.VRIJ):
            label_knop_afronden = "afronden en toevoegen"
            label_knop_afbreken = "afronden en beëindigen"
        else:
            label_knop_afronden = "afronden"
            label_knop_afbreken = "afbreken"
        
        formulier_knop_afronden.form_submit_button(
            label = label_knop_afronden,
            key = f"knop_afronden_{self.oefening.naam_underscore}_{self.set_nummer}",
            )
        
        formulier_knop_afbreken.form_submit_button(
            label = label_knop_afbreken,
            key = f"knop_afbreken_{self.oefening.naam_underscore}_{self.set_nummer}",
            )
        
        if self.set_type in (SetType.AMSAP, SetType.VRIJ) and self.set_nummer > 1:
            
            formulier_knop_verwijderen.form_submit_button(
                label = "verwijderen",
                key = f"knop_verwijderen_{self.oefening.naam_underscore}_{self.set_nummer}",
                )
        
        return expander
    
    def toevoegen_set(self) -> None:
        
        set = copy(self)
        set.set_nummer += 1
        
        st.session_state["opslaan_uitgeschakeld"] = True
        
        st.session_state[f"repetities_{self.oefening.naam_underscore}_{set.set_nummer}"] = self.repetitie_gedaan
        if self.oefening.dextraal:
            st.session_state[f"repetities_links_{self.oefening.naam_underscore}_{set.set_nummer}"] = self.repetitie_links_gedaan
        
        if not self.oefening.gewichtloos:
            st.session_state[f"gewicht_ingevuld_{self.oefening.naam_underscore}_{set.set_nummer}"] = st.session_state[f"gewicht_ingevuld_{self.oefening.naam_underscore}_{self.set_nummer}"]
            st.session_state[f"gewicht_{self.oefening.naam_underscore}_{set.set_nummer}"] = self.gewicht_gedaan
        
        self.sessie_oefening.sets[self.setgroep].append(set)
    
    def verwijderen_set(self) -> None:
        self.sessie_oefening.sets[self.setgroep].pop(-1)