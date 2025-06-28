import asyncio
from multiprocessing import Process

from media_server import app
from main import main as bot_main


def run_media_server() -> None:
    app.run(host="0.0.0.0", port=8181)


async def run_both() -> None:
    server = Process(target=run_media_server)
    server.start()
    try:
        await bot_main()
    finally:
        server.terminate()
        server.join()


if __name__ == "__main__":
    asyncio.run(run_both())
