from bleak import BleakScanner, BleakClient
import asyncio
import argparse

service_uuids = ["AAAAA", "BBBBB"]
devices = {}
reconnect_attempts = 0

def add_device(device: BleakClient):
    devices[device.address] = device

async def remove_device(device: BleakClient):
    if device.is_connected:
        await device.disconnect()

    devices.pop(device.address)

async def cleanup():
    for device in devices:
        print(f"Disconnecting {device.address}")
        await device.disconnect()

async def scan():
    discovered = await BleakScanner.discover(
        # return_adv=True,
        service_uuids=service_uuids,
    )
    print("Found devices:")
    for device in discovered:
        client = BleakClient(device)
        await client.connect()
        
        print(f"Connected to device: {device.name}")


async def disconnected_cbk(client: BleakClient):
    await remove_device(client)

    if reconnect_attempts <= 0:
        print(f"Client disconnected: {client.address}")
    for i in range(1, reconnect_attempts + 1):
        print(f"Client disconnected: {client.address} . Reconnect attempt {i}")
        new_client = BleakClient(client.address)
        await new_client.connect()

        if new_client.is_connected:
            add_device(new_client)
        else:
            continue

    print(f"Failed to reconnect to: {client.address}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("--reconnect_attempts", help="The number of times to reconnect to a device after it has disconnected", type=int, default=3)

    args = parser.parse_args()

    try:
        while len(devices) <= 0:
            asyncio.run(scan())
    except KeyboardInterrupt:
        exit(0)

    match input():
        case "scan":
            asyncio.run(scan())
        case "start":
            # start recording
            pass
        case "stop":
            # stop recording
            pass

    print(devices)

    asyncio.run(cleanup())
