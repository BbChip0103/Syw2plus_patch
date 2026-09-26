# 2026-09-20 | lap 400 | 목표 G2 (전역 UnitStruct 풀 확장 스파이크 — lap399 독립 검수)

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5` / high, **중간(middle) 컨펌 역할**.
  게임 코드 hands-on 수정 없음. PROMPT ⑥ 2단(새 컨펌 세션이 이전 work 결과를 독립 검수).
- 가설 / 사용자 관찰: lap399 work가 낸 N=1210 후보(`303c78f8…`)와 그 네 가지 주장(C1 N=1300 위험,
  C2 사이트 카운트 교차검증, C3 후보 재현성, C4 `PS=40`은 패치 결함 아님)을 바이트로 독립 재유도한다.
  lap399가 **묻지 않은** 질문 하나를 추가한다: 커진 풀이 물리적으로 차지하는 주소 구간이
  **참조되고 있는가**.
- 예상 PASS / FAIL 조건: C1~C3이 재유도되면 ACCEPT. 커진 풀 구간에 `.text` 리터럴 참조가 1건이라도
  있고 후보가 그것을 고치지 않으면 후보는 **REJECT**(W3 §A S-6 "인접 상태영역 무손상" 위반).

## 판정 요약

| 주장 | 판정 | 근거 |
|---|---|---|
| C1 N=1300 위험, `N<=1217` | **ACCEPT(재현)** — 단 이 상한은 **무의미**하다 | D1이 더 낮은 곳에서 먼저 깨짐을 보임 |
| C2 사이트 카운트(pool 986/28 등) | **ACCEPT(재현)** | 수집 카운트 일치 |
| C3 후보 재현성·N=1200 항등·원본 불변 | **ACCEPT(재현)** | SHA `303c78f8…` 동일 재생성 |
| C4 `PS=40`은 패치 결함 아님 | **부분 ACCEPT** | 대조군 로그는 실재하나 **양성 대조군이 없음**(아래 §3) |
| **후보 N=1210 자체** | **REJECT** | §1 — 설계상 live state와 별칭 |

## 1. 결정적 결함 — 후보는 풀을 **재배치하지 않았다**(D1/D2)

`base_preserving_storage_layout_v1`은 이름 그대로 **unit_pool의 base가 절대 움직이지 않는** 계산기다
(모듈 docstring: `cumulative_insert_below(unit_pool.base) == 0`). lap399가 B-1을 이 계산기에 위임한
결과 후보의 실제 fixup 적용 수는 다음과 같다(기계 산출 `build_candidate` 리포트 인용, 손 전사 아님):

```
"b3_fixup_site_counts": { "unit_pool": 0, "unit_existence": 34, "unit_age": 4 }
"deltas":               { "unit_pool": "0x00000000", ... }
```

즉 C2가 교차검증한 **풀 사이트 1,014건(disp 986 + imm 28)은 수집만 되고 0건 적용**됐다. 풀은
`0x0066B790`에 그대로 있고 **제자리에서 위로 자란다**. 이것은 lap397 A6·W3 §B-1이 `NOT_FEASIBLE`로
판정하고 "**재배치 필수**, 새 공간은 이미지 꼬리를 늘려 확보한다"로 대체했던 바로 그 경로다.
lap399 기록은 `b3_fixup_site_counts`를 공개하지 않아 이 사실이 드러나지 않았다.

그 결과 N=1210에서 풀 slot 1200~1209는 `[0x00892410, 0x00896D80)` **18,800 B**를 차지한다.
`0x892410`은 이 모듈 자신의 docstring이 "triple alias"로 명시한 주소다 — 풀의 옛 끝이자 **live
game state의 시작**이자 **bulk save/load blob의 시작**(save `0x440F02` src / load `0x4412DC` dst).

독립 스캔 결과(probe D1):

| 구간 | `.text` 리터럴 사이트 | 후보가 고친 수 |
|---|---|---|
| `[0x892410, 0x896D80)` (N=1210 풀 침범 구간) | **1,311건** (disp 1,072 / imm 239) | **0** |
| 그중 정확히 `0x892410` (bulk base) | 179건 | 0 |

예: `mov eax, dword ptr [0x8924c4]` / `mov dword ptr [0x8924c4], edx`(읽기·쓰기 모두 존재),
`mov ecx, 0x892410` ×179. ⇒ **slot 1200~1209의 UnitStruct 바이트와 살아 있는 전역이 같은 메모리를
공유한다.** W3 §A의 S-6는 실행 전에 이미 설계로 위반됐고, S-2(`existence[slot>=1200]!=0`)를 이
후보에서 관측하더라도 그것이 실제 할당인지 bulk load 잔재인지 **구분할 수 없다**.

부수 결함(D3): 재배치된 existence/age 목적지 `[0x0089DA38, 0x0089ED20)`는 직접 리터럴 참조는 0건이나
**bulk blob `[0x892410, +0xE397C)` 내부**다. save000 로드의 `fread`가 이 구간을 옛 레이아웃 바이트로
통째로 덮는다. 따라서 S-1이 외견상 통과해도 그 뒤의 유닛 상태는 신뢰할 수 없다.

**C1 재평가:** lap399가 계산한 상한 `N<=1217`은 catA/catB/FO-3 gap만 본 것이라 **안전 상한이 아니다**.
제자리 성장 경로에서는 `N>1200`인 **모든 N**이 첫 바이트부터 live state를 침범한다.

## 2. 올바른 목적지는 이미 W3에 적혀 있다 (D4)

W3 §B-1이 요구한 이미지 꼬리(`.data` BSS 끝 `0x0108BA38` 위, `.rsrc`는 계산기가 이미 밀어 올림)를
같은 방법으로 스캔하면:

| 구간 | 크기 | `.text` 리터럴 사이트 |
|---|---|---|
| `[0x0108BA38, 0x012B8310)` (pool+existence+age, N=1210 = 2,279,640 B) | 2.18 MB | **1건** |

유일한 1건은 `0x00401402 push 0x1100007`로 주소가 아닌 플래그 즉치로 보인다(구현 세션이 분류할 것).
**1,311 대 1** — 목적지 선택만으로 충돌이 사라진다. 세 배열을 전부 이 꼬리로 옮기면 bulk blob 내부는
한 바이트도 움직이지 않으므로 catA/catB/active/PlayerStruct/179개 별칭은 계속 손대지 않아도 된다.

## 3. C4(`PS=40`) — 대조군은 실재하나 **양성 대조군이 없다**

보존된 산출물로 확인: `local/runtime/20260920_012749_2958612_0/driver_out/session.json`은
`exe=control_renamed_original.exe`, `exe_sha256=b56986e0…`(원본과 바이트 동일)이고 `trace.jsonl`은
31 표본 전부 `ps=40, tick=0`(30.07초). ⇒ "바이트 동일 원본을 이름만 바꾸면 PS=40" 은 **ACCEPT**.
후보 run의 로그는 lap399가 스스로 기록한 대로 덮여 없어졌다(provenance 사각, 보존).

그러나 **같은 prepare 환경에서 `syw2plus_original.exe`가 PS9에 도달한 관측이 없다.** `manifest.json`의
`runtime_config`는 lap334 N9대로 prepare 스모크 기술문일 뿐 이 run을 기술하지 않고,
`feature_patch_execution_observed`는 `"unknown (startup smoke only)"`다. 따라서 "파일명 의존"과
"이 prepare run 환경 회귀"는 아직 구분되지 않았다 — lap399의 실패가설 1회 소진은 유효하나 결론은
**under-determined**다. 추가 정적 사실: `runtime_driver.SUPPORTED_EXECUTABLES`의 profile 문자열은
기동 절차를 바꾸지 않고(SHA 게이트 라벨일 뿐), `dxwrapper.ini`의 `IncludeProcess`/`ExcludeProcess`는
**비어 있어** 래퍼가 exe 이름으로 게이트하지 않는다. 즉 "래퍼 ini가 이름을 가린다"는 가설은 배제된다.

## 변경 파일 / source fingerprint / 커밋

- 신규(문서·probe만, 제품/게임 코드 0): 이 기록,
  `docs/history/laps/probes/20260920_lap400_middle_g2_pool_overrun_probe.py`
  (SHA `a52c36fc8bc5c654a3b29cc0c20f560d9576f338fe32b845b98a7904a4f83476`),
  산출물 `docs/history/laps/probes/out/20260920_lap400_middle_g2_pool_overrun.json`
  (SHA `734eb0b29e3f93e9aff5dfee4e4d81202b4a9062b155d230b09241222f06f287`),
  work 카드 `docs/work/active/G2_UNIT_POOL_RELOCATION_SPIKE_LAP400.md`(W4).
- 수정: `docs/work/active/G2_UNIT_POOL_EXPANSION_SPIKE_LAP397.md`(W3 상단에 SUPERSEDED 주석만),
  `docs/STATUS.md`.
- 커밋 없음(`LOOP_ALLOW_COMMITS=0`). uncommitted 보존. 파일 해시(PROMPT ⑤):
  - `docs/work/active/G2_UNIT_POOL_RELOCATION_SPIKE_LAP400.md` `deb5f2e38f8523d74d38c709f537fda9c2d1b202a05c06ef746df8636e26410b`
  - `docs/work/active/G2_UNIT_POOL_EXPANSION_SPIKE_LAP397.md` `57972f9a2f2d653eb30f81f213fd5e775bc4d6296d8014043f8a2a081c3007e4`
  - `docs/STATUS.md` `3ee83ddd7329cce83928f7ee8c189331591c7e01c13b08cb750d1a59ad658eb1`
  - (이 기록 자신의 해시는 이 줄을 추가하기 전 값 `6bcdfcf6…ec54c369`에서 바뀐다 — 자기참조 회피)

## 원본 SHA / 후보 SHA / 환경 / fixture

- 원본 `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac` — **읽기만**, 검수 전후 재해시
  불변(`Syw2plus/`·`Syw2plus_re/Syw2plus/` 둘 다 확인).
- lap399 후보 `303c78f81f816ed82e495fa4545cc23af3fa7200344eb029b4e9f31cabe96522` — 메모리에서만 재생성,
  파일로 쓰지 않음.
- fixture: 없음(게임 미실행). 기존 run 산출물은 읽기만 했고 삭제/정리하지 않았다.

## 실행 명령 / 로그

```
python3 docs/history/laps/probes/20260920_lap400_middle_g2_pool_overrun_probe.py \
    --output docs/history/laps/probes/out/20260920_lap400_middle_g2_pool_overrun.json
