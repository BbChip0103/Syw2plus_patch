# 2026-10-04 | lap921 | G1 P5-H 독립 raw·source·HUD 검수

- 지정 역할/모드: 중간 tier 진단·컨펌, solo. 실제 API model/effort 메타데이터가 이 표면에 노출되지 않아 특정 Sol/high 호출을 주장하지 않는다. 게임 구현·하네스·tests·validator·원본·기존 raw·golden 변경0, 새 게임 실행0, subagent0, commit0(uncommitted). `loop/.lap_counter` bytes `921`을 읽기만 했다.
- 입력/가설: PROMPT①~⑥, 최신 INBOX/APPROVALS, STATUS, DESIGN1~4, MODEL_ROUTING, lap914 카드·주소, lap918 인계, lap919 수리와 lap920 실행 기록을 확인했다. 최신 계약은 G1 최우선/G2·G5 종료/G3 중단/G4 보류다. lap920의 source-matched GREEN/B′2/C3가 lap918의 미충족을 해소하는지 독립 확인한다. 과거 C2 실패는 삭제하거나 원인 판정으로 바꾸지 않는다.
- 사전 성공식: build48/current·DLL·trace·PNG·snapshot SHA 및 보호 EXE/save 일치, PH-a~d, V1위반0·V2/s/q≤2000(5tag), Scale2x PASS, GREEN/B′2 상태·일정 parity/30present, C3 ratio≥0.95·p95Δ≤16ms, HUD 배치·키 확인. 입력효과/HD90%/P5-T/GDI/다른 장면/사용자승인은 별도 미충족으로 유지한다.
- 변경 파일: 이 lap 기록, `docs/work/active/G1_MIDDLE_W70_P5H_ACCEPTANCE_P5T_HANDOFF_LAP921.md`, `docs/STATUS.md`만. 재계산/비교 PNG/감사는 공유 temp `20261004_lap921_middle_review/`에 보존한다. INBOX348/APPROVALS250줄은 추가하지 않았고 미결·반려·원문 삭제0. STATUS는130줄 이하·Blockers1로 유지한다.

## 식별·안전

- 보호 EXE SHA256 `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`, 비합성 save006 SHA256 `616b79978917c8fd6f996a5cafca50e1e411b24a4fccca05efa3cb9289a0d064` 재해시 MATCH. 일본 save006, 원본800×600/후보1600×1200. owner records8은 활성8인 부하 증거가 아니다.
- 6개 pair별 build48 입력/current SHA·복사본 MATCH. 생성 `inmm_stub.c`의 poll 삽입과 Makefile bridge 추가를 원문 변환식으로 대조했다. bridge source·각 DLL SHA는 build manifest와 일치하며 전체 값은 recalculation.json에 있다. probe `09b2862ccb24406b2b96ac9931da7f8c37a0e3abbc2a2070c382b16ef197f397`, tests `ee2fca2f5df1603828a6cd75d3baf5dc5a214da2ce2a8d76fd9da41adb99b3f7`도 lap920 기록과 MATCH.
- 12lane source/private EXE·fixture SHA, trace SHA, PNG60장 SHA, snapshot30개 SHA·header를 확인했다. 각 private manifest의 bridge SHA도 일치. 각 lane `status=PASS`, source_unchanged/cleanup.ok=true, 자기 game 사본 부재. 새 사본/기존 세션 접촉0.
- panel hook pin `51 53 8b 5c 24 10`은 보호 EXE PE에서 재확인. 설치6바이트 pin·분리 rollback·원본 우선 호출·반환주소4곳·opt-in은 source 검토했다. 실제 API 실패 주입/강제 rollback byte-restore는 이번 세션 미실행이며 기존 한계를 유지한다. 새 바이너리 파일 패치·배포 없음.

## 독립 수치·시각 판정

- PH-b: 보호 `fnt/pannelj.spr` header `(9,831,143,1)`·offset3060에서 RLE를 독립 해독, EOF 정확 일치. 앞800열×143 SHA256 `f649fe68a8f9a71b9e451c01cb5b0a1d79fbb06607cc8d566d3d30d108b66000`이 6trace frame SHA와 일치. 첫128byte FNV-1a `5939fabc`·writer/source/831×143 key도 일치, 신규6실행 pack_loaded0. 실제 HD pack 경로의 lap918 부분수용은 보존하며 이번6실행을 pack 실행으로 부르지 않는다.
- PH-a/d: bound 전사969/977/972/892/886/905, unbound·Lock·pointer·pitch 오류 및 key subpixel 모두0, foreign_writer_calls0. 이는 raw의 누적 metrics 재검산이며 모든 present에 독립 panel binding 필드가 있다는 주장이 아니다. PH-c는 전체 PS3 present5596행의 `(covered-stale)/480000` median으로 계산한다.

