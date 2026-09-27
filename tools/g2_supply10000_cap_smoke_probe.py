#!/usr/bin/env python3
"""lap691 work -- G2 전비10000 첫 단계: 실 게임 기동 스모크 + 개인/전역 병목 실측.

`patches/population/fixed_supply_10000.py` 후보(원본 대비 두 자리 immediate만
5000->10000)를 격리된 사본에서 실제 기동해 PlayerStruct `+0x2012`(전비 상한)가
살아있는 프로세스에서 10000으로 정확히 읽히는지, 그리고 원본 개인 개체 상한
(`+0x2010`)/전역 공유 슬롯이 patch로 바뀌지 않았는지 실측한다.

Scope: 읽기 전용 스냅샷(`op=snapshot`)만 보낸다. 유닛 생성/자원 지급 등 fixture
쓰기는 이 스크립트의 범위가 아니다(다음 회차가 population fixture로 이어간다).
원본/참고 저장소는 읽기 전용, 새 격리 사본에만 패치를 적용한다.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from tools import runtime_env  # noqa: E402
from patches.population.fixed_supply_10000 import create_copy  # noqa: E402


def free_display() -> str:
    for num in range(150, 250):
        if not Path(f"/tmp/.X{num}-lock").exists() and not Path(f"/tmp/.X11-unix/X{num}").exists():
            return f":{num}"
    raise SystemExit("no free X display found in range")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--timeout", type=float, default=90)
    args = ap.parse_args()

    manifest = runtime_env.prepare(bridge=None, timeout=args.timeout)
    game_root = Path(manifest["game"]["root"])
    prefix = Path(manifest["wine"]["prefix"])
    run_dir = Path(manifest["output"]["run_dir"])
    out_dir = run_dir / "output" / "g2_supply10000_smoke"
    out_dir.mkdir(parents=True, exist_ok=True)

    candidate_path = game_root / "g2_supply_10000.exe"
    candidate_sha = create_copy(game_root / "syw2plus_original.exe", candidate_path)

    display = free_display()
    driver = subprocess.Popen(
        [
            sys.executable,
            str(REPO / "patches/population/runtime_driver.py"),
            "--game-root", str(game_root),
            "--prefix", str(prefix),
            "--out", str(out_dir),
            "--display", display,
            "--exe", "g2_supply_10000.exe",
        ],
    )
    result: dict[str, object] = {
        "candidate_sha256": candidate_sha,
        "manifest_run_dir": str(run_dir),
        "display": display,
    }
    try:
        deadline = time.monotonic() + args.timeout
        session = None
        while time.monotonic() < deadline:
            try:
                session = json.loads((out_dir / "session.json").read_text())
                break
            except (OSError, ValueError):
                time.sleep(0.5)
        if session is None:
            raise SystemExit("driver never wrote session.json (game failed to launch)")
        result["session"] = session
        if session["exe_sha256"] != candidate_sha:
            raise SystemExit("launched exe sha does not match freshly built candidate")

        req_id = 1
        (out_dir / "request.json").write_text(json.dumps({"id": req_id, "op": "snapshot"}))
        response = None
        while time.monotonic() < deadline:
            try:
                response = json.loads((out_dir / "response.json").read_text())
                if response.get("id") == req_id:
                    break
            except (OSError, ValueError):
                pass
            time.sleep(0.5)
        if response is None or response.get("id") != req_id:
            raise SystemExit("no snapshot response before timeout")
        if "error" in response:
            raise SystemExit(f"snapshot op failed: {response['error']}")
        result["snapshot"] = response["state"]

        req_id = 2
        (out_dir / "request.json").write_text(json.dumps({"id": req_id, "op": "stop"}))
        stopped = False
        stop_deadline = time.monotonic() + 15
        while time.monotonic() < stop_deadline:
            if driver.poll() is not None:
                stopped = True
                break
            time.sleep(0.5)
        result["driver_returncode"] = driver.poll()
        result["clean_stop"] = stopped
    finally:
        if driver.poll() is None:
            driver.terminate()
            try:
                driver.wait(timeout=10)
            except subprocess.TimeoutExpired:
                driver.kill()
        subprocess.run(
            ["wineserver", "-k"],
            env=dict(os.environ, WINEPREFIX=str(prefix)),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

    (out_dir / "result.json").write_text(json.dumps(result, indent=2, ensure_ascii=False))
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