# rc 0, "failures": []
make check              # rc 0, 728 passed 207.74s, Ruff/compileall/mypy10 Success, CONTEXT_PASS
checks/safety.sh check  # SAFETY_PASS
```

## 측정값 / 판정

- C1/C2/C3: **PASS(재현)**. C4: **부분 PASS**(대조군 실재, 양성 대조군 없음 → 결론 under-determined).
- 후보 N=1210: **REJECT**(실행 금지). 근거는 정적 바이트 사실 1,311건, 실행 필요 없음.
- 게임 실행 0회, 제품 바이트 변경 0, 메모리 쓰기 0, 커밋 0.

## 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태

- lap399의 정적 산출물(패처 골격·B-2 4상수·FO-4 제외·재스캔 방식)은 **버리지 않는다**. 잘못된 것은
  B-1 목적지 하나이며, `deltas["unit_pool"]`을 0이 아닌 값으로 만드는 layout 공급자만 바꾸면 된다.
- lap385/388 저장포맷 통합 blocker, lap389 NO_GO, `ESCALATE_SOL` §5~§10(F4 포함)은 **뒤집지 않는다**.
  이 lap은 그 어느 것도 닫지 않았다.
- 이 lap은 컨펌 역할이므로 스스로 제품 PASS를 선언하지 않는다. 사용자 마일스톤 승인 대상 아님.
- 남은 위험: W4가 꼬리 재배치를 구현해도 저장 호환성은 깨진다(W3 §E대로 후속 필수 blocker).

## 다음 한 가지

**W4(`docs/work/active/G2_UNIT_POOL_RELOCATION_SPIKE_LAP400.md`)를 다음 work 회차가 구현한다** —
pool/existence/age 세 배열을 이미지 꼬리 virgin BSS로 **실제 재배치**하고(pool delta != 0, 1,014건
적용), 실행 전에 "침범 구간 참조 0건" 게이트를 통과시킨 뒤 S-1을 재시도한다. 파일명 제약 조사는
그 전에 **양성 대조군 1회**(같은 prepare run에서 `syw2plus_original.exe` → PS9)로 먼저 확정한다.
