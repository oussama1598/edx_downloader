import os

from src.modules.config import Config

config = Config(
    os.path.join(
        os.getcwd(),
        'config.json'
    )
)
