# 2026-09-27 | lap 708 | 목표 G4 (길찾기 개선 후보 v1)

- 실제 provider/model/effort / 지정 역할: Claude Code Sonnet 5 (실무, 세션 자체 확인 "이번
  세션은 일반 작업자다"). STATUS "다음 한 가지"(2026-09-27 08:55 운영자 판정, 구현 우선)
  수행: ① 원본 길찾기 함수 상수를 정적으로 특정, ② 상수 1개를 바꾼 후보 v1 빌드, ③
  obstacle_row(world (93,56)) 원본 N=3 대 후보 N=3 paired 비교.
- 가설 / 사용자 관찰: 기존 G4 기록(`docs/history/laps/*g4*`, `analysis/memory_maps/*ai*`)에는
  실제 길찾기 알고리즘 상수 기록이 없어(전부 AI order-issuance/postload 계측) 새로 정적
  특정했다. `Unit+0x290==3`(MOVE) per-tick 핸들러의 유일 호출 경로
  `0x48E706→0x40C390→0x40B7E0(mode=4)→0x40B810`을 추적해, `0x40B810`이 목표 방향
  ±1타일 로컬 nudge를 최대 `mode`값(=4)회까지 시도하다 실패하면 `0x40B740`(경로 재계산이
  아니라 원거리 목표로 리셋)으로 넘어가는 구조를 확인했다(근거
  `analysis/memory_maps/g4_move_order_local_step_retry_20260927.md` §1-2). **H1**: 이
  로컬 재시도 한도를 4→8로 올리면 lap707이 정한 obstacle_row `path_ratio_max`(2.540, world
  (93,56))가 개선된다.
- 예상 PASS / FAIL 조건: 후보 obstacle_row N=3(world (93,56))의 `path_ratio_max`/`arrival_rate`가
  원본 N=3 대비 악화되지 않고(동률 이상 개선 기대) 개선되면 PASS, 변화 없거나 악화되면 H1
  FALSIFIED. 크래시 0, `source_unchanged=true`, `cleanup.ok=true` 전 실행 요구.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted): 신규
  `patches/pathing/g4_move_retry_budget_v1.py`(EDITS 1건, 파일 오프셋 `0xC395`,
  `6a04`→`6a08`), 신규 `patches/pathing/test_g4_move_retry_budget_v1.py`(7 tests),
  `tools/g4_path_baseline_probe.py`(`--variant {original,candidate}` 추가, 기본
  `original` 무변경 — 회귀 8 tests로 확인), 신규
  `analysis/memory_maps/g4_move_order_local_step_retry_20260927.md`(정적 근거+실측 결과).
  uncommitted, `LOOP_ALLOW_COMMITS=0`. 게임 EXE/DLL 원본 미변경(사설 사본만 패치).
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 원본 SHA
  `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`(10회 전부 불변).
  후보 SHA `62a100fc65b8b454aa357a9dce8dccbc6e5785dde3c48c50eb6c54250ce5b72a`(5회 전부
  `patched_bytes` 재계산과 일치). 환경 `[ESL]Syw2plus/` 소스, 1600x1200x24 Xvfb,
  `SYW2_SUPPLY_PROBE=1`. 활성: 솔로(비고정 시드) 1인 × 10회(원본 5 + 후보 5). fixture:
  기존 워커(슬롯1198) + owner0 type2 55기 dense fixture, 원본 20-cap 드래그로 20기 선택,
  `obstacle_row` 목적지(8타일, 본진 footprint 방향).
