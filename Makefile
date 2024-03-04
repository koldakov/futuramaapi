SHELL = /bin/bash

help: # Display this message
	@sed -ne '/@sed/!s/# //p' $(MAKEFILE_LIST)

messages-init: # locale=LANG, init LANG language
	@test $${locale?Please specify locale. Example \"locale=en_CA\"}
	@pybabel init -l $(locale) -i locale/messages.pot -d locale

messages-extract: # Extract messages to locale/messages.pot
	@pybabel extract \
	--version=0.0.1 \
	--msgid-bugs-address=coldie322@gmail.com \
	--project=FuturamaAPI \
	--copyright-holder=FuturamaAPI \
	--mapping babel.cfg \
	--output-file=locale/messages.pot \
	.

messages: # Update all locales
	@$(MAKE) messages-extract
	@pybabel update --input-file=locale/messages.pot --output-dir=locale

messages-compile: # Generate .mo files for all locales
	@pybabel compile --directory=locale

tests: # Run tests
	@python -m pytest
