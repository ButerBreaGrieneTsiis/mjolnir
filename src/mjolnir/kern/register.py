from __future__ import annotations
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Tuple
from uuid import uuid4

from grienetsiis.json import openen_json, opslaan_json, Ontcijferaar, Vercijferaar
from grienetsiis.opdrachtprompt import invoeren, kiezen

from .enums import ENUMS


class Singleton(type):
    
    objecten = {}
    
    def __call__(cls, *args, **kwargs):
        if cls not in Singleton.objecten:
            Singleton.objecten[cls] = super().__call__(*args, **kwargs)
        return Singleton.objecten[cls]

class Subregister(dict):
    
    def __init__(self, type):
        self.type = type
    
    def filter(
        self,
        inclusief: bool = True,
        **filters,
        ) -> Subregister | Tuple[str, GeregistreerdObject]:
        
        subregister = Subregister(type = self.type)
        
        for uuid, geregistreerd_object in self.items():
            
            masker = []
            
            for sleutel, waardes in filters.items():
                if isinstance(waardes, list):
                    for waarde in waardes:
                        if getattr(geregistreerd_object, sleutel, None) == waarde:
                            masker.append(True)
                            break
                    else:
                        masker.append(False)
                else:
                    if getattr(geregistreerd_object, sleutel, None) == waardes:
                        masker.append(True)
                    else:
                        masker.append(False)
            
            if inclusief:
                if all(masker):
                    subregister[uuid] = geregistreerd_object
            else:
                if any(masker):
                    subregister[uuid] = geregistreerd_object
        
        return subregister
    
    @property
    def lijst(self) -> List[GeregistreerdObject]:
        return list(self.values())
    
    def nieuw(
        self,
        geef_uuid: bool = True,
        ):
        
        print(f"maak een nieuw {self.type.__name__.lower()}")
        
        basis_type = self.type.nieuw({sleutel: veld for sleutel, veld in self.type.__annotations__.items() if sleutel not in self.type.__dict__})
        
        if geef_uuid:
            return basis_type.uuid
        return basis_type
    
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
        
        keuze_optie = kiezen(
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
    
    TYPES: Dict[str, Dict[str, Any]] = {}
    ONTCIJFERAARS: List[Ontcijferaar] = []
    VERCIJFERAARS: List[Vercijferaar] = []
    ENUMS: Dict[str, Enum] = ENUMS
    
    def __getattr__(self, naam):
        if naam not in self.TYPES:
            raise ValueError(f"onbekend type {naam}")
        
        if naam not in self:
            self[naam] = Subregister(type = self.TYPES[naam])
        return self[naam]
    
    @classmethod
    def openen(cls):
        
        register = cls()
        
        if not cls.BESTANDSMAP.is_dir():
            cls.BESTANDSMAP.mkdir()
        
        GeregistreerdObjectMeta.NIEUW = False
        
        for class_naam, class_dict in cls.TYPES.items():
            
            bestandspad = cls.BESTANDSMAP / f"{class_naam}.{cls.EXTENSIE}"
            
            subregister = Subregister(class_dict["type"])
            
            if bestandspad.is_file():
                
                geregistreerde_objecten = openen_json(
                    bestandspad = bestandspad,
                    ontcijfer_functie_object = class_dict["ontcijferaar"],
                    ontcijfer_functie_subobjecten = cls.ONTCIJFERAARS,
                    ontcijfer_enum = ENUMS,
                    )
                
                for uuid, geregistreerd_object in geregistreerde_objecten.items():
                    
                    geregistreerd_object.uuid = uuid
                    subregister[uuid] = geregistreerd_object
            
            register[class_naam] = subregister
        
        GeregistreerdObjectMeta.NIEUW = True
        
        return register
    
    def opslaan(self) -> None:
        
        for class_naam, class_dict in self.TYPES.items():
            
            bestandspad = self.BESTANDSMAP / f"{class_naam}.{self.EXTENSIE}"
            
            opslaan_json(
                self[class_naam],
                bestandspad,
                vercijfer_functie_object = class_dict["vercijferaar"],
                vercijfer_functie_subobjecten = self.VERCIJFERAARS,
                vercijfer_enum = ENUMS,
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
                waarde = kiezen(
                    beschrijving = veld,
                    keuzes = {enum.value: enum for enum in _type},
                    )
            elif _type in (int, float, str):
                waarde = invoeren(
                    beschrijving = veld,
                    type = _type,
                    )
            else:
                continue
            
            dict[veld] = waarde
        
        return cls(**dict)