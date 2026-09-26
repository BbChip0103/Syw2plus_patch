from pathlib import Path


BRIDGE_SOURCE = Path(__file__).with_name("runtime_bridge.c")


def test_resource_only_probe_does_not_write_population_ledger_or_units() -> None:
    source = BRIDGE_SOURCE.read_text(encoding="utf-8")
    branch = source.split("} else if (op == 7) {", 1)[1].split(
        "} else if (op == 5 || op == 6) {", 1
    )[0]

    assert "SetResource)0x43ed60u" in branch
    assert "SetResource)0x43ed80u" in branch
    assert "0x200a" not in branch
    assert "0x200c" not in branch
    assert "0x1c" not in branch
    assert "0x66b790" not in branch
    assert "0x8990c8" not in branch
