# 2026-09-28 | lap 729 | 목표 G5

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-sonnet-5`, 실무(work, 구현·실행).
- 가설 / 사용자 관찰: STATUS 2026-09-28 lap728 "다음 한 가지" — 체크리스트 (C) 명령 전부 중 남은
  항목(일꾼 채집/건설/수리 등 특수 명령, 특수능력/변신, 승선/하선 등 툴바 전체 버튼과 단축키)을
  원본20/v5 50 paired로 raw 측정하라는 지시. 이번 lap은 그 첫 항목 **일꾼 채집(gather)** 하나만
  다룬다(한 바퀴 한 가지 가설). 배경: `analysis/memory_maps/g5_command_packer_xref_falsification_lap676.md`
  §"2026-09-27 lap719 정정"이 확정한 유일한 실제 명령 발행 호출부 `0x41F0A4`(런타임 opcode
  `word [0x892ffe]`)는 이동/공격/정지류에 국한되지 않는 **공용 opcode 슬롯**이므로, v5의 반전
  게이트(선택 개수와 무관하게 opcode로 판정)가 채집에도 동일하게 적용될 것이라는 가설.
- 예상 PASS / FAIL 조건: PASS = 원본에서 선택된 유닛 수(상한20)와 후보 v5에서 선택된 유닛 수(상한50)
  전원이 채집 목적지 우클릭 후 pending word `0x1000008`을 한 번이라도 보인다(=명령이 앞 20칸에서
  잘리지 않는다). FAIL = 후보에서 선택 수보다 적은 수만 `0x1000008`을 받는다.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted):
  - 신규 `tools/g5_worker_gather_command_probe.py`(SHA256
    `9a02d9fbfe6e329f1f01bf0bf85ec3cff1d0d7c036b6df6f09446116639fcb94`). 기존 `g5_command_coverage_probe`/
    `g5_shift_click_add_probe`와 같은 solo-lobby 부트스트랩·9점 화면↔월드 아핀을 재사용하되, 제너릭
    SEED_TYPE=2 대신 **런타임에 읽은 실제 일꾼 unit_type(=7)**으로 worker 기준 7x8 격자(55기)를
    스폰하고(`worker_grid_requests`, `dense_fixture_requests`와 동일 좌표 로직을 로컬 복제해 SEED_TYPE
    의존을 피함), 채집 목적지는 라이브 일꾼(slot1198) 우클릭 탐색으로 pending word가
    `0x1000008`(gather)이 되는 오프셋을 먼저 찾아 고정한 뒤(`GATHER_OFFSET_CANDIDATES`), 전체
    드래그 선택 후 `g5_command_coverage_probe.observe()`(무수정 재사용)로 선택 전 슬롯의 pending
    "ever" 값을 집계한다. 이 파일을 참조하는 pytest 없음(기존 G5 probe 도구들과 동일 패턴, 순수
    read-only 계측 스크립트).
  - `patches/selection/g5_selection_cap50_v5.py`/원본 EXE 무변경(읽기만). 커밋 없음(uncommitted,
    `LOOP_ALLOW_COMMITS=0`).
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 보호 원본
  `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`(양 실행 전후
  `source_unchanged=true`). v5 후보 `29e61074c622c77debb5053a412e3337fc8100f1eda29bd68efb163b1a9ee146`
  (lap723~728과 동일). 격리 Wine/Xvfb 1600×1200, PS3 solo, owner0. worker unit_type=7(런타임
  실측, lap712의 owner0 HQ49/worker7과 일치). fixture는 worker 기준 7x8(-3..3 x -3..4, 중심 제외)
  격자에 unit_type=7 각 1기(=55기, `dense_fixture_requests`와 동일 좌표, 타입만 worker로 교체).
  채집 목적지: worker-relative offset (0,6) → world(93,62), 화면(220,421) — 원본·후보 두 실행 모두
  같은 오프셋에서 pending `0x1000008` 확인. 소스 `[ESL]Syw2plus`(SHA 위와 동일).
- 실행 명령 / 로그 / 캡처 경로 및 해시: 전체 artifact
  `/home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/20260928_lap729_worker_gather/`
  {gather-original, gather-candidate-v5(FAIL, 아래 참고), gather-candidate-v5-r2}/.
  1. `PYTHONPATH=. .venv/bin/python tools/g5_worker_gather_command_probe.py --variant original
     --runtime-root local/runtime/lap729_gather_orig --artifact-root .../gather-original` →
     `COMPLETE None`. 결과 JSON SHA256 `d824a5c4b1cd4de77170de8e5948691bb7d2e7bc450f8b1b30fb36de7b8287ff`.
  2. 같은 명령 `--variant candidate --runtime-root local/runtime/lap729_gather_v5
     --artifact-root .../gather-candidate-v5` → **1회차 FAIL**: `fixture failed:
     {'reason': 'unsupported_army_fixture_type', ...}`(브리지 `patches/population/runtime_bridge.c`
     :209~213의 type-7 allow-list·flags·width/height 게이트 자체는 원본 실행에서 같은 type=7로 55/55
     성공했으므로 EXE/브리지 코드 문제가 아니라 **일회성 타이밍 flake**로 판단, 원인 재추적 없이
     즉시 재실행). 결과 JSON SHA256 `d45ddc14eb34891dda1431e757043874aee8091eca80cd6cf2b980e05f615bf9`
     (`source_unchanged=true`, `cleanup.prefix_processes_after=[]` — 안전 위반 없음, FAIL이어도 정리는
     정상).
  3. 재실행 `--runtime-root local/runtime/lap729_gather_v5_r2 --artifact-root
     .../gather-candidate-v5-r2` → `COMPLETE None`, `private_exe_sha256`=v5 확인. 결과 JSON SHA256
     `b62e043c97cfff2cb13e61d580a61202196fbda494587592bb511e37176a8413`.
  4. `make check`(foreground nohup + 로그 폴링, 로그 `logs/gates/20260928_lap729_make_check.log`),
     `bash checks/safety.sh check`.
  5. 각 run 뒤 `local/runtime/lap729_gather_*/*/game`(~1.4GB) 삭제, output/manifest/prefix/log는
     보존(디스크 위생). 디스크 여유 150G(20G 임계 여유).
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN):
  1. **원본**: worker unit_type=7 확인, 채집 목적지 탐색 1회에 성공(오프셋 (0,6)), 55기 스폰 성공,
     전체 드래그 선택 **20/20**(상한), 채집 클릭 후 `pending_ever["0x1000008"]=20` — **20/20 전원
     채집 PASS**(`all_selected_gathered=True`).
  2. **후보 v5 (재실행분)**: 같은 오프셋(0,6)이 같은 world(93,62)로 재현(9점 아핀 재계산에도 좌표
     안정), 55기 스폰 성공, 전체 드래그 선택 **50/50**(상한, `legacy_count=0`은 v5가 옛 20칸 전역
     카운트를 갱신하지 않는 기존 알려진 동작과 일치, 회귀 아님), 채집 클릭 후
     `pending_ever["0x1000008"]=50` — **50/50 전원 채집 PASS**(`all_selected_gathered=True`).
     보조 관측: `pending_ever`에 `0x1000001`(대기/유휴 계열) 50, `0x10001`/`0x10002`(다른 유닛의
     잔여 pending, 3/3 — 채집 대상이 아닌 값이므로 무시) 소수 포함, 채집 판정에는 영향 없음.
  3. **판정: PASS.** `0x41F0A4` 공용 명령-opcode 호출부에 대한 v5 반전 게이트가 이동/공격/정지류/
     부대지정뿐 아니라 **일꾼 채집에도 동일하게 일반화**됨을 실측으로 확인했다. 크래시 0(2/2 완주 run),
     `source_unchanged` 3/3, `cleanup.prefix_processes_after=[]` 3/3(FAIL 포함). `make check`
     **1106 passed(787.50s)**, ruff/mypy/`CONTEXT_PASS`/`SAFETY_PASS` 전부 PASS(신규 pytest 0개,
     제품 코드 무변경).
- 남은 제약 / 다음 probe 후보: 이 lap은 체크리스트 (C)의 **채집 한 항목만** 다뤘다(한 바퀴 한 가지
  가설 규칙). 여전히 미측정: 건설(건물 배치 UI, foundation placement), 수리(손상된 아군 건물
  대상), 특수능력/변신(해당 유닛 타입·단축키 미조사), 승선/하선(운송 유닛 존재 여부 미확인),
  명령 직후 대기열·목적지 좌표 정확 일치(이번 lap은 "받았는지"만 측정, 좌표 일치는 미측정). 다음
  work는 이 중 하나(권장: 수리 — 손상 건물 fixture로 채집과 유사한 방식 재사용 가능)를 같은 방식으로
  이어서 측정한다. `0x41F0A4` 공용 게이트 가설이 이미 이동/공격/정지류/채집 4종에서 확인됐으므로,
  남은 항목들도 PASS가 유력하다는 근거를 남기되 실측 없이 체크리스트를 완료로 표시하지 않는다.
