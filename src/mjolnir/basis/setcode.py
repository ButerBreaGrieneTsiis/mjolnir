from typing import Dict, Tuple

from grienetsiis import Decoder, Encoder

from .constantes import *
from .enums import GewichtType, RepetitieType, SetType
from .register import Register


class Setcode:
    
    def __init__(
        self,
        set_type: SetType = SetType.AANTAL,
        repetitie_type: RepetitieType = RepetitieType.AANTAL,
        gewicht_type: GewichtType = GewichtType.PERCENTAGE,
        set_aantal: int = 1,
        repetitie_aantal: int = 5,
        repetitie_maximaal: int = REPETITIE_AANTAL_MAX,
        gewicht_aantal: float | int | None = 100,
        ) -> "Setcode":
        
        self.set_type = set_type
        self.repetitie_type = repetitie_type
        self.gewicht_type = gewicht_type
        self.set_aantal = set_aantal
        self.repetitie_aantal = repetitie_aantal
        self.repetitie_maximaal = repetitie_maximaal
        self.gewicht_aantal = gewicht_aantal
    
    def __repr__(self) -> str:
        return self.tekst
    
    def __str__(self) -> str:
        return self.tekst
    
    @classmethod
    def van_tekst(
        cls,
        tekst: str,
        ) -> "Setcode":
        
        setcode = cls()
        setcode.tekst = tekst
        
        return setcode
    
    @classmethod
    def van_json(
        cls,
        **dict,
        ) -> "Setcode":
        
        return cls.van_tekst(dict["__setcode__"])
    
    def naar_json(self) -> Dict[str, str]:
        return {"__setcode__": self.tekst}
    
    @property
    def tekst(self) -> str:
        
        if self.set_type == SetType.VRIJ:
            set_tekst = "?"
        elif self.set_type == SetType.AANTAL:
            set_tekst = f"{self.set_aantal}"
        else:
            set_tekst = f"{self.set_aantal}+"
        
        if self.repetitie_type == RepetitieType.VRIJ:
            repetitie_tekst = "?"
        elif self.repetitie_type == RepetitieType.AANTAL:
            repetitie_tekst = f"{self.repetitie_aantal}"
        elif self.repetitie_type == RepetitieType.AMRAP:
            repetitie_tekst = f"{self.repetitie_aantal}+"
        elif self.repetitie_type == RepetitieType.BEREIK:
            repetitie_tekst = f"{self.repetitie_aantal}-{self.repetitie_maximaal}"
        else:
            repetitie_tekst = f"{self.repetitie_aantal}-{self.repetitie_maximaal}+"
        
        if self.gewicht_type == GewichtType.GEWICHTLOOS:
            if set_tekst == "1":
                return f"{repetitie_tekst}"
            return f"{set_tekst}x{repetitie_tekst}"
        elif self.gewicht_type == GewichtType.VRIJ:
            gewicht_tekst = "?"
        elif self.gewicht_type == GewichtType.GEWICHT:
            gewicht_tekst = f"{self.gewicht_aantal}"
        else:
            gewicht_tekst = f"{self.gewicht_aantal:.0f}%"
        
        if set_tekst == "1":
            return f"{repetitie_tekst}@{gewicht_tekst}"
        return f"{set_tekst}x{repetitie_tekst}@{gewicht_tekst}"
    
    @tekst.setter
    def tekst(self, tekst: str):
        
        _set_aantal, _set_type = self._sets_set_type(tekst)
        _repetitie_aantal, _repetitie_maximaal, _repetitie_type = self._repetities_repetitie_type(tekst)
        _gewicht_aantal, _gewicht_type = self._gewicht_gewicht_type(tekst)
        
        self._set_aantal = _set_aantal
        self._set_type = _set_type
        self._repetitie_aantal = _repetitie_aantal
        self._repetitie_maximaal = _repetitie_maximaal
        self._repetitie_type = _repetitie_type
        self._gewicht_aantal = _gewicht_aantal
        self._gewicht_type = _gewicht_type
    
    @staticmethod
    def _setcode_van_waardes(
        set_type: SetType,
        repetitie_type: RepetitieType,
        gewicht_type: GewichtType,
        set_aantal: int | None,
        repetitie_aantal: int | None,
        repetitie_maximaal: int,
        gewicht_aantal: float,
        ) -> str:
        
        if set_type == SetType.VRIJ:
            set_tekst = "?"
        elif set_type == SetType.AANTAL:
            set_tekst = f"{set_aantal}"
        else:
            set_tekst = f"{set_aantal}+"
        
        if repetitie_type == RepetitieType.VRIJ:
            repetitie_tekst = "?"
        elif repetitie_type == RepetitieType.AANTAL:
            repetitie_tekst = f"{repetitie_aantal}"
        elif repetitie_type == RepetitieType.AMRAP:
            repetitie_tekst = f"{repetitie_aantal}+"
        elif repetitie_type == RepetitieType.BEREIK:
            repetitie_tekst = f"{repetitie_aantal}-{repetitie_maximaal}"
        else:
            repetitie_tekst = f"{repetitie_aantal}-{repetitie_maximaal}+"
        
        if gewicht_type == GewichtType.GEWICHTLOOS:
            if set_tekst == "1":
                return f"{repetitie_tekst}"
            return f"{set_tekst}x{repetitie_tekst}"
        elif gewicht_type == GewichtType.VRIJ:
            gewicht_tekst = "?"
        elif gewicht_type == GewichtType.GEWICHT:
            gewicht_tekst = f"{gewicht_aantal}"
        else:
            gewicht_tekst = f"{gewicht_aantal * 100:.0f}%"
        
        if set_tekst == "1":
            return f"{repetitie_tekst}@{gewicht_tekst}"
        return f"{set_tekst}x{repetitie_tekst}@{gewicht_tekst}"
    
    @staticmethod
    def _sets_set_type(tekst: str) -> Tuple[int, SetType]:
        
        if "x" in tekst:
            set_tekst = tekst.split("x")[0]
            if "?" in set_tekst:
                return (0, SetType.VRIJ)
            if "+" in set_tekst:
                return (int(set_tekst.replace("+", "")), SetType.AMSAP)
            return (int(set_tekst), SetType.AANTAL)
        
        return (1, SetType.AANTAL)
    
    @staticmethod
    def _repetities_repetitie_type(tekst: str) -> Tuple[int, int, RepetitieType]:
        
        if "x" in tekst:
            repetitie_tekst = tekst.split("x")[1].split("@")[0]
        else:
            repetitie_tekst = tekst.split("@")[0]
        
        if "?" in repetitie_tekst:
            return (0, REPETITIE_AANTAL_MAX, RepetitieType.VRIJ)
        if "-" in repetitie_tekst and "+" in repetitie_tekst:
            return (int(repetitie_tekst.split("-")[0]), int(repetitie_tekst.split("-")[1].replace("+", "")), RepetitieType.BEREIK_AMRAP)
        if "-" in repetitie_tekst:
            return (int(repetitie_tekst.split("-")[0]), int(repetitie_tekst.split("-")[1]), RepetitieType.BEREIK)
        if "+" in repetitie_tekst:
            return (int(repetitie_tekst.replace("+", "")), REPETITIE_AANTAL_MAX, RepetitieType.AMRAP)
        return (int(repetitie_tekst), int(repetitie_tekst), RepetitieType.AANTAL)
    
    @staticmethod
    def _gewicht_gewicht_type(tekst: str) -> Tuple[float | None, GewichtType]:
        
        if "@" in tekst:
            gewicht_tekst = tekst.split("@")[1]
            if "?" in gewicht_tekst:
                return (0.0, GewichtType.VRIJ)
            if "%" in gewicht_tekst:
                return (int(gewicht_tekst.replace("%", "")), GewichtType.PERCENTAGE)
            return (int(gewicht_tekst), GewichtType.GEWICHT)
        return (None, GewichtType.GEWICHTLOOS)
    
    @property
    def set_aantal(self) -> int:
        return self._set_aantal
    
    @set_aantal.setter
    def set_aantal(self, waarde: int):
        if not isinstance(waarde, int):
            raise ValueError(f"`set_aantal` moet een `int` zijn, niet \"{waarde}\" (type \"{type(waarde)}\")")
        if waarde < 0 or waarde > SET_AANTAL_MAX:
            raise ValueError(f"`set_aantal` moet tussen {0} en {SET_AANTAL_MAX} liggen")
        self._set_aantal = waarde
        if waarde == 0:
            self._set_type = SetType.VRIJ
    
    @property
    def set_type(self) -> SetType:
        return self._set_type
    
    @set_type.setter
    def set_type(self, waarde: SetType):
        self._set_type = waarde
        if waarde == SetType.VRIJ:
            self._set_aantal = 0
    
    @property
    def repetitie_aantal(self) -> int:
        return self._repetitie_aantal
    
    @repetitie_aantal.setter
    def repetitie_aantal(self, waarde: int):
        if not isinstance(waarde, int):
            raise ValueError(f"`repetitie_aantal` moet een `int` zijn, niet \"{waarde}\" (type \"{type(waarde)}\")")
        if waarde < 0 or waarde > REPETITIE_AANTAL_MAX:
            raise ValueError(f"`repetitie_aantal` moet tussen {0} en {REPETITIE_AANTAL_MAX} liggen")
        self._repetitie_aantal = waarde
        if waarde == 0:
            self._repetitie_type = RepetitieType.VRIJ
    
    @property
    def repetitie_maximaal(self) -> int:
        return self._repetitie_maximaal
    
    @repetitie_maximaal.setter
    def repetitie_maximaal(self, waarde):
        self._repetitie_maximaal = waarde
    
    @property
    def repetitie_type(self) -> RepetitieType:
        return self._repetitie_type
    
    @repetitie_type.setter
    def repetitie_type(self, waarde):
        self._repetitie_type = waarde
        if waarde == RepetitieType.VRIJ:
            self._repetitie_aantal = 0
    
    @property
    def gewicht_aantal(self):
        return self._gewicht_aantal
    
    @gewicht_aantal.setter
    def gewicht_aantal(self, waarde: int | float | None):
        if not isinstance(waarde, (int, float)) and waarde is not None:
            raise ValueError(f"`gewicht_aantal` moet een `int`, `float` of `None` zijn, niet \"{waarde}\" (type \"{type(waarde)}\")")
        if waarde is not None and self.gewicht_type == GewichtType.GEWICHT and (waarde < 0.0 or waarde > GEWICHT_AANTAL_MAX):
            raise ValueError(f"`gewicht_aantal` moet tussen {0} en {GEWICHT_AANTAL_MAX} liggen")
        self._gewicht_aantal = waarde
        if waarde is None:
            self._gewicht_type = GewichtType.GEWICHTLOOS
        elif waarde == 0.0:
            self._gewicht_type = GewichtType.VRIJ
    
    @property
    def gewicht_type(self) -> GewichtType:
        return self._gewicht_type
    
    @gewicht_type.setter
    def gewicht_type(self, waarde):
        self._gewicht_type = waarde
        if waarde == GewichtType.GEWICHTLOOS:
            self._gewicht_aantal = None
        elif waarde == GewichtType.VRIJ:
            self._gewicht_aantal = 0.0

Register.DECODERS.append(Decoder(
    decoder_functie = Setcode.van_json,
    velden = frozenset(("__setcode__",)),
    ))
Register.ENCODERS.append(Encoder(
    class_naam = "Setcode",
    encoder_functie = "naar_json",
    ))