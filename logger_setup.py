import logging

def setup_logging(config):
    logging.basicConfig(
        level=getattr(logging, config.logging.level),
        format=config.logging.format
    )
    return logging.getLogger(__name__)