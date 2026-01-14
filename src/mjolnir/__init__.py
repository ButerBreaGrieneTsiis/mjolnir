from grienetsiis import Decoder, Encoder

from mjolnir.basis import Register, Setcode
from mjolnir.schema import Schema, Sjabloon
from mjolnir.sessie import Halterstang, Halterschijf, paneel
from mjolnir.resultaat import Resultaat, ResultaatSet, ResultaatOefening


__all__ = [
    "Register",
    "paneel",
    ]

__version__ = "0.1.0-dev"

Register.TYPES["halterstangen"] = {
    "type": Halterstang,
    "decoder": Halterstang.van_json,
    "encoder": Halterstang.naar_json,
    }
Register.TYPES["halterschijven"] = {
    "type": Halterschijf,
    "decoder": Halterschijf.van_json,
    "encoder": Halterschijf.naar_json,
    }
Register.TYPES["schema"] = {
    "type": Schema,
    "decoder": Schema.van_json,
    "encoder": Schema.naar_json,
    }
Register.TYPES["sjablonen"] = {
    "type": Sjabloon,
    "decoder": Sjabloon.van_json,
    "encoder": Sjabloon.naar_json,
    }
Register.DECODERS.append(Decoder(
    decoder_functie = Setcode.van_json,
    velden = frozenset((
        "__setcode__",
        )),
    ))
Register.ENCODERS.append(Encoder(
    class_naam = "Setcode",
    encoder_functie = "naar_json",
    ))