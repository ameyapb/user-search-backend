import logging

logger = logging.getLogger("user-search-backend")


def setup_logging():
    logging.basicConfig(
        level=logging.WARNING,
        format="\033[91m[%(asctime)s]\033[0m \033[92m[%(filename)s:%(lineno)d]\033[0m \033[93m%(levelname)s\033[0m - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    logger.setLevel("DEBUG")
    return logger
