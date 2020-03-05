import click
import yaml
from jinja2 import Environment
from jinja2 import Template
from collections import deque
from collections import namedtuple
from jinja2.loaders import FileSystemLoader
import json
import os
import sys
import logging
import pathlib
import xmltodict
import shutil

env = Environment(trim_blocks=True, lstrip_blocks=True)

supported_input_format_file = ['json', 'yaml', 'yml', 'xml']

# Config logging
log = logging.getLogger("techdoc")
log.setLevel(logging.DEBUG)
fh = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
log.addHandler(fh)
deque = deque()
urls = list()
Record = namedtuple("Record", ['url', 'target_template', 'data'])
ctx = {}


def template_function(func):
    env.globals[func.__name__] = func
    return func


@template_function
def url(**param):
    """
    # Обязательные параметры
    # url - шаблон url
    # target_template - имя шаблона
    # data - данные для передачи в шаблон
    """
    # Рендерим url
    tmplt = env.from_string(param['url'])
    new_url = tmplt.render(**param)

    # Регистрируем страницу для обработки
    if new_url not in urls:
        rec = Record(
            url=new_url, target_template=param['target_template'], data=param['data'])
        deque.append(rec)
        urls.append(new_url)
        log.info("Finded and registered new url %s" % new_url)

    # Возвращаем url
    return new_url


@template_function
def from_file(file, format=''):

    if not format:
        extension = file.split('.')[-1]
        format = extension.lower()
    with open(file, "r", encoding='utf-8') as read_file:
        if format == 'json':
            return json.load(read_file)
        elif format == 'yaml' or format == 'yml':
            return yaml.load(read_file)
        elif format == 'xml':
            ord_dct = xmltodict.parse(
                read_file.read(), process_namespaces=False, encoding='utf-8')
            return ord_dct
    return None    

@template_function
def from_dir(path, mask):
    log.info(" Loading data from %s" % str(path))
    data = {}
    root = pathlib.Path(path)
    for data_file in root.glob(mask):
        if data_file.is_file():
            
            filename = os.path.basename(os.path.realpath(data_file))
            relpath = os.path.relpath(data_file, path)
            file_path = os.path.realpath(data_file)
            name = os.path.splitext(filename)[0]

            # Skiop file If file extension not in suppoted format
            extension = file_path.split('.')[-1]
            if extension not in supported_input_format_file:
                log.debug(" Skip %s" % data_file)
                continue

            log.info(" Loaded %s" % str(data_file))
            lnk = relpath.split('/')
            for i in range(len(lnk)):
                lnk[i] = lnk[i].replace('.', '_')
            rec_key = '/'.join(lnk)
            data[rec_key] = from_file(file_path)

    return _nest_dict(data)


def _nest_dict(dict1):
    result = {}
    for k, v in dict1.items():
        _split_rec(k, v, result)
    return result


def _split_rec(k, v, out):
    k, *rest = k.split('/', 1)
    if rest:
        _split_rec(rest[0], v, out.setdefault(k, {}))
    else:
        out[k] = v


@click.group()
@click.option("--log-level", "log_level", envvar='LOG_LEVEL', required=False,
              help="Log level [CRITICAL, FATAL, ERROR, WARNING, DEBUG, INFO, NOTSET]",)
def cli(log_level):
    if log_level:
        log.setLevel(log_level)
    else:
        log.setLevel(logging.INFO)


@cli.command()
@click.option("--templates", "-t", "templates", envvar='TEMPLATES', required=False,
              help="Path to template files.",
              type=click.Path(exists=True, dir_okay=True, readable=True),)
@click.option("--start-templates", "-s", "start_templates", default="main.j2", envvar='START_TEMPLATES', required=False,
              help="Root templates separated by comma.",)
@click.option("--data-file", "-f", "data_file", envvar='DATA_FILE', required=False,
              help="Input data file (Global for all templates).",
              type=click.Path(exists=True, dir_okay=False, readable=True),)
@click.option("--data-dir", "-d", "data_dir", envvar='DATA_DIR', required=False,
              help="Input data dir (Global for all templates).",
              type=click.Path(exists=True, dir_okay=True, readable=True),)
@click.option("--data-dir-mask", "-m", "data_dir_mask", envvar='DATA_DIR_MASK', required=False,
              help="Files mask for option '--data-dir-mask'.",)
@click.option("--output-dir", "-o", "output_dir", default="./doc", envvar='OUTPUT_DIR', required=False,
              help="Output dir for documentation.",
              type=click.Path(exists=True, dir_okay=True, readable=True),)
@click.option("--erase-output-dir", default=False, is_flag=True, required=False,
              help="Erase output dir befor build.",)
@click.option("--output-format", "output_format", default="md", envvar='OUTPUT_FORMAT', required=False,
              help="File extention for output files.",)
def build(templates, start_templates, data_file, output_dir, erase_output_dir, data_dir, output_format, data_dir_mask):
    log.info('Build documentation')

    global ctx

    # Erase output dir if non empty and set key "--erase-output-dir"
    if output_dir and erase_output_dir:
        log.debug("Erase output dir '%s'" % str(output_dir))

        root = pathlib.Path(output_dir)
        for p in root.glob('*'):
            if p.is_dir():
                shutil.rmtree(p)
                log.debug(" Deleted '%s'" % str(p))
            elif p.is_file():
                os.remove(p)
                log.debug(" Deleted '%s'" % str(p))

    # Set templates dir
    file_loader = FileSystemLoader(templates)
    env.loader = file_loader

    # If set --data-file parameter read data from file
    if data_file:
        log.info("Load global data from file '%s'" % data_file)
        with open(data_file) as file_handler:
            json_data = file_handler.read()
            # ctx = (json.loads(json_data))
            gl = (json.loads(json_data))
            env.globals.update(gl)

    # If set --data-dir parameter read data from dir
    if data_dir and data_dir_mask:
        log.info("Loading global data from dir '%s' with mask '%s'" %
                 (data_dir, data_dir_mask))
        gl = from_dir(data_dir, data_dir_mask)
        env.globals.update(gl)

    # Add starts template
    tmplts = start_templates.split(',')
    log.info("Adding main templates in queue")
    for tmpl in tmplts:
        url = ''.join([tmpl, '.', output_format])
        rec = Record(url=url, target_template=''.join([tmpl, '.j2']),
                     data=ctx)
        deque.append(rec)
        urls.append(url)
        log.info(" Added '%s'" % str(urls))

    # Proccess queue
    log.info("Proccess")
    while deque:
        # Get element
        rec = deque.popleft()
        log.info("Proccessing template '%s' for url '%s'" %
                 (rec.target_template, rec.url))

        # Render
        template = env.get_template(rec.target_template)
        doc = template.render(rec.data)

        # Get file path
        file_path = os.path.join(output_dir, rec.url)
        log.debug("File path (rel_file_path) '%s'" % file_path)

        # Get file name
        filename = os.path.basename(os.path.realpath(file_path))

        # Get dirname
        dirname = os.path.dirname(os.path.realpath(file_path))

        # Create dirs
        try:
            os.makedirs(dirname)
        except:
            pass

        # Save rendered document
        full_path = os.path.join(dirname, filename)
        try:
            with open(full_path, 'x', encoding='utf-8') as res_file:
                res_file.write(doc)
                log.info("Saved to '%s'" % full_path)
        except:
            log.error("Can not save rendered document", exc_info=1)


if __name__ == '__main__':
    cli(auto_envvar_prefix='D2DOC')
