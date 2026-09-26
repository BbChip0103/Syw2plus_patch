# lap378 middle — lap377 방향 검수와 work handoff

2026-09-15 / Codex 현재 세션 / 정확한 모델 ID 미노출·미주장 / 사용자 지정
middle(high), 진단·계획·확인 전용. 게임 코드·하네스·tests·EXE/DLL/save는 수정하지 않았고
게임/Wine/Xvfb/입력/PNG 실행은 0회다.

## 1. 판정

`G1_G2_ASTRA_DIRECTION_LAP377.md`의 **G1 제품 증거 우선, M1 유지, G2 읽기 전용 구조
조사 병행 방향을 ACCEPT**한다. 이 판정은 아래 두 work 범위만 승인한다.

- G1: lap376이 복원 가능하다고 판정한 lap372 pre-image·실제 endpoint diff를 먼저 물질화한다.
- G2: G1 공유 파일을 건드리지 않는 원본 읽기 전용 용량 지도 조사 봉투를 RELEASE한다.

실제 원본 n=1, S1 결정성, Stage B, WM_CLOSE, 제품 G1~G4, M1 종료/M2 이동 및 사용자
마일스톤 승인은 모두 미발효/UNKNOWN이다. 현재 큐는 한 가지여야 하므로 다음 work는 G1
provenance 물질화만 수행한다. G2 봉투는 독립 카드로 승인됐지만 STATUS의 현재 다음 작업은 아니다.

## 2. 독립 근거 대조

- `loop/.lap_counter=378`을 사용했다. 사용자 메시지의 runtime evidence `lap=377`은 이전
  상위 회차 표지로 보고 counter를 쓰거나 복원하지 않았다.
- 현행 SHA는 `tools/runtime_env.py=2d4e478f073f1e4c981b42c39e0cff6a8ba0f058217a5d8e1aec0377b1ca790e`,
  `tools/s1_load_evidence.py=44e8c1a70372d0748b19497f3d7c91249807ff3600701ba238aa6e3fac2c4861`,
  `tests/test_s1_load_evidence.py=69e714045a464f6c047099c479929ba8bec4f64108b102a0036252d2558b755d`다.
- raw source log `logs/laps/2026-09-14/lap-0373.log`는
  `3ee03b31f1fbf96797e0b5c8a38573c0888b660590c8afd131c3a3b203d7fb0c`로 lap376과 일치한다.
  로그에는 lap372 endpoint SHA `2d957c43...f2ac5ce`/`d53e5cde...dc2958f`, 편집 전 원문과
  두 apply-patch 출력이 존재한다. 이번에는 로그 내용과 현행 endpoint만 독립 확인했으며 exact reverse
  2/2는 lap376의 과거 판정이다. artifact를 대신 쓰거나 과거 판정을 fresh 실행으로 승격하지 않았다.
- private 보호 입력은 EXE 1,032,192 B / `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`,
  save000 3,093,902 B / `1c703551888f5c85a1fa2fb7b43d28309eb0b88e4bbf6e859f1a98b629e719da`로
  lap362 pin과 일치한다. 읽기·해시만 수행했다.
- G2 입력 세 문서는 현행 트리에 있고 SHA는 `ec426595...1c45`, `43f788a6...e8`,
  `d1170aba...9dfc`다. `player_offsets.md`의 `0x00B92CC0` 구 라벨은 STATUS의 별도 정정 대기이므로
  G2 work가 확정 근거로 재사용하면 안 된다.

## 3. 다음 Luna/high work — G1 provenance 한 가지

허용 변경은 새 `docs/history/laps/snapshots/<자기 lap>_lap372_preimage_recovery/` artifact와
자기 lap 기록·STATUS·handoff뿐이다. 현행 production/test 세 파일, 원본, fixture, pin,
reference/golden, 과거 probe는 변경하지 않는다.

