#!/usr/bin/env python3
"""lap519 middle — W32(lap518 work) 독립 검수: 원시 비참조 재집계 + 반증조건② 원인 판별 (읽기 전용).

원본 EXE와 lap518 원시 `samples.jsonl`을 **읽기만** 한다. 바이너리/메모리 쓰기 0, 게임 실행 0.
lap518의 `build_funnel_summary.json`·`run_summary.json`은 재집계에 쓰지 않는다(비교 숫자는 lap518 문서
`analysis/memory_maps/ai_build_order_funnel_probe_lap518_20260923.md` §2 표를 이 파일에 옮겨 적은 값이다).

쟁점: W32 카드 §3 반증조건②("`+0xD32==1`이 아닌 표본에서 `+0x33AC`가 바뀜")가 8/8 owner에서 성립했다.
lap518은 (A) 스케줄러 8-tick 이하 초고속 종료 vs (B) SCH §2 모델 결함을 미판별로 남겼다.
lap519 가설: 카드가 상태1의 **같은 호출 안 종료 경로**를 빠뜨렸다 — 스케줄러 `0x43F871` 블록이
`[+0x33AC]=tick`·`+0xD32=1`·`+0xD34=1` 후 같은 호출에서 `0x43FB62`→`FUN_0043E0E0` 상태1(`0x43E113`)로 가고,
`call 0x43DBB0`이 0이면 곧바로 `call 0x43F5A0`(+0xD32·+0xD34 = 0)으로 끝난다. 그러면 다음 표본은
`+0x33AC`만 바뀌고 `+0xD32==0`인 상태를 본다 ⇒ 반증조건②는 SCH 모델 결함이 아니라 카드 설계 결함이다.

사전 고정 단언(데이터 개봉 전에 이 파일에 적은 것):
  A1 원본 SHA256 = b56986e0….
  A2 `0x43F871`~`0x43F8A2`: `[esi+0x33AC]` 쓰기 직후 `+0xD32`·`+0xD34`에 1을 쓰고 `jmp 0x43FB62`
     (+0x33AC 쓰기와 +0xD32=1이 분리 불가 ⇒ "33AC가 +0xD32=1 없이 바뀐다"는 모델 결함(B)는 바이트로 불가).
  A3 `0x43E113`~`0x43E13C`: `call 0x43DBB0; test eax,eax; jne 0x43E13D; mov ecx,edi; call 0x43F5A0; ... ret`
     (선택 실패 = 같은 호출 안 오더 종료).
  A4 `0x43E13D`~`0x43E173`: 선택 성공 시 `+0xD34` = 2 또는 4를 쓰고 ret — 같은 호출에서 발부(`+0x3A70` 쓰기) 없음.
  B1 samples.jsonl SHA256 = b695365c…, 1,438줄, 표본 간 tick 간격 최대 ≤ 20.
  B2 비참조 재집계 f_idle(3자리)·S·C·B·D·반증표본 수가 lap518 §2 표와 8/8 일치.
  B3 모든 `+0x33AC` 변화의 새 값 t_s가 (직전 표본 tick, 현재 표본 tick] 안에 있다(표본 사이 시작, 누락 없음).
  B4 연속 시작 간격 t_s − t_s(prev) > 100 (쿨다운 위반 0, 바이트 `jle` 규칙).
  B5 [핵심, A3/A4에서 유도] 반증표본 중 `sample_tick − t_s < 8`(그 owner의 다음 스케줄러 호출이 표본 전에
     없었음)인 것은 **전부** 같은 구간에서 `+0x3A70` 변화가 없다 — 오더가 설정된 그 호출 안에서
     선택 실패(`0x43DBB0`==0)로 끝났다는 뜻이다. 1건이라도 발부가 있으면 가설 기각.
  B6 `+0x3A70` 변화가 있는 모든 구간에 대해, 그 구간 또는 직전 구간 끝에서 건설 오더가 살아 있었다
     (직전 표본 `+0xD32==1` 또는 같은 구간 안 새 시작) — 발부는 건설 오더 안에서만 일어난다.
  O1 [관찰] 시작별 운명: ISSUED(수명 안 발부) / ENDED_NO_ISSUE, 반증표본의 gap 분포(<8, 8~15, ≥16)와
     그 안 발부 동반 수. 같은 호출 선택 실패 하한 SF_lb = B5 대상 수.
  O2 [관찰] 반증표본의 `mask_active_count` 분포(0 여부) — 선택 실패가 "후보 0"만으로 설명되는지.

[사후 추가 — 1차 실행(단언 전부 PASS) 뒤 원시를 본 다음 적은 것. 사전 등록 아님, 라벨 근거로 쓰지 않는다]
  1차 결과 B5 대상은 2건뿐이었고 gap<8 시작 354건 중 352건이 `+0xD32==1`이었다 ⇒ 위 lap519 가설
  ("같은 호출 선택 실패가 주 기전")은 **기각**(같은 호출 종료 2/354). 대신 오더가 두 번째 호출에서 끝난다.
  P5 [정적] `[0x43E174,0x43E2FD)`(상태2): `F5A0` 호출 2곳(`0x43E252`·`0x43E2D8`), 성공 끝 `+0xD34=3` 후 ret,
     `+0x3A70` 쓰기 없음 ⇒ 두 번째 호출(start+8)에서는 발부가 불가능, 종료면 상태2 실패다.
  P6 [원시] gap∈[8,16) 시작 구간(=start+8 호출 1회만 지남)에서 `+0x3A70` 변화 0건.
  O3 gap<8 & `+0xD32==1` 시작(=선택 직후 관측)의 상태·선택 종·운명(발부/무발부, 다음 표본까지 종료 여부).
  O4 gap∈[8,16) 시작의 `+0xD32` 0/1 분할과 1인 표본의 `+0xD34` 값 ⇒ 상태2 실패율 추정.

사용법:
    python3 docs/history/laps/probes/20260923_lap519_middle_w32_independent_review.py

exit 0 = 모든 단언 통과. exit 1 = 단언 실패. B5가 실패하면 lap519 가설(카드 설계 결함)이 기각된다.
프로세스 exit 0 자체는 제품 검증이 아니다.
"""

