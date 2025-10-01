class WasteType:
    def __init__(self, name: str):
        self.key = (
            name.lower()
            .replace(" ", "_")
            .replace("ł", "l")
            .replace("ś", "s")
            .replace("ó", "o")
            .replace("ą", "a")
            .replace("ę", "e")
            .replace("ć", "c")
            .replace("ń", "n")
            .replace("ź", "z")
            .replace("ż", "z")
        )
        self.name = name.lower()

    def __hash__(self):
        return hash(self.key)

    def __eq__(self, other):
        return isinstance(other, WasteType) and self.key == other.key