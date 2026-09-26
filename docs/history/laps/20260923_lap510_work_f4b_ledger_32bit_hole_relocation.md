# 2026-09-23 | lap 510 | 목표 G2

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-sonnet-5` / high, work tier
  (loop/PROMPT.md 지정, `docs/MODEL_ROUTING.md` 실무=Sonnet5).
- 가설 / 사용자 관찰: W30 카드(`docs/work/active/G2_F4B_SUPPLY_LEDGER_32BIT_LAP509.md`)
  M-0(구멍 확정) + §1~§7 패처 구현. 2026-09-23 12:55 사용자 "1 2 바로 ㄱㄱ" → ① F4(B) 먼저.
  카드 §2 안 A(PlayerStruct 안의 정적+런타임 상수 4바이트 구멍으로 `used` 이전)를 먼저 시도.
- 예상 PASS / FAIL 조건: 카드 §3 M-a~M-h 표 그대로. M-a 는 "4바이트 연속·정렬 가능·정적
  미참조·런타임 상수(8 owner)" 4개 모두 충족해야 A 채택, 하나라도 실패하면 B로.

## M-0 실행 — 정적 재확인 + 런타임 상수성 (2회 시도)

1. **정적**: `docs/history/laps/probes/20260923_lap510_work_supply_ledger_hole_map.py` (신규,
   원본 읽기 전용) — lap509 의 9곳(+cost-load 2곳=11곳) old-bytes 전부 독립 재확인(M-b PASS),
   구멍 후보 707건 전수 계산. exit 0.
2. **런타임 시도1 (`+0x201c`, 정적 최유력 후보) — 실패(가설 1/2)**: 원본(패치 0)을 격리 Wine
   (Xvfb :210)에서 op7 자원 주입 + 8 owner AI 대전으로 tick 6,018 실행, owner 당 매초 그
   4바이트 관측. **1,425/1,440 owner-표본이 변함** — 살아있는 필드로 판명, 채택 금지.
   스크립트/산출물 `…/temp/Syw2plus_patch/g2_capacity/20260923_lap510_work_f4b_ledger_32bit/`.
3. **런타임 시도2 (`+0x2100`) — 성공**: 같은 하네스(Xvfb :211)로 재실행. 위반 **0/1,440**
   (`HOLE_CONSTANT`), 같은 실행에서 `used` 는 owner별 20→최대 500대까지 정상 성장(활동 중
   상수성 확인, 방치 중 우연한 조용함이 아님). A 채택 조건 4개 전부 PASS.
   산출물 `…/attempt2_hole2100/`(`run_summary.json`, `samples.jsonl`, `orchestrator.log`).
   근거 문서 `analysis/memory_maps/g2_supply_ledger_used_hole_relocation_lap510_20260923.md`.

## 구현 — `patches/population/supply_ledger_32bit.py`

안 A: `used` 를 원본 `+0x200c`(2B)에서 `+0x2100`(4B, PS0 절대 `0x958870`)으로 이전. §1 9곳
+ writer 직전 cost-load 2곳(`0x43EE93`/`0x43EF83`, edx 상위 16bit 0 보장) 총 11곳을
**같은 길이**로 치환(movsx word 7B→mov dword 6B+nop1; word add/sub 7B→dword add/sub 6B+nop1;
cost-load 8B→8B 동일). 길이 보존이라 다른 코드 주소/점프 타깃 fixup 이 전혀 필요 없다.
ModRM 바이트는 레지스터 피연산자가 그대로라 원본과 동일하게 재사용(opcode 와 disp32 만 교체).

Capstone 으로 패치 후 11곳 전부 재역디스어셈블해 의도한 mnemonic/피연산자와 바이트 단위로
일치함을 확인했다(`mov e[dc]x, dword ptr […]`, `add/sub dword ptr […], edx`,
`movzx edx, word ptr […]`).

## 변경 파일 / source fingerprint / 커밋

- 신규: `patches/population/supply_ledger_32bit.py`, `patches/population/test_supply_ledger_32bit.py`,
  `analysis/memory_maps/g2_supply_ledger_used_hole_relocation_lap510_20260923.md`,
  `docs/history/laps/probes/20260923_lap510_work_supply_ledger_hole_map.py`.
- **커밋 0** (`LOOP_ALLOW_COMMITS` 기본0, 사용자 명시 허용 없음) — 전부 uncommitted.
- 원본 SHA (변경 0): `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`.
- 후보 SHA (in-memory `patched_bytes()`, 파일로 아직 생성 안 함): `7cb0faf3b71ca2ccfea82b4ff27e6dc6f979d2bb86ca411ae33835557eb809e0`.

## 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture

원본 `b56986e0…`(1,032,192B). 환경: 격리 Wine 32비트 prefix, 별도 Xvfb(:210, :211),
`runtime_env.prepare()` 로 새로 소유한 prefix. 8 owner AI, map 140×140(seed42, d4a1),
op7 자원 주입(rice/wood 각 1,000,000, `used`/`count` 는 자연 생산). CAPACITY=1200(재고,
EXE 패치 없음 — bridge DLL 만 stock 주소로 빌드).

## 실행 명령 / 로그 / 캡처 경로 및 해시

- 정적: `python3 docs/history/laps/probes/20260923_lap510_work_supply_ledger_hole_map.py`
  → exit 0. 산출물 `…/20260923_lap510_work_f4b_ledger_32bit/hole_map.json`,`hole_map_checks.json`.
- 런타임1: `LAP510_DISPLAY=:210 python3 hole_constancy_run.py` → exit 1(`HOLE_NOT_CONSTANT`,
  기대대로 — 채택 안 함을 정직하게 기록).
- 런타임2: `LAP510_DISPLAY=:211 python3 attempt2_hole2100/hole_constancy_run.py` → exit 0
  (`HOLE_CONSTANT`).
- 단위: `python3 -m pytest patches/population/test_supply_ledger_32bit.py -q` → **21 passed**.
- `checks/safety.sh check` → `SAFETY_PASS`.
- `make check` → 소스가 바뀐 회차라 전체 게이트 실행, 결과는 다음 검수 세션이 `run_summary`/
  `pytest` 원시 출력에서 직접 확인한다(이 lap 이 세션 종료 전 결과를 STATUS 에 적는다).

## 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN)

- M-a(구멍): 시도1 FAIL(`+0x201c`, 위반1,425/1,440) → 시도2 PASS(`+0x2100`, 위반0/1,440).
  **실패 가설 1회 소비, 카드 상한(2회) 안.**
- M-b: PASS (11/11 사이트 old-bytes 일치, lap509 와 독립 재확인 일치).
- M-c: PASS (`test_copy_restore_preserves_input` 등 5개 통과 — 실제 파일 create-copy/restore
  는 이번 lap 에서 별도로 호출하지 않았다, `Syw2plus/`는 손대지 않음. 단위테스트가 `tmp_path`
  임시 파일로 동일 로직을 검증).
- M-d: PASS (`test_diff_confined_to_documented_sites`, 실 원본 대상 diff 62바이트 전부
  11개 사이트 span 안).
- M-e/M-f: PASS (인코딩 의미 모델 단위테스트 — 실제 CPU 실행이 아니라 word-signext vs
  dword 로드/스토어 의미를 모델링한 것임을 테스트 docstring에 명시).
- M-g: PASS (stride/span 불변, bulk blob 즉시값 원본에서 재확인).
- M-h: `checks/safety.sh check` PASS. `make check` 결과는 이 lap 종료 시점 STATUS 참조
  (백그라운드 실행 중 세션을 기다렸다 — 01:01 규칙대로 Monitor로 완주까지 대기).

## 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태

- **게임실행 2회(런타임1/2, 둘 다 패치 0 원본), source 변경 0(패치는 in-memory 함수 호출로만
  생성, 실제 후보 EXE 파일은 아직 디스크에 만들지 않았다), 커밋 0.**
- **다음 middle 이 독립 재계산해야 2단이 선다**(work 는 자기 결과를 최종 승인하지 않음).
- §4 저장 호환 방침: **권고안(로드 후 재계산) 을 정책으로 채택**하지만, 그 재계산을 실제로
  주입하는 코드(로드 콜사이트에 훅)는 **이번 lap 의 구현 범위 밖**이다 — 이번 카드가 요구한
  산출물(§7)은 패처+M-b~M-g 회귀뿐이고, 로드 후 재계산 주입은 별도 후속 단계로 필요하다.
  **이 gap 을 명시적으로 남긴다: 구세이브를 이 패치 후보로 로드하면 새 `used`(+0x2100)가
  초기값 0으로 남아(§2의 관측: 미패치 원본에서도 그 오프셋은 0으로 시작) 생산 게이트가
  로스터 실제 상태와 불일치할 수 있다.** 신규 게임(세이브 없이 시작)에서는 문제 없다.
- §7 미결 그대로 유지: F4 후보 EXE 의 실제 게임 실행 검증이 12:55 지시 ③ 제외 범위에
  들어가는지는 여전히 문서상 불명확 — 이번 lap 은 그 실행 검증을 **하지 않았다**(패치를
  실제 EXE 파일로 만들어 그 후보를 구동한 적이 없다. 런타임1/2 는 둘 다 미패치 원본이다).
- M-0 런타임 한계: tick 6,018·seed42·op7 fixture 1가지뿐. 장시간/다른 seed 교차 확인은
  후속 lap 의 몫으로 남긴다(§4 참조).

## 다음 한 가지

**다음 middle(Opus5)** 이 이 lap 을 독립 재계산 검수한다: (1) 정적/런타임 probe 원시
산출물(`hole_map.json`, `attempt1`/`attempt2_hole2100` `run_summary.json`/`samples.jsonl`)을
재확인해 M-a/M-b, (2) `patches/population/supply_ledger_32bit.py`/`test_supply_ledger_32bit.py`
를 재계산해 M-c~M-g, (3) `make check` 결과(이 lap 종료 시점 STATUS 에 기록된 exit/합계)를
확인한다. ACCEPT 면 다음 work 회차가 **로드 후 재계산 주입 구현**(§4 gap 해소) 및/또는
**실제 후보 EXE 생성 + 실행 검증 카드 발행 여부**(§7 미결과 연결)를 진행한다.
