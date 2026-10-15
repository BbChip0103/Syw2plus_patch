# 2026-10-13 | lap1277 | G1 H-HDSINGLE middle diagnosis / BLOCKED

- 지정 역할: middle(진단·계획·확인). 모델 계약은 Codex sol / gpt-6.1-sol, high; 이 App 호출의 actual resolved ID/effort는 노출되지 않아 추측하지 않는다. 하위 모델 호출/자동 폴백 없음.
- ① 합격 기준: DESIGN 1~4절 및 최신 INBOX 2026-10-13 16:56 정정이 우선. 원본 포맷 `_hd.<ext>`와 프레임/순서/2배 픽셀을 유지한다. PROMPT의 과거 G2 10000/G4 활성 문구는 최신 사용자 종료 결정을 대체하지 않는다.
- ② 입력: PROMPT→AGENTS→INBOX 최신/상시 지시·APPROVALS 반려/미결→STATUS 전체→DESIGN 1~4→MODEL_ROUTING→lap1276 기록/ESCALATE→관련 extractor/converter/DLL. STOP 파일 없음. 러너 counter=1277 읽기만 수행.
- ③ 범위/종료: 원본 parser 의미와 BMP map의 구현근거가 명확하면 검증 가능한 work handoff; 의미를 확정 못 하면 원본/기존 변경/raw 보존·ESCALATE_SOL·종료. 게임/하네스/변환기/테스트 구현은 하지 않는다. 실패 수리 3회 조건과 별개로 구현 근거 충돌 조건이 적용된다.
- ④ 이전 바퀴 검수/가설: SItem 불일치가 전사 오류인지 원본 바이트로 직접 재계산한다. sheet 150칸 추측이나 safe skip을 선택하지 않는다. 기존 후보 수/크기와 BMP 소스 경계를 독립 확인한다.
- 원본 SHA: SItem `c1575b2f176f4cdbbc10549701a8168034948bcd30ad138819fa1bee1a4f9281`; 공식2613 `818721a5e8539f9ed97090a6d64cfdba429d46ec9caaa5671528005b22f5b724`. 원본/참고 변경0, 원본 자동배치0.
- 후보/fixture: 이전 `native_layout_retry1` 파일 3,366·1,168,997,818 B 직접 MATCH, SItem HD 없음. 이전 보고 135,293 frames/96,138 defaults/error_count1/pass=false는 lap1276 보고값이며 이번 프레임 전수 재검사를 수행한 값이 아니다. 기존 게임/맵/활성인원 fixture 없음(실행0).
- 직접 측정: SItem 51,775 B, `(9,64,32,1)`·sheet `(48715,1920,160)`·payload48,715·RLE307,200·extract_exact=false. food 참조31개·frame5..119. 기존 예외와 직접 raw가 일치한다. 데이터가 불명확하므로 형식 수용 BLOCKED; lap1158 partial 수용을 complete native 수용으로 확대할 수 없다.
- 직접 소스 확인: scanner는 확장자 제한 없이 `_hd.*`를 발견하지만 native loader는 0xBF4/version9 SPR 헤더만 수용해 BMP를 등록하지 못한다. Python 8-bit BMP writer와 DLL build 성공은 BMP runtime-map 통과 증거가 아니다.
- 도구: reverse-engineer-anything skill 적용. REA MCP 미노출; `rea doctor --client codex --json`은 config_drift(실제 검사 실패)·Hopper available, Ghidra unset을 보고했다. 전역 설정 수정/엔진 설치 없이 설치된 CLI 사용. `rea decompile '../patch_history/[ESL]Syw2plus 2613.exe' 0x4672E0 --provider hopper --format json`은 exact EXE 정체성/정적 RLE draw를 반환. static 출력을 게임 실행 증거로 쓰지 않는다. CLI 명령 끝까지 대기해 exit0 회수, 진행 중 작업 없음.
- REA Evidence: `ev_516f475f148cee2af520a400c56160343e2b117979060521f611cec7c075f371`. 추가 shell PE/Capstone 좁은 읽기로 native file transport `0x463D60`/sheet encoder 후보 `0x463E50` 위치 기록; 주소 문서 `analysis/memory_maps/g1_hdsingle_native_parser_boundary_lap1277.md`.
- 판정: raw 정체성/이전 후보 수치 MATCH(국소 확인), H-HDSINGLE BLOCKED. Transport/draw 함수만으로 SItem의 frame 분할을 확정 못 한다. decoder 단순 truncation, frame_count150 강제변경, 오류제외→PASS, 원본/핀 수정은 승인하지 않는다. 근거 상충을 억지로 마감하지 않는다.
- ⑤ 보존: 이전 ESCALATE 3,020 B·SHA256 `7b4120ae320ccce8d01f746c65a7b3b301bcd42027849a7da6cc37069bd82d33`를 `20261013_lap1277_preserved_lap1276_escalate_sol.md`에 byte-exact 보존 후 현행 승격문 작성. lap/STATUS/주소문서만 수정; 기존 제품/테스트 미커밋 변경 보존, INBOX/APPROVALS 원문 불변, counter 불변. HEAD `27dad8128791b70770dbabc6f21342eea76ef53c`는 provenance뿐. 이번 입력6파일 SHA와 raw는 공유 temp `20261013_lap1277_middle_hdsingle/raw_review.json`.
- ⑥ 검증 범위: 문서-only이므로 PROMPT 예외에 따라 전체 Fast/린트·typecheck/DLL 재빌드/동일 후보 실게임 SKIP. lap569 old wrapper는 source mismatch로 사용하지 않았다. lap1276의 145+1 테스트/빌드는 이번 독립 PASS로 재선언하지 않는다. 이번 fresh 문서·안전·diff/소스불변 검사는 아래 결과를 따른다.
- 미검증: 완전한 native round-trip, BMP C map/실제 key lookup, 공식2613·변형2종 fresh 게임, `_hd` 원본 오인 열거 여부, 전체 Fast, Windows/G1 사용자 마일스톤. 전달/커밋/사용자 승인0.

