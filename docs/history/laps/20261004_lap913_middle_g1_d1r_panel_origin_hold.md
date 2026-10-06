# 2026-10-04 | lap913 | G1 D-1R independent review / panel origin HOLD

- 날짜/lap: runtime `loop/.lap_counter=913` 읽기 전후 불변. 사용자 prompt runtime lap912 표기는 이전 실행 provenance이며 이번 lap은 파일913을 따른다.
- 실제 provider/model/effort / 지정 역할: 중간 tier 진단·계획·확인. 실제 model ID/effort는 API 미노출, 실제 Sol/high로 호출됐다고 주장하지 않는다. native role-routing agent_type 표면 없음, subagent0, OMX strategy/consensus 권한 주장 없음.
- 가설: lap912 D-1R source-bound maps는 lap909 메뉴맵 결함을 해소했고, panel writer표가 P5-H의 구현 근거를 제공하는지 확인한다. 성공=47build/DLL/raw/binary/protected SHA·G1~G4·분모3표·P-a~P-f 독립 일치 및 panel 원천 계약. 실패/보류=설명되지 않는 raw 차이 또는 panel 구현 근거 UNKNOWN.
- 먼저 읽은 계약: PROMPT①~⑥→AGENTS/INBOX 최신14:37 지시·APPROVALS 반려/STATUS 전체·DESIGN1~4·MODEL_ROUTING·lap912 record/handoff·lap911 strategy§6/7·관련 DD 주소 문서. patch-validation 적용. 최신 G2/G5종료·G3중단·G4보류 유지; PROMPT의 과거10000/G4 문구로 재개하지 않는다.
- 변경 파일: 이 lap 기록·`docs/work/active/G1_MIDDLE_W70_P5H_PANEL_ORIGIN_HOLD_LAP913.md`·`loop/ESCALATE_SOL`·STATUS/APPROVALS. 게임 구현·하네스·테스트·validator·임계값·pins·기존raw 수정0, 새게임실행0, commit0/uncommitted. 공유temp 검산 스크립트/JSON만 추가; 원본·기존raw 쓰기0.
- 원본 EXE SHA `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`, 비합성 save006 SHA `616b79978917c8fd6f996a5cafca50e1e411b24a4fccca05efa3cb9289a0d064` 직접 read-only 재계산 MATCH. 후보는 EXE 변경 없는 opt-in 진단DLL `90e35818702dff8cd2e4e0d8c8863c13ba44cd23b583d17d064547f7d689b219`. build47개 및 runtime_bridge source/current MATCH, manifest DLL MATCH; raw/map/context/capture SHA MATCH. `game_removed=True`, private prefix 잔류 프로세스 기록[]·game경로 실제 부재 확인. 이번 세션은 새 Wine/prefix/display/game을 만들지 않았다.
- 환경/fixture: 이전 lap912의 fresh Wine ddraw=b·private game/prefix/Xvfb·logical800×600·save006 장면. 이 세션은 보존 raw의 독립 검산이며 fresh runtime 증거 아님. 8 player records를 활성8인 부하로 세지 않는다.
- 실행명령: `make doctor`, `make lint`, `make typecheck`; `.venv/bin/python -m pytest -q tests/test_g1_census.py tests/test_g1_saved_scene_probe.py tests/test_g1_mirror2x.py::test_present_fallback_is_handled_without_second_blt_fast` → **149 passed/6.05s**. `.venv/bin/python /home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/20261004_lap913_middle_d1r_review/recalculate.py` → 독립 assertion PASS. `checks/safety.py check`·`checks/context_limits.py` PASS.
- 검산 artifact `/home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/20261004_lap913_middle_d1r_review/recalculation.json` SHA256 `e220780f64bceaf196e5083251346e5e2dff9adda30b89564944e9d34b1ec780`. 스크립트 SHA256 `209ead89ccbd03d27beebf97bb0bb94b455c149b658881e5e48d1260be50ff52`. 입력source/raw/protected/counter read-audit 69파일 changed0, 전체해시는 JSON에 보존. 기존 re-calculate.py는 PNG/JSON을 덮어쓰므로 실행하지 않고 독립 스크립트를 새temp에서 실행했다.
- 1단 재검산/2단 수용: 9hook 원본 old bytes/nonoverlap MATCH; raw active9/9, PS3 presents64/64, source buffer0x0223DC00/stride832 exact, PS3 primitive bound samples96. 두 binary각30,722,048bytes/64headers, sequence1..64/offset/stride/buffer/state 및 map category0..10·writer_pixels/assigned/unknown 모두 MATCH. payload64종, G1~G4 PASS, dropped0, DD attempts/captured64/64·missed0. byte-exact restore/unsupported-byte refusal는 source상 확인이며 이번 세션의 동적 API failure/rollback 실증은 SKIP.

