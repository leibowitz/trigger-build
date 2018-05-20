all:
	zip -r build.zip . -x "sns.json" -x "setup.cfg" -x "build.zip" -x "Makefile" -x "ca.pem"
