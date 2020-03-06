import pprint

def parse(text):
    bsl = Bsl(text)
    return bsl.parse()


class Bsl:

    def __init__(self, text):
        super().__init__()
        self.text = text

    def parse(self):
        module = self._get_description()
        module['funcs'] = {}
        # module['spaces'] = {}

        module.update(self._get_procs())
        return module

    def _get_description(self):
        
        # description
        
        return {
            "description": "Описание модуля",
            "spaces": [
                {
                    "name": "Область1",
                    "spaces": [
                        {
                            "name": "Вложенная область"
                        }
                    ]
                }
            ]
            }

    def _get_procs(self):
        return {
            "funcs": [
                {
                    "name": "Имя процедуры",
                    "description": "Описание процедуры",
                    "space": "Область1",
                    "in": [
                        {
                            "name": "Параметр 1",
                            "type": "Тип параметра",
                            "description": "Описание параметра",
                            "byvalue": True
                        }
                    ],
                    "out": [
                        {
                            "name": "Параметр 1",
                            "type": "Тип параметра",
                            "description": "Описание параметра"
                        }
                    ],
                    "example": "Пример использования"
                }
            ]
            }


if __name__ == '__main__':

    with open('./test/test1/data/test.bsl', 'r', encoding='utf-8') as rf:
        pprint.pprint(parse(rf.read()))
