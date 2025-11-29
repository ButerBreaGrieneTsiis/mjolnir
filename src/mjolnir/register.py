from __future__ import annotations
from dataclasses import dataclass
import datetime as dt
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List
from uuid import uuid4

from grienetsiis import Decoder, openen_json, opslaan_json, invoer_validatie, invoer_kiezen

from mjolnir.enums import ENUMS


class Singleton(type):
    
    objecten = {}
    
    def __call__(cls, *args, **kwargs):
        if cls not in Singleton.objecten:
            Singleton.objecten[cls] = super().__call__(*args, **kwargs)
        return Singleton.objecten[cls]

@dataclass
class Subregister(dict):
    
    type: type
    
    def selecteren(
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
    def lijst(self) -> List[GeregistreerdObject]:
        return list(self.values())
    
    def nieuw(self):
        
        print(f"maak een nieuw {self.type.__name__.lower()}")
        
        basis_type = self.type.nieuw({sleutel: veld for sleutel, veld in self.type.__annotations__.items() if sleutel not in self.type.__dict__})
        
        return basis_type.uuid
    
    def verwijderen(self):
        
        uuid = self.kiezen(nieuw_toestaan = False)
        del self[uuid]
    
    def kiezen(
        self,
        geef_uuid = True,
        nieuw_toestaan = True,
        ) -> str:
        
        keuzes = {f"{geregistreerd_object}": uuid for uuid, geregistreerd_object in self.items()}
        
        if nieuw_toestaan:
            keuzes = {f"nieuw {self.type.__name__.lower()}": "nieuw"} | keuzes
        
        keuze_optie = invoer_kiezen(
            beschrijving = f"{self.type.__name__.lower()}",
            keuzes = keuzes,
            )
        
        if keuze_optie == "nieuw":
            uuid = self.nieuw()
        else:
            uuid = keuze_optie
        
        if geef_uuid:
            return uuid
        else:
            return self[uuid]

class Register(dict, metaclass = Singleton):
    
    BESTANDSMAP: Path = Path("gegevens")
    EXTENSIE: str = "json"
    
    DECODERS: Dict[str, Callable] = {}
    ENCODERS: Dict[str, Callable] = {}
    ENUMS: Dict[str, Enum] = ENUMS
    
    def __getattr__(self, naam):
        return self[naam]
    
    @classmethod
    def openen(cls):
        
        register = cls()
        
        if not cls.BESTANDSMAP.is_dir():
            cls.BESTANDSMAP.mkdir()
        
        GeregistreerdObjectMeta.NIEUW = False
        
        for class_naam, class_dict in cls.DECODERS.items():
            
            bestandspad = cls.BESTANDSMAP / f"{class_naam}.{cls.EXTENSIE}"
            
            if not bestandspad.is_file():
                continue
            
            geregistreerde_objecten = openen_json(
                bestandspad = bestandspad,
                decoder_functie = class_dict["decoder_functie"],
                # decoder_lijst = cls.DECODER_LIJST,
                enum_dict = ENUMS,
                )
            
            subregister = Subregister(class_dict["class"])
            
            for uuid, geregistreerd_object in geregistreerde_objecten.items():
                
                geregistreerd_object.uuid = uuid
                subregister[uuid] = geregistreerd_object
            
            register[class_naam] = subregister
        
        GeregistreerdObjectMeta.NIEUW = True
        
        return register
    
    def opslaan(self) -> None:
        
        for class_naam, class_dict in Register.ENCODERS.items():
            
            bestandspad = self.BESTANDSMAP / f"{class_naam}.{self.EXTENSIE}"
            
            opslaan_json(
                self[class_naam],
                bestandspad,
                encoder_functie = class_dict["encoder_functie"],
                # encoder_dict = self.ENCODER_DICT,
                enum_dict = ENUMS,
                )

class GeregistreerdObjectMeta(type):
    
    NIEUW: bool = True
    
    def __call__(self, *args, **kwargs):
        instantie = super().__call__(*args, **kwargs)
        
        if GeregistreerdObjectMeta.NIEUW:
            
            instantie.uuid = str(uuid4())
            
            sleutel = instantie.BESTANDSNAAM
            
            if sleutel not in Register():
                Register()[sleutel] = Subregister()
            
            Register()[sleutel][instantie.uuid] = instantie
        
        return instantie

class GeregistreerdObject(metaclass = GeregistreerdObjectMeta):
    
    @classmethod
    def van_json(
        cls,
        **dict,
        ) -> GeregistreerdObject:
        
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
        ) -> GeregistreerdObject:
        
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