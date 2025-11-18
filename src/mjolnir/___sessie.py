import datetime as dt
from enum import Enum
from typing import List, Union








class Set:
    
    REPETITIES_MAXIMAAL = 50
    
    def __init__(
        self,
        repetities: Union[int, Amrap],
        gewicht: Union[float, None] = None,
        # belading: Union[Belading, None] = None,
        ) -> Set:
        
        self.repetities = repetities
        self.gewicht = gewicht
        # self.belading = belading
        self._repetities_gedaan = None
        
    # def __repr__(
    #     self,
    #     ) -> str:
        
    #     f"set van {}"
        
    @property
    def repetities_gedaan(
        self,
        ):
        
        return self._repetities_gedaan

    @repetities_gedaan.setter
    def repetities_gedaan(
        self,
        repetities: int,
        ):
        
        try:
            int(repetities)
        except ValueError:
            print(f"waarde moet een integer zijn")
        else:
            if 0 <= repetities <= self.REPETITIES_MAXIMAAL:
                self._repetities_gedaan = int(repetities)
            else:
                print(f"repetities moeten tussen 0 en {self.REPETITIES_MAXIMAAL} zitten")
    
    @property
    def volume(self) -> float:
        
        if self.gewicht is None:
            return None
        else:
            return self.gewicht * self.repetities_gedaan

class Oefening:
    
    def __init__(
        self,
        naam: OefeningEnum,
        sets: List[Set] = None,
        ) -> Oefening:
        
        self.naam = naam
        self.sets = list() if sets is None else sets
    
    @classmethod
    def bouwen(
        cls,
        naam: OefeningEnum,
        
        ):
        ...
    
    # @property
    # def volume(
    #     self,
    #     ) -> float:
        
    #     return None

class Sessie:
    
    def __init__(
        self,
        datum: dt.date = dt.date.today(),
        oefeningen: List[Oefening] = None,
        ) -> Sessie:
        
        self.datum = datum
        self.oefeningen = list() if oefeningen is None else oefeningen
    
    @classmethod
    def openen(
        cls,
        datum: dt.date = dt.date.today(),
        ) -> Sessie:
        
        ...
        
        return cls()
    
    def opslaan(
        self,
        ) -> None:
        
        ...
    
    def start(
        self,
        ):
        
        ...

s = Set(5)

print(Amrap)