from __future__ import annotations

import collections
import hashlib
import json
import pathlib
import sys

import capstone
import pefile

WORKSPACE = pathlib.Path(__file__).resolve().parents[5]
ORIGINAL_EXE = WORKSPACE / "Syw2plus_re" / "Syw2plus" / "syw2plus_original.exe"
ORIGINAL_SHA256 = "b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac"
IMAGE_BASE = 0x400000

SHARED_TEMP = WORKSPACE / "temp" / "Syw2plus_patch" / "g2_capacity"
LAP518_DIR = SHARED_TEMP / "20260923_lap518_work_w32_build_funnel"
SAMPLES_SHA256 = "b695365cd4416ec6a5256000327ada285bea46eef2f003a0a9bf9935f7c1a94f"
OUT_DIR = SHARED_TEMP / "20260923_lap519_middle_w32_review"

# lap518 문서 §2 표: owner -> (f_idle, S, C, B, D, 반증표본)
LAP518_TABLE = {
    0: (0.896, 102, 23, 16, 0, 26), 1: (0.902, 97, 18, 13, 0, 43),
    2: (0.898, 87, 24, 15, 0, 31), 3: (0.915, 89, 20, 14, 0, 36),
    4: (0.887, 88, 27, 14, 0, 23), 5: (0.900, 88, 11, 9, 0, 41),
    6: (0.895, 83, 20, 14, 0, 35), 7: (0.896, 86, 23, 18, 0, 32),
}
INIT = -10000
CALL_PERIOD = 8

results: dict[str, object] = {}
failures: list[str] = []


