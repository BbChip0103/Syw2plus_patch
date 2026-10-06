from __future__ import annotations

import ctypes

import pytest

from patches.population import runtime_driver


def _iov(pointer) -> runtime_driver.IOV:
    return ctypes.cast(pointer, ctypes.POINTER(runtime_driver.IOV)).contents


def test_read_uses_single_local_and_remote_iov_and_returns_zero_bytes(monkeypatch):
    payload = b"A\x00BC"
    observed = {}

    def process_vm_readv(pid, local_ptr, local_count, remote_ptr, remote_count, flags):
        local = _iov(local_ptr)
        remote = _iov(remote_ptr)
        observed.update(
            pid=pid,
            local_base=local.base,
            local_size=local.size,
            remote_base=remote.base,
            remote_size=remote.size,
            local_count=local_count,
            remote_count=remote_count,
            flags=flags,
        )
        ctypes.memmove(local.base, payload, len(payload))
        return len(payload)

    monkeypatch.setattr(runtime_driver.LIBC, "process_vm_readv", process_vm_readv)
    result = runtime_driver.read(321, 0x1234, len(payload))

    assert result == payload
    assert observed == {
        "pid": 321,
        "local_base": observed["local_base"],
        "local_size": len(payload),
        "remote_base": 0x1234,
        "remote_size": len(payload),
        "local_count": 1,
        "remote_count": 1,
        "flags": 0,
    }
    assert observed["local_base"]


@pytest.mark.parametrize(("count", "errno"), [(2, 5), (-1, 13)])
def test_read_preserves_short_or_negative_read_error(count, errno, monkeypatch):
    monkeypatch.setattr(runtime_driver.LIBC, "process_vm_readv", lambda *args: count)
    monkeypatch.setattr(ctypes, "get_errno", lambda: errno)

    with pytest.raises(OSError) as caught:
        runtime_driver.read(321, 0x1234, 4)

    assert caught.value.errno == errno
    assert str(caught.value) == f"[Errno {errno}] read 321:1234, got {count}/4"
