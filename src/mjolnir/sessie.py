from dataclasses import dataclass
import datetime as dt
from pathlib import Path
from typing import Any, Dict, List, Tuple

from grienetsiis import opslaan_json
import streamlit as st

from mjolnir.belading import Halter
from mjolnir.enums import OefeningEnum, OefeningBarbell, OefeningCurl, OefeningDumbbell, GewichtType, RepetitieType, SetType, Status, ENUMS, HALTERS
from mjolnir.register import Register


@dataclass
class Set:
    
    setcode: str
    
    oefening: OefeningEnum
    set_nummer: int
    
    set_type: SetType
    set_aantal: int
    
    repetitie_type: RepetitieType
    repetitie_aantal: int | Tuple[int, int]
    
    gewicht_type: GewichtType
    gewicht: float | None
    
    halter: Halter | None
    
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
        
        oefening_type = oefening.__class__
        
        set_type, set_aantal = cls.sets_uit_setcode(setcode)
        repetitie_type, repetitie_aantal = cls.repetities_uit_setcode(setcode)
        gewicht_type, gewicht = cls.gewicht_uit_setcode(setcode, trainingsgewichten, oefening)
        
        if oefening_type in [OefeningBarbell, OefeningCurl, OefeningDumbbell] and gewicht is not None:
            
            halterstangen = Register().halterstangen.filter(halter_type = HALTERS[oefening.__class__.__name__])
            
            if len(halterstangen) == 1:
                halterstang = list(halterstangen.values())[0]
                halterschijven = list(Register().halterschijven.filter(diameter = halterstang.diameter).values())
            else:
                raise NotImplementedError
            
            halter = halterstang.laden(
                haltermassa = gewicht,
                halterschijven = halterschijven,
                )
        else:
            halter = None
        
        return cls(
            setcode = setcode,
            oefening = oefening,
            set_nummer = set_nummer,
            set_type = set_type,
            set_aantal = set_aantal,
            repetitie_type = repetitie_type,
            repetitie_aantal = repetitie_aantal,
            gewicht_type = gewicht_type,
            gewicht = gewicht,
            halter = halter,
            )
    
    @staticmethod
    def sets_uit_setcode(setcode: str) -> Tuple[SetType, int]:
        
        if "x" in setcode:
            _set_aantal = setcode.split("x")[0]
        else:
            _set_aantal = "1"
        
        if "?" in _set_aantal:
            set_type = SetType.VRIJ
            set_aantal = -1
        elif "-" in _set_aantal and "+" in _set_aantal:
            set_type = SetType.BEREIK_AMSAP
            set_aantal = (int(_set_aantal.split("-")[0]), int(_set_aantal.split("-").replace("+", "")[1]))
        elif "-" in _set_aantal:
            set_type = SetType.BEREIK
            set_aantal = (int(_set_aantal.split("-")[0]), int(_set_aantal.split("-")[1]))
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
            repetitie_aantal = -1
        elif "-" in _repetitie_aantal and "+" in _repetitie_aantal:
            repetitie_type = RepetitieType.BEREIK_AMRAP
            repetitie_aantal = (int(_repetitie_aantal.split("-")[0]), int(_repetitie_aantal.split("-").replace("+", "")[1]))
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
        
        if "x" in setcode:
            _gewicht_aantal = setcode.split("@")[1]
        else:
            _gewicht_aantal = setcode.split("@")[1]
        
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
        
    def paneel(self):
        
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
        
        if f"expander_{oefening}_{self.set_nummer}" not in st.session_state:
            st.session_state[f"expander_{oefening}_{self.set_nummer}"] = True
        if f"expander_{oefening}_{self.set_nummer + 1}" not in st.session_state:
            st.session_state[f"expander_{oefening}_{self.set_nummer + 1}"] = False
        
        if f"repetities_{oefening}_{self.set_nummer}" not in st.session_state:
            st.session_state[f"repetities_{oefening}_{self.set_nummer}"] = aantal_repetities
        
        if f"knop_{oefening}_{self.set_nummer}" in st.session_state:
            if st.session_state[f"knop_{oefening}_{self.set_nummer}"]:
                self.repetitie_gedaan = st.session_state[f"repetities_{oefening}_{self.set_nummer}"]
                self.gewicht_gedaan = self.halter.massa
                st.session_state[f"expander_{oefening}_{self.set_nummer}"] = False
                st.session_state[f"expander_{oefening}_{self.set_nummer + 1}"] = True
        
        expander = st.expander(
            label = f"set {self.set_nummer} ({self.setcode})",
            expanded = st.session_state[f"expander_{oefening}_{self.set_nummer}"],
            )
        
        kolom1, kolom2, kolom3 = expander.columns(3)
        
        kolom1.markdown("**repetities**")
        kolom1.markdown(f"{self.repetitie_aantal} ({self.repetitie_type.value})")
        # TODO veranderen naar: "5", "5+", "3-5", "3-5+" of "vrij"
        
        kolom2.markdown("**gewicht**")
        kolom2.markdown(f"{f"{self.halter.massa}".replace(".", ",")} kg")
        
        kolom3.markdown("**halter**")
        kolom3.markdown(self.halter)
        
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
        
        
    # @property
    # def volume(self) -> float:
    #     ...

@dataclass
class Oefening:
    
    oefening: OefeningEnum
    sets: Dict[str, List[Set]]
    
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
                
                _, set_aantal = Set.sets_uit_setcode(setcode)
                
                for _ in range(set_aantal):
                
                    set_nummer += 1
                    
                    set = Set.van_setcode(
                        setcode = setcode,
                        set_nummer = set_nummer,
                        oefening = oefening,
                        trainingsgewichten = trainingsgewichten,
                        )
                    
                    if sjabloon.setgroep_type.value not in sets:
                        sets[sjabloon.setgroep_type.value] = []
                    
                    sets[sjabloon.setgroep_type.value].append(set)
        
        return cls(
            oefening = oefening,
            sets = sets,
            )
    
    @property
    def volume(self) -> float:
        ...
    
    def paneel(self):
        
        st.write(self.oefening.value[0].upper())
        for setgroep, sets in self.sets.items():
            st.write(setgroep)
            for set in sets:
                set.paneel()

@dataclass
class Sessie:
    
    schema_uuid: str
    week: int
    dag: int
    datum: dt.date
    oefeningen: List[Oefening]
    
    @classmethod
    def huidig(cls):
        
        schemas = Register().schema.filter(status = Status.HUIDIG)
        
        schema_uuid = list(schemas.keys())[0]
        schema = list(schemas.values())[0]
        
        for week_tekst, sessie_week in schema.sessies.items():
            for dag_tekst, sessie_dag in sessie_week.items():
                if sessie_dag["status"] == Status.GEPLAND:
                    week = int(week_tekst.replace("week", "").strip())
                    dag = int(dag_tekst.replace("dag", "").strip())
                    break
            else:
                continue
            break
        else:
            raise RuntimeError("geen geplande sessies staan")
        
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
        
        bestandspad = Path(f"gegevens\\{self.datum.strftime("%Y-%m-%d")}.json")
        
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
            
            for setgroep, sets in oefening.sets.items():
                for set in sets:
                    oefening_dict["sets"].append({
                        "repetities": set.repetitie_gedaan,
                        "gewicht": set.gewicht_gedaan,
                        })
            
            resultaten.append(oefening_dict)
        
        return resultaten