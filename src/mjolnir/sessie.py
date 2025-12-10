from copy import copy
from dataclasses import dataclass
import datetime as dt
import keyboard
import os
from pathlib import Path
import psutil
from typing import Any, Dict, List, Tuple

from grienetsiis import opslaan_json
import streamlit as st

from mjolnir.belading import Halter
from mjolnir.enums import OefeningEnum, OefeningLichaamsgewicht, OefeningBarbell, OefeningCurl, OefeningDumbbell, GewichtType, RepetitieType, SetType, SetGroepType, Status, ENUMS, HALTERS
from mjolnir.register import Register


@dataclass
class Set:
    
    setcode: str
    
    oefening: OefeningEnum
    set_nummer: int
    
    set_type: SetType
    
    repetitie_type: RepetitieType
    repetitie_aantal: int | Tuple[int, int]
    
    gewicht_type: GewichtType
    gewicht: float | None
    halter: Halter | None = None
    
    afgerond: bool = False
    repetitie_gedaan: int = 0
    gewicht_gedaan: float = 0.0
    
    @classmethod
    def van_setcode(
        cls,
        setcode: str,
        set_nummer: int,
        oefening: OefeningEnum,
        trainingsgewichten,
        ):
        
        set_type, set_aantal = cls.sets_uit_setcode(setcode)
        repetitie_type, repetitie_aantal = cls.repetities_uit_setcode(setcode)
        gewicht_type, gewicht = cls.gewicht_uit_setcode(setcode, trainingsgewichten, oefening)
        
        return cls(
            setcode = setcode,
            oefening = oefening,
            set_nummer = set_nummer,
            set_type = set_type,
            repetitie_type = repetitie_type,
            repetitie_aantal = repetitie_aantal,
            gewicht_type = gewicht_type,
            gewicht = gewicht,
            )
    
    @property
    def repetitie_tekst(self) -> str:
        if "x" in self.setcode:
            return self.setcode.split("x")[1].split("@")[0]
        else:
            return self.setcode.split("@")[0]
    
    @staticmethod
    def sets_uit_setcode(setcode: str) -> Tuple[SetType, int]:
        
        if "x" in setcode:
            _set_aantal = setcode.split("x")[0]
        else:
            _set_aantal = "1"
        
        if "?" in _set_aantal:
            set_type = SetType.VRIJ
            set_aantal = 0
        elif "+" in _set_aantal:
            set_type = SetType.AMSAP
            set_aantal = int(_set_aantal.replace("+", ""))
        else:
            set_type = SetType.AANTAL
            set_aantal = int(_set_aantal)
        
        return set_type, set_aantal
    
    @staticmethod
    def repetities_uit_setcode(setcode: str) -> Tuple[RepetitieType, int]:
        
        if "x" in setcode:
            _repetitie_aantal = setcode.split("x")[1].split("@")[0]
        else:
            _repetitie_aantal = setcode.split("@")[0]
        
        if "?" in _repetitie_aantal:
            repetitie_type = RepetitieType.VRIJ
            repetitie_aantal = 0
        elif "-" in _repetitie_aantal and "+" in _repetitie_aantal:
            repetitie_type = RepetitieType.BEREIK_AMRAP
            repetitie_aantal = (int(_repetitie_aantal.split("-")[0]), int(_repetitie_aantal.split("-")[1].replace("+", "")))
        elif "-" in _repetitie_aantal:
            repetitie_type = RepetitieType.BEREIK
            repetitie_aantal = (int(_repetitie_aantal.split("-")[0]), int(_repetitie_aantal.split("-")[1]))
        elif "+" in _repetitie_aantal:
            repetitie_type = RepetitieType.AMRAP
            repetitie_aantal = int(_repetitie_aantal.replace("+", ""))
        else:
            repetitie_type = RepetitieType.AANTAL
            repetitie_aantal = int(_repetitie_aantal)
        
        return repetitie_type, repetitie_aantal
    
    @staticmethod
    def gewicht_uit_setcode(setcode: str, trainingsgewichten, oefening) -> Tuple[GewichtType, int]:
        
        if "@" in setcode:
            _gewicht_aantal = setcode.split("@")[1]
        else:
            _gewicht_aantal = ""
        
        if "?" in _gewicht_aantal:
            gewicht_type = GewichtType.VRIJ
            gewicht = None
        elif "%" in _gewicht_aantal:
            gewicht_type = GewichtType.PERCENTAGE
            trainingsgewicht = next(trainingsgewicht_dict["trainingsgewicht"] for trainingsgewicht_dict in trainingsgewichten if trainingsgewicht_dict["oefening"] == oefening)
            gewicht = int(_gewicht_aantal.replace("%", "")) / 100 * trainingsgewicht
        elif _gewicht_aantal == "":
            gewicht_type = GewichtType.GEWICHTLOOS
            gewicht = None
        else:
            gewicht_type = GewichtType.GEWICHT
            gewicht = int(_gewicht_aantal)
        
        return gewicht_type, gewicht
        
    def paneel(
        self,
        kolom,
        ):
        
        if self.repetitie_type == RepetitieType.AANTAL:
            max_repetities = self.repetitie_aantal
            aantal_repetities = self.repetitie_aantal
        elif self.repetitie_type == RepetitieType.BEREIK:
            max_repetities = self.repetitie_aantal[1]
            aantal_repetities = self.repetitie_aantal[1]
        else:
            max_repetities = 10
            if self.repetitie_type == RepetitieType.BEREIK_AMRAP:
                aantal_repetities = self.repetitie_aantal[1]
            else:
                aantal_repetities = self.repetitie_aantal
        
        oefening = self.oefening.value[0].replace(" ", "_")
        
        # status expander van deze set
        if f"expander_{oefening}_{self.set_nummer}" not in st.session_state:
            st.session_state[f"expander_{oefening}_{self.set_nummer}"] = True
        
        # status expander van de volgende set
        if f"expander_{oefening}_{self.set_nummer + 1}" not in st.session_state:
            st.session_state[f"expander_{oefening}_{self.set_nummer + 1}"] = False
        
        # aantal repetities van deze set
        if f"repetities_{oefening}_{self.set_nummer}" not in st.session_state:
            st.session_state[f"repetities_{oefening}_{self.set_nummer}"] = aantal_repetities
        
        if f"knop_{oefening}_{self.set_nummer}" in st.session_state:
            if st.session_state[f"knop_{oefening}_{self.set_nummer}"]:
                
                self.repetitie_gedaan = st.session_state[f"repetities_{oefening}_{self.set_nummer}"]
                
                if self.oefening.__class__ in [OefeningBarbell, OefeningCurl, OefeningDumbbell]: 
                    if self.halter is not None:
                        self.gewicht_gedaan = self.halter.massa
                elif self.gewicht_type != GewichtType.GEWICHTLOOS:
                    raise NotImplementedError
                
                self.afgerond = True
                
                st.session_state[f"expander_{oefening}_{self.set_nummer}"] = False
                st.session_state[f"expander_{oefening}_{self.set_nummer + 1}"] = True
        
        if f"label_{oefening}_{self.set_nummer}" not in st.session_state:
            st.session_state[f"label_{oefening}_{self.set_nummer}"] = f"set {self.set_nummer}: {self.setcode}"
        else:
            if self.afgerond:
                st.session_state[f"label_{oefening}_{self.set_nummer}"] = f":white_check_mark: set {self.set_nummer}: {self.setcode}"
        
        expander = kolom.expander(
            label = st.session_state[f"label_{oefening}_{self.set_nummer}"],
            expanded = st.session_state[f"expander_{oefening}_{self.set_nummer}"],
            )
        
        kolom_repetities, kolom_gewicht, kolom_halter = expander.columns([0.2, 0.2, 0.6])
        
        kolom_repetities.markdown("**repetities**")
        kolom_repetities.markdown(f"{self.repetitie_tekst} ({self.repetitie_type.value})")
        
        if self.gewicht_type == GewichtType.GEWICHT or self.gewicht_type == GewichtType.PERCENTAGE:
            kolom_gewicht.markdown("**gewicht**")
            kolom_gewicht.markdown(f"{f"{self.halter.massa}".replace(".", ",")} kg")
        
        if self.oefening.__class__ in [OefeningBarbell, OefeningCurl, OefeningDumbbell]:
            kolom_halter.markdown("**halter**")
            kolom_halter.markdown(self.halter)
        
        expander.slider(
            label = "repetities",
            min_value = 0,
            max_value = max_repetities,
            key = f"repetities_{oefening}_{self.set_nummer}",
            label_visibility = "hidden",
            )
        
        expander.button(
            label = "afronden",
            key = f"knop_{oefening}_{self.set_nummer}",
            )
        
        return expander
    
    @property
    def volume(self) -> float | None:
        if self.gewicht_type == GewichtType.GEWICHTLOOS:
            return None
        else:
            return self.gewicht_gedaan * self.repetitie_gedaan
    
    @property
    def e1rm(self) -> float | None:
        if self.gewicht_type == GewichtType.GEWICHTLOOS:
            return None
        else:
            return self.gewicht_gedaan * (1 + self.repetitie_gedaan/30)

