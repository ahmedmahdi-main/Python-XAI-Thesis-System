"""Test-only network guard, enabled explicitly by XAI_TEST_OFFLINE=1."""

import os
import socket

if os.environ.get("XAI_TEST_OFFLINE") == "1":
    _connect = socket.socket.connect
    _connect_ex = socket.socket.connect_ex
    _getaddrinfo = socket.getaddrinfo
    _local = {"localhost", "127.0.0.1", "::1", None}

    def _check(host):
        if host not in _local:
            raise OSError(f"Offline acceptance test denied external network: {host}")

    def connect(connection, address):
        if isinstance(address, tuple):
            _check(address[0])
        return _connect(connection, address)

    def connect_ex(connection, address):
        if isinstance(address, tuple):
            _check(address[0])
        return _connect_ex(connection, address)

    def getaddrinfo(host, *args, **kwargs):
        _check(host)
        return _getaddrinfo(host, *args, **kwargs)

    socket.socket.connect = connect
    socket.socket.connect_ex = connect_ex
    socket.getaddrinfo = getaddrinfo
