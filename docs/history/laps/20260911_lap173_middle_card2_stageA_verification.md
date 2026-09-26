# 2026-09-11 | lap 173 | 목표 G1 (카드2 Stage A 2단 독립 검수)

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5` / high / middle tier
  (진단·계획·확인). 게임 코드 hands-on 수정 없음, 게임 run 0회, 코드 변경 0줄.
- 가설 / 사용자 관찰: lap172 work가 구현한 Stage A(A-1~A-5)가 카드
  `docs/work/active/G1_CARD2_INPUT_PARITY_HANDOFF.md`(lap171 절 L171-0~L171-6 우선)의 범위·
  세탁 방지 불변식·좌표 계약·증거 schema를 실제로 충족하는지 코드로 독립 확인한다.
- 예상 PASS / FAIL 조건: A-1(a~d)·A-2(menu 포함 공용 헬퍼·×2 선변환 없음)·A-3(단계별 즉시
  flush)·A-5(승인 주소만)가 코드로 성립하고 허용 파일 밖 변경이 없으면 Stage A 승인. 세탁 방지
  불변식(**production BLOCKED 동안 overall PASS 불가**)이 어느 한쪽 경로에서라도 깨지면 반려.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted):
  이번 바퀴 코드 변경 없음. 검수 대상 트리는 lap172 기록과 동일:
  `tools/runtime_env.py` `7a0374e5259c7d6201fa634540658d223839cc12492894dca4b885b3b12fa1fb`,
  `tests/test_runtime_env.py` `4d18c5d55f6ee9c3bd019b29db72d68fda44ed184d775b2cfb7f52d8ea9dfa51`
  (`sha256sum` 재계산 2/2 MATCH). 문서 변경: 이 파일, `docs/STATUS.md`,
  `docs/work/active/G1_CARD2_INPUT_PARITY_HANDOFF.md`(lap173 절 추가). uncommitted, 커밋 없음.
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture:
  게임/후보 실행 0회이므로 활성 플레이어·지도·군대·fixture는 N/A. 원본·제품 EXE/DLL/assets/
  baseline/golden 변경 0 — 2026-09-11 00:00 이후 수정된 비캐시 파일 전수 목록에 해당 경로가
  **한 건도 없음**을 `find -newermt`로 독립 확인했다. lap172가 건드린 파일은 22:07~22:12의
  `tests/test_runtime_env.py`, `tools/runtime_env.py`, `docs/STATUS.md`,
  `docs/history/laps/20260911_lap172_luna_g1_card2_stageA.md` 4개뿐이며 모두 허용 범위다.
- 실행 명령 / 로그 / 캡처 경로 및 해시:
  `sha256sum tools/runtime_env.py tests/test_runtime_env.py` (2/2 MATCH);
  `find . -newermt "2026-09-11 00:00" -type f ...`(범위 확인);
  `make check` / `bash checks/safety.sh check` / `.venv/bin/python -m pytest` 는 **비대화형 권한
  거부로 실행 불가**(3회 형태 시도, 재시도 없음) → SKIP. 보조 정황으로 lap172 실행 직후 남은
  `.pytest_cache/v/cache/lastfailed`가 `{}`(빈 집합)이나, 이는 내 독립 실행이 아니며 승인 근거로
  쓰지 않는다. 캡처 생성 0건.

## 판정: **Stage A 조건부 반려 (CONDITIONAL REJECT). Stage B 개시 불가.**

### 독립 확인한 PASS 항목 (코드 근거)

1. **A-1(a) production 클릭 콜러블 미호출** — `_g1_production_click_if_authorized`(`:1544~1553`)는
   인자를 `del`하고 무조건 `{"status":"BLOCKED", ...}`를 반환한다. 공용 시퀀스는 `:2089`에서
   실제 클릭 대신 `lambda: None`을 넘긴다. 클릭 경로가 구조적으로 존재하지 않는다.
2. **A-1(b) 효과 대기 미진입** — `:2089`의 production 레코드와 `:2105`의 drag 준비 사이에
   `wait(...)` 호출이 없다. 레코드에 `waited=false`/`blocked_reason`을 남긴다(`:2101~2102`).
3. **A-1(c) 후속 단계 도달** — `drag_select`(`:2105~2133`), `minimap`(`:2135~2162`)이 production
   레코드 뒤에 그대로 실행된다.
4. **A-1(d) baseline 절반만 성립** — `checks["required_inputs"]`(`:2793~2794`)는 5개 태그가 모두
   존재하고 **모두 `result=="PASS"`**일 것을 요구한다. production은 `"BLOCKED"`이므로 False이며
   `overall`(`:2797`)은 `all(checks.values())`를 요구하므로 **`g1_a` verdict는 PASS가 될 수 없다.**
   (후보 쪽은 아래 B1에서 깨진다.)
5. **A-2 공용 헬퍼·menu 대칭(L171-2)** — `_g1_run_input_sequence`를 baseline(`:2715`)과 후보
   (`:3076`)가 동일 인자 계약으로 호출한다. menu도 양쪽이 같은 기록 함수 `_g1_record_input`과
   같은 술어 `_g1_menu_input_pass`(PS9→PS7 **그리고** 전/후 캡처 SHA 상이)를 쓴다
   (baseline `:2560~2566`, 후보 `:3003~3011`). 후보의 "무조건 PASS"는 제거됐다.
6. **A-2 좌표 계약(lap149) 유지** — `_g1_input_geometry`(`:1909~1922`)는 `content`와
   `x11 = content_crop + (x,y)`만 만들고 `scale`은 **기록만 하고 곱하지 않는다.** 실제 전송 경로인
   `baseline_click/drag`(`:2697~2707`)와 `candidate_click/drag`(`:3053~3065`)도 `content_crop`
   오프셋만 더한다. `x11_mouse_click.py`에 스케일 인자 추가 없음.
7. **A-3 / L171-5 단계별 즉시 flush** — `record()`가 각 레코드 직후 `flush()`를 호출하고(`:2053`),
   `_g1_flush_input_stage`(`:2019~2027`)가 `evidence.json`과 `inputs.jsonl`을 그 자리에서 쓴다.
   무반응으로 `_wait_state`가 아니라 술어 실패로 끝나는 경우에도 **record→flush가 raise보다 먼저**
   실행된다(`:2070~2083`, `:2119~2133`, `:2149~2162`). 캡처 레코드는 `path`/`sha256`/`dimensions`를
   포함하고(`:844~860`) PNG는 승인된 `/home/dev_00/sharedfolder/260320_Syw2plus/temp/`에
   `YYYYMMDD_HHMMSS_` 접두사로 저장된다(`:157`, `:849`).
8. **A-5 장면 대조 필드·주소 승인** — `_g1_scene_snapshot`(`:1962~2016`)이 owner별
   nation/active_units, 유닛 슬롯(owner/type/world), owner0 HQ world, camera, tick, 맵 경계를
   PS3 직후·입력 이전에 남긴다(baseline `:2682`, 후보 `:3030`). 사용 주소는
   `0x00B3DE34/0x00B3DE36`(`:241~242`)로 `analysis/memory_maps/population_runtime_bridge_0910.md:87`에
   근거가 있고 camera `0x00B42D7C`는 기존 승인 주소다. **새 오프셋 추가 0건.**
9. **opt-in 기본 off** — `--g1-input-sequence`는 `store_true`(`:3417`)로 기본 off이며 CLI 전달
   테스트가 있다(`tests/test_runtime_env.py:99~117`). dwell과 입력의 동시 사용은 `:2826`에서 거부된다.

### B1. 반려 사유 (블로킹) — 후보 verdict가 세탁 방지 불변식을 깬다

`g1-presentation-trace`의 verdict(`tools/runtime_env.py:3187~3188`)는

```
"overall": "PASS" if not error and bool(cleanup.get("ok"))
           and evidence["validator"].get("status") == "PASS" else "BLOCKED"