def check(name: str, ok: bool, detail: object) -> None:
    results[name] = {"pass": bool(ok), "detail": detail}
    if not ok:
        failures.append(name)


def disasm(pe: pefile.PE, lo: int, hi: int) -> list[tuple[int, str, str]]:
    md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
    data = pe.get_data(lo - IMAGE_BASE, hi - lo)
    return [(i.address, i.mnemonic, i.op_str) for i in md.disasm(data, lo)]


def static_checks() -> None:
    raw = ORIGINAL_EXE.read_bytes()
    sha = hashlib.sha256(raw).hexdigest()
    check("A1", sha == ORIGINAL_SHA256, sha)
    pe = pefile.PE(data=raw)

    a2 = [(m, o) for _, m, o in disasm(pe, 0x43F871, 0x43F8A7)]
    a2_want_tail = [
        ("mov", "eax, 1"),
        ("mov", "dword ptr [esi + 0x33ac], ecx"),
        ("mov", "word ptr [esi + 0xd32], ax"),
        ("mov", "word ptr [esi + 0xd34], ax"),
        ("jmp", "0x43fb62"),
    ]
    check("A2", a2[-5:] == a2_want_tail and ("jle", "0x43fb62") in a2, a2)

    a3 = [(m, o) for _, m, o in disasm(pe, 0x43E113, 0x43E13D)]
    a3_ok = (
        ("call", "0x43dbb0") in a3
        and a3[a3.index(("call", "0x43dbb0")) + 1] == ("test", "eax, eax")
        and a3[a3.index(("call", "0x43dbb0")) + 2] == ("jne", "0x43e13d")
        and ("call", "0x43f5a0") in a3
        and a3[-1] == ("ret", "")
    )
    check("A3", a3_ok, a3)

    a4 = disasm(pe, 0x43E13D, 0x43E174)
    a4_ops = [(m, o) for _, m, o in a4]
    no_issue_write = all("0x3a70" not in o for _, o in a4_ops)
    no_call = all(m != "call" for m, _ in a4_ops)
    writes_state = ("mov", "word ptr [edi + 0xd34], cx") in a4_ops
    check("A4", no_issue_write and no_call and writes_state and a4_ops[-1] == ("ret", ""), a4_ops)

    p5 = disasm(pe, 0x43E174, 0x43E2FD)
    p5_ops = [(a, m, o) for a, m, o in p5]
    f5a0_sites = [hex(a) for a, m, o in p5_ops if m == "call" and o == "0x43f5a0"]
    set3 = [i for i, (a, m, o) in enumerate(p5_ops) if (m, o) == ("mov", "word ptr [edi + 0xd34], 3")]
    set3_ret = bool(set3) and any(m == "ret" for _, m, _ in p5_ops[set3[0]:set3[0] + 8])
    no_issue = all("0x3a70" not in o for _, _, o in p5_ops)
    check("P5", f5a0_sites == ["0x43e252", "0x43e2d8"] and set3_ret and no_issue,
          {"f5a0_sites": f5a0_sites, "set_state3": [hex(p5_ops[i][0]) for i in set3], "no_3a70_write": no_issue})


def load_samples() -> list[dict]:
    path = LAP518_DIR / "samples.jsonl"
    raw = path.read_bytes()
    sha = hashlib.sha256(raw).hexdigest()
    rows = [json.loads(line) for line in raw.decode().splitlines() if line.strip()]
    gaps = [b["tick"] - a["tick"] for a, b in zip(rows, rows[1:])]
    check("B1", sha == SAMPLES_SHA256 and len(rows) == 1438 and max(gaps) <= 20,
          {"sha": sha, "rows": len(rows), "max_gap": max(gaps), "mean_gap": sum(gaps) / len(gaps)})
    return rows


