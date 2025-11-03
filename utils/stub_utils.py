import os
import pickle
from logger import logger

def save_stub(stub_path, objects):
    os.makedirs(os.path.dirname(stub_path), exist_ok=True)

    if stub_path:
        try:
            with open(stub_path, "wb") as f:
                pickle.dump(objects, f)
            logger.info(f"Stub saved successfully at {stub_path}")
        except Exception as e:
            logger.info(f"Dumping stub error: {e}")

def read_stub(read_from_stub: bool = False, stub_path: str = None):
    if read_from_stub and stub_path and os.path.exists(stub_path):
        try:
            with open(stub_path, "rb") as f:
                logger.info(f"Stub loading...")
                obj = pickle.load(f)
                logger.info(f"stub loaded ")
                return obj
        except Exception as e:
            logger.info(f"load/read from stub error: {e}")
            return None
