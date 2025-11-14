from pathlib import Path
from typing import Callable, Dict, List

from grienetsiis import Decoder, openen_json, opslaan_json

from .enums import ENUM_DICT


class RegisterType:
    
    REGISTRATIES = {}
    
    BESTANDSMAP: Path = Path("gegevens")
    EXTENSIE: str = "json"
    
    DECODER_FUNCTIE: Callable = None
    DECODER_LIJST: List[Decoder] = None
    
    ENCODER_FUNCTIE: Callable = None
    ENCODER_DICT: Dict[str, str] = None
    
    def __init__(
        self,
        identifier,
        ):
        
        def set_recursively(register, object, identifier, parent = None):
            parent = object.__class__.__bases__[0] if parent is None else parent
            
            if object.__class__ is RegisterType:
                register[identifier] = object
            
            elif parent is RegisterType:
                if not object.__class__.__name__ in register:
                    register[object.__class__.__name__] = {}
                
                register[object.__class__.__name__][identifier] = object
            else:
                set_recursively(register[parent.__name__], object, identifier, parent.__bases__[0])
        
        set_recursively(self.REGISTRATIES, self, identifier)
    
    @classmethod
    def openen(cls) -> "RegisterType":
        
        if not cls.BESTANDSMAP.is_dir():
            cls.BESTANDSMAP.mkdir()
        
        bestandspad = cls.BESTANDSMAP / f"{cls.BESTANDSNAAM}.{cls.EXTENSIE}"
        
        if bestandspad.is_file():
            
            cls.REGISTRATIES = openen_json(
                bestandspad,
                decoder_functie = cls.DECODER_FUNCTIE,
                decoder_lijst = cls.DECODER_LIJST,
                enum_dict = ENUM_DICT,
                )
            
            return cls
        else:
            return cls()
    
    def opslaan(self) -> None:
        bestandspad = self.BESTANDSMAP / f"{self.BESTANDSNAAM}.{self.EXTENSIE}"
        
        opslaan_json(
            self.REGISTRATIES,
            bestandspad,
            encoder_functie = self.ENCODER_FUNCTIE,
            encoder_dict = self.ENCODER_DICT,
            enum_dict = ENUM_DICT,
            )
    
    @property
    def lijst(self) -> List["RegisterType"]:
        return list(self.values())