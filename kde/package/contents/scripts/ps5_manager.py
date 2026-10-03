#!/usr/bin/env python3
import os
import fcntl
import sys
import json
import subprocess
import re
import warnings

warnings.filterwarnings('ignore', category=DeprecationWarning)

USBDEVFS_RESET = 21780

def turn_off(target_mac):
    turned_off = 0
    if re.match(r"^([0-9A-F]{2}:){5}[0-9A-F]{2}$", target_mac):
        try:
            subprocess.run(["bluetoothctl", "disconnect", target_mac], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            turned_off += 1
        except Exception:
            pass
            
    battery_dir = f"/sys/class/power_supply/ps-controller-battery-{target_mac.lower()}"
    if os.path.exists(battery_dir):
        device_link = os.path.join(battery_dir, "device")
        if os.path.exists(device_link):
            real_path = os.path.realpath(device_link)
            current_path = real_path
            while current_path != "/" and len(current_path) > 10:
                if os.path.exists(os.path.join(current_path, "busnum")) and os.path.exists(os.path.join(current_path, "devnum")):
                    try:
                        with open(os.path.join(current_path, "busnum"), "r") as f:
                            bus = int(f.read().strip())
                        with open(os.path.join(current_path, "devnum"), "r") as f:
                            dev = int(f.read().strip())
                        dev_node = f"/dev/bus/usb/{bus:03d}/{dev:03d}"
                        with open(dev_node, "w") as f:
                            fcntl.ioctl(f.fileno(), USBDEVFS_RESET, 0)
                        turned_off += 1
                    except Exception:
                        pass
                    break
                current_path = os.path.dirname(current_path)
    return turned_off

def get_battery(client):
    import gi
    gi.require_version('UPowerGlib', '1.0')
    from gi.repository import UPowerGlib
    controllers = []
    try:
        devices = client.get_devices()
        for d in devices:
            if d.get_property("kind") == UPowerGlib.DeviceKind.GAMING_INPUT:
                model = d.get_property("model") or "DualSense Controller"
                native_path = d.get_property("native-path") or ""
                mac = ""
                if "ps-controller-battery-" in native_path:
                    mac = native_path.split("ps-controller-battery-")[-1].upper()
                controllers.append({"id": mac, "name": model, "capacity": int(d.get_property("percentage"))})
    except Exception:
        pass
    return controllers

def daemon_mode():
    import gi
    gi.require_version('UPowerGlib', '1.0')
    from gi.repository import UPowerGlib, GLib

    client = UPowerGlib.Client.new_full(None)
    
    def print_state(*args):
        print(json.dumps(get_battery(client)))
        sys.stdout.flush()

    print_state()
    
    def on_notify(device, pspec):
        print_state()
        
    devices = client.get_devices()
    for d in devices:
        if d.get_property("kind") == UPowerGlib.DeviceKind.GAMING_INPUT:
            d.connect('notify::percentage', on_notify)
        
    def on_device_added(client, device):
        if device.get_property("kind") == UPowerGlib.DeviceKind.GAMING_INPUT:
            device.connect('notify::percentage', on_notify)
        print_state()
        
    client.connect('device-added', on_device_added)
    client.connect('device-removed', print_state)

    loop = GLib.MainLoop()
    try:
        loop.run()
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    if len(sys.argv) > 2 and sys.argv[1] == "turnoff":
        res = turn_off(sys.argv[2])
        print(json.dumps({"turned_off": res}))
    elif len(sys.argv) > 1 and sys.argv[1] == "daemon":
        daemon_mode()
    else:
        import gi
        gi.require_version('UPowerGlib', '1.0')
        from gi.repository import UPowerGlib
        client = UPowerGlib.Client.new_full(None)
        print(json.dumps(get_battery(client)))
