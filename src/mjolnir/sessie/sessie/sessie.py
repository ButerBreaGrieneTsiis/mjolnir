"""mjolnir.sessie.sessie"""
from __future__ import annotations
from dataclasses import dataclass
import datetime as dt
import keyboard
import locale
import os
import psutil
from typing import List

from grienetsiis.register import Register
import streamlit as st

from mjolnir.kern.enums import Status
from mjolnir.resultaat import Resultaat
from mjolnir.sessie.sessie import SessieOefening
from mjolnir.sessie.functies import st_horizontaal


locale.setlocale(locale.LC_ALL, "nl_NL.UTF-8")

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
        ) -> Sessie:
        
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
        
        kolom_titel, kolom_knoppen = st.columns([0.5, 0.5], vertical_alignment = "bottom")
        
        with kolom_knoppen:
            with st_horizontaal(uitlijning = "rechts"):
                top_knop_afbreken = st.empty()
                top_knop_opslaan = st.empty()
        
        kolom_titel.header(
            body = f"{Register().schema[self.schema_uuid].naam}, week {self.week} dag {self.dag}",
            anchor = False,
            )
        kolom_titel.subheader(
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