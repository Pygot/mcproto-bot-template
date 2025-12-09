from utils import compression_helper
from mcproto.buffer import Buffer


async def login_start(conn, username):
    packet = Buffer()
    packet.write_varint(0x00)  # Packet ID
    packet.write_utf(username)

    await conn.write_varint(len(packet))
    await conn.write(packet)


async def read_login_success(conn):
    _response_len = await conn.read_varint()
    _response = await conn.read(_response_len)
    response = Buffer(_response)
    packet_id = response.read_varint()

    return response, packet_id


async def login_acknowledged(conn, threshold):
    packet = Buffer()
    packet.write_varint(0x03)

    await compression_helper(conn, threshold, packet)
