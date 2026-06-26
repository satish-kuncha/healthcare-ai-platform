# main.py
import asyncio
from workflows.console_loop import run_console


if __name__ == "__main__":
    asyncio.run(run_console())