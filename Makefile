
.PHONY: prepare_venv install run-dir run-env run dist

VENV_NAME?=venv
PYTHON=${VENV_NAME}/bin/python

prepare_venv: $(VENV_NAME)/bin/activate

$(VENV_NAME)/bin/activate: requirements.txt
	test -d $(VENV_NAME) || python -m venv $(VENV_NAME)
	${PYTHON} -m pip install -U pip
	${PYTHON} -m pip install -r requirements.txt
	touch $(VENV_NAME)/bin/activate

install: prepare_venv
	
run-dir: prepare_venv
	${PYTHON} -m d2doc build \
		--templates ./d2doc/test/test1/templates \
		--start-templates 'index' \
		--data-dir ./d2doc/test/test1/data \
		--data-dir-mask '**/*.json' \
		--output-dir './d2doc/test/test1/doc' \
		--static './d2doc/test/test1/templates/static' \
		--static './d2doc/test/test1/templates/static2' \
		--erase-output-dir

run-env: prepare_venv
	export D2DOC_BUILD_TEMPLATES='./d2doc/test/test1/templates' \
	&& export D2DOC_BUILD_START_TEMPLATES='index' \
	&& export D2DOC_BUILD_DATA_DIR='./d2doc/test/test1/data' \
	&& export D2DOC_BUILD_DATA_DIR_MASK='**/*.json' \
	&& export D2DOC_BUILD_OUTPUT_DIR='./d2doc/test/test1/doc' \
	&& export D2DOC_LOG_LEVEL='DEBUG' \
	&& ${PYTHON} -m d2doc build --erase-output-dir

run: run-env

dist:
	${PYTHON} setup.py sdist bdist_wheel