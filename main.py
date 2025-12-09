from utils import pretty_print_server_info, read_any_packet
from mcproto.connection import TCPAsyncConnection
from packets import *

import traceback
import functools
import asyncio


def safely(func):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except ConnectionResetError:
            print("[ERROR] ConnectionResetError")
        except Exception:
            traceback.print_exc(chain=False)

    return wrapper


class BotTemplate:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.threshold = None
        # Bot position
        self.x = None
        self.y = None
        self.z = None

    @safely
    async def ping_server(self):
        async with await TCPAsyncConnection.make_client(
            (self.ip, self.port), 2
        ) as connection:
            await handshake(connection, self.ip, self.port)
            pretty_print_server_info(await get_status(connection), self.ip, self.port)

    @safely
    async def packet_loop(self, conn, username):
        try:
            while True:
                packet_id, payload = await read_any_packet(conn, self.threshold)
                print(f"Packet {hex(packet_id)} ({len(payload)} bytes)")
                await self.handle_packet(conn, packet_id, payload)
        except OSError:
            print(
                f"Connection: {username} - disconnected from server: {self.ip}:{self.port}"
            )
            return

    @safely
    async def handle_packet(self, conn, pid, payload):
        if pid == 0x05:  # Spawn Position
            self.x, self.y, self.z = await read_spawn_position(payload)

    #       elif pid == Xx0X:  # Packet ID
    #           DoSomethingElse(payload)

    @safely
    async def join_server(self, username):
        connection = await TCPAsyncConnection.make_client((self.ip, self.port), 5)

        # Entire login process
        await handshake(connection, self.ip, self.port, 2)
        await login_start(connection, username)

        # Packet compression handling
        self.threshold = await read_set_compression(connection)

        await read_login_success(connection)
        await login_acknowledged(connection, self.threshold)
        # State Play
        await read_join_game(connection)
        await client_settings(connection, self.threshold)

        await self.packet_loop(connection, username)


def main():
    ip = "mc.survival-games.cz"
    port = 25565

    bot = BotTemplate(ip, port)
    asyncio.run(bot.ping_server())
    asyncio.run(bot.join_server("AhojSvete"))


if __name__ == "__main__":
    main()