- 실행 명령 / 로그 / 캡처 경로 및 해시: `PYTHONPATH=. .venv/bin/python
  tools/g4_path_baseline_probe.py --scenario obstacle_row --variant {original|candidate}
  --runtime-root local/runtime/g4-lap708-<variant>-run<N> --artifact-root
  .../temp/Syw2plus_patch/20260927_lap708_g4_move_retry_budget/<variant>-run<N>`. 결과
  JSON SHA256(대표): original-run3 `e6812fe7…6b05d`, run4 `7b73af4e…4b8`, run5
  `d8281c8a…8568`, candidate-run1 `1a794382…8693`, run3 `f46e5f36…558`, run4
  `dff1a931…56d`(전체 10개 해시는 이 lap 세션 로그에 보존). `make check` 로그
  `logs/gates/20260927_lap708_g4_move_retry_budget_make_check.log`.
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN): 10회 중 5회(원본3+후보2)는 world (10,49)로
  착지해 lap706/707 제외 판정대로 배제(그 world는 -Y쪽 이동 명령 자체가 안 나감,
  `ever_move_command_count=0`). world (93,56) 착지분(원본3/후보3)만 비교:

  | variant | unit_type | arrival_rate | arrived/expected | path_ratio_max |
  |---|---:|---:|---|---:|
  | original ×2 | 7 | 0.90 | 18/20 | 1.9864005845210897 |
  | original ×1 | 21 | 0.90 | 18/20 | 1.9328098099980875 |
  | candidate ×3 | 21 | 0.85 | 17/20 | 1.9328098099980875 |

  같은 `unit_type=21` 표본이 원본·후보 양쪽에 있어 직접 매치된다:
  **`path_ratio_max`는 완전히 동일(16자리 일치), `arrival_rate`는 18/20→17/20로 하락**.
  `unit_type=7`(원본 최악값 1.9864) 표본은 후보에서 재현되지 않아 직접 비교 없음(한계).
  **판정: `H1 FALSIFIED`** — 로컬 재시도 한도 4→8 상향은 이 시나리오의 `path_ratio_max`를
  개선하지 못했고 도착률을 소폭 악화시켰다. 크래시 0, `source_unchanged=true`,
  `cleanup.ok=true` 10/10. `make check` **1042 passed(849.56s)**, ruff/compileall/mypy/
  `CONTEXT_PASS` 전부 PASS, `checks/safety.sh check` **SAFETY_PASS**. 신규 테스트
  15개(7+8) 전부 PASS. 원본 SHA 10회 전부 불변, cleanup 전부 ok, 크래시 0. 각 run 종료
  후 `local/runtime/g4-lap708-*/*/game` 사본 삭제(디스크 위생, manifest/output/prefix/
  로그 보존).
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: 회귀 없음(위 make check/ruff/mypy/safety
  전부 PASS, 기본 `--variant original`은 기존 산출물과 동일함을 8개 회귀 테스트로 확인).
  **남은 위험**: (1) `unit_type=7` 표본은 후보 쪽에서 한 번도 안 나와 원본의 최악값(1.9864)
  자체는 후보와 비교되지 않았다 — 이 패치가 그 표본에서 우연히 개선/악화를 만들 가능성은
  미확인. (2) 도착률 하락(17/20 vs 18/20)의 원인(재시도 예산 증가가 다른 유닛 스케줄을
  밀어냈는지)은 미조사. (3) 이번 v1 바이트 패치는 **채택하지 않는다** — falsified 가설의
  증거로만 보존한다(패치 파일/테스트는 남기되 다음 후보에 이어 쓰지 않음). 독립 검수/사용자
  승인 없음(work tier 자체 raw 측정, 정보 제공용).
- 다음 한 가지: `analysis/memory_maps/g4_move_order_local_step_retry_20260927.md` §3이
  미조사로 남긴 `FUN_0041AF90`(실제 탐색 진입점, bounding-box 마진 `0x1E`=30타일, vtable
  호출 대상 객체 미특정)을 다음 work가 정적으로 이어서 특정한다 — 마진 상수나 vtable 안쪽
  탐색 본체의 노드/스텝 예산이 `path_ratio_max`를 실제로 좌우하는 지점일 가능성이 높다.
  실패 가설 1/2 소비(이 lap), 다음 회차에서 2번째 가설이 실패하면 STATUS/APPROVALS에
  FEASIBLE/NOT_FEASIBLE/BLOCKED 판정을 명시하고 strategy 판정을 요청한다.
