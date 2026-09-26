# 2026-09-12 | lap 280 | lap279 S1 정적 검수의 독립 교차검증 (middle)

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5`/high, middle tier
  (진단·계획·컨펌). 외부 subagent/provider 호출 0. 게임 구현·hands-on 수정 0.
  lap 번호는 `loop/PROMPT.md` 규칙대로 `loop/.lap_counter`=**280**을 사용했다(읽기만 함).
  주의: 러너 배너는 `lap=279`로 표시됐다. 파일 값을 우선했고 불일치를 여기 기록만 한다.
- 가설 / 사용자 관찰: lap279가 `loop/ESCALATE_SOL`로 승격 요청한 항목 —
  "여섯 행 CONFIRMED 교체를 수용할지" — 를 **같은 읽기 전용 범위**에서 독립 판정한다.
  lap279 probe 재실행만으로는 불충분하므로 원시 objdump에서 다시 읽는다. 사용자 신규 관찰 없음.
- 예상 PASS / FAIL 조건: (a) lap279 probe 재실행이 exit0/failures=[]이고 출력이 기록과 같다,
  (b) 다른 추출 경로로 21블록 표·로스터 기하·G3 산술이 재현된다 → 수용.
  어느 하나라도 어긋나거나 lap279가 보지 않은 경로가 여섯 행을 뒤집으면 → 반려.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted):
  `docs/work/active/G1_S1_MIDDLE_ACCEPTANCE_LAP277.md` §4.3 추가
  (`b6cf5226…102aa844`), `docs/history/laps/probes/20260912_lap280_middle_s1_crossverify_probe.py`
  신규(`8b75e394…5beb3247`), `logs/lap280/s1_crossverify_probe.json` 신규
  (`3d4fe307…6a6d6a9126`), `docs/STATUS.md` 갱신, 본 기록, `loop/ESCALATE_SOL` lap280 항목 추가.
  **게임 코드·comparator·producer·tests·원본 EXE/DLL/assets·PASS 규칙·slot 강등 규칙 변경 0.**
  커밋 없음(`LOOP_ALLOW_COMMITS=0`, uncommitted 보존).
- 원본 SHA / 후보 SHA / 환경 / 활성 인원 / 지도 / 군대 / fixture:
  원본 EXE `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`
  (저장소 사본 `Syw2plus/syw2plus_original.exe`). 후보 없음.
  `../Syw2plus/save/save000.dat` `1c703551…629e719da` 3,093,902 B,
  `save006.dat` `616b7997…9289a0d064` 3,437,942 B — **읽지도 파싱하지도 않았다**(해시/크기만).
  `tools/runtime_env.py` `e4f6a834…22455837`, `tools/compare_g1_stage_b.py` `9b684cec…f32e426efdb`
  전부 lap279 기록과 일치. `patches/population/runtime_driver.py` `8c2465b8…0be82e94`.
  환경 `.venv`/Linux 정적 도구(objdump, sha256sum). **게임 실행 0.** runtime fixture 없음.
- 실행 명령 / 로그 / 캡처 경로 및 해시:
  `.venv/bin/python docs/history/laps/probes/20260912_lap279_middle_s1_serializer_probe.py`
  → **exit 0, failures=[]**, 출력이 lap279 기록과 동일(재실행 검증).
  `objdump -d -Mintel -j .text` 범위 `0x440C20..0x440FF0`, `0x440FF0..0x442E00`,
  `0x40F4B0..0x40F560`, `0x42A900..0x42BD00`, `0x401000..0x4E0000`.
  신규 probe → `logs/lap280/s1_crossverify_probe.json`, **exit 0, failures=[]**.
  Fast: `make check` → **291 passed in 44.24s**, Ruff/compileall/mypy(10 files) 성공,
  `CONTEXT_PASS`; `LOOP_DRY_RUN=0 bash checks/safety.sh check` → `SAFETY_PASS`. PNG/capture 없음.
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN):
  **판정: lap279 §4.2.3 여섯 행 CONFIRMED 교체를 수용(ACCEPT)한다. 정정 2건 동반.**
  재현한 것 — literal 블록 21개/`save_fwrite=22`,`load_fread=22`/표 완전 동일,
  bulk `0x892410`+`0xE397C` → `0x975D8C`, camera `0xB42D7C`(4B)+`0xB42D80`(4B) 인접,
  로스터 1200×`0x758` = `0x66B790..0x892410`, load 순서 bulk(`0x4412DC`)→로스터(`0x441305`),
  G3 넘침 `0x991330-0x975D8C=0x1B5A4`. 전부 독립 재계산 일치.
  **보강:** load 로스터 `0x40F51B`가 미존재 슬롯을 `rep stos` `0x1D6` dword(=`0x758` B)로
  0 채움 → 로스터 영역에 잔여 상태가 남지 않는다(lap279보다 강한 결정성 근거).
  **정정1(§4.2.2):** "포맷이 정적으로 완전히 열거된다"는 과장이다. literal 표 밖에
  비-literal 스택 블록 1개(`0x440C70`, `0x40` B)와 **map-layer serializer 28쌍**
  (save `0x42A920`…`0x42BC40`+`0x42AB70` / load `0x42A960`…`0x42BC80`+`0x42ABA0`)이 있다.
  lap279는 그중 1개의 앞 `0x40` 바이트만 봤다. 이번에 28쌍 개수 동일·주소 인접(델타 0x30~0xA0)·
  **28개 save 전부 `fwrite` 호출, 28개 load 전부 `fread` 호출**을 기계 확인했다. 지형 레이어라
  여섯 행을 뒤집지 않는다. **레이어별 원소 수 동일성은 여전히 미검증.**
  **정정2(§4.2.5-1):** 전제가 틀렸다. `tools/runtime_env.py`에는 유닛 좌표 읽기 경로가 **없다**
  (line 2412는 `scene_state["units"]`를 그대로 받아쓴다). 실제 생산자는
  `patches/population/runtime_driver.py:84-100`이고 오프셋은 이미 고정돼 있다:
  type `+0x8D`, owner `+0x8E`, internal_id `+0x29C`(4B), **x `+0x2A2`(2B), y `+0x2A4`(2B)**.
  원본 교차근거: `WORD PTR [reg+0x66BA32]` **115회**, `WORD PTR [reg+0x66BA34]` **115회**,
  전부 WORD 폭이고 `0x4069C7`/`0x4069D1` 처럼 **항상 짝으로** `movsx` 읽힌다.
  `DWORD [eax*8+0x66BA2C]` 67회 + 접근자 `0x40F540`(`eax*8 = slot*0x758`)가 `+0x29C`를 반환한다.
  → **x/y 오프셋 고정은 CONFIRMED.** 남은 것은 상수 승격이라는 구현 작업 하나뿐이다.
  **항목2 방향 정정:** `active_units`는 PlayerStruct 필드가 아니라 `units` 리스트의 owner별
  집계다(`tools/runtime_env.py:2398-2401`). PlayerStruct 후보는 `+0x200A/+0x200C/+0x2010`이며
  집계와 장부는 **다른 양**이다. 같다고 전제하지 않고 대조는 work tier로 넘긴다.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태:
  회귀 없음(코드·검사 규칙 무변경, Fast 291 passed 유지). 이것은 **S1 fixture 정적 타당성**의
  2단 판정이다. 두 run의 실제 값 동일성·제품 G1 증거·Stage B 허가·runtime 쌍 예산·
  마일스톤 종료는 **아니다**. 자기 승인 금지에 따라 상위/다음 세션이 이 수용 판정을 재확인한다.
  유지되는 위험: map-layer 28쌍의 원소 수 동일성 미검증, WM_CLOSE teardown 결함,
  실제 후보 scene/input evidence 부재, R17/R6-B-R2, offline 8건 주차, M-d/M-e 사각,
  **G3 저장 포맷 `0x1B5A4` 넘침(상위 결정 사안)**, G2~G4 미해결. 사용자 마일스톤 승인 없음.
  추가 관찰(수리 계열 열지 않음): `tools/runtime_env.py:186`
  `G1_UNIT_TYPE_TABLE_BASE_ADDRESS=0x0066BE88`은 `G1_UNIT_BASE_ADDRESS+0x6F8`이고
  `unit_type * 0x758`로 인덱싱된다 — 즉 **살아있는 유닛 배열을 type id로 재인덱싱**한다.
  원본에도 `[eax*8+0x66BE88]` 형태가 있어 문법은 맞지만 의미는 미확정이다. 기록만 한다.
- 다음 한 가지: work tier 인계 — `x=+0x2A2`, `y=+0x2A4`, `internal_id=+0x29C`를
  `tools/runtime_env.py`에 이름 있는 상수로 승격하고 위 정적 근거를 `analysis/memory_maps/`에
  인용으로 남긴다(실행 예산 0). runtime 쌍·Stage B 예산·G3 저장 포맷 방향은 상위(Astra) 대기.
