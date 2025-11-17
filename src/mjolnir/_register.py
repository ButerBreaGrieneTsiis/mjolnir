import datetime as dt
from pathlib import Path
from typing import Callable, Dict, List
from uuid import uuid4

from grienetsiis import Decoder, openen_json, opslaan_json, invoer_validatie

from .enums import ENUM_DICT


class BasisType:
    
    # def __init__(
    #     self,
    #     id = None,
    #     ):
        
    #     def krijg_ouder(kind):
    #         for ouder in kind.__bases__:
    #             if hasattr(ouder, "REGISTRATIES"):
    #                 return ouder
    #         else:
    #             return None
        
    #     if self.__class__ is Register:
    #         return self
        
    #     self.id = str(uuid4()) if id is None else id
        
    #     generaties = []
    #     _self = self.__class__
    #     ouder = krijg_ouder(_self)
        
    #     while self.REGISTRATIES is getattr(ouder, "REGISTRATIES", None):
            
    #         generaties.append(_self.__name__)
    #         _self = krijg_ouder(_self)
    #         ouder = krijg_ouder(_self)
        
    #     generaties = list(reversed(generaties))
        
    #     if not generaties:
    #         self.REGISTRATIES[self.id] = self
    #     else:
    #         sub_registraties = self.REGISTRATIES
    #         for kind in generaties[:-1]:
    #             sub_registraties = sub_registraties.setdefault(kind, {})
    #         if generaties[-1] not in sub_registraties:
    #             sub_registraties[generaties[-1]] = {}
    #         sub_registraties[generaties[-1]][self.id] = self
    
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
        ) -> "BasisType":
        
        dict = {}
        
        for veld, type in velden.items():
            waarde = invoer_validatie(veld, type)
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
        basis_type = self.TYPE.nieuw(self.TYPE.VELDEN)
        id = str(uuid4())
        self[id] = basis_type
        return self
