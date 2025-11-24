from dataclasses import dataclass
import datetime as dt
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List
from uuid import uuid4

from grienetsiis import Decoder, openen_json, opslaan_json, invoer_validatie, invoer_kiezen

from .enums import ENUM_DICT


@dataclass
class GeregistreerdObject:
    
    @classmethod
    def van_json(
        cls,
        **dict,
        ) -> "Register":
        
        if "datum" in dict:
            dict["datum"] = dt.datetime.strptime(dict["datum"], "%Y-%m-%d").date()
        
        return cls(**dict)
    
    def naar_json(self):
        
        dict_naar_json = {}
        
        for veld_sleutel, veld_waarde in self.__dict__.items():
            
            # alle velden uitsluiten die standaardwaardes hebben; nutteloos om op te slaan
            if veld_waarde is None:
                continue
            elif isinstance(veld_waarde, bool) and not veld_waarde:
                continue
            elif isinstance(veld_waarde, list) and len(veld_waarde) == 0:
                continue
            elif isinstance(veld_waarde, dict) and not bool(veld_waarde):
                continue
            elif isinstance(veld_waarde, str) and veld_waarde == "":
                continue
            elif isinstance(veld_waarde, int) and veld_waarde == 0:
                continue
            elif veld_sleutel == "uuid":
                continue
            elif isinstance(veld_waarde, dt.date):
                dict_naar_json[veld_sleutel] = veld_waarde.strftime("%Y-%m-%d")
            else:
                dict_naar_json[veld_sleutel] = veld_waarde
        
        return dict_naar_json
    
    @classmethod
    def nieuw(
        cls,
        velden,
        ) -> "GeregistreerdObject":
        
        dict = {}
        
        for veld, _type in velden.items():
            
            if isinstance(_type, type) and issubclass(_type, Enum):
                waarde = invoer_kiezen(
                    beschrijving = veld,
                    keuzes = {enum.value: enum for enum in _type},
                    )
            elif _type in [int, float, str]:
                waarde = invoer_validatie(
                    beschrijving = veld,
                    type = _type,
                    )
            else:
                continue
            
            dict[veld] = waarde
        
        return cls(**dict)

class Register(dict):
    
    BESTANDSMAP: Path = Path("gegevens")
    EXTENSIE: str = "json"
    
    DECODER_FUNCTIE: str = "van_json"
    DECODER_LIJST: List[Decoder] = None
    
    ENCODER_FUNCTIE: str = "naar_json"
    ENCODER_DICT: Dict[str, str] = None
    
    @classmethod
    def openen(cls) -> "Register":
        
        if not cls.BESTANDSMAP.is_dir():
            cls.BESTANDSMAP.mkdir()
        
        bestandspad = cls.BESTANDSMAP / f"{cls.BESTANDSNAAM}.{cls.EXTENSIE}"
        
        if bestandspad.is_file():
            
            return cls(**openen_json(
                bestandspad,
                decoder_functie = getattr(cls.TYPE, cls.DECODER_FUNCTIE),
                decoder_lijst = cls.DECODER_LIJST,
                enum_dict = ENUM_DICT,
                ))
        else:
            return cls()
    
    def opslaan(self) -> None:
        bestandspad = self.BESTANDSMAP / f"{self.BESTANDSNAAM}.{self.EXTENSIE}"
        
        opslaan_json(
            self,
            bestandspad,
            encoder_functie = getattr(self.TYPE, self.ENCODER_FUNCTIE),
            encoder_dict = self.ENCODER_DICT,
            enum_dict = ENUM_DICT,
            )
    
    def selecteer(
        self,
        veld: str,
        waarde: Any,
        geef_object: bool = True,
        ) -> GeregistreerdObject | None:
        
        for uuid, geregistreerd_object in self.items():
            if getattr(geregistreerd_object, veld, None) == waarde:
                if geef_object:
                    return geregistreerd_object
                else:
                    return uuid
        
        return None
    
    @property
    def lijst(self) -> List["Register"]:
        return list(self.values())
    
    def nieuw(self):
        
        print(f"maak een nieuw {self.TYPE.__name__.lower()}")
        
        basis_type = self.TYPE.nieuw(self.TYPE.__annotations__)
        uuid = str(uuid4())
        
        basis_type.uuid = uuid
        self[uuid] = basis_type
        
        return uuid
    
    def kiezen(self) -> str:
        
        keuze_optie = invoer_kiezen(
            beschrijving = f"{self.TYPE.__name__.lower()}",
            keuzes = {
                f"nieuw {self.TYPE.__name__.lower()}": "nieuw",
            } | {
                f"{geregistreerd_object}": uuid for uuid, geregistreerd_object in self.items()
                },
            )
        
        if keuze_optie == "nieuw":
            uuid = self.nieuw()
        else:
            uuid = keuze_optie
        
        return uuid