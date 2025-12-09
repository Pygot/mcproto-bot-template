from mcproto.protocol.base_io import StructFormat
from mcproto.buffer import Buffer


async def handshake(conn, ip, port, intent_state=1):
    handshake = Buffer()
    handshake.write_varint(47)
    handshake.write_utf(ip)
    handshake.write_value(StructFormat.USHORT, port)
    handshake.write_varint(intent_state)  # 1 for Status, 2 for Login, 3 for Transfer.
    packet = Buffer()
    packet.write_varint(0x00)  # Handshake packet ID
    packet.write(handshake)

    await conn.write_varint(len(packet))  # size of packet id + data
    await conn.write(packet)