| 실행 | 전체 PS3 coverage p50 | B′/C 독립 결과 |
|---|---:|---|
| GREEN | 0.8333625000 | snapshot5×2/reference5×2·양lane 전필드diff0, DOWN/RIGHT30 PASS |
| B′1 | 0.8333552083 | 같은 snapshot/parity PASS, DOWN/RIGHT30 PASS |
| B′2 | 0.8333562500 | 같은 snapshot/parity PASS, DOWN/RIGHT30 PASS |
| C1 | 0.8255562500 | ratio0.9975020001538175, p95Δ13ms PASS |
| C2 | 0.8255354167 | ratio0.9999823006269007, p95Δ10ms PASS |
| C3 | 0.8255166667 | ratio0.9999958030855071, p95Δ11ms PASS |

- V1全6713present 위반0, Scale2x6실행 PASS. PNG raw로 계산한 V2/V2s/V2q30tag MATCH·모두PASS, 최댓값155/165/1008. 3개 scroll pair의 fixed first/last20, DOWN/RIGHT30 coverage 배열·하위중앙값·264000/전coverage90%·layer bounds·schedule을 대조했다.
- C duration은 양lane20.000~20.0015초, histogram dropped0·합계와 meta 일치, 원시 bin 누적95% p95 재계산 MATCH. baseline/candidate present 수는 C1 **400/384**, C2 400/385, C3 400/399. lap920 서술 C1의400/385는 raw를 직접 재계산해 확인한 전사 오류이며 이 기록에서 바로잡는다(기존 raw/기록은 보존). present span≥18000ms와 금지된 snapshot/census/perf_sections 관측행0도 확인했다.
- lap919 `_pair_status`는 performance 요청 시 PASS를 요구한다. 이번6pair saved/current 판정 모두PASS다. lap918 C2 ratio0.9175002925914916/p95Δ37ms의 유효FAIL은 그대로 남으며 이번 비재현은 병목 원인 해명이 아니다.
- selection HUD6쌍과 B′1 전체 배치를 직접 보았다. 원본 nearest2× HUD/후보 원해상도 HUD에서 패널 조각분리·키 색 얼룩·구멍·미니맵/버튼 위치변형은 보이지 않았다. P5-H/V3 화면 범위 부분수용. C1 선택 초상화/스탯은 양lane이 달라 같은 선택 효과의 증거로 쓰지 않는다. 나머지 같은 내용 대조도 exact same-frame oracle은 아니다.
- `_compare_input_effects` 재계산은6pair 모두 저장값과 같은 HOLD. scroll3pair selection_target=false, C3pair true; empty_click/drag_exact=true, minimap_gate_restore/production_effect=false. 이미 기록된 미충족이며 이번 회차에서 입력 성공으로 승격0.

## 검증·판정·다음

- 명령: `make doctor`; `make lint`; `make typecheck`; `.venv/bin/python -m pytest -q tests/test_g1_panel_layer.py tests/test_g1_mirror2x.py tests/test_g1_saved_scene_probe.py` — doctor 보호원본 verified/top-level ok=true, lint/typecheck PASS, focused **169 passed /5.70s**. optional 기본 runtime manifest 부재는 새 runtime 거부로 해석하지 않는다.
- 재현: `.venv/bin/python /home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/20261004_lap921_middle_review/recalculate.py`. 이 스크립트는 lap918 검산식을 읽어 현재6pair·성능gate·30표본에 맞춰 별도 작성했다. SHA256 `ce3a066002f31450a1c84038fde8e721e4071b4c36ad036d24c6a57472deb296`; recalculation.json SHA256 `5168384bd06589db311009d697d390ebdfcf55b60c2578eecd459d0ed5b697f1`. 기존 입력495파일의 계산 전후 SHA 변화0.
- 판정: **P5-H/H2·GREEN/B′2/C3 `PASS(partial)` / G1 HOLD**. lap918 성능 gate 누락은 lap919 수리와 이번 raw로 해소, 기존 실패는 보존. 설명되지 않는 새 실패·실행근거 충돌·마일스톤 경계 없음 → ESCALATE_SOL 생성 조건 없음. P단계 전환은 마일스톤이 아니다.
- 다음은 승인된 lap911§5 **P5-T 최소 구현/probe** work 인계다. 중간 tier는 구현하지 않았다. 전체HD90%/입력효과/GDI/D-2/두번째장면/최종사용자승인은 미충족으로 유지한다. 재계획·G2/G5 재개·기준완화 없음.
- 문서/handoff를 먼저 확정한 뒤 `make check`를 끝까지 기다리고 결과는 fingerprint 예외 STATUS에만 기록한다. 로그 `logs/gates/lap921-middle-final-check.log`, 검사 전후 inventory와 raw/protected/counter audit는 공유 temp에 보존한다. 전체 Fast와 새 runtime/제품 승인은 구분한다.