@dataclass
class SetKnop:
    
    oefening: "Oefening"
    setgroep: str
    set: Set
    set_nummer: int
    
    def toevoegen_set(self):
        
        self.set_nummer += 1
        
        set = copy(self.set)
        set.set_nummer = self.set_nummer
        
        self.oefening.sets[self.setgroep].append(set)
    
    def paneel(
        self,
        kolom,
        ):
        
        oefening = self.oefening.oefening.value[0].replace(" ", "_")
        
        kolom.button(
            label = "set toevoegen",
            key = f"setknop_{oefening}_{self.setgroep}",
            on_click = self.toevoegen_set,
            )

@dataclass
class Oefening:
    
    oefening: OefeningEnum
    sets: Dict[str, List[Set]]
    setknoppen: Dict[str, SetKnop] = None
    trainingsgewicht: float = None
    
    def __post_init__(self):
        
        oefening_type = self.oefening.__class__
        
        if oefening_type in [OefeningBarbell, OefeningCurl, OefeningDumbbell]:
            
            halterstangen = Register().halterstangen.filter(halter_type = HALTERS[self.oefening.__class__.__name__])
            
            if len(halterstangen) == 1:
                halterstang = list(halterstangen.values())[0]
                halterschijven = list(Register().halterschijven.filter(diameter = halterstang.diameter).values())
            else:
                raise NotImplementedError("momenteel wordt maximaal één halterstang ondersteund per halter_type")
            
            gewichten = [set.gewicht for setgroep in self.sets.values() for set in setgroep if set.gewicht is not None]
            
            if len(gewichten) > 0:
                
                halters = halterstang.optimaal_laden(
                    gewicht_per_set = gewichten,
                    halterschijven = halterschijven,
                    )
                
                for set, halter in zip([set for setgroep in self.sets.values() for set in setgroep], halters):
                    set.halter = halter
        
        else:
            halter = None
        
        setknoppen = {}
        
        for setgroep, sets in self.sets.items():
            
            if len(sets) == 1 and sets[0].set_type in [SetType.AMSAP, SetType.VRIJ]:
                
                setknop = SetKnop(
                    oefening = self,
                    setgroep = setgroep,
                    set = sets[0],
                    set_nummer = sets[0].set_nummer,
                    )
                
                setknoppen[setgroep] = setknop
        
        self.setknoppen = setknoppen
    
    @classmethod
    def nieuw(
        cls,
        oefening: OefeningEnum,
        sjablonen: List[str],
        week: int,
        trainingsgewichten: List[Dict[str, Any]],
        ):
        
        sets = {}
        
        set_nummer = 0
        
        for sjabloon_uuid in sjablonen:
            
            sjabloon = Register().sjablonen[sjabloon_uuid]
            
            if sjabloon.weken == 0:
                setcodes = sjabloon.sets["week 0"]
            else:
                setcodes = sjabloon.sets[f"week {week}"]
            
            for setcode in setcodes:
                
                set_type, set_aantal = Set.sets_uit_setcode(setcode)
                
                if sjabloon.setgroep_type.value not in sets:
                    sets[sjabloon.setgroep_type.value] = []
                
                if set_type == SetType.AANTAL or set_type == SetType.AMSAP:
                    for _ in range(set_aantal):
                    
                        set_nummer += 1
                        
                        set = Set.van_setcode(
                            setcode = setcode,
                            set_nummer = set_nummer,
                            oefening = oefening,
                            trainingsgewichten = trainingsgewichten,
                            )
                        
                        sets[sjabloon.setgroep_type.value].append(set)
                else:
                    set_nummer += 1
                    
                    set = Set.van_setcode(
                        setcode = setcode,
                        set_nummer = set_nummer,
                        oefening = oefening,
                        trainingsgewichten = trainingsgewichten,
                        )
                    
                    sets[sjabloon.setgroep_type.value].append(set)
        
        trainingsgewicht = next((trainingsgewicht_dict["trainingsgewicht"] for trainingsgewicht_dict in trainingsgewichten if trainingsgewicht_dict["oefening"] == oefening), None)
        
        return cls(
            oefening = oefening,
            sets = sets,
            trainingsgewicht = trainingsgewicht,
            )
    
    @property
    def hoofdoefening(self) -> bool:
        return SetGroepType.OVERIG.value not in self.sets
    
    @property
    def volume(self) -> float | None:
        if self.oefening.__class__ == OefeningLichaamsgewicht:
            return None
        else:
            return sum(set.volume for setgroep in self.sets.values() for set in setgroep)
    
    @property
    def e1rm(self) -> float | None:
        if self.oefening.__class__ == OefeningLichaamsgewicht:
            return None
        else:
            return max(set.e1rm for setgroep in self.sets.values() for set in setgroep)
    
    @property
    def titel(self) -> str:
        
        if self.volume is None and self.e1rm is None:
            return f"{self.oefening.value[0].upper()}"
        
        if self.trainingsgewicht is None:
            return f"{self.oefening.value[0].upper()} (volume: {self.volume:.1f} kg, e1rm: {self.e1rm:.1f} kg)"
        else:
            return f"{self.oefening.value[0].upper()} (TM: {self.trainingsgewicht:.1f} kg, volume: {self.volume:.1f} kg, e1rm: {self.e1rm:.1f} kg)"
    
    def paneel(
        self,
        kolom,
        ):
        
        titel = kolom.empty()
        for setgroep, sets in self.sets.items():
            if self.hoofdoefening:
                kolom.write(setgroep)
            for set in sets:
                
                set.paneel(kolom)
            
            if setgroep in self.setknoppen:
                self.setknoppen[setgroep].paneel(kolom)
            
        titel.write(self.titel)

