class JsonStorage():
    def __init__(self, folder: str, indent: int) -> None:
        self.folder = folder
        self.indent = indent

    def read(self):
        pass

    def write(self):
        pass


class BsonStorage():
    def __init__(self, folder: str) -> None:
        self.folder = folder

    def read(self):
        pass

    def write(self):
        pass
