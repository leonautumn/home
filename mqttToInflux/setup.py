import logging as log
import logging.handlers as log_handler


def setup_logger(current_path, log_level, log_file_size_mb, log_file_numbers):
    """
    Set up logging functionality
    :param current_path: Current path of main application
    :param log_level: Set log level (e.g. log.DEBUG or log.WARNING)
    :param log_file_size_mb: Size per log file in mega bytes
    :param log_file_numbers: Number of log files which should be created after rotation of logging starts
    """
    log_format = "%(asctime)s %(levelname)s  %(message)s"
    log_formatter = log.Formatter(log_format)
    log_file = current_path + "/log/" + "Application.log"
    log.basicConfig(level=log_level, format=log_format)
    root_logger = log.getLogger()

    # Set rotating file handler with following settings:
    file_handler = log_handler.RotatingFileHandler(filename=log_file, mode='a', maxBytes=log_file_size_mb * 1024 * 1024,
                                                   backupCount=log_file_numbers,
                                                   encoding=None, delay=False, errors=None)

    file_handler.setFormatter(log_formatter)
    root_logger.addHandler(file_handler)

    console_handler = log.StreamHandler()
    console_handler.setFormatter(log_formatter)
