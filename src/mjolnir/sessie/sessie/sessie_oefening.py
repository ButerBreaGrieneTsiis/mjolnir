"""mjolnir.sessie.sessie_oefening"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict, List

from grienetsiis.register import Register
import streamlit as st

from mjolnir.kern.enums import Oefening, SetType, SetGroepType
from mjolnir.sessie.sessie import SessieSet
from mjolnir.resultaat import Resultaat


@dataclass
class SessieOefening:
    
    oefening: Oefening
    sets: Dict[str, List[SessieSet]]
    trainingsgewicht: float = None
    
    def __post_init__(self):
        
        if self.oefening.halter_type is not None:
            
            halterstangen = Register().halterstangen.filter(halter_type = self.oefening.halter_type).lijst
            
            if len(halterstangen) > 1:
                raise NotImplementedError("momenteel wordt maximaal één halterstang ondersteund per halter_type")
            
            halterstang = halterstangen[0]
            halterschijven = Register().halterschijven.filter(diameter = halterstang.diameter).lijst
            
            gewichten = []
            
            for sessie_setgroep in self.sets.values():
                for sessie_set in sessie_setgroep:
                    gewichten.append(sessie_set.gewicht_aantal)
            
            halters = halterstang.optimaal_laden(
                gewicht_per_set = gewichten,
                halterschijven = halterschijven,
                )
            
            for sessie_set, halter in zip([sessie_set for sessie_setgroep in self.sets.values() for sessie_set in sessie_setgroep], halters):
                sessie_set.halter = halter
        
        for sessie_setgroep, sessie_sets in self.sets.items():
            
            if len(sessie_sets) == 1 and sessie_sets[0].set_type in (SetType.AMSAP, SetType.VRIJ):
                
                sessie_sets[0].sessie_oefening = self
                sessie_sets[0].setgroep = sessie_setgroep
    
    @classmethod
    def nieuw(
        cls,
        oefening: Oefening,
        sjablonen: List[str],
        week: int,
        trainingsgewichten: List[Dict[str, Any]],
        ):
        
        trainingsgewicht = next((trainingsgewicht_dict["trainingsgewicht"] for trainingsgewicht_dict in trainingsgewichten if trainingsgewicht_dict["oefening"] == oefening), None)
        
        sessie_sets = {}
        
        set_nummer = 0
        
        for sjabloon_uuid in sjablonen:
            
            sjabloon = Register().sjablonen[sjabloon_uuid]
            
            if sjabloon.weken == 0:
                setcodes = sjabloon.setcodes["week 0"]
            else:
                setcodes = sjabloon.setcodes[f"week {week}"]
            
            for setcode in setcodes:
                
                set_type = setcode.set_type
                set_aantal = setcode.set_aantal
                
                if sjabloon.setgroep_type.value not in sessie_sets:
                    sessie_sets[sjabloon.setgroep_type.value] = []
                
                if set_type == SetType.AANTAL or set_type == SetType.AMSAP:
                    for _ in range(set_aantal):
                    
                        set_nummer += 1
                        
                        sessie_set = SessieSet(
                            setcode = setcode,
                            set_nummer = set_nummer,
                            oefening = oefening,
                            trainingsgewicht = trainingsgewicht,
                            )
                        
                        sessie_sets[sjabloon.setgroep_type.value].append(sessie_set)
                else:
                    set_nummer += 1
                    
                    sessie_set = SessieSet(
                        setcode = setcode,
                        set_nummer = set_nummer,
                        oefening = oefening,
                        trainingsgewicht = trainingsgewicht,
                        )
                    
                    sessie_sets[sjabloon.setgroep_type.value].append(sessie_set)
        
        return cls(
            oefening = oefening,
            sets = sessie_sets,
            trainingsgewicht = trainingsgewicht,
            )
    
    @property
    def hoofdoefening(self) -> bool:
        return SetGroepType.OVERIG.value not in self.sets
    
    @property
    def volume(self) -> float | None:
        if self.oefening.gewichtloos:
            return None
        return sum(sessie_set.volume for sessie_setgroep in self.sets.values() for sessie_set in sessie_setgroep)
    
    @property
    def e1rm(self) -> float | None:
        if self.oefening.gewichtloos:
            return None
        return max(sessie_set.e1rm for sessie_setgroep in self.sets.values() for sessie_set in sessie_setgroep)
    
    @property
    def titel(self) -> str:
        
        if self.volume is None and self.e1rm is None:
            return f"{self.oefening.naam.upper()}"
        
        if self.trainingsgewicht is None:
            return f"{self.oefening.naam.upper()} (volume: {self.volume:.1f} kg, e1rm: {self.e1rm:.1f} kg)"
        return f"{self.oefening.naam.upper()} (TM: {self.trainingsgewicht:.1f} kg, volume: {self.volume:.1f} kg, e1rm: {self.e1rm:.1f} kg)"
    
    def paneel(
        self,
        kolom,
        ):
        
        titel = kolom.container()
        if not self.hoofdoefening:
            self.recent_resultaat(kolom)
        
        for sessie_setgroep, sessie_sets in self.sets.items():
            if self.hoofdoefening:
                kolom.markdown(sessie_setgroep)
            
            for sessie_set in sessie_sets:
                sessie_set.paneel(kolom)
        
        for regel in self.titel.split("\n"):
            titel.markdown(f":primary[{regel}]")
    
    def recent_resultaat(
        self,
        kolom,
        ):
        
        if f"recent_resultaat_{self.oefening.naam_underscore}" not in st.session_state:
            st.session_state[f"recent_resultaat_{self.oefening.naam_underscore}"] = Resultaat.tabel_recent(self.oefening, 5)
        
        expander = kolom.expander(
            label = f"recente resultaten {self.oefening.naam}",
            )
        if st.session_state[f"recent_resultaat_{self.oefening.naam_underscore}"]:
            expander.dataframe(
                data = st.session_state[f"recent_resultaat_{self.oefening.naam_underscore}"],
                # hide_index = True,
                )
        else:
            expander.markdown("deze oefening is nog niet uitgevoerd")