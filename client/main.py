import asyncio
import dbus
import dbus.service
import dbus.mainloop.glib
import gi
import signal

gi.require_version("Gtk", "4.0")
from gi.repository import GLib

DEVICE_NAME = "MyBLEDevice"
SERVICE_UUID = "12345678-1234-5678-1234-56789abcdef0"
CHARACTERISTIC_UUID = "12345678-1234-5678-1234-56789abcdef1"

data_store = b"Hello BLE!"

class Characteristic(dbus.service.Object):
    def __init__(self, bus, path, uuid, flags):
        dbus.service.Object.__init__(self, bus, path)
        self.uuid = uuid
        self.flags = flags
        self.value = data_store

    @dbus.service.method("org.bluez.GattCharacteristic1", in_signature="", out_signature="ay")
    def ReadValue(self):
        print(f"Read request on {self.uuid}")
        return dbus.Array(bytearray(self.value), signature='y')

    @dbus.service.method("org.bluez.GattCharacteristic1", in_signature="ay", out_signature="")
    def WriteValue(self, value):
        global data_store
        print(f"Write request on {self.uuid}: {bytes(value)}")
        self.value = bytes(value)
        data_store = self.value

class Application(dbus.service.Object):
    def __init__(self, bus):
        dbus.service.Object.__init__(self, bus, "/org/bluez/example")
        self.path = "/org/bluez/example"
        self.characteristics = []

        self.characteristic = Characteristic(bus, f"{self.path}/char1", CHARACTERISTIC_UUID, ["read", "write"])
        self.characteristics.append(self.characteristic)

    def get_path(self):
        return dbus.ObjectPath(self.path)

async def main():
    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
    bus = dbus.SystemBus()
    app = Application(bus)
    loop = GLib.MainLoop()

    def stop_server(signum, frame):
        print("Stopping BLE server...")
        loop.quit()
    
    signal.signal(signal.SIGINT, stop_server)

    print(f"{DEVICE_NAME} is advertising...")
    loop.run()

if __name__ == "__main__":
    asyncio.run(main())
