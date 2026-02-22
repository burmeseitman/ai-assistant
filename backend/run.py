import subprocess
import threading
import sys
import time
import os

from server import app

import uvicorn
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_fastapi():
    """Runs the FastAPI server."""
    logger.info("Starting FastAPI server on port 8000...")
    # NOTE: Run inside docker, so host should be 0.0.0.0
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=False)

if __name__ == "__main__":
    run_fastapi()