```

로 **입력 결과를 전혀 보지 않는다.** `--g1-input-sequence` on에서 production이 `BLOCKED`인데도
`error is None` + cleanup ok + validator PASS면 후보 verdict는 `overall="PASS"`가 된다.
카드 A-1의 필수 불변식은 "`g1_a`/**후보** verdict의 overall은 PASS가 될 수 없다. 이 불변식을 깨는
구현은 반려다"이므로 이는 명시적 반려 사유다.

지금 당장 그 경로가 관측되지 않는 이유는 **무관한 close/teardown 결함이 항상 먼저 BLOCKED를
만들기 때문**뿐이다. 즉 현재의 안전은 설계가 아니라 **다른 결함에 의한 우연한 차폐**이며,
P6/close 수리가 성공하는 순간 "production 미승인 상태의 후보 run이 overall=PASS"가 기록된다.
또한 후보 verdict에는 입력 관련 필드가 **하나도 없어**(`error`/`cleanup`/`validator`만) L171-4의
"입력 관측값 / production BLOCKED / teardown 실패를 각각 별도 필드"도 충족하지 못한다.

### B2. 반려 사유 (블로킹) — L171-1이 요구한 회귀 (d)가 없다

L171-1은 "회귀 테스트는 네 가지를 모두 고정한다 … (d) production BLOCKED 동안 `required_inputs`
FAIL 유지 및 overall PASS 불가"라고 못박았다. 실제 테스트 파일 전수 검색 결과
`required_inputs`/`overall` 불변식을 검사하는 테스트는 **0건**이다
(`grep -n "required_inputs\|overall" tests/test_runtime_env.py` → verdict 불변식 테스트 없음,
`:107`의 `{"overall": "BLOCKED"}`는 CLI 전달 테스트의 더미 반환값이다).
(a)(b)(c)는 `test_g1_shared_input_sequence_blocks_production_but_reaches_later_stages`
(`tests/test_runtime_env.py:1160~1211`)로 고정돼 있으나 (d)는 **코드로만 성립하고 테스트로 고정돼
있지 않다.** B1이 정확히 이 결손으로 통과한 사례다.

### B3. 보완 요구 (비블로킹) — 시퀀스 수준에서 "클릭 미전송"이 고정되지 않았다

`:1194`의 시퀀스 테스트는 `click=lambda _x, _y: None`으로 호출 기록을 남기지 않는다. 따라서
누군가 production 단계에서 `click(670, 490)`을 호출하도록 바꿔도 이 테스트는 통과한다.
`_g1_production_click_if_authorized` 단위 테스트(`:1090~1106`)는 그 함수만 덮는다.
클릭 좌표를 리스트에 기록하고 `(670,490)`이 **한 번도 전송되지 않음**을 단언해야 한다.

### B4. 기록해 둘 거동 변화 (승인된 범위, 반려 아님)

lap169 본문의 "off면 기존 거동 **바이트 그대로**"는 lap171 L171-2/L171-3에 의해 사실상 완화됐다.
`--g1-input-sequence` **off** 경로도 다음이 바뀌었다: (i) 후보 menu가 술어 실패 시 예외로 run을
끝낸다(`:3010~3011`, 이전에는 무조건 PASS 기록 후 계속), (ii) `_g1_scene_snapshot`(`:3030`)이
상세 state에 players/units가 없으면 `RuntimeSafetyError`를 던진다. **lap168 P5 대조군을 그대로
재실행하면 이전과 다른 지점에서 중단될 수 있다.** 다음 바퀴가 그것을 새 회귀로 오독하지 않도록
여기에 남긴다.

### B5. Stage B 개시 전 판단해야 할 예산 문제 (미해결)

L171-1은 "입력 단계를 추가/건너뛸 때 `_wait_state`의 단계별 마감시한 부재 예산 문제를 항상 같이
판단한다"고 요구했으나 lap172 기록에 그 판단이 없다. `--g1-input-sequence`는 PS3 이후
`_wait_state`를 3회 추가하고(`:2061`, `:2110`, `:2140`) 이들 중 하나라도 무반응이면 run 전체
timeout(≤90초)을 소진해 close/finalization 증거까지 잃는다. Stage B를 열기 전에 (a) 단계별 마감
시한 도입 여부와 (b) 90초 예산 내 단계별 소요 실측 계획을 **명시적으로 결정**해야 한다.

- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN):
  source SHA 2/2 MATCH; 허용 파일 범위 PASS; 원본·제품·baseline·golden 변경 0 PASS;
  A-1(a)(b)(c) PASS; A-1(d) baseline PASS / **후보 FAIL(B1)**; A-2 PASS; A-3/L171-5 PASS;
  A-5 PASS(새 오프셋 0); A-4 회귀 (a)(b)(c) PASS / **(d) 부재(B2)**; `make check`·safety·pytest
  **SKIP(비대화형 권한 거부)**. Stage A 종합 **조건부 반려**. Stage B **개시 불가**.
  제품 진척 0, 마일스톤 승인 0.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태:
  이번 바퀴 코드 변경이 없으므로 회귀 위험 0. 현재 트리의 Fast 수치(`196 passed`)는 **lap172의
  자기 보고이며 이번 middle이 독립 재현하지 못했다** — Claude 세션의 비대화형 권한 거부가 lap167·
  169·171·173에서 반복된 구조적 검증 공백이다. B1은 오늘 관측되지 않지만 close 결함이 해소되는
  즉시 실재화한다. Stage B의 Tier-2 비교는 A-5 필드 일치 전까지 여전히 UNKNOWN이다.
  사용자 마일스톤 승인 없음.
- 바퀴 종료 시 파일 해시(커밋 없음, uncommitted 보존):
  `tools/runtime_env.py` `7a0374e5259c7d6201fa634540658d223839cc12492894dca4b885b3b12fa1fb`(불변),
  `tests/test_runtime_env.py` `4d18c5d55f6ee9c3bd019b29db72d68fda44ed184d775b2cfb7f52d8ea9dfa51`(불변),
  `docs/STATUS.md` `25019a38502957de262dc8f2fe7ade104eedfce4c4755f11edc8ec8c44132d84`,
  `docs/work/active/G1_CARD2_INPUT_PARITY_HANDOFF.md`
  `32dd647ac9be00fb5cdc81eead39103c174473305cf1b22fe51ef0f8645ec06d`.
  STATUS는 207줄로 늘었다. 다음 compaction 시점이 가까우니 provenance를 보존해 history로 옮긴다.
- 다음 한 가지: work tier(Luna/high 또는 Sonnet5/high)가 B1·B2·B3를 수리한다 —
  카드 lap173 절 A-6/A-7/A-8. 그 뒤 새 middle 세션이 재검수하고, 그때까지 Stage B 게임 실행·P6·
  G1 마감·G2 전환은 없다.
