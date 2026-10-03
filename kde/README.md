# PS5 Controller KDE Plasmoid

A native KDE Plasma 6 widget (Plasmoid) for displaying the battery percentage of a Sony PS5 DualSense controller and turning it off. 

This plasmoid iterates through attached PS5 DualSense controllers to display battery data, and issues USB resets to turn the controller off.

## Udev Rule (Required)

To allow the plasmoid to programmatically reset the controller's USB device node without requiring `sudo` or root privileges, you **must** install a udev rule to grant your logged-in user access.

1. Copy the included udev rule to your system's udev directory:
```bash
sudo cp 99-ps5-controller.rules /etc/udev/rules.d/
```

3. Apply the new rule by running:
```bash
sudo udevadm control --reload-rules && sudo udevadm trigger
```
*(You may need to unplug and plug your controller back in once for the rule to take effect).*

## Packaging & Installation

Because this widget operates natively through scripts, there is no C++ compilation required. It is distributed as a single `PS5Controller.plasmoid` zip file!

To package your code into the `.plasmoid` file, simply run this from the `kde/` directory:
```bash
make
```

You can then install or upgrade it directly from your terminal:
```bash
make install
```
*(This automatically runs the `kpackagetool6` command for you).*

Alternatively, you can install it graphically:
1. Right-click your Plasma desktop or panel and click **Add Widgets...** (or **Enter Edit Mode** -> **Add Widgets**).
2. Click **Get New Widgets...** in the top right corner.
3. Click **Install from local file...**
4. Select the `PS5Controller.plasmoid` file.

## Adding to Panel / Desktop

1. Right-click on your Plasma desktop or panel.
2. Select **Add Widgets...** (or **Enter Edit Mode** -> **Add Widgets**).
3. Search for **"PS5 Controller"**.
4. Drag and drop the widget onto your panel or desktop.
