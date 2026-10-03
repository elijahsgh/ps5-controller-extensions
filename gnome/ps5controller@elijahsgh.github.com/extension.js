import St from 'gi://St';
import Clutter from 'gi://Clutter';
import GLib from 'gi://GLib';
import UPowerGlib from 'gi://UPowerGlib';
import * as Main from 'resource:///org/gnome/shell/ui/main.js';
import * as PanelMenu from 'resource:///org/gnome/shell/ui/panelMenu.js';
import * as PopupMenu from 'resource:///org/gnome/shell/ui/popupMenu.js';
import { Extension } from 'resource:///org/gnome/shell/extensions/extension.js';

export default class PS5ControllerExtension extends Extension {
    enable() {
        this._indicator = new PanelMenu.Button(0.0, this.metadata.name, false);

        this._box = new St.BoxLayout({
            vertical: false,
            style_class: 'panel-status-menu-box',
        });
        
        let icon = new St.Icon({
            icon_name: 'input-gaming-symbolic',
            style_class: 'system-status-icon',
        });
        
        this._label = new St.Label({
            text: '',
            y_align: Clutter.ActorAlign.CENTER,
            style: 'margin-left: 5px; font-weight: bold;'
        });

        this._box.add_child(icon);
        this._box.add_child(this._label);
        this._indicator.add_child(this._box);
        
        Main.panel.addToStatusArea(this.uuid, this._indicator);

        this._scriptPath = this.dir.get_child('scripts').get_child('ps5_manager.py').get_path();

        this._upowerClient = UPowerGlib.Client.new_full(null);
        this._deviceSignals = new Map();
        
        this._deviceAddedId = this._upowerClient.connect('device-added', this._syncControllers.bind(this));
        this._deviceRemovedId = this._upowerClient.connect('device-removed', this._syncControllers.bind(this));

        this._syncControllers();
    }

    _syncControllers() {
        // Clear old signal handlers
        for (let [device, signalId] of this._deviceSignals.entries()) {
            device.disconnect(signalId);
        }
        this._deviceSignals.clear();

        let devices = this._upowerClient.get_devices();
        
        for (let device of devices) {
            if (device.kind === UPowerGlib.DeviceKind.GAMING_INPUT) {
                // Watch for percentage changes
                let sigId = device.connect('notify::percentage', this._rebuildMenuFromCache.bind(this));
                this._deviceSignals.set(device, sigId);
            }
        }
        
        this._rebuildMenuFromCache();
    }
    
    _rebuildMenuFromCache() {
        let controllers = [];
        for (let device of this._deviceSignals.keys()) {
            let nativePath = device.native_path || "";
            let mac = nativePath.includes("ps-controller-battery-") ? 
                      nativePath.split("ps-controller-battery-").pop().toUpperCase() : "";
            let name = device.model || "DualSense Controller";
            
            controllers.push({
                id: mac,
                name: name,
                capacity: Math.round(device.percentage)
            });
        }
        this._rebuildMenu(controllers);
    }

    _rebuildMenu(controllers) {
        this._indicator.menu.removeAll();

        if (controllers.length === 0) {
            this._label.set_text('');
            this._indicator.menu.addMenuItem(new PopupMenu.PopupMenuItem("No PS5 Controllers Connected"));
            return;
        }

        this._label.set_text(`${controllers[0].capacity}%`);

        for (let ctrl of controllers) {
            let item = new PopupMenu.PopupBaseMenuItem({ reactive: false });
            
            let layout = new St.BoxLayout({ vertical: false, x_expand: true });
            
            let nameLabel = new St.Label({
                text: `${ctrl.name}: ${ctrl.capacity}%`,
                y_align: Clutter.ActorAlign.CENTER,
                x_expand: true
            });
            
            layout.add_child(nameLabel);
            
            let turnOffBtn = new St.Button({
                style_class: 'button',
                label: 'Turn Off',
                y_align: Clutter.ActorAlign.CENTER,
                style: 'margin-left: 20px; padding: 4px 12px; border-radius: 4px;'
            });
            
            turnOffBtn.connect('clicked', () => {
                this._turnOffController(ctrl.id);
            });
            
            layout.add_child(turnOffBtn);
            item.add_child(layout);
            
            this._indicator.menu.addMenuItem(item);
        }
    }

    _turnOffController(macId) {
        if (!macId) return;
        try {
            GLib.spawn_command_line_async(`python3 ${this._scriptPath} turnoff ${macId}`);
        } catch(e) {
            console.error(`PS5Controller: ${e}`);
        }
    }

    disable() {
        if (this._upowerClient) {
            if (this._deviceAddedId) this._upowerClient.disconnect(this._deviceAddedId);
            if (this._deviceRemovedId) this._upowerClient.disconnect(this._deviceRemovedId);
            
            for (let [device, signalId] of this._deviceSignals.entries()) {
                device.disconnect(signalId);
            }
            this._deviceSignals.clear();
            
            this._upowerClient = null;
        }
        
        if (this._indicator) {
            this._indicator.destroy();
            this._indicator = null;
        }
    }
}
