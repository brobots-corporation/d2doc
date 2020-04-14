
# d2doc
Генерация документации на основании входных файлов с данными и шаблонов выходных документов

[![Build Status](https://travis-ci.org/brobots-corporation/d2doc.svg?branch=master)](https://travis-ci.org/brobots-corporation/d2doc) [![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=d2doc&metric=alert_status)](https://sonarcloud.io/dashboard?id=d2doc)

## Возможности
* Работа в ОС: `Linux`, `Mac OS X`, `Windows`;
* Формат шаблонов [jinja2](https://jinja.palletsprojects.com/);
* Формат файлов входных данных `xml,json,yaml,bsl`.
* Статика

## Установка и обновление
Установка зависимостей
```sh
pip install -r requirements.txt
```

## Использование скрипта
```
Usage: d2doc.py [OPTIONS] COMMAND [ARGS]...

Options:
  --log-level TEXT  Log level [CRITICAL, FATAL, ERROR, WARNING, DEBUG, INFO,
                    NOTSET]                 
  --help            Show this message and exit.

Commands:
  build
```  
Использование команды `build`
```
Usage: d2doc.py build [OPTIONS]

Options:
  -t, --templates PATH        Path to template files.
  -s, --start-templates TEXT  Root templates separated by comma.
  -f, --data-file FILE        Input data file (Global for all templates).
  -d, --data-dir PATH         Input data dir (Global for all templates).
  -m, --data-dir-mask TEXT    Files mask for option '--data-dir-mask'.
  -o, --output-dir PATH       Output dir for documentation.
  --erase-output-dir          Erase output dir befor build.
  --output-format TEXT        File extention for output files.
  --transliterate-urls        Transliterate urls.
  --static PATH               Dir with static files to copy in output (multiple).
  --help                      Show this message and exit.
```


### Пример использования скрипта в Linux
```sh
d2doc.py build \
	--templates './test/test1/templates' \
	--start-templates 'Оглавление' \
	--data-dir './test/test1/data' \
	--data-dir-mask '**/*.json' \
	--output-dir './test/test1/doc' \
  --static './test/test1/static' \
	--erase-output-dir
```

### Пример использования скрипта в Linux c использованием переменных среды
```sh
export D2DOC_BUILD_TEMPLATES='./test/test1/templates'
export D2DOC_BUILD_START_TEMPLATES='Оглавление'
export D2DOC_BUILD_DATA_DIR='./test/test1/data'
export D2DOC_BUILD_DATA_DIR_MASK='**/*.json'
export D2DOC_BUILD_OUTPUT_DIR='./test/test1/doc'
export D2DOC_BUILD_STATIC='./test/test1/doc/static'
export D2DOC_LOG_LEVEL='DEBUG'
d2doc.py build --erase-output-dir
```

## Шаблоны
Для рендера страниц используется движок `jinja2`

### Вспомогательные функции
Функции для использования в шаблонах (плюсом к разнообразию функций [jinja2](https://jinja.palletsprojects.com/))

#### tolist
Используется для обработки коллекций из файлов xml в jinja2, когда возможен только один элемент в колекции. Если передан один объект, то возвращается список с этим объектом.

```
tolist(obj_or_list)
```
| Parameter | Requare|Description |
| --- | --- | --- |
| `obj_or_list` | Да | Список произвольных объектов или произвольный объект |

Пример:
```
{% set config_xml = from_file("./configuration.xml") %}
{% set config_props = config_xml.MetaDataObject.Configuration.Properties %}
{% for role in tolist(config_props.DefaultRoles['xr:Item']) %}
    * {{role['#text']}}\\
{% endfor %}
```

#### url
Используется для построения внутренних ссылок.

```
url(url,target_template,data, [other])
```
| Parameter | Requare|Description |
| --- | --- | --- |
| `url` | Да | Шаблон ссылки в формате jinja2 |
| `target_template` | Да | Имя файла шаблона, по которому должна генерироваться ссылка `url` |
| `url` | Да | Данные для передачи в шаблон `target_template` |
| `other` | Нет | Прочие параметры для рендера ссылки по шаблону `url` |

Пример:
```
[Справочник {{ name }}]({{ url(url = 'sprs/{{ name }}.md', target_template = 'spr.j2', data = spr, name='Users') }})

Результат:
[Справочник Users](sprs/Users.md) 
```

#### from_file
Получение данных из файла. Поддерживаемые форматы `xml,json,yaml,bsl` 

```
from_file(file, format)
```

| Parameter | Requare|Description | Default
| --- | --- | --- | --- |
| `file` | Да | Путь к файлу данных | |
| `format` | Нет | Формат файла (`xml,json,yaml,bsl`) | Определяется по расширению файла |

Пример:
```
{% set s2 = from_file("./test/test1/data/s2.json") %}
...
далее используем переменную s2
```

#### from_dir
Получение данных из каталога с файлами данных. Файлы данных объединяются в единый объект данных в памяти. Поддерживаниемые форматы `xml,json,yaml,bsl` 

```
from_dir(path, mask)
```

| Parameter | Requare|Description|
| --- | --- | --- |
| `path` | Да | Путь к каталогу с файлами данных |
| `mask` | Да | Маска файлов (формат `glob`).|

Пример:
```
{% set s1 = from_dir("./test/test1/data", '**/*.json') %}
{% set s2 = from_dir("./test/test1/data", '**/*') %}
...
Далее используем переменную s1 и s2. 
Имена вложенных каталогов и имена файлов встраиваются в выходную структуру. 
Точка (.) в именах файлов (включая расширение файла) и каталогов заменяется на _
```