@dataclass
class Sessie:
    
    schema_uuid: str
    week: int
    dag: int
    datum: dt.date
    oefeningen: List[Oefening]
    
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
        
        oefeningen = []
        trainingsschema = schema.oefeningen[f"dag {dag}"]
        
        for oefening_dict in trainingsschema:
            
            oefening = Oefening.nieuw(
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
            datum = dt.date.today(),
            oefeningen = oefeningen,
            )
    
    def opslaan(self) -> None:
        
        schema = Register().schema[self.schema_uuid]
        
        schema.sessies[f"week {self.week}"][f"dag {self.dag}"]["status"] = Status.AFGEROND
        schema.sessies[f"week {self.week}"][f"dag {self.dag}"]["datum"] = self.datum
        
        if schema.datum_begin is None:
            schema.datum_begin = self.datum
        
        if all([dag["status"] != Status.GEPLAND for week in schema.sessies.values() for dag in week.values()]):
            schema.datum_eind = self.datum
            schema.status = Status.AFGEROND
        
        bestandspad = Path(f"gegevens\\sessies\\{self.datum.strftime("%Y-%m-%d")}.json")
        
        sessie = {
            "schema_uuid": self.schema_uuid,
            "week": self.week,
            "dag": self.dag,
            "datum": self.datum.strftime("%Y-%m-%d"),
            "resultaten": self.resultaten,
            }
        
        opslaan_json(
            sessie,
            bestandspad,
            enum_dict = ENUMS,
            )
    
    @property
    def resultaten(self):
        
        resultaten = []
        
        for oefening in self.oefeningen:
            
            oefening_dict = {
                "oefening": oefening.oefening,
                "sets": [],
                }
            
            for sets in oefening.sets.values():
                for set in sets:
                    if set.gewicht_type == GewichtType.GEWICHTLOOS:
                        oefening_dict["sets"].append({
                            "repetities": set.repetitie_gedaan,
                            })
                    else:
                        oefening_dict["sets"].append({
                            "repetities": set.repetitie_gedaan,
                            "gewicht": set.gewicht_gedaan,
                            })
            
            resultaten.append(oefening_dict)
        
        return resultaten
    
    def paneel(self):
        
        top = st.empty()
        
        aantal_hoofdoefeningen = sum(oefening.hoofdoefening for oefening in self.oefeningen)
        kolommen = st.columns(aantal_hoofdoefeningen + 1)
        
        kolommen[-1].write("AANVULLENDE OEFENINGEN")
        
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
            st.session_state["opslaan_uitgeschakeld"] = not all(set.afgerond for oefening in self.oefeningen for setgroep in oefening.sets.values() for set in setgroep)
        
        if "volledig_scherm" not in st.session_state:
            st.session_state["volledig_scherm"] = True
            keyboard.press_and_release("f11")
        
        if top.button(
            label = "opslaan en afsluiten",
            key = "opslaan",
            disabled = st.session_state["opslaan_uitgeschakeld"],
            ):
            
            st.session_state["sessie"].opslaan()
            st.session_state["register"].opslaan()
            
            keyboard.press_and_release("ctrl+w")
            pid = os.getpid()
            p = psutil.Process(pid)
            p.terminate()