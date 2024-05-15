import logging
import os

if not os.path.exists('./config'):
    os.makedirs('./config')

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s]: %(message)s",
    handlers=[
        logging.FileHandler('./config/output.log'),
        logging.StreamHandler()
    ]
)