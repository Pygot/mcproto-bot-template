from urllib.request import urlopen
from mcproto.buffer import Buffer
from hashlib import md5
from uuid import UUID

import struct
import zlib
import json


def pretty_print_server_info(info, ip, port):
    protocol, version_text, online, max_players, motd = info

    labels = [
        "Server IP",
        "Server Port",
        "Protocol Version",
        "Game Version",
        "Max Players",
        "Players Online",
        "MOTD",
    ]

    values = [ip, port, protocol, version_text, online, max_players, motd]

    longest = max(len(label) for label in labels)

    for label, value in zip(labels, values):
        if isinstance(value, str) and "\n" in value:
            print(f"{label:<{longest}} :")
            for line in value.splitlines():
                print(f"{' ' * (longest + 3)}{line}")
        else:
            print(f"{label:<{longest}} : {value}")


def get_offline_uuid(username):
    hash = md5(f"OfflinePlayer:{username}".encode("utf-8")).digest()
    return str(UUID(bytes=hash))


def get_online_uuid(username):
    url = f"https://api.mojang.com/users/profiles/minecraft/{username}"
    try:
        with urlopen(url, timeout=1) as response:
            data = json.loads(response.read().decode("utf-8"))
            uuid = data["id"]
            return str(UUID(uuid))
    except Exception:
        return "Could not reach mojang api!"


async def compression_helper(conn, threshold, packet):
    len_packet = len(packet)
    if len_packet >= threshold:  # Above threshold - compressed
        await conn.write_varint(len_packet)
        await conn.write(zlib.compress(packet))
    else:
        await conn.write_varint(len_packet)
        await conn.write(packet)


async def read_any_packet(conn, threshold):
    packet_length = await conn.read_varint()
    packet_body = await conn.read(packet_length)
    buf = Buffer(packet_body)

    data_length = buf.read_varint()
    remaining = buf.remaining
    data_bytes = buf.read(remaining)

    if threshold is None or data_length == 0:
        packet_data = data_bytes
    else:
        packet_data = zlib.decompress(data_bytes)

        if len(packet_data) != data_length:
            raise Exception(
                f"Decompressed size {len(packet_data)} != expected {data_length}"
            )
    pdata = Buffer(packet_data)

    packet_id = pdata.read_varint()

    payload_length = pdata.remaining
    payload = pdata.read(payload_length)

    return packet_id, payload


def decode_position(pos):
    (signed_packed,) = struct.unpack(">q", pos)
    pos = signed_packed & ((1 << 64) - 1)

    x = pos >> 38
    y = (pos >> 26) & 0xFFF
    z = pos & 0x3FFFFFF

    return x, y, z