1. 위 raw log의 정확한 원문과 실제 patch 출력만으로 `tools/runtime_env.py`와
   `tests/test_s1_load_evidence.py`의 lap372 pre-image를 만든다. 기대 SHA는 각각
   `2d957c43a8b3526d95b0b1685e6d4d2f02d436150f535b81086f397d6f2ac5ce`,
   `d53e5cde55e1d14f4639b3ab794ad702075039721416cb035595cc803dc2958f`다.
2. 두 pre-image, 현행 endpoint와의 unified diff, source-log path/size/SHA, 추출·변환 명령,
   전후 파일 SHA·size를 manifest에 기록한다. diff는 runtime 5 hunks(+9/-8), test 2 hunks(+25/-2)를
   독립 재확인하고 forward 적용이 현행 SHA, reverse 적용이 기대 SHA가 되는지 검사한다.
3. 현행 세 source/test SHA 불변을 확인한 뒤 targeted `tests/test_s1_load_evidence.py` → repo-root
   provenance를 출력한 lap354 probe exact-once → `make doctor` → `make check` → safety 두 명령을
   fresh 실행한다. 실패나 SHA 불일치면 산출물·출력을 보존하고 재pin/재시도/게임 실행 없이 승격한다.
4. 다음 새 middle이 artifact·적용 양방향·게이트를 ACCEPT하기 전 original n=1은 0회다. ACCEPT 뒤에도
   lap361/362의 fixture/slot/좌표/150초/cleanup/argv/output 필드를 유지한 실행 카드를 Astra에 반환하고,
   Astra가 n=1을 별도 발효해야 한다. 이 provenance 회차 뒤 같은 내용의 재계획 회차를 추가하지 않는다.

## 4. RELEASED G2 work 카드 — 현재 큐 아님

Luna/Sonnet5/high work가 별도 회차에서 `analysis/memory_maps/g2_capacity_boundaries.md` 한 파일만
작성한다. 원본 SHA를 fresh 확인하고 다음 항목을 주소/old bytes/폭/경계/직접 caller·writer/
`CONFIRMED|INFERRED|UNKNOWN`으로 표 작성한다: 개인 count·supply·reservation, owner roster,
전역 alloc/free와 sentinel, ID 폭, save serializer, 지원 통신 경계. 출발 필드 `+0x200a/+0x200c/
+0x2010/+0x2012`는 현행 원본에서 재확인 전 확정하지 않는다.

종료 산출물은 “5000보다 먼저 닿는 첫 제약”과 단일 measurable probe다. probe에는 활성8인,
저/고전비·건물/효과 혼합, per-owner count/supply/reserved, pool high-water/allocation failure,
RSS/address space/tick, 생성거부·손상·OOM·CPU정체 구분식을 넣는다. 실제 G2 실행·패치·새 fixture는
금지한다. 60~90분 또는 실패 가설2회면 주소/경로 한 개의 concrete blocker로 종료한다.

## 5. 검증과 정지선

fresh `make doctor`는 top `ok=true`, 보호 원본 verified이며 runtime manifest 부재는
`side_effects=false`인 선택적 상태다. `make check`는 430 passed, Ruff/compileall/mypy/
`CONTEXT_PASS`; `.venv/bin/python checks/safety.py`와 `bash checks/safety.sh check`는 모두
`SAFETY_PASS`였다. 바이너리 patch 변경이 없어 old/new bytes, unsupported-version rejection,
combined non-overlap, byte-exact restore는 N/A/SKIP이며 과거 캡처를 fresh 실행 증거로 승격하지 않았다.

implementation-unchanged-streak는 이번 종료 시 2다. lap377 Astra와 이번 middle이 다음 측정 가능한
변화를 위 G1 artifact로 승인했으므로 다음 회차는 이를 수행해야 하며, 통과 뒤에는 독립 middle 검수와
Astra 실행 발효로 곧바로 이어간다. 필수 게이트의 예상 밖 실패·근거 충돌·마일스톤 경계에서는 현물을
보존하고 `loop/ESCALATE_SOL`로 반환한다.
