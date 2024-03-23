"""Provides logging functionality"""

import concurrent.futures
import logging
import os

# custom module
from neosearch.app.utils.singleton import Singleton


# constants
_DEFAULT_LOG_NAME = "neosearch"
_DEFAULT_LOG_LEVEL = "DEBUG"
_DEFAULT_CONSOLE_LOG_LEVEL = "WARNING"
_DEFAULT_MAX_BYTES = 10485760
_DEFAULT_BACKUP_COUNT = 10
_DEFAULT_LOGGING_WORKERS = 1


class Logger(metaclass=Singleton):
    """Logger class."""

    def __init__(
        self,
        use_file_handler: bool = True,
        use_rotate_file_handler=True,
        rotate_max_byte: int = _DEFAULT_MAX_BYTES,
        rotate_backup_count: int = _DEFAULT_BACKUP_COUNT,
        log_module_name: bool = False,
        log_thread_ids: bool = False,
    ) -> None:
        """
        Initialize the logger.

        Use the proxy pattern to create a singleton logger when it is actually required.
        """
        self.log_name = os.getenv("LOG_NAME", _DEFAULT_LOG_NAME)

        # [DEBUG, INFO, WARNING, ERROR, CRITICAL]
        self.log_level = os.getenv(
            "LOG_LEVEL", _DEFAULT_LOG_LEVEL
        )
        self.console_log_level = os.getenv(
            "CONSOLE_LOG_LEVEL", _DEFAULT_CONSOLE_LOG_LEVEL
        )

        self.log_module_name = log_module_name
        self.log_thread_ids = log_thread_ids

        self.logger = None
        self.use_file_handler = use_file_handler
        self.use_rotate_file_handler = use_rotate_file_handler
        self.rotate_max_byte = rotate_max_byte
        self.rotate_backup_count = rotate_backup_count

        self.executor = concurrent.futures.ThreadPoolExecutor(
            max_workers=_DEFAULT_LOGGING_WORKERS
        )

    def get_logger(self) -> logging.Logger:
        """
        Get a logger instance

        Returns:
            logging.Logger: Logger instance
        """
        if not self.logger:
            logger = logging.getLogger(self.log_name)
            logger.setLevel(self.log_level)

            # optimize logging: reference: <https://docs.python.org/3/howto/logging.html#optimization>
            logging.raiseExceptions = False
            logging.logProcesses = False
            logging.logMultiprocessing = False

            if self.log_module_name:
                if self.log_thread_ids:
                    fmt_str = "%(asctime)s | %(levelname)s | %(thread)d | %(module)s | %(funcName)s | %(message)s"
                else:
                    logging.logThreads = False
                    fmt_str = "%(asctime)s | %(levelname)s | %(module)s | %(funcName)s | %(message)s"
            else:
                logging._srcfile = None
                if self.log_thread_ids:
                    fmt_str = "%(asctime)s | %(levelname)s | %(thread)d | %(message)s"
                else:
                    logging.logThreads = False
                    fmt_str = "%(asctime)s | %(levelname)s | %(message)s"
            formatter = logging.Formatter(fmt_str)

            console_handler = logging.StreamHandler()
            console_handler.setLevel(self.console_log_level)
            console_handler.setFormatter(formatter)

            logger.addHandler(console_handler)

            # check whether to use file handler
            if self.use_file_handler:
                # check whether to use rotate file handler
                if self.use_rotate_file_handler:
                    from logging.handlers import RotatingFileHandler

                    rotate_file_handler = RotatingFileHandler(
                        f"{self.log_name}.log",
                        maxBytes=self.rotate_max_byte,
                        backupCount=self.rotate_backup_count,
                    )
                    rotate_file_handler.setLevel(self.log_level)
                    rotate_file_handler.setFormatter(formatter)

                    logger.addHandler(rotate_file_handler)
                else:
                    file_handler = logging.FileHandler(f"{self.log_name}.log")
                    file_handler.setLevel(self.log_level)
                    file_handler.setFormatter(formatter)

                    logger.addHandler(file_handler)

            self.logger = logger
            return logger
        return self.logger

    def log_debug(self, msg: str) -> None:
        """
        Log debug message.

        Args:
            msg (str): Message to log

        Raises:
            AssertionError: If logger is not initialized
        """
        if self.logger is None:
            self.get_logger()
            assert isinstance(self.logger, logging.Logger)
        self.executor.submit(self.logger.debug, msg)

    def log_info(self, msg: str) -> None:
        """
        Log info message.

        Args:
            msg (str): Message to log

        Raises:
            AssertionError: If logger is not initialized
        """
        if self.logger is None:
            self.get_logger()
            assert isinstance(self.logger, logging.Logger)
        self.executor.submit(self.logger.info, msg)

    def log_warning(self, msg: str) -> None:
        """
        Log warning message.

        Args:
            msg (str): Message to log

        Raises:
            AssertionError: If logger is not initialized
        """
        if self.logger is None:
            self.get_logger()
            assert isinstance(self.logger, logging.Logger)
        self.executor.submit(self.logger.warning, msg)

    def log_error(self, msg: str) -> None:
        """
        Log error message.

        Args:
            msg (str): Message to log

        Raises:
            AssertionError: If logger is not initialized
        """
        if self.logger is None:
            self.get_logger()
            assert isinstance(self.logger, logging.Logger)
        self.executor.submit(self.logger.error, msg)

    def log_critical(self, msg: str) -> None:
        """
        Log critical message.

        Args:
            msg (str): Message to log

        Raises:
            AssertionError: If logger is not initialized
        """
        if self.logger is None:
            self.get_logger()
            assert isinstance(self.logger, logging.Logger)
        self.executor.submit(self.logger.critical, msg)
