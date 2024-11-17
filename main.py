import asyncio

import application


async def main() -> None:
    app = application.Application("config.toml")
    await app.run()
    return


if __name__ == "__main__":
    asyncio.run(main())
