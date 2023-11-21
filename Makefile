SHELL = /bin/bash

help: # Display this message
	@sed -ne '/@sed/!s/# //p' $(MAKEFILE_LIST)
