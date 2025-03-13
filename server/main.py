from bleak import BleakScanner
import asyncio
import argparse

service_uuids = ["AAAAA", "BBBBB"]

async def scan():
    devices = await BleakScanner.discover(
        # return_adv=True,
        service_uuids=service_uuids,
    )
    return devices

if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    args = parser.parse_args()

    devices = []
    try:
        while len(devices) <= 0:
            devices = asyncio.run(scan())
    except KeyboardInterrupt:
        exit(0)

    print(devices)
