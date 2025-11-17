from enum import Enum


class OefeningType(Enum):
    
    LICHAAMSGEWICHT = 1
    GEWICHT = 2
    HALTER = 3
    EZ_CURL = 4

class OefeningEnum(Enum):
    
    PRESS = ("press", OefeningType.HALTER)
    SQUAT = ("squat", OefeningType.HALTER)
    BENCH = ("bench", OefeningType.HALTER)
    DEADLIFT = ("deadlift", OefeningType.HALTER)
    
    def oefening_type(self) -> OefeningType:
        return self.value[1]