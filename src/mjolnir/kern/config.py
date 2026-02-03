"""mjolnir.kern.config"""
from dotenv import dotenv_values


CONFIG_STANDAARD = {
    "REPETITIE_AANTAL_MAX": 30,
    "SET_AANTAL_MAX": 10,
    "GEWICHT_AANTAL_MAX": 200.0,
    }

config_env = {
    sleutel: type(CONFIG_STANDAARD[sleutel])(waarde) for sleutel, waarde in dotenv_values(".env").items() if sleutel in CONFIG_STANDAARD
    }

CONFIG = {
    **CONFIG_STANDAARD,
    **config_env,
    }