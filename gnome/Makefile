UUID = ps5controller@elijahsgh.github.com
EXT_DIR = ~/.local/share/gnome-shell/extensions/$(UUID)

.PHONY: all build install clean

all: build

build:
	@echo "Packaging GNOME extension..."
	cd $(UUID) && zip -r ../PS5Controller-GNOME.zip *
	@echo "Created PS5Controller-GNOME.zip"

install:
	@echo "Installing GNOME extension..."
	mkdir -p $(EXT_DIR)
	cp -r $(UUID)/* $(EXT_DIR)/
	@echo "Installed to $(EXT_DIR)"
	@echo "Please restart GNOME Shell (Alt+F2 -> r -> Enter on X11, or log out/in on Wayland)"
	@echo "Then enable it with: gnome-extensions enable $(UUID)"

clean:
	rm -f PS5Controller-GNOME.zip
