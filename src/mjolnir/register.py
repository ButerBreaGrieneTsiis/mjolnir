from dataclasses import dataclass
import datetime as dt
from enum import Enum
from pathlib import Path
from typing import Callable, Dict, List
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
    
    @classmethod
    def nieuw(
        cls,
        velden,
        ) -> "GeregistreerdObject":
        
        dict = {}
        
        for veld, type in velden.items():
            if issubclass(type, Enum):
                waarde = invoer_kiezen(
                    beschrijving = veld,
                    keuzes = {choice.value: choice for choice in type},
                    )
            else:
                waarde = invoer_validatie(
                    beschrijving = veld,
                    type = type,
                    )
            dict[veld] = waarde
        
        return cls(**dict)

class Register(dict):
    
    BESTANDSMAP: Path = Path("gegevens")
    EXTENSIE: str = "json"
    
    DECODER_FUNCTIE: str = "van_json"
    DECODER_LIJST: List[Decoder] = None
    
    ENCODER_FUNCTIE: Callable = None
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
            encoder_functie = getattr(self, "ENCODER_FUNCTIE"),
            encoder_dict = self.ENCODER_DICT,
            enum_dict = ENUM_DICT,
            )
    
    @property
    def lijst(self) -> List["Register"]:
        return list(self.values())
    
    def nieuw(self):
        basis_type = self.TYPE.nieuw(self.TYPE.__annotations__)
        id = str(uuid4())
        self[id] = basis_type
        return id
