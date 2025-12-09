from mcproto.buffer import Buffer

import json


async def status_request(conn):
    packet = Buffer()
    packet.write_varint(0x00)  # Status request packet ID

    await conn.write_varint(len(packet))
    await conn.write(packet)


async def read_status_response(conn):
    _response_len = await conn.read_varint()
    _response = await conn.read(_response_len)
    response = Buffer(_response)
    packet_id = response.read_varint()

    return response, packet_id


async def get_status(conn, full=False):
    await status_request(conn)
    response, _ = await read_status_response(conn)

    if full:
        return json.loads(response.read_utf())
    else:
        data = json.loads(response.read_utf())
        return [
            data["version"]["protocol"],
            data["version"]["name"],
            data["players"]["max"],
            data["players"]["online"],
            data["description"],
        ]
