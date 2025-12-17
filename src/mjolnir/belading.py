from dataclasses import dataclass
from itertools import permutations, product
from typing import ClassVar, List

from mjolnir.enums import HalterType
from mjolnir.register import GeregistreerdObject, Register


@dataclass
class Halterschijf(GeregistreerdObject):
    
    massa: float
    diameter: int
    aantal: int
    breedte: int
    
    BESTANDSNAAM: ClassVar[str] = "halterschijven"
    
    def __repr__(self) -> str:
        return f"halterschijf {self.massa} kg Ø{self.diameter}"
    
@dataclass
class Halterstang(GeregistreerdObject):
    
    naam: str
    halter_type: HalterType
    massa: float
    diameter: int
    opname_breedte: int
    
    BESTANDSNAAM: ClassVar[str] = "halterstangen"
    
    def __repr__(self) -> str:
        return f"halterstang \"{self.naam}\" van type \"{self.halter_type.value}\""
    
    def optimaal_laden(
        self,
        gewicht_per_set: List[float],
        halterschijven: List[Halterschijf],
        ) -> List["Halter"]:
        
        halterschijven_per_kant = [halterschijf.massa for halterschijf in halterschijven for _ in range(halterschijf.aantal//2)]
        
        # berekenen totaal gewicht per kant nodig
        gewicht_per_kant_per_set = []
        for gewicht_set in gewicht_per_set:
            
            gewicht_per_kant = round((gewicht_set - self.massa)/2/min(halterschijven_per_kant))*min(halterschijven_per_kant)
            gewicht_per_kant_dict = {
                "gewicht": gewicht_per_kant,
                "permutaties": [],
                "permutaties_filter": [],
                }
            
            gewicht_per_kant_per_set.append(gewicht_per_kant_dict)
        
        # alle mogelijke halterschijf combinaties berekenen
        for gewicht_per_kant_dict in gewicht_per_kant_per_set:
            stop_iteratie = True
            for aantal_gewichten in range(1, 1 + len(halterschijven_per_kant)):
                for volgorde_gewichten in set(permutations(halterschijven_per_kant, aantal_gewichten)):
                    if sum(volgorde_gewichten) == gewicht_per_kant_dict["gewicht"]:
                        gewicht_per_kant_dict["permutaties"].append(["halterstang"] + list(volgorde_gewichten))
                        stop_iteratie = False
            if stop_iteratie:
                gewicht_per_kant_dict["permutaties"].append(["halterstang"])
        
        # filter creëeren op basis van minimum gewicht
        minimum_gewicht_per_kant = min(gewicht_per_kant_dict["gewicht"] for gewicht_per_kant_dict in gewicht_per_kant_per_set)
        volgorde_gewichten_minimum = []
        for halterschijf in sorted(halterschijven_per_kant, reverse = True):
            if halterschijf <= minimum_gewicht_per_kant - sum(volgorde_gewichten_minimum):
                if halterschijven_per_kant.count(halterschijf) > 1: # want bij twee of meer van gelijk gewicht, kan deze nog aangevuld worden
                    volgorde_gewichten_minimum.append(halterschijf)
                else:
                    if all([halterschijf in permutatie for gewicht_per_kant_dict in gewicht_per_kant_per_set for permutatie in gewicht_per_kant_dict["permutaties"]]):
                        volgorde_gewichten_minimum.append(halterschijf)
        
        volgorde_gewichten_minimum.insert(0, "halterstang")
        
        # filter toepassen
        for gewicht_per_kant_dict in gewicht_per_kant_per_set:
            for permutatie in gewicht_per_kant_dict["permutaties"]:
                if permutatie[:len(volgorde_gewichten_minimum)] == volgorde_gewichten_minimum:
                    gewicht_per_kant_dict["permutaties_filter"].append(permutatie)
        
        # berekenen halterschijven volgorde met minste verschuivingen
        kost_minimaal = 100
        
        for volgorde_gewichten in product(*[gewicht_per_kant_dict["permutaties_filter"] for gewicht_per_kant_dict in gewicht_per_kant_per_set]):
            
            kost = 0
            belading = []
            
            for gewichten in volgorde_gewichten:
                
                if belading == gewichten:
                    continue
                
                for aantal_overeenkomend in reversed(range(1, len(belading) + 1)):
                    if belading[:aantal_overeenkomend] == gewichten[:aantal_overeenkomend]:
                        break
                else:
                    aantal_overeenkomend = 0
                
                
                kost += len(belading) - aantal_overeenkomend
                belading = belading[:aantal_overeenkomend]
                
                for gewicht in gewichten[aantal_overeenkomend:]:
                    belading.append(gewicht)
                    kost += 1
            
            kost += len(belading) # volledig ontladen
            
            if kost < kost_minimaal:
                kost_minimaal = kost
                volgorde_optimaal = volgorde_gewichten
        
        # halters laden
        halters = []
        
        for gewichten_per_kant in volgorde_optimaal:
            
            halterschijven_per_kant = []
            for gewicht_per_kant in gewichten_per_kant[1:]:
                halterschijf = next(halterschijf for halterschijf in halterschijven if halterschijf.massa == gewicht_per_kant)
                halterschijven_per_kant.append(halterschijf)
            
            halter = Halter(self, halterschijven_per_kant, halterschijven_per_kant)
            halters.append(halter)
        
        return halters
    
    def laden(
        self,
        gewicht: float,
        halterschijven: List[Halterschijf],
        ) -> "Halter":
        
        halterschijf_min = min(halterschijf.massa for halterschijf in halterschijven)
        
        halterschijven.sort(key = lambda x: x.massa, reverse = True)
        halterschijven_per_kant = [halterschijf for halterschijf in halterschijven for _ in range(halterschijf.aantal//2)]
        
        gewicht_per_kant = round((gewicht - self.massa)/2/halterschijf_min)*halterschijf_min
        
        halterschijven_kant = []
        
        for halterschijf in halterschijven_per_kant:
            if halterschijf.massa + sum(halterschijf.massa for halterschijf in halterschijven_kant) <= gewicht_per_kant:
                halterschijven_kant.append(halterschijf)
            else:
                continue
        
        return Halter(
            self,
            halterschijven_kant,
            halterschijven_kant,
            )

@dataclass
class Halter: 
    
    halterstang: Halterstang
    halterschijven_links: List[Halterschijf] = None
    halterschijven_rechts: List[Halterschijf] = None
    
    def __repr__(self):
        links = "".join([f"[{halterschijf.massa}]" for halterschijf in reversed(self.halterschijven_links)])
        rechts = "".join([f"[{halterschijf.massa}]" for halterschijf in self.halterschijven_rechts])
        return f"{links}---[{self.halterstang.naam}]---{rechts}"
    
    @property
    def massa(self) -> float:
        
        return self.halterstang.massa + \
            sum([halterschijf.massa for halterschijf in self.halterschijven_links]) + \
            sum([halterschijf.massa for halterschijf in self.halterschijven_rechts])

Register.DECODERS["halterstangen"] = {
    "class": Halterstang,
    "decoder_functie": Halterstang.van_json,
    }
Register.ENCODERS["halterstangen"] = {
    "class": Halterstang,
    "encoder_functie": Halterstang.naar_json,
    }
Register.DECODERS["halterschijven"] = {
    "class": Halterschijf,
    "decoder_functie": Halterschijf.van_json,
    }
Register.ENCODERS["halterschijven"] = {
    "class": Halterschijf,
    "encoder_functie": Halterschijf.naar_json,
    }