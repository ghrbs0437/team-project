import logging
import os


LOG_FORMAT = "%(asctime)s %(levelname)s [%(name)s] %(message)s"


def configure_logging() -> None:
    log_level_name = os.getenv("APP_LOG_LEVEL", "INFO").upper()
    log_level = getattr(logging, log_level_name, logging.INFO)

    app_logger = logging.getLogger("app")
    app_logger.setLevel(log_level)
    app_logger.propagate = False

    has_app_handler = any(
        getattr(handler, "_team_project_app_handler", False)
        for handler in app_logger.handlers
    )
    if has_app_handler:
        return

    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(logging.Formatter(LOG_FORMAT))
    console_handler._team_project_app_handler = True
    app_logger.addHandler(console_handler)
