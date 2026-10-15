from __future__ import annotations

import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_embedded_sha256_matches_standard_empty_and_multiblock_vectors(tmp_path: Path) -> None:
    source = tmp_path / "sha256.c"
    binary = tmp_path / "sha256"
    source.write_text(r'''
#include <stdio.h>
#include <string.h>
#include "tools/inmm_stub/g1_sha256.h"
static void print_hash(const void *data, size_t size) {
    G1Sha256 ctx; unsigned char digest[32]; unsigned i;
    g1_sha256_init(&ctx); g1_sha256_update(&ctx, data, size); g1_sha256_final(&ctx, digest);
    for (i=0; i<32; ++i) printf("%02x", digest[i]);
    putchar('\n');
}
int main(void) {
    char repeated[1000]; memset(repeated, 'a', sizeof(repeated));
    print_hash("", 0); print_hash("abc", 3); print_hash(repeated, sizeof(repeated)); return 0;
}
''', encoding="utf-8")
    subprocess.run(["cc", "-Wall", "-Wextra", "-Werror", "-I", str(ROOT), str(source), "-o", str(binary)],
                   check=True, capture_output=True, text=True)
    result = subprocess.run([str(binary)], check=True, capture_output=True, text=True)
    assert result.stdout.splitlines() == [
        "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad",
        "41edece42d63e8d9bf515a9ba6932e1c20cbc9f5a5d134645adb5db1b9737ea3",
    ]
