
import logging

DEBUG = 0
INFO = 1

class Logger:
    def __init__(self, level):
        self.logger_level = self._get_logging_level(level)

#        logging.basicConfig(level=self.logger_level)

        request_logger = logging.getLogger("requests.packages.urllib3")
        request_logger.setLevel(self.logger_level)
        request_logger.propagate = level

    def getLogger(self):
        # create logger
        logger = logging.getLogger('Python CloudFlare API v4')
        logger.setLevel(self.logger_level)

        ch = logging.StreamHandler()
        ch.setLevel(self.logger_level)

        # create formatter
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        # add formatter to ch
        ch.setFormatter(formatter)

        # add ch to logger
        logger.addHandler(ch)

        return logger

    def _get_logging_level(self, level):
        if level == True:
            return logging.DEBUG
        else:
            return logging.INFO
