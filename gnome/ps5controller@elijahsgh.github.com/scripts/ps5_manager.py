#!/usr/bin/env python3
import os
import fcntl
import sys
import json
import subprocess
import re

USBDEVFS_RESET = 21780

def get_battery():
    controllers = []
    base_dir = "/sys/class/power_supply"
    if not os.path.exists(base_dir):
        return controllers
    for d in os.listdir(base_dir):
        try:
            is_ps5 = False
            model = ""
            mac = ""
            
            # Extract MAC from directory
            if "ps-controller-battery-" in d:
                mac = d.split("ps-controller-battery-")[-1].upper()
            
            # Check model_name if it exists
            model_path = os.path.join(base_dir, d, "model_name")
            if os.path.exists(model_path):
                with open(model_path, "r") as f:
                    model = f.read().strip()
                if "DualSense" in model or "DualShock" in model or "PS5" in model:
                    is_ps5 = True
                    
            # Fallback to checking the directory name itself
            if not is_ps5 and "ps-controller-battery" in d:
                is_ps5 = True
                model = "DualSense Controller"
                
            if is_ps5:
                with open(os.path.join(base_dir, d, "capacity"), "r") as f:
                    cap = int(f.read().strip())
                controllers.append({"id": mac, "name": model, "capacity": cap})
        except Exception:
            pass
    return controllers

def turn_off(target_mac):
    turned_off = 0
    
    # 1. Try Bluetooth disconnect
    if re.match(r"^([0-9A-F]{2}:){5}[0-9A-F]{2}$", target_mac):
        try:
            subprocess.run(["bluetoothctl", "disconnect", target_mac], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            turned_off += 1
        except Exception:
            pass
            
    # 2. Try USB disconnect by tracing the sysfs tree up to the usb_device
    battery_dir = f"/sys/class/power_supply/ps-controller-battery-{target_mac.lower()}"
    if os.path.exists(battery_dir):
        device_link = os.path.join(battery_dir, "device")
        if os.path.exists(device_link):
            real_path = os.path.realpath(device_link)
            # Traverse upwards to find the USB device root containing busnum and devnum
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

if __name__ == "__main__":
    if len(sys.argv) > 2 and sys.argv[1] == "turnoff":
        res = turn_off(sys.argv[2])
        print(json.dumps({"turned_off": res}))
    else:
        print(json.dumps(get_battery()))
