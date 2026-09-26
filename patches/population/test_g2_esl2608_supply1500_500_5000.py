from pathlib import Path

import pefile
import pytest

from patches.population import g2_esl2608_supply1500_500_5000 as mod


INPUT = Path(__file__).parents[2].parent / "260921_temp"
NAMES = {
    "seven": "[ESL]Syw2plus 2608_AI상점개설_장수7명_전비1600-200-3000_G2_개인500_공용4092_시험용.exe",
    "seven_fixed_start": "[ESL]Syw2plus 2608_AI상점개설_장수7명_전비1600-200-3000_시작자리고정_G2_개인500_공용4092_시험용.exe",
}


@pytest.mark.parametrize("variant", NAMES)
def test_exact_two_operands_and_pe(variant: str) -> None:
    original = (INPUT / NAMES[variant]).read_bytes()
    assert mod.digest(original) == mod.INPUT_SHA256[variant]
    candidate, report = mod.build_candidate(original)
    assert report["variant"] == variant
    assert mod.digest(original) == mod.INPUT_SHA256[variant]
    changed = {i for i, (a, b) in enumerate(zip(original, candidate)) if a != b}
    expected = {i for off, old, new in mod.PATCHES for i in range(off, off + len(old)) if old[i-off] != new[i-off]}
    assert changed == expected
    for off, _, new in mod.PATCHES:
        assert candidate[off : off + len(new)] == new
    pe = pefile.PE(data=candidate, fast_load=True)
    assert len(pe.sections) == 10
    assert not pe.get_warnings()
    pe.close()


@pytest.mark.parametrize("variant", NAMES)
def test_copy_restore_and_version_refusal(variant: str, tmp_path: Path) -> None:
    original = (INPUT / NAMES[variant]).read_bytes()
    source = tmp_path / "source.exe"
    output = tmp_path / "candidate.exe"
    source.write_bytes(original)
    report = mod.create_copy(source, output)
    assert mod.digest(output.read_bytes()) == report["candidate_sha256"]
    with pytest.raises(FileExistsError):
        mod.create_copy(source, output)
    assert mod.restore_copy(output, source) == report["source_sha256"]
    assert output.read_bytes() == original
    with pytest.raises(ValueError, match="exact candidate"):
        mod.restore_copy(output, source)
    changed = bytearray(original)
    changed[0x100] ^= 1
    with pytest.raises(ValueError, match="unsupported"):
        mod.build_candidate(bytes(changed))
