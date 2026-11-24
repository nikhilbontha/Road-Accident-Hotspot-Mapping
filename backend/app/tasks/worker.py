"""Background task worker for processing long-running analyses and imports."""
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("worker")

def main():
    logger.info("Road Accident Hotspot Mapping Worker started. Listening for tasks...")
    try:
        while True:
            time.sleep(5)
    except KeyboardInterrupt:
        logger.info("Worker stopped.")

if __name__ == "__main__":
    main()
