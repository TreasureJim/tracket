import asyncio
import dbus
import dbus.service
import dbus.mainloop.glib
import signal
from gi.repository import GLib

DEVICE_NAME = "MyBLEDevice"
SERVICE_UUID = "12345678-1234-5678-1234-56789abcdef0"
CHARACTERISTIC_UUID = "12345678-1234-5678-1234-56789abcdef1"
ADAPTER_PATH = "/org/bluez/hci0"

data_store = b"Hello BLE!"

class Advertisement(dbus.service.Object):
    """Handles BLE advertising"""
    
    def __init__(self, bus):
        path = "/org/bluez/example/advertisement"
        dbus.service.Object.__init__(self, bus, path)
        self.bus = bus

    @dbus.service.method("org.freedesktop.DBus.Properties", in_signature="ss", out_signature="v")
    def Get(self, interface, prop):
        if interface == "org.bluez.LEAdvertisement1":
            if prop == "Type":
                return "peripheral"
            if prop == "ServiceUUIDs":
                return [SERVICE_UUID]
        raise dbus.exceptions.DBusException("org.freedesktop.DBus.Error.UnknownProperty", "Unknown property")

    @dbus.service.method("org.freedesktop.DBus.Properties", in_signature="s", out_signature="a{sv}")
    def GetAll(self, interface):
        if interface == "org.bluez.LEAdvertisement1":
            return {"Type": "peripheral", "ServiceUUIDs": [SERVICE_UUID]}
        return {}

    @dbus.service.method("org.bluez.LEAdvertisement1", in_signature="")
    def Release(self):
        print("Advertisement released")

def register_advertisement(bus):
    """Registers advertisement with BlueZ"""
    adapter = dbus.Interface(bus.get_object("org.bluez", ADAPTER_PATH), "org.freedesktop.DBus.Properties")
    adapter.Set("org.bluez.Adapter1", "Powered", dbus.Boolean(True))
    
    ad_manager = dbus.Interface(bus.get_object("org.bluez", ADAPTER_PATH), "org.bluez.LEAdvertisingManager1")
    
    ad = Advertisement(bus)
    ad_manager.RegisterAdvertisement(ad, {})

    print("Advertisement registered")

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

    register_advertisement(bus)

    print(f"{DEVICE_NAME} is advertising...")

    def stop_server(signum, frame):
        print("Stopping BLE server...")
        loop.quit()
    
    signal.signal(signal.SIGINT, stop_server)
    loop.run()

if __name__ == "__main__":
    asyncio.run(main())
