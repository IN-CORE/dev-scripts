# Copyright 2017 Palantir Technologies, Inc.
import argparse
import json
import logging
import logging.config
import sys
from . import language_server
from .python_ls import PythonLanguageServer
import jsonrpc
import asyncio
import websockets

LOG_FORMAT = "%(asctime)s UTC - %(levelname)s - %(name)s - %(message)s"
server_handler = PythonLanguageServer()


def add_arguments(parser):
    parser.description = "Python Language Server"

    parser.add_argument(
        "--tcp", action = "store_true",
        help = "Use TCP server instead of stdio"
    )
    parser.add_argument(
        "--host", default = "127.0.0.1",
        help = "Bind to this address"
    )
    parser.add_argument(
        "--port", type = int, default = 2087,
        help = "Bind to this port"
    )

    parser.add_argument(
        "--log-file",
        help = "Redirect logs to the given file instead of writing to stderr."
               "Has no effect if used with --log-config."
    )
    parser.add_argument(
        "--log-config",
        help = "Path to a JSON file containing Python logging config."
    )


def main():
    parser = argparse.ArgumentParser()
    add_arguments(parser)
    args = parser.parse_args()

    if args.log_config:
        with open(args.log_config, 'r') as f:
            logging.config.dictConfig(json.load(f))
    elif args.log_file:
        logging.basicConfig(filename = args.log_file, level = logging.WARNING, format = LOG_FORMAT)
    else:
        logging.basicConfig(level = logging.WARNING, format = LOG_FORMAT)

    if args.tcp:
        language_server.start_tcp_lang_server(args.host, args.port, PythonLanguageServer)
    else:
        server = websockets.serve(handle, 'localhost', 2087)

        asyncio.get_event_loop().run_until_complete(server)
        asyncio.get_event_loop().run_forever()
        # stdin, stdout = _binary_stdio()
        # language_server.start_io_lang_server(stdin, stdout, PythonLanguageServer)


async def handle(websocket, path):
    server_handler.websocket = websocket

    while True:
        msg = await websocket.recv()
        pos = msg.find('\r\n\r\n')
        data = msg[pos + 4:]

        try:
            # data = self._read_message()
            response = jsonrpc.JSONRPCResponseManager.handle(data, server_handler)
            if response is not None:
                websocket.send('Content-Length: 105\r\n\r\n{"jsonrpc":"2.0","method":"window/logMessage","params":{"type":4,'
                                     '"message":"Message Received."}}')
                await server_handler._write_message(response.data)
                # await websocket.send(send_msg)
        except Exception:
            print("Language server shutting down for uncaught exception")
            break


def _binary_stdio():
    """Construct binary stdio streams (not text mode).

    This seems to be different for Window/Unix Python2/3, so going by:
        https://stackoverflow.com/questions/2850893/reading-binary-data-from-stdin
    """
    PY3K = sys.version_info >= (3, 0)

    if PY3K:
        stdin, stdout = sys.stdin.buffer, sys.stdout.buffer
    else:
        # Python 2 on Windows opens sys.stdin in text mode, and
        # binary data that read from it becomes corrupted on \r\n
        if sys.platform == "win32":
            # set sys.stdin to binary mode
            import os
            import msvcrt
            msvcrt.setmode(sys.stdin.fileno(), os.O_BINARY)
            msvcrt.setmode(sys.stdout.fileno(), os.O_BINARY)
        stdin, stdout = sys.stdin, sys.stdout

    return stdin, stdout
