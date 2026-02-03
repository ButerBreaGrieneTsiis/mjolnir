"""
Mjölnir
"""
from pathlib import Path

from grienetsiis.json import Ontcijferaar, Vercijferaar
from grienetsiis.register import Register

from mjolnir.kern import Setcode
from mjolnir.kern.enums import ENUMS
from mjolnir.schema import Sjabloon, Schema
from mjolnir.sessie import Halterstang, Halterschijf, programma_sessie


__all__ = [
    "Register",
    "programma_sessie",
    ]

__version__ = "1.0.1"

Register.instellen(
    registratie_methode = "uuid",
    bestandsmap = Path("gegevens"),
    )

Register.registreer_type(
    geregistreerd_type = Halterstang,
    subregister_naam = "halterstangen",
    bestandsmap = Path("gegevens"),
    bestandsnaam = "halterstangen",
    vercijfer_methode = "functie",
    vercijfer_functie_objecten = Halterstang.naar_json,
    ontcijfer_functie_objecten = Halterstang.van_json,
    enums = ENUMS,
    )
Register.registreer_type(
    geregistreerd_type = Halterschijf,
    subregister_naam = "halterschijven",
    bestandsmap = Path("gegevens"),
    bestandsnaam = "halterschijven",
    vercijfer_methode = "functie",
    vercijfer_functie_objecten = Halterschijf.naar_json,
    ontcijfer_functie_objecten = Halterschijf.van_json,
    enums = ENUMS,
    )
Register.registreer_type(
    geregistreerd_type = Sjabloon,
    subregister_naam = "sjablonen",
    bestandsmap = Path("gegevens"),
    bestandsnaam = "sjablonen",
    vercijfer_methode = "functie",
    vercijfer_functie_objecten = Sjabloon.naar_json,
    ontcijfer_functie_objecten = Sjabloon.van_json,
    vercijfer_functie_subobjecten = [
        Vercijferaar(
            class_naam = "Setcode",
            vercijfer_functie_naam = "naar_json",
            ),
        ],
    ontcijfer_functie_subobjecten = [
        Ontcijferaar(
            velden = frozenset((
                "__setcode__",
                )),
            ontcijfer_functie = Setcode.van_json,
            ),
        ],
    enums = ENUMS,
    )
Register.registreer_type(
    geregistreerd_type = Schema,
    subregister_naam = "schema",
    bestandsmap = Path("gegevens"),
    bestandsnaam = "schema",
    vercijfer_methode = "functie",
    vercijfer_functie_objecten = Schema.naar_json,
    ontcijfer_functie_objecten = Schema.van_json,
    enums = ENUMS,
    )