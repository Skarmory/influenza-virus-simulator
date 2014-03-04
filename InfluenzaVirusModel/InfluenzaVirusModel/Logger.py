from abc import ABCMeta, abstractmethod

class Logger(object):
    __metaclass__ = ABCMeta

    @staticmethod
    @abstractmethod
    def out(str):
        pass

    @staticmethod
    @abstractmethod
    def err(str):
        pass

class StdOutLogger(Logger):
    def __init__(self, *args):
        super(StdOutLogger, self).__init__()

    @staticmethod
    def err(str):
        print(str)

    @staticmethod
    def out(str):
        print(str)
