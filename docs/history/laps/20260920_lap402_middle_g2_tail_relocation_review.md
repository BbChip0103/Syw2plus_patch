# 2026-09-20 | lap 402 | 목표 G2 (lap401 W4 §1 B-1 재배치 독립 검수)

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5` / high, **middle(중간계획·컨펌) 역할**.
  게임 코드 hands-on 수정 없음, 게임 실행 0회, 메모리 쓰기 0, 바이너리 쓰기 0.
  검수 대상 `docs/history/laps/20260920_lap401_work_g2_unit_pool_tail_relocation.md`(work, `claude-sonnet-5`/high).
- 가설 / 사용자 관찰: lap401이 보고한 R1/R2/Ga/Gb PASS는 `failures == []`만으로 믿지 않고 독립 경로로
  재유도한다. 추가로 W4 §4의 두 게이트(G-a/G-b)가 **묻지 않는 질문** — 재배치된 세 배열이 후보 자신의
  섹션 테이블에서 실제로 매핑되는 영역에 있는가 — 를 검사한다.
- 예상 PASS / FAIL 조건: C1~C4 중 하나라도 재현 실패 시 lap401 REJECT. C1~C4 전부 재현되더라도
  재배치 블록이 어떤 섹션의 `[VA, VA+VirtualSize)`에도 들어가지 않으면 **실행 전 REJECT**(후보 기동 금지).

## 검수 결과 — C1~C4 ACCEPT, **D1 FAIL ⇒ 후보 `2571d6a2…` 실행 REJECT**

신규 read-only probe `docs/history/laps/probes/20260920_lap402_middle_g2_tail_relocation_review_probe.py`
(SHA `5eaa540f880359ff4f0a93e252a06ea94d9178f225086d61dbdf80f07ff2c06d`), 산출물
`docs/history/laps/probes/out/20260920_lap402_middle_g2_tail_relocation_review.json`, **rc1**
(`failures`는 D1 1건뿐 — C1~C4는 전부 통과).

- **C1 ACCEPT — N=1200 항등.** `build_candidate(original, 1200)` 바이트 동일. lap401 최강 앵커 생존.
- **C2 ACCEPT — 카드 필수 카운트.** `b3_fixup_site_counts == {"unit_pool":1014,"unit_existence":34,
  "unit_age":4}`, W4 §3 필수치와 정확 일치. lap399의 REJECT 사유(`unit_pool: 0`)는 실제로 해소됐다.
- **C3 ACCEPT (신규·독립, lap401 검수요청 (2)에 대한 답) — `_patch_literal` 재디코드 수리는 옳다.**
  lap401의 카운트 재확인이 아니라 원본/후보 `.text`를 **나란히 디스어셈블**해 직접 대조했다:
  명령 경계/길이 드리프트 **0건**, 리터럴이 바뀐 명령 **1,056개 = 기대치 1,056개**(B-3 1,052 + B-2 4),
  기대 밖 변경 **0건**, 누락 **0건**, `old + region_delta`가 아닌 값 **0건**.
  ⇒ 고정 16B 윈도우가 read-modify-write 세트의 **다른 명령**을 잘못 패치한 사례는 후보 전체에 없다.
- **C4 ACCEPT — G-a 재유도.** 꼬리 목적지 `[0x0108C000, 0x012B88D8)`를 가리키는 원본 `.text` 리터럴은
  `0x00401402`(`push 0x1100007`, 비주소 즉치) **1건**뿐. lap400 D4와 일치.
  부수 확인: 블록 끝 `0x012B88D8`은 lap400 D4 스캔 끝 `0x012B8310`을 1,480 B 넘지만, lap401 probe와 이
  probe 모두 **실제 블록 범위**를 스캔하므로 사각 없음.

### D1 (신규 결함, 결정적) — 재배치 블록의 99.24%가 어떤 섹션에도 속하지 않는다

후보 `2571d6a2…`(N=1210)의 **자기 섹션 테이블**에서 측정한 값이다:

| 영역 | 새 범위 | 크기 | 선언된 섹션 안 |
|---|---|---|---|
| unit_pool | `[0x0108C000, 0x012B75F0)` | 2,274,800 | **17,360** |
| unit_existence | `[0x012B75F0, 0x012B7F64)` | 2,420 | **0** |
| unit_age | `[0x012B7F64, 0x012B88D8)` | 2,420 | **0** |
| 합계 | `[0x0108C000, 0x012B88D8)` | 2,279,640 | **17,360 (0.76%)** |

후보 `.data`는 `VA 0x004EC000 / VirtualSize 0x00BA43D0`이라 가상 끝이 **`0x010903D0`**이고,
다음 섹션 `.rsrc`는 **`0x012B9000`**에서 시작한다. 재배치 블록은 그 사이 구멍에 놓인다 —
SizeOfImage(`0xEBC000`) 안이지만 **모든 섹션의 `[VA, VA+VirtualSize)` 밖**이다.
`d1_first_pool_slot_outside_data_vsize = 9` ⇒ **unit_pool slot 10부터**, 그리고 existence/age는
**전부**, 선언된 매핑 밖이다.

**원인(바이트로 확정).** `tail_relocation_storage_layout_v1.build_layout_artifact`는
`total_growth = sum(region.delta for region in result.regions)`를 `.data` VirtualSize에 더한다.
이 한 줄은 `base_preserving_storage_layout_v1`에서 그대로 복제됐는데, 그 모듈의 `RegionLayout.delta`는
자기 정의에 **`array span growth (array_new_span - array_old_span) -- NOT an address shift`**라고
적혀 있다. 제자리 성장(base-preserving)에서는 *성장량 == 위쪽 전체의 이동량*이라 이 식이 옳다.
**재배치(tail)에서는 배열이 통째로 옮겨가므로 성장량(18,840 B)과 확보해야 할 공간(2,279,640 B)이
전혀 다른 양이다.** 후보는 18,840 B만 늘렸다 — 필요량의 **0.83%**.

**왜 기존 가드가 못 잡았나.** 같은 함수의
`if data_va + new_data_vsz > new_rsrc_rva: raise`는 **과확장만** 막고 **미확장은 통과**시킨다.
W4 §4의 G-a/G-b, lap401의 pytest 10+1건, lap401 probe의 R1/R2/Ga/Gb 어디에도
"재배치 목적지가 매핑되는가"를 묻는 단언이 없다 — 이 회차가 그 사각을 닫는다.

**D2 — 수리 가능성(정적).** 블록 전체를 덮는 `.data` VirtualSize는 **`0x00DCC8D8`**(원본 대비
+2,281,120 B)이고, 이 값은 모듈 자신의 `.rsrc` 비침범 가드를 **1,832 B 여유로 통과**한다
(`d2_repair_fits_under_existing_rsrc_guard: true`). 즉 배치 설계(꼬리 재배치)는 바꿀 필요가 없고,
결함은 `.data` VirtualSize 산출식 한 곳에 국한된다.

## 판정

- **lap401의 구현 성과는 실재한다**: lap400이 지목한 결정적 결함(제자리 성장 → live state 침범)은
  실제로 해소됐고(C2), `_patch_literal` 수리도 후보 전체에서 옳다(C3). 이 부분은 **ACCEPT**.
- **후보 `2571d6a2d07396215dadc323a42e1c763ff332132463e5b049fb2135b9d264de`는 기동 REJECT.**
  선언된 섹션 밖 메모리에 놓인 풀은, 로더가 섹션 사이 구멍을 커밋하지 않는 통상 동작에서 **slot 10
  접근 시점에 폴트**한다. 구멍 페이지의 실제 커밋 여부는 **UNKNOWN**이며 스파이크가 의존해서는 안 되는
  미문서 동작이다. 어느 쪽이든 S-2~S-5(slot≥1200 관측)는 이 후보로 도달할 수 없고, S-1 결과는
  "패치 결함"과 "환경/파일명"을 구분하지 못해 해석 불가가 된다.
- lap385/388 저장포맷 통합 blocker, lap389 NO_GO, `ESCALATE_SOL` §5~§10(F4 포함)은 **뒤집지 않는다**.
  이 lap은 그중 어느 것도 닫지 않았다. 저장/LAN 호환은 W4 §6대로 여전히 후속 필수 blocker.
- **새 불가능성 증명이 아니다.** 꼬리 재배치 경로는 여전히 구조적으로 `FEASIBLE`이다(lap397 판정 유지).

## 측정값 (기계 산출 인용, 손 전사 아님)

산출물 `20260920_lap402_middle_g2_tail_relocation_review.json`에서:
`c1_n1200_identity: true` / `c2_b3_fixup_site_counts: {"unit_age":4,"unit_existence":34,"unit_pool":1014}` /
`c3_instruction_boundary_drift: []` / `c3_changed_site_count: 1056` == `c3_expected_changed_site_count: 1056` /
`c3_unexpected_changed_sites: []` / `c3_missing_fixup_sites: []` / `c3_wrong_value_sites: []` /
`c4_hits: {"0x401402": [["imm", 17825799]]}` / `d1_block_size: 2279640` /
`d1_bytes_inside_a_declared_section: 17360` / `d1_bytes_outside_every_section: 2262280` /
`d1_first_pool_slot_outside_data_vsize: 9` / `d2_candidate_data_vsize_growth: 18840` /
`d2_required_data_virtual_size: "0xdcc8d8"` / `d2_required_growth: 2281120` /
`d2_repair_fits_under_existing_rsrc_guard: true` / `d2_slack_bytes_to_new_rsrc_rva: 1832`.

## 변경 파일 / source fingerprint / 커밋

- 신규(검수 산출물, 제품코드 아님):
  `docs/history/laps/probes/20260920_lap402_middle_g2_tail_relocation_review_probe.py`,
  `docs/history/laps/probes/out/20260920_lap402_middle_g2_tail_relocation_review.json`,
  (SHA `12bc169f9973812af4ac11980ad08e5871fcfd6f36dfe1df07a2729b0205fec2`),
  이 기록, work 카드 `docs/work/active/G2_POOL_SECTION_COVERAGE_REPAIR_LAP402.md`(W5).
- 수정: `docs/STATUS.md`, `docs/feedback/INBOX.md`(처리 상태 한 줄).
- **제품 코드/바이너리 변경 0**(`patches/**` 무수정). 커밋 없음(`LOOP_ALLOW_COMMITS=0`), uncommitted 보존.

## 원본 SHA / 후보 SHA / 환경 / fixture

- 원본 `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac` — **읽기만**. 회차 전후
  `Syw2plus/`·`Syw2plus_re/Syw2plus/` 양쪽 재해시 불변 확인.
- 검수 후보 `2571d6a2d07396215dadc323a42e1c763ff332132463e5b049fb2135b9d264de`(N=1210, 메모리 재생성,
  파일로 쓰지 않음) — lap401 기록값과 일치.
- fixture: 없음(게임 미실행).

## 실행 명령 / 로그

```
PYTHONPATH=. python3 docs/history/laps/probes/20260920_lap401_work_g2_pool_tail_relocation_probe.py \
    --output /tmp/lap402/lap401_probe_rerun.json            # rc0, failures=[]
                                                            # 산출물이 lap401 기록본과 byte-equal 재현
PYTHONPATH=. python3 docs/history/laps/probes/20260920_lap402_middle_g2_tail_relocation_review_probe.py \
    --output docs/history/laps/probes/out/20260920_lap402_middle_g2_tail_relocation_review.json   # rc1 (D1)
make check                  # rc0, 739 passed, Ruff/compileall/mypy Success, CONTEXT_PASS
checks/safety.sh check      # SAFETY_PASS
```

## 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태

- **N17(신규, 낮음, 수치 영향 0):** lap400·lap401 probe 둘 다 `REPO_ROOT = Path(__file__).resolve().
  parents[3]`로 잡는데 실제 저장소 루트는 `parents[4]`다(`parents[3]` == `docs/`). 두 기록에 적힌
  `python3 docs/history/laps/probes/…` 명령은 **그대로는 `ModuleNotFoundError: No module named 'patches'`**
  로 죽고, 저장소 루트를 CWD로 둔 채 `PYTHONPATH=.`를 줘야 rc0이 재현된다(위 명령란 참조).
  이 회차 probe는 `parents[4]`로 바로잡았다. 기록된 명령이 그대로 재현되지 않는 provenance 계열
  ((c)/(h))의 재발이며, 과거 기록은 **고쳐 쓰지 않는다**. 게이트 영향 없음(lap339: 필수 게이트 어느
  것도 `docs/history/laps/probes`를 실행하지 않는다).
- D1 수리 뒤에도 **게임 실행 증거는 여전히 0**이다. 이 lap은 정적 판정만 했다. 마일스톤 승인 아님.
- 다음 work 결과는 또 **다음 새 middle 세션이 독립 검수**한다. middle은 직접 구현하지 않았다.

## 다음 한 가지

**다음 work 회차가 W5(`docs/work/active/G2_POOL_SECTION_COVERAGE_REPAIR_LAP402.md`) §1을 수리한 뒤
W4 §5 실행에 들어간다.** P-0(양성 대조군)은 **원본** 바이너리만 쓰므로 D1과 무관하고 먼저/병행 가능하다.
S-1은 D1 수리 + 새 게이트 G-c PASS 전에는 **착수 금지**.
