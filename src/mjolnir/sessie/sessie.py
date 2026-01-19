from copy import copy
from dataclasses import dataclass
import datetime as dt
import keyboard
import locale
import os
import psutil
from typing import Any, Dict, List

import streamlit as st

from mjolnir.basis import Register, Setcode
from mjolnir.basis.constantes import *
from mjolnir.basis.enums import Oefening, GewichtType, HalterType, RepetitieType, SetType, SetGroepType, Status
from mjolnir.sessie import Halter
from mjolnir.resultaat import ResultaatOefening, Resultaat


locale.setlocale(locale.LC_ALL, "nl_NL.UTF-8")

@dataclass
class SessieSet:
    
    setcode: Setcode
    
    set_nummer: int
    oefening: Oefening
    
    sessie_oefening: "SessieOefening" = None
    setgroep: str = None
    
    trainingsgewicht: float | None = None
    halter: Halter | None = None
    
    status: Status = Status.GEPLAND
    repetitie_gedaan: int = 0
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
            max_repetities = REPETITIE_AANTAL_MAX
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
            self.gewicht_gedaan = st.session_state[f"gewicht_{self.oefening.naam_underscore}_{self.set_nummer}"]
            
            if self.set_type in (SetType.AMSAP, SetType.VRIJ):
                self.toevoegen_set()
            
            self.status = Status.AFGEROND
            
            st.session_state[f"expander_{self.oefening.naam_underscore}_{self.set_nummer}"] = False
            st.session_state[f"expander_{self.oefening.naam_underscore}_{self.set_nummer + 1}"] = True
            
        # afbreken van deze set
        if st.session_state.get(f"knop_afbreken_{self.oefening.naam_underscore}_{self.set_nummer}", False):
            
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
            
            max_value = int(GEWICHT_AANTAL_MAX) if self.oefening.halter_type == HalterType.BARBELL else 50
            
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
        
        formulier.slider(
            label = "repetities",
            min_value = 0,
            max_value = max_repetities,
            key = f"repetities_{self.oefening.naam_underscore}_{self.set_nummer}",
            )
        
        formulier_knop_afronden, formulier_knop_afbreken, formulier_knop_verwijderen, _ = formulier.columns([0.2, 0.2, 0.25, 0.35])
        
        formulier_knop_afronden.form_submit_button(
            label = "afronden",
            key = f"knop_afronden_{self.oefening.naam_underscore}_{self.set_nummer}",
            )
        
        formulier_knop_afbreken.form_submit_button(
            label = "afbreken",
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
        if not self.oefening.gewichtloos:
            st.session_state[f"gewicht_ingevuld_{self.oefening.naam_underscore}_{set.set_nummer}"] = st.session_state[f"gewicht_ingevuld_{self.oefening.naam_underscore}_{self.set_nummer}"]
            st.session_state[f"gewicht_{self.oefening.naam_underscore}_{set.set_nummer}"] = self.gewicht_gedaan
        
        self.sessie_oefening.sets[self.setgroep].append(set)
    
    def verwijderen_set(self) -> None:
        self.sessie_oefening.sets[self.setgroep].pop(-1)

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
            st.session_state[f"recent_resultaat_{self.oefening.naam_underscore}"] = ResultaatOefening.recent(self.oefening, 5)
        
        expander = kolom.expander(
            label = f"recente resultaten {self.oefening.naam}",
            )
        if st.session_state[f"recent_resultaat_{self.oefening.naam_underscore}"]:
            expander.table(
                data = st.session_state[f"recent_resultaat_{self.oefening.naam_underscore}"],
                # hide_index = True,
                )
        else:
            expander.markdown("deze oefening is nog niet uitgevoerd")

@dataclass
class Sessie:
    
    schema_uuid: str
    week: int
    dag: int
    datum: dt.date
    oefeningen: List[SessieOefening]
    
    @classmethod
    def huidig(cls):
        
        schemas_huidig = Register().schema.filter(status = Status.HUIDIG)
        schemas_gepland = Register().schema.filter(status = Status.GEPLAND)
        
        if len(schemas_huidig) == 0 and len(schemas_gepland) == 0:
            print("er zijn geen sessies gepland")
            Register().schema.nieuw()
            Register().opslaan()
            schemas = Register().schema.filter(status = Status.HUIDIG)
            schema_uuid = list(schemas.keys())[0]
            schema = list(schemas.values())[0]
        else:
            if len(schemas_huidig) == 0:
                schema_uuid = list(schemas_gepland.keys())[0]
                schema = list(schemas_gepland.values())[0]
                schema.status = Status.HUIDIG
            else:
                schema_uuid = list(schemas_huidig.keys())[0]
                schema = list(schemas_huidig.values())[0]
        
        stop_iteratie = False
        for week_tekst, sessie_week in schema.sessies.items():
            for dag_tekst, sessie_dag in sessie_week.items():
                if sessie_dag["status"] == Status.GEPLAND:
                    week = int(week_tekst.replace("week", "").strip())
                    dag = int(dag_tekst.replace("dag", "").strip())
                    stop_iteratie = True
                    break
            if stop_iteratie:
                break
        
        return cls.nieuw(
            schema_uuid = schema_uuid,
            week = week,
            dag = dag,
            datum = dt.date.today(),
            )
    
    @classmethod
    def nieuw(
        cls,
        schema_uuid : str,
        week: int,
        dag: int,
        datum: dt.date,
        ) -> "Sessie":
        
        schema = Register().schema[schema_uuid]
        
        oefeningen = []
        trainingsschema = schema.oefeningen[f"dag {dag}"]
        
        for oefening_dict in trainingsschema:
            
            oefening = SessieOefening.nieuw(
                oefening = oefening_dict["oefening"],
                sjablonen = oefening_dict["sjablonen"],
                week = week,
                trainingsgewichten = schema.trainingsgewichten,
                )
            
            oefeningen.append(oefening)
        
        return cls(
            schema_uuid = schema_uuid,
            week = week,
            dag = dag,
            datum = datum,
            oefeningen = oefeningen,
            )
    
    def opslaan(
        self,
        afgebroken: bool = False,
        ) -> None:
        
        schema = Register().schema[self.schema_uuid]
        
        schema.sessies[f"week {self.week}"][f"dag {self.dag}"]["status"] = Status.AFGEBROKEN if afgebroken else Status.AFGEROND
        schema.sessies[f"week {self.week}"][f"dag {self.dag}"]["datum"] = self.datum
        
        if schema.datum_begin is None:
            schema.datum_begin = self.datum
        
        if all(dag["status"] != Status.GEPLAND for week in schema.sessies.values() for dag in week.values()):
            schema.datum_eind = self.datum
            schema.status = Status.AFGEROND
        
        self.resultaat.opslaan()
    
    @property
    def resultaat(self) -> Resultaat:
        return Resultaat.van_sessie(self)
    
    def paneel(self):
        
        top_titel, top_knop_afbreken, top_knop_opslaan = st.columns([0.7, 0.15, 0.15], vertical_alignment = "bottom")
        
        top_titel.header(
            body = f"{Register().schema[self.schema_uuid].naam}, week {self.week} dag {self.dag}",
            anchor = False,
            )
        st.subheader(
            body = f"{self.datum.strftime("%A %d %B %Y")}",
            anchor = False,
            )
        
        aantal_hoofdoefeningen = sum(oefening.hoofdoefening for oefening in self.oefeningen)
        kolommen = st.columns(aantal_hoofdoefeningen + 1)
        
        kolom_nummer = 0
        for oefening in self.oefeningen:
            if oefening.hoofdoefening:
                kolom = kolommen[kolom_nummer]
                kolom_nummer += 1
            else:
                kolom = kolommen[-1]
            oefening.paneel(kolom)
        
        if "opslaan_uitgeschakeld" not in st.session_state:
            st.session_state["opslaan_uitgeschakeld"] = True
        else:
            st.session_state["opslaan_uitgeschakeld"] = not all(sessie_set.status in (Status.AFGEROND, Status.AFGEBROKEN) for oefening in self.oefeningen for sessie_setgroep in oefening.sets.values() for sessie_set in sessie_setgroep)
        
        # if "volledig_scherm" not in st.session_state:
        #     st.session_state["volledig_scherm"] = True
        #     keyboard.press_and_release("f11")
        
        if top_knop_opslaan.button(
            label = ":white_check_mark: opslaan en afsluiten",
            key = "opslaan",
            disabled = st.session_state["opslaan_uitgeschakeld"],
            ):
            
            st.session_state["sessie"].opslaan()
            st.session_state["register"].opslaan()
            
            keyboard.press_and_release("ctrl+w")
            pid = os.getpid()
            p = psutil.Process(pid)
            p.terminate()
        
        if top_knop_afbreken.button(
            label = ":heavy_multiplication_x: afbreken en afsluiten",
            key = "afbreken",
            ):
            
            st.session_state["sessie"].opslaan(afgebroken = True)
            st.session_state["register"].opslaan()
            
            keyboard.press_and_release("ctrl+w")
            pid = os.getpid()
            p = psutil.Process(pid)
            p.terminate()