from mcproto.buffer import Buffer


async def read_set_compression(conn):
    _response_len = await conn.read_varint()
    _response = await conn.read(_response_len)
    response = Buffer(_response)
    packet_id = response.read_varint()
    threshold = response.read_varint()

    return threshold
