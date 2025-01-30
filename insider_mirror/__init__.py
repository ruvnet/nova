"""Insider Trading Mirror System."""

import logging

# Configure root logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)8s] %(message)s (%(name)s:%(lineno)d)',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Create package logger
logger = logging.getLogger("insider_mirror")
logger.setLevel(logging.INFO)