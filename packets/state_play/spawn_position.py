from utils import decode_position


async def read_spawn_position(payload):
    x, y, z = decode_position(payload)
    print(f"[Spawn Position] x={x} y={y} z={z}")
    return x, y, z
