# -*- coding: utf-8 -*-

class NotSuperuserError(Exception):
    def __init__(self, message):
        Exception.__init__(self, message)

class PlatformNotSupportedError(Exception):
    def __init__(self, message):
        Exception.__init__(self, message)

class AptGetUnavailableError(Exception):
    def __init__(self, message):
        Exception.__init__(self, message)

class UpgradeTypeInvalidError(Exception):
    def __init__(self, message):
        Exception.__init__(self, message)

class AptSystemBrokenError(Exception):
    def __init__(self, message):
        Exception.__init__(self, message)

class SignatureFileError(Exception):
    def __init__(self, message):
        Exception.__init__(self, message)

class WrongDataTypeError(Exception):
    def __init__(self, message):
        Exception.__init__(self, message)

class DownloadFileFormatError(Exception):
    def __init__(self, message):
        Exception.__init__(self, message)