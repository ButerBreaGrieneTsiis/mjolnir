from dataclasses import dataclass
import datetime as dt
from typing import Any, Dict, List, Tuple

import streamlit as st

from mjolnir.belading import Halter
from mjolnir.enums import OefeningEnum, OefeningBarbell, OefeningCurl, OefeningDumbbell, GewichtType, RepetitieType, SetType, Status, HALTERS
from mjolnir.register import Register
from mjolnir.schema import Sjabloon


@dataclass
class Set:
    
    code: str
    
    set_type: SetType
    set_aantal: int | Tuple[int, int]
    
    repetitie_type: RepetitieType
    repetitie_aantal: int | Tuple[int, int]
    
    gewicht_type: GewichtType
    gewicht: float | None
    
    halter: Halter | None
    
    set_gedaan: int = 0
    repetitie_gedaan: int = 0
    gewicht_gedaan: float = 0.0
    
    @classmethod
    def van_setcode(
        cls,
        code: str,
        oefening: OefeningEnum,
        trainingsgewichten,
        ):
        
        oefening_type = oefening.__class__
        
        if "x" in code:
            _set_aantal = code.split("x")[0]
            _repetitie_aantal = code.split("x")[1].split("@")[0]
            _gewicht_aantal = code.split("@")[1]
        else:
            _set_aantal = "1"
            _repetitie_aantal = code.split("@")[0]
            _gewicht_aantal = code.split("@")[1]
        
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
            code = code,
            set_type = set_type,
            set_aantal = set_aantal,
            repetitie_type = repetitie_type,
            repetitie_aantal = repetitie_aantal,
            gewicht_type = gewicht_type,
            gewicht = gewicht,
            halter = halter,
            )
    
    @property
    def paneel(self):
        
        container = st.container()
        container.write(self.code)
        
        return container
        
        
    # @property
    # def volume(self) -> float:
    #     ...

@dataclass
class Oefening:
    
    oefening: OefeningEnum
    sets: Dict[str, List[Set]] # waar str = SetGroepType.value
    
    @classmethod
    def nieuw(
        cls,
        oefening: OefeningEnum,
        sjablonen: List[str],
        week: int,
        trainingsgewichten: List[Dict[str, Any]],
        ):
        
        sets = {}
        
        for sjabloon_uuid in sjablonen:
            
            sjabloon = Register().sjablonen[sjabloon_uuid]
            
            if sjabloon.weken == 0:
                setcodes = sjabloon.sets["week 0"]
            else:
                setcodes = sjabloon.sets[f"week {week}"]
            
            for setcode in setcodes:
                
                set = Set.van_setcode(
                    code = setcode,
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

@dataclass
class Sessie:
    
    schema_uuid: str
    week: int
    dag: int
    datum: dt.date
    oefeningen: List[Oefening]
    resultaten = None
    
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
        
        # Register().opslaan() -> ergens anders runnen
        
        # zichzelf opslaan
        # alles opslaan behalve Sessie.oefening
        # focus ligt op Sessie.resultaten
        
        # resultaten -> naar alle Set objecten en *_gedaan pakken
        
        
        
        ...
        # opslaan van deze sessie na afronden dashboard
        # schema_uuid:
        # week:
        # dag:
        # datum:
        # oefeningen:
        #   oefening 1:
        #     OefeningEnum
        #     setgroep 1: (ook al is er geen setgroep, bijv. bij assistance, alsnog setgroep "overig")
        #       set 1:
        #         repetities: int # enkel repetities gedaan, repetities gepland volgt wel uit schema_uuid
        #         (gewicht: float) indien toepasselijk # enkel gewicht gedaan, gewicht gepland volgt wel uit schema_uuid
        #       set 2: # enkel sets gedaan, sets gepland volgt wel uit schema_uuid
        #       :
        #     setgroep 2:
        #     :
        #   oefening 2:
        #   :
        #
        
        
        # koppeling van de HalterType vindt op de achtergrond plaats:
        # oefening is gelinkt aan een HalterType
        # indien meerdere HalterTypes gedefinieerd zijn, is op het dashboard een keuze te maken (voor nu nog niet nodig om te implementeren)