| category | screen480000 | world384000 | HUD96000 |
|---|---:|---:|---:|
| unknown | 7251 | 0 | 7251 |
| rle_clip | 730.5 | 508 | 216 |
| rle_plain | 17127.5 | 6769.5 | 10382 |
| rect_fill | 135 | 0 | 135 |
| block_copy | 0 | 0 | 0 |
| rect_border | 19 | 0 | 19 |
| rle_tinted_clip | 35345 | 29493 | 5852 |
| rle_tinted | 19243.5 | 19242.5 | 1 |
| set_pixel | 0 | 0 | 0 |
| terrain_cache_transfer | 329553 | 325960 | 3598 |
| dd_surface_blt | 70637.5 | 2101 | 68536.5 |

- P-a/P-b: 64bound/64unique. P-c world terrain_cache_transfer p50 325960, 최대category·0아님→전사 덮임 분기 열지 않음. P-d HUD dd_surface_blt68536.5. P-e 마지막unknown7251/bbox[0,512,798,599], p50 unknown은 y512..599. P-f set_pixel32/32가 panel0x020D16E0/pitch800과 일치. 원 기록표와 모두 MATCH.
- writer calls_ps3: rle_clip3969/rle_plain15943/rect_fill2639/block_copy405/rect_border927/rle_tinted_clip5567/rle_tinted32022/set_pixel6473; terrain cache405, DD64. per-buffer8개 표는 JSON 그대로 보존, panel writer_calls8=6473/area522, 다른panel category0. 전체원천 원인으로 확대 해석하지 않는다.
- 시각 직접 확인: 이전 같은 실행 `present64_vs_loaded.png`를 view_image로 봄. 오른쪽map은 월드 terrain흰면·tinted건물·HUD 회색panel/프리미티브·미니맵모양으로 좌측selection.png와 viewport/패널윤곽이 맞아 메뉴맵이 아님을 확인. 두 그림의 자원/명령내용은 시점 차이가 있어 same-frame oracle/픽셀 일치 판정 아님. loaded.png의 전부검정은 이미 제외됨, 새PNG 생성0.
- **새 미확인 범위:** panel source 표면0x01E75790/backing0x020D16E0/800×203. PS3에서 분류된522만 전부set_pixel이고 **161878/162400=99.6786%의 원천writer 미분류**. 19 trace표본은 caller0x41C60C의 source_rect[0,0,800,143]→dest(0,457)/surface0x01E758C0/hresult0; 그 visible source 중113878/114400=99.5437% 미분류. 최종HUD category10면적은 그 패널의 전사결과이지 초기화/원천writer 증명 아님. PS3이전정적asset/직접쓰기/GDI 등은 가설이고 raw는 구분하지 못한다. 99.68%가 검정이라는 의미도 아님.
- 명확한 구현결함은 별도 work 인계: present_source_surface가 buffer로 직렬화(같은첫game_tick2414400610 trace actual source0x01E758C0/raw field0x0223DC00). exact buffer/pitch/headerbind는 정상, 설명가능한 필드결함으로 근거충돌 승격하지 않음. surface_blt captured는 begin에서 올라 failure-after-Lock이 가려질 수 있음; actual destination category10 writer_calls64는 정상 완료 실행을 지지. 이에 대한 일반failure injection은 미검증, 게임코드 손대지 않음.
- 판정: **D-1R `PASS(partial)` / P5-H `HOLD_PANEL_ORIGIN_UNPROVEN` / G1 HOLD**. lap911§2/§7의 panel 주writerunknown 재판정 조건과 사용자 구현근거불명확 stop 적용. 층미러불가능/게임결함확정/기준완화/마일스톤승인 아님. 내부ESCALATE_SOL 생성, 승인질문 없음.
- 필수 전체Fast `make check`: **SKIP(user evidence-stop)**. 패널 원천 구현근거가 불명확하다고 확인한 뒤 추가실행·억지마감 금지하는 최신사용자지시가 skill의 make check보다 우선한다. 검사3회 미설명 실패 없음; 이번새fullFast/runtime/HD90%/최종입력/GDI/두번째장면/사용자승인은 미검증. 과거full-test exit0/source mismatch를 현재PASS로 승격하지 않음, FULL_TEST요청도 만들지 않음.
- 다음 한 가지: 승격 작업자가 panel 초기화/원천과 층미러근거 또는 fallback범위를 확인→명시적 최소work handoff. D-1R 계측수치 재요약 회차/긴전수조사를 반복하지 않음. 세부조건은 위 handoff.
