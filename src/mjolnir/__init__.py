"""
Mjölnir
"""
from grienetsiis.json import Ontcijferaar, Vercijferaar

from mjolnir.kern import Register, Setcode
from mjolnir.schema import Schema, Sjabloon
from mjolnir.sessie import Halterstang, Halterschijf, programma_sessie


__all__ = [
    "Register",
    "programma_sessie",
    ]

__version__ = "0.1.0-dev"

Register.TYPES["halterstangen"] = {
    "type": Halterstang,
    "ontcijferaar": Halterstang.van_json,
    "vercijferaar": Halterstang.naar_json,
    }
Register.TYPES["halterschijven"] = {
    "type": Halterschijf,
    "ontcijferaar": Halterschijf.van_json,
    "vercijferaar": Halterschijf.naar_json,
    }
Register.TYPES["schema"] = {
    "type": Schema,
    "ontcijferaar": Schema.van_json,
    "vercijferaar": Schema.naar_json,
    }
Register.TYPES["sjablonen"] = {
    "type": Sjabloon,
    "ontcijferaar": Sjabloon.van_json,
    "vercijferaar": Sjabloon.naar_json,
    }
Register.ONTCIJFERAARS.append(Ontcijferaar(
    ontcijfer_functie = Setcode.van_json,
    velden = frozenset((
        "__setcode__",
        )),
    ))
Register.VERCIJFERAARS.append(Vercijferaar(
    class_naam = "Setcode",
    vercijfer_functie_naam = "naar_json",
    ))