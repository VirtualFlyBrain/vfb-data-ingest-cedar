
class CrawlerException(Exception):

    def __init__(self, message):
        Exception.__init__(self)
        self.message = message


class TemplateParserException(Exception):

    def __init__(self, message):
        Exception.__init__(self)
        self.message = message


class VfbClientException(Exception):

    def __init__(self, message):
        Exception.__init__(self)
        self.message = message
