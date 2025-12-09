from mcproto.protocol.base_io import StructFormat
from utils import compression_helper
from mcproto.buffer import Buffer


async def client_settings(conn, threshold):
    packet = Buffer()
    packet.write_varint(0x15)
    packet.write_utf("en_GB")
    packet.write_value(StructFormat.BYTE, 1)
    packet.write_value(StructFormat.BYTE, 0)
    packet.write_value(StructFormat.BOOL, False)
    skin_parts = (
        0x01  # cape
        | 0x02  # jacket
        | 0x04  # left sleeve
        | 0x08  # right sleeve
        | 0x10  # left pants leg
        | 0x20  # right pants leg
        | 0x40  # hat
    )
    packet.write_value(StructFormat.UBYTE, skin_parts)

    await compression_helper(conn, threshold, bytes(packet))
