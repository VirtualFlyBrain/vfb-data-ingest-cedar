

class TechnicalException(Exception):
    """
    These exceptions are reported to the technical maintenance team.
    """

    def __init__(self, message):
        Exception.__init__(self)
        self.message = message


class ContentException(Exception):
    """
    These exceptions are reported to the editor of the template.
    """

    def __init__(self, message):
        Exception.__init__(self)
        self.message = message


class TemplateParserException(ContentException):

    def __init__(self, message):
        Exception.__init__(self)
        self.message = message


class CrawlerException(TechnicalException):

    def __init__(self, message):
        Exception.__init__(self)
        self.message = message


class VfbClientException(TechnicalException):

    def __init__(self, message):
        Exception.__init__(self)
        self.message = message
