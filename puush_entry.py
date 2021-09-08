class PuushEntry:
    identifier = None
    date = None
    url = None
    filename = None
    views = None
    unknown = None

    def __init__(self, identifier, date, url, filename, views, unknown=0):
        self.identifier = identifier
        self.date = date
        self.url = url
        self.filename = filename
        self.views = views
        self.unknown = unknown

    def __str__(self):
        return "{},{},{},{},{},{}".format(
            self.identifier,
            self.date,
            self.url,
            self.filename,
            self.views,
            self.unknown)
