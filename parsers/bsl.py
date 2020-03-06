import re
import pprint


def parse(text):
    bsl = Bsl(text)
    return bsl.parse()


class Bsl:

    def __init__(self, text):
        super().__init__()
        self.text = text
        self.module = {}

    def parse(self):
        self._set_stub_module()
        self._set_description()
        self._set_regions()
        self._set_procs()

        return self.module

    def _set_stub_module(self):

        self.module = {
            "description": "",
            "regions": [],
            "funcs": []
        }

    def _set_description(self): #TODO: Получение описания модуля
        """ Получение описания модуля"""
        self.module['description'] = ""

    def _set_procs(self):
        """ Получение описаний процедур и функций 
        {
            "funcs": [
                {
                    "name": "Имя процедуры",
                    "description": "Описание процедуры",
                    "region": "Область1",
                    "export": True,
                    "params": "Список параметров через ,"
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
        """

        pattern = r'^\s*(?P<type>Процедура|Функция)\s+(?P<name>[А-Яа-я\w]+)s*\((?P<params>[^)]*)\)\s*(?P<export>Экспорт)?'
        matches = re.finditer(pattern, self.text, re.MULTILINE)
        listfunc = list()
        for matchNum, match in enumerate(matches, start=1):
            all = match.group()
            groups = match.groups()
            if len(groups) == 4:
                tp = groups[0]
                name = groups[1]
                params = groups[2]
                export = groups[3]

                record = {
                    "name": name,
                    "full": all,
                    "description": "",
                    "params": params,
                    "export": str(export).upper() == "ЭКСПОРТ",
                    "region": "",
                    "in": "",
                    "out": "",
                    "example": ""
                }
                listfunc.append(record)

        # Add in,out, description, example
        self._add_details(listfunc)
        self.module.update({"funcs": listfunc})

    def _get_fn_byname(self, fn, listfunc):
        for f in listfunc:
            if f['name'] == fn:
                return (True, f)
        return (False, None)
        pass

    def _add_details(self, listfunc):
        """Add 'in, out, description, example' """

        pattern = r"^\n(?P<desc>(?:\s*\/\/[^\r\n]*\n)+?\/\/\n)(?P<comment>(?:\s*\/\/[^\r\n]*\n)*)\s*(?P<type1>Процедура|Функция)\s+(?P<name1>[А-Яа-я\w]+)s*\((?P<params>[^)]*)\)\s*(?P<export>Экспорт)"
        matches = re.finditer(pattern, self.text, re.MULTILINE)

        for matchNum, match in enumerate(matches, start=1):
            groups = match.groups()
            if len(groups) >= 4:
                namefunc = groups[3]
                found, fn = self._get_fn_byname(namefunc, listfunc)
                fn['description'] = groups[0]
                if found:
                    in_out_exmpl = groups[1]
                    fn['in'] = self._in(in_out_exmpl)
                    fn['out'] = self._out(in_out_exmpl)
                    fn['example'] = self._example(in_out_exmpl)

    def _get_block(self, block, inputtext):
        pattern = ''.join(
            (r"(?:", block, "\s*[:]?\s*)(?P<block>[^\r]*?\/\/\n)"))
        matches = re.finditer(pattern, inputtext, re.MULTILINE)

        for matchNum, match in enumerate(matches, start=1):
            # all = match.group()
            groups = match.groups()
            example = ""
            if len(groups) == 1:
                example = groups[0]
            return example
        return ""

    def _in(self, inputtext):
        textparams = self._get_block('Параметры', inputtext)

        # Разбираем входные параметры

        return textparams

    def _out(self, inputtext):
        returnvalue = self._get_block('Возвращаемое значение', inputtext)

        # Разбираем выходные параметры

        return returnvalue

    def _example(self, inputtext):
        return self._get_block('Пример', inputtext)

    def _set_regions(self):
        """ Получение областей
        return {
            "regions": [
                {
                    "name": "Область1",
                    "regions": [
                        {
                            "name": "Вложенная область 1"
                        }
                    ]
                }
            ]
        }
        """

        pass


if __name__ == '__main__':
    with open('./test/test1/data/test.bsl', 'r', encoding='utf-8') as rf:
        fn = parse(rf.read())
        pprint.pprint(fn)
