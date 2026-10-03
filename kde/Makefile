.PHONY: all build install clean

all: build

build:
	@echo "Packaging plasmoid..."
	cd package && zip -r ../PS5Controller.plasmoid *
	@echo "Created PS5Controller.plasmoid"

install: build
	@echo "Installing plasmoid..."
	kpackagetool6 -t Plasma/Applet -u PS5Controller.plasmoid || kpackagetool6 -t Plasma/Applet -i PS5Controller.plasmoid

clean:
	rm -f PS5Controller.plasmoid
