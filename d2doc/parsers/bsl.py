"""Модуль содержит класс для обработки файлов bsl."""
import re
import pprint
from collections import deque


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
            "description_short": "",
            "description": "",
            "regions": [],
            "funcs": []
        }

    def _set_description(self):  # TODO: Получение описания модуля
        """ Получение описания модуля"""
        pattern = r'^\/\/@ (?P<name>.*(?:\n))(?P<desc>(?:\s*\/\/[^\r\n]*\n)+?\/\/\n)'
        matches = re.finditer(pattern, self.text, re.MULTILINE)
        for match_num, match in enumerate(matches, start=1):
            groups = match.groups()
            if len(groups) == 2:
                self.module['description_short'] = self._format_text(groups[0])
                self.module['description'] = self._format_text(groups[1])
                return               
        

    def _set_procs(self):
        """ Получение описаний процедур и функций 
        {
            "funcs": [
                {
                    "name": "Имя процедуры",
                    "full": "Полное имя с параметрами",
                    "start": Стартовая позиция в модуле
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
        for match_num, match in enumerate(matches, start=1):
            all = match.group()
            start = match.start(1)
            groups = match.groups()
            if len(groups) == 4:
                name = groups[1]
                params = groups[2]
                export = groups[3]

                record = {
                    "name": name,
                    "full": all,
                    "start": start,
                    "description": "",
                    "params": params,
                    "export": str(export).upper() == "ЭКСПОРТ",
                    "region": self._get_region_by_start(start),
                    "in": [],
                    "out": [],
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

    def _add_details(self, listfunc):
        """Add 'in, out, description, example' """

        pattern = r"^\n(?P<desc>(?:\s*\/\/[^\r\n]*\n)+?\/\/\n)(?P<comment>(?:\s*\/\/[^\r\n]*\n)*)\s*(?P<type1>Процедура|Функция)\s+(?P<name1>[А-Яа-я\w]+)s*\((?P<params>[^)]*)\)\s*(?P<export>Экспорт)"
        matches = re.finditer(pattern, self.text, re.MULTILINE)

        for match_num, match in enumerate(matches, start=1):
            groups = match.groups()
            if len(groups) >= 4:
                namefunc = groups[3]
                found, fn = self._get_fn_byname(namefunc, listfunc)
                fn['description'] = self._format_text(groups[0])
                if found:
                    in_out_exmpl = groups[1]
                    fn['in'] = self._in(in_out_exmpl)
                    fn['out'] = self._out(in_out_exmpl)
                    fn['example'] = self._example(in_out_exmpl)

    def _get_block(self, block, inputtext):
        pattern = ''.join(
            (r"(?:", block, "\s*[:]?\s*)(?P<block>[^\r]*?\/\/\n)"))
        matches = re.finditer(pattern, inputtext, re.MULTILINE)

        for match_num, match in enumerate(matches, start=1):            
            groups = match.groups()
            example = ""
            if len(groups) == 1:
                example = groups[0]
            return example
        return ""

    def _in(self, inputtext):
        textparams = self._get_block('Параметры', inputtext)
        params = self._get_in_params(textparams)
        return params

    def _get_in_params(self, inputtext):
        pattern = r'(?:^\s*\/\/[\s]{2,5})(?P<name>[А-Яа-я\w]+)(?:(?:\s*-\s*)(?P<type>[^-\n]*))?(?:\s*-\s*(?P<description_start>.))?'
        matches = re.finditer(pattern, inputtext, re.MULTILINE)
        listparams = list()
        for match_num, match in enumerate(matches, start=1):
            groups = match.groups()
            if len(groups) == 3:
                param = {
                    "name": groups[0].strip(),
                    "param_types": groups[1].strip(),
                    "start_desc": match.start(3),
                    "start_param": match.start(0)
                }
                listparams.append(param)
        out = list()
        if listparams:
            count = len(listparams)
            i = 0
            for param in listparams:
                if i == count - 1:  # Последний элемент
                    description = inputtext[param['start_desc']:]
                else:
                    description = inputtext[param['start_desc']
                        :listparams[i+1]['start_param']]
                i = i + 1
                out.append({
                    "name": param['name'],
                    "type": param['param_types'],
                    "description": self._format_text(description)
                })
        return out

    def _out(self, inputtext):
        returnvalue = self._get_block('Возвращаемое значение', inputtext)
        params = self._get_out_params(returnvalue)
        return params

    def _get_out_params(self, inputtext):
        pattern = r'(?:^\s*\/\/[\s]{2,5})(?P<type>\S.*)-(?P<description_start>.)'
        matches = re.finditer(pattern, inputtext, re.MULTILINE)
        listparams = list()
        for match_num, match in enumerate(matches, start=1):
            groups = match.groups()
            if len(groups) == 2:
                param = {
                    "type": groups[0].strip(),
                    "start_desc": match.start(2),
                    "start_param": match.start(1)
                }
                listparams.append(param)
        out = list()
        if listparams:
            count = len(listparams)
            i = 0
            for param in listparams:
                if i == count - 1:  # Последний элемент
                    description = inputtext[param['start_desc']:]
                else:
                    description = inputtext[param['start_desc']                                            :listparams[i+1]['start_param']]
                i = i + 1
                out.append({
                    "type": param['type'],
                    "description": self._format_text(description)
                })
        return out

    def _example(self, inputtext):
        return self._format_example(self._get_block('Пример', inputtext))

    def _format_text(self, text):
        return re.sub(r'[\/\n\r\t]', '', text).strip()

    def _format_example(self,text):
        return text

    def _set_regions(self):
        """ Получение областей
        module['regions'] = {
            "regions": [
                {
                    "name": "Область1",
                    "start": Стартовая позиция в модуле
                    "end": Позиция окончания в модуле
                }
            ]
        }
        """
        self.module['regions'] = self._get_regions_start()

    def _get_regions_start(self):
        pattern = r'(?:^#Область) (?P<name>.*)'
        matches = re.finditer(pattern, self.text, re.MULTILINE)
        rs = list()
        for match_num, match in enumerate(matches, start=1):
            groups = match.groups()
            if len(groups) == 1:
                region = {
                    "name": groups[0].strip(),
                    "start": match.start(1),
                }
                rs.append(region)

        pattern = r'(?:^#КонецОбласти).*'
        matches = re.finditer(pattern, self.text, re.MULTILINE)
        for match_num, match in enumerate(matches, start=1):
            groups = match.groups()
            if len(groups) == 0:
                regionend = {
                    "name": "",
                    "start": match.start(0),
                }
                rs.append(regionend)
        rs = sorted(rs, key=lambda el: el['start'])

        regions = list()
        helpqueue = deque()
        for item in rs:
            if item['name']:
                helpqueue.append(item)
            else:
                region_item = helpqueue.pop()
                regions.append({
                    "name": region_item["name"],
                    "start": region_item["start"],
                    "end": item["start"]
                })
        regions = sorted(regions, key=lambda el: el['start'])
        return regions

    def _get_region_by_start(self, start):
        regname = ""
        if self.module['regions']:
            for region in self.module['regions']:
                if start > region['start'] and start < region['end']:
                    regname = region['name']
        return regname
            

if __name__ == '__main__':
    with open('./test/test1/data/test.bsl', 'r', encoding='utf-8') as rf:
        fn = parse(rf.read())
        pprint.pprint(fn)
