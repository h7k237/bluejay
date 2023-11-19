QUIET = @

BUILD_DIR = ./bin/build
VENV_DIR = $(BUILD_DIR)/venv

.PHONY: help
help:
	@echo "Makefile for bluejayhost."
	@echo
	@echo "Usage:"
	@echo "    make install        Install the python virtual environment."
	@echo "    make clean          Clean up the build."
	@echo "    make help           Show this help message."

.PHONY: install
install: requirements.txt
	$(info Installing Python packages...)
	$(QUIET)python3 -m venv $(VENV_DIR)
	$(QUIET)/bin/sh -c " \
	    source $(VENV_DIR)/bin/activate; \
	    pip3 install --disable-pip-version-check -r requirements.txt; \
	"

.PHONY: clean
clean:
	$(QUIET)rm -rf $(BUILD_DIR)
