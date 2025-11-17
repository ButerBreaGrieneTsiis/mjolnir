from typing import Dict, List


class TrainingsDag:
    
    def __init__(
        self,
        oefeningen: 
        ):
        
        ...
    
    # een blauwprint: lijst van oefeningen
        # een oefening: deze <oefening> met een lijst van sets
            # een set: aantal reps en (gewicht of percentage) -> TM zelf niet in dit bestand, dit is puur een blauwprint

class TrainingsCyclus: # of TrainingsSchema
    
    def __init__(
        self,
        naam: str,
        weken: int,
        dagen: int,
        trainingsschemas: Dict[int, Dict[int, TrainingsDag]]
        ) -> TrainingsCyclus:
        
        self.naam = naam
        self.weken = weken
        self.dagen = dagen
        self.trainingsschemas = trainingsschemas

# class TrainingsSuperCyclus: # of TrainingsSchema ?
    
#     def __init__(
#         self,
#         cycli: List[TrainingsCyclus] = None,
#         ) -> TrainingsSuperCyclus:
        
#         self.cycli = cycli

