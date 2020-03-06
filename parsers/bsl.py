
def parse(text):
    bsl = Bsl(text)
    return bsl.parse()

class Bsl:

    def __init__(self, text):
        super().__init__()
        self.text = text

    def parce(self):
        return {}