def owner_series(rows: list[dict], o: int) -> list[dict]:
    out = []
    for r in rows:
        own = r["owners"][o]
        ext = r["build_ext"][o]
        assert own["owner"] == o and ext["owner"] == o
        out.append({
            "tick": r["tick"],
            "kind": own["order_kind"],
            "bcount": own["building_count"],
            "start": ext["build_order_start_tick"],
            "issue": r["build_issue"][o],
            "mask": ext["mask_active_count"],
            "state": own["build_state"],
            "sel": own["build_sel_kind"],
        })
    return out


def analyse_owner(ser: list[dict]) -> dict:
    n = len(ser)
    f_idle = sum(1 for s in ser if s["kind"] == 0) / n
    starts, issues = [], []
    b_inc = b_dec = 0
    for i in range(1, n):
        prev, cur = ser[i - 1], ser[i]
        if cur["start"] != prev["start"]:
            starts.append(i)
        if cur["issue"] != prev["issue"] and cur["issue"] != INIT:
            issues.append(i)
        d = cur["bcount"] - prev["bcount"]
        b_inc += max(d, 0)
        b_dec += max(-d, 0)
    issue_set = set(issues)

    refute = [i for i in starts if ser[i]["kind"] != 1]
    b3_bad = [i for i in starts if not (ser[i - 1]["tick"] < ser[i]["start"] <= ser[i]["tick"])]
    start_vals = [ser[i]["start"] for i in starts]
    b4_bad = [(a, b) for a, b in zip(start_vals, start_vals[1:]) if b - a <= 100]

    buckets = collections.Counter()
    bucket_issue = collections.Counter()
    b5_targets, b5_bad = [], []
    for i in refute:
        gap = ser[i]["tick"] - ser[i]["start"]
        key = "lt8" if gap < CALL_PERIOD else ("8to15" if gap < 16 else "ge16")
        buckets[key] += 1
        if i in issue_set:
            bucket_issue[key] += 1
        if gap < CALL_PERIOD:
            b5_targets.append(i)
            if i in issue_set:
                b5_bad.append({"tick": ser[i]["tick"], "start": ser[i]["start"], "issue": ser[i]["issue"]})

    b6_bad = []
    start_set = set(starts)
    for i in issues:
        alive = ser[i - 1]["kind"] == 1 or i in start_set
        if not alive:
            b6_bad.append({"tick": ser[i]["tick"], "issue": ser[i]["issue"]})

    # 시작별 운명: 수명 = 시작 구간부터 (+0xD32가 1이 아닌 첫 표본 또는 다음 시작 직전)까지
    fates = collections.Counter()
    for k, i in enumerate(starts):
        nxt = starts[k + 1] if k + 1 < len(starts) else n
        issued = i in issue_set
        j = i
        while not issued and ser[j]["kind"] == 1 and j + 1 < nxt:
            j += 1
            issued = j in issue_set
        fates["ISSUED" if issued else "ENDED_NO_ISSUE"] += 1

    mask_zero_refute = sum(1 for i in refute if ser[i]["mask"] == 0)

    o3 = collections.Counter()
    o3_kind = collections.defaultdict(collections.Counter)
    o4 = collections.Counter()
    p6_issue = 0
    for k, i in enumerate(starts):
        gap = ser[i]["tick"] - ser[i]["start"]
        if gap < CALL_PERIOD and ser[i]["kind"] == 1 and i + 1 < n:
            nxt = starts[k + 1] if k + 1 < len(starts) else n
            issued, j = False, i
            while j + 1 < n and j + 1 <= nxt:
                j += 1
                if j in issue_set:
                    issued = True
                if ser[j]["kind"] != 1 or ser[j]["start"] != ser[i]["start"]:
                    break
            fate = "ISSUED" if issued else "NO_ISSUE"
            ended_next = ser[i + 1]["kind"] != 1 or ser[i + 1]["start"] != ser[i]["start"]
            o3[(ser[i]["state"], fate, "ended_by_next_sample" if ended_next else "alive_next_sample")] += 1
            o3_kind[ser[i]["sel"]][fate] += 1
        elif CALL_PERIOD <= gap < 16:
            if i in issue_set:
                p6_issue += 1
            o4[("kind1_state%d" % ser[i]["state"]) if ser[i]["kind"] == 1 else "kind%d" % ser[i]["kind"]] += 1
    return {
        "f_idle": round(f_idle, 3), "S": len(starts), "C": len(issues), "B": b_inc, "D": b_dec,
        "refute": len(refute), "refute_frac": round(len(refute) / len(starts), 4) if starts else None,
        "b3_bad": len(b3_bad), "b4_bad": len(b4_bad),
        "refute_gap_buckets": dict(buckets), "refute_gap_bucket_with_issue": dict(bucket_issue),
        "SF_lb": len(b5_targets), "b5_bad": b5_bad, "b6_bad": b6_bad,
        "fates": dict(fates), "refute_mask_zero": mask_zero_refute,
        "O3": {"|".join(map(str, key)): v for key, v in sorted(o3.items())},
        "O3_by_sel_kind": {str(kd): dict(v) for kd, v in sorted(o3_kind.items())},
        "O4": dict(sorted(o4.items())), "P6_issue_in_8to15": p6_issue,
    }