## 명시적 handoff

다음 한 가지는 root/승격자가 exact `0x463D60` incoming caller→frame-offset 선택/렌더 연결로 SItem 의미를 확정하는 것. static 연결이 안 되면 work가 격리 asset-load 관측 한 가지로 filename/loaded header/payload 및 frame0·nonzero참조의 source pointer/draw w,h를 기록한다. 이름·food 표만으로 sheet 정책을 정하지 않는다. 의미가 결정되기 전 complete candidate/전달은 HOLD. lap1276에는 제품 코드/DLL 변경이 있었으므로 무제품진척 2회 상한에 도달했다고 단정하지 않는다. 이번은 중간판정 1회이며 같은 근거의 middle 검수를 반복 기동하지 않는다; 구체 blocker와 이 최소 증거로 사용자에게 보고한다.

그 결정 뒤 work가 `tools/g1_hd_extract.py`/`tools/g1_hd_convert.py`/`tools/inmm_stub/g1_hd_asset.c` 및 관련 G1 테스트를 단일 소유한다. SItem writer/reader를 결정된 의미대로 정합화하고 BMP native 파서/매핑을 구현한다. BMP는 BM·DIB>=40·8bpp/BI_RGB·stride/orientation/bounds·원본 palette/FE 색키를 Python과 대조하고 기존 key/identity/guard 경로에 연결한다. 임의의 새 렌더 경로나 팔레트 추측을 추가하지 않는다. 일반 SPR/YTL·831폭 panel·BMP의 실제 C reader/lookup과 Python round-trip이 일치해야 하며 malformed/truncated 입력은 fail-closed여야 한다. 기존 sidecar/display-only 기능을 보존한다.

필요한 구현 회귀→완전한 `_hd` 후보 round-trip→공식2613/변형2종 요청된 display-only 새게임·save006 실게임(env 없이, HD hit/reject/stale/안전·close/소유 cleanup)→lint/typecheck 선행 및 통합후보 full Fast→fresh middle 순서를 유지한다. 이 handoff는 시험판 전달/마일스톤 승인 또는 모든 장면·Windows/G2부하/G9동작 통과를 뜻하지 않는다.

## 이번 문서/안전 검증 결과

- `.venv/bin/python checks/context_limits.py` → `CONTEXT_PASS`; STATUS128/INBOX346/APPROVALS60줄, Blockers 제목 정확히1개.
- `.venv/bin/python checks/safety.py --require-game` → `SAFETY_PASS`(보호 원본 EXE SHA·reference/golden pin 및 Git 입력검사; 게임 실행 PASS가 아님).
- `git diff --check` → exit0. raw_review의 제품/테스트 입력6파일 SHA 재비교 → `SOURCE_UNCHANGED`; counter1277 불변·STOP 없음. 이전ESCALATE 보존본 byte MATCH.
- 기록/주소/승격/raw 최종 SHA는 공유 `20261013_lap1277_middle_hdsingle/final_record_hashes.json`에 보존. 코드/게임/후보 수정0, 전체Fast·실게임·전달·사용자승인 SKIP/미완료 유지.
