
.PHONY: prepare_venv install run-dir run-env run

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
	${PYTHON} d2doc.py build \
		--templates ./test/test1/templates \
		--start-templates 'index' \
		--data-dir ./test/test1/data \
		--data-dir-mask '**/*.json' \
		--output-dir './test/test1/doc' \
		--static './test/test1/templates/static' \
		--static './test/test1/templates/static2' \
		--erase-output-dir

run-env: prepare_venv
	export D2DOC_BUILD_TEMPLATES='./test/test1/templates' \
	&& export D2DOC_BUILD_START_TEMPLATES='index' \
	&& export D2DOC_BUILD_DATA_DIR='./test/test1/data' \
	&& export D2DOC_BUILD_DATA_DIR_MASK='**/*.json' \
	&& export D2DOC_BUILD_OUTPUT_DIR='./test/test1/doc' \
	&& export D2DOC_LOG_LEVEL='DEBUG' \
	&& ${PYTHON} d2doc.py build --erase-output-dir

run: run-env