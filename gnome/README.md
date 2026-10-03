# PS5 Controller GNOME Extension

A GNOME Shell Extension for displaying the battery percentage of your Sony PS5 DualSense controllers and allowing you to turn them off directly from the top panel.

This extension natively integrates into the GNOME Shell system tray, showing the primary controller's battery percentage next to a gamepad icon. Clicking the icon opens a dropdown menu displaying all connected controllers, their battery levels, and individual "Turn Off" buttons.

## Requirements

You must install the project's udev rule to allow the backend script to programmatically reset the controller's USB device node without requiring `sudo` or root privileges. 

*(If you haven't already installed this from the main project instructions)*:
```bash
sudo cp ../kde/99-ps5-controller.rules /etc/udev/rules.d/
sudo udevadm control --reload-rules && sudo udevadm trigger
```

## Packaging & Installation

This extension is built with modern GJS and ESM (ECMAScript Modules) and targets GNOME 45+. 

To package the extension into a zip file, simply run this from the `gnome/` directory:
```bash
make
```

To install or upgrade the extension on your local machine:
```bash
make install
```

This will automatically copy the extension files into your `~/.local/share/gnome-shell/extensions/` directory.

## Enabling the Extension

After running `make install`, you must restart the GNOME Shell for it to detect the new extension:
- **X11:** Press `Alt+F2`, type `r`, and press `Enter`.
- **Wayland:** Log out and log back in.

Once the shell has restarted, enable the extension via the terminal:
```bash
gnome-extensions enable ps5controller@elijahsgh.github.com
```
*(Alternatively, you can enable it using the "Extensions" GUI app).*
