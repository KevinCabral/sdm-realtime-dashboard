import logging

logger = logging.getLogger("audit")


def setup_audit_logging() -> None:
    if logger.handlers:
        return
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler()
    formatter = logging.Formatter("%(asctime)s %(levelname)s audit=%(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)


def log_data_access(actor: str, action: str) -> None:
    logger.info("actor=%s action=%s", actor, action)