def main() -> int:
    static_checks()
    rows = load_samples()
    per_owner = {o: analyse_owner(owner_series(rows, o)) for o in range(8)}
    results["per_owner"] = per_owner

    mism = {}
    for o, want in LAP518_TABLE.items():
        a = per_owner[o]
        got = (a["f_idle"], a["S"], a["C"], a["B"], a["D"], a["refute"])
        if got != want:
            mism[o] = {"got": got, "want": want}
    check("B2", not mism, mism or "0/8 mismatch")
    check("B3", all(a["b3_bad"] == 0 for a in per_owner.values()),
          {o: a["b3_bad"] for o, a in per_owner.items()})
    check("B4", all(a["b4_bad"] == 0 for a in per_owner.values()),
          {o: a["b4_bad"] for o, a in per_owner.items()})
    check("B5", all(not a["b5_bad"] for a in per_owner.values()) and sum(a["SF_lb"] for a in per_owner.values()) > 0,
          {o: {"SF_lb": a["SF_lb"], "bad": a["b5_bad"]} for o, a in per_owner.items()})
    check("B6", all(not a["b6_bad"] for a in per_owner.values()),
          {o: a["b6_bad"] for o, a in per_owner.items()})
    check("P6", all(a["P6_issue_in_8to15"] == 0 for a in per_owner.values()),
          {o: a["P6_issue_in_8to15"] for o, a in per_owner.items()})

    agg_o3, agg_o4, agg_kind = collections.Counter(), collections.Counter(), collections.defaultdict(collections.Counter)
    for a in per_owner.values():
        agg_o3.update(a["O3"])
        agg_o4.update(a["O4"])
        for kd, v in a["O3_by_sel_kind"].items():
            agg_kind[kd].update(v)
    results["aggregate"] = {"O3": dict(agg_o3), "O4": dict(agg_o4),
                            "O3_by_sel_kind": {k: dict(v) for k, v in sorted(agg_kind.items(), key=lambda x: int(x[0]))}}

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out = OUT_DIR / "w32_independent_review.json"
    payload = json.dumps({"failures": failures, "results": results}, indent=1, sort_keys=True, ensure_ascii=False)
    out.write_text(payload + "\n")
    print(json.dumps({"failures": failures, "out": str(out),
                      "out_sha256": hashlib.sha256((payload + "\n").encode()).hexdigest()}, ensure_ascii=False))
    for o, a in per_owner.items():
        print(o, {k: a[k] for k in ("f_idle", "S", "C", "B", "D", "refute", "SF_lb", "refute_gap_buckets",
                                    "refute_gap_bucket_with_issue", "fates", "refute_mask_zero", "O4")})
    print("aggregate", json.dumps(results["aggregate"], ensure_ascii=False))
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
