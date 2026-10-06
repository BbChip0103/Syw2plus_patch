# G1 P5-T — lap928 D1 독립검수 / clip 준비 비용 work 인계 (lap929 middle)

중간 tier, solo. 게임/source/probe/tests/validator/바이너리 수정·새 게임 실행·커밋0.
현재 실행 큐는 STATUS만 따른다. lap925 §2·§4·§6과 lap927 D1 계약을 유지한다.
이것은 비용 수리의 부분 확인과 work 인계이며 P5-T/G1 종료 또는 마일스톤 승인이 아니다.

## 1. 독립 확인

- 10개 시도 원문을 전부 읽었다. 최초 D1/4-byte unroll은 historical source로 구분한다.
  REP STOS 이후 8개 build의 입력48개/current MATCH, DLL/manifest/trace/capture SHA MATCH.
  7개 scroll pair의 snapshot70개를 다시 decode해 baseline/candidate 각5tick 전필드 상태 parity PASS.
  보호 EXE/save SHA 및 tinted 두 hook old bytes MATCH. 완료 cleanup/game 삭제·prefix process0 확인.
- 첫 D1 DOWN first30: whole QPC35.609248ms, exclusive clip33.649507ms, 기존 sections1.602690ms,
  residual0.357052ms/present. 동일 first/last row·10MHz·29간격 차분이다. whole은 sections에 더하지 않는다.
  RIGHT28개는 INCOMPLETE. REP STOS 범위/값/정렬 앞뒤 byte 보정은 소스상 유지된다.
- B′1 diagnostic: DOWN whole26.579059/clip24.704238/sections1.530576/residual0.344245ms,
  RIGHT27.186614/25.507176/1.392572/0.286866ms. 최초 대비 clip 비용 감소가 관측된다.
  전후 실행 환경과 계측 간 차이가 있으므로 전부 REP STOS 단일 원인의 효과라고 확정하지 않는다.
  frame−whole 약25.25/26.78ms는 simulation/present/trace/wait 등 외부 시간의 합이며 특정 병목 UNKNOWN이다.
- coarse GetTickCount 합과 whole QPC는 동등한 계측이 아니다. 호출별 정수ms 누적과 QPC 차이를
  미해명 근거충돌로 취급하거나 1.5ms sections를 전체 재호출로 읽지 않는다.

| 비계측 실행 | DOWN PT-c ms | RIGHT PT-c ms | 독립 판정 |
|---|---:|---:|---|
| REP STOS 첫 GREEN | 52.103448 | 51.344828 | DOWN FAIL |
| GREEN2 | 50.586207 | 50.413793 | PASS |
| B′1 | 56.068966 | 52.482759 | 두 키 FAIL |
| B′2 | 50.344828 | 51.379310 | PASS |

표본 seq/sim_tick/covered−stale를 raw와 대조했다. 각30개가 observation tick 경계 안이다.
진단 B′1 RIGHT53.965517ms도 FAIL이며 진단 실행을 연속2회 조건에 끼우지 않는다.
**B′ 연속2 미충족, PT-c HOLD.** pair-result의 PASS는 PT-c 승인과 별개다.

## 2. 화면·상태·성능 한계

- 전체10시도 PS3 present9456개에서 V1 위반0. 최종 source8개 실행의 PNG40쌍을 재계산해
  V2·V2s·V2q 값/원문 MATCH·PASS, 활성 Scale2x validator/gate PASS를 확인했다.
  GREEN2/B′1/B′2 loaded/drag contact sheet도 원본/후보로 나란히 보았다.
  캡처는 동일 snapshot tick의 최종 입력 증명이 아니므로 클릭/선택/생산 효과를 새 PASS로 바꾸지 않는다.
- old nearest `mirror_validator BLOCKED`는 보존하되 새로운 화면 결함으로 귀속하지 않는다.
  `g1_mirror2x_probe.py:158`은 ratio 미달 **또는** same_frame_oracle!=1에 같은 오류 문구를 출력한다.
  `0.999812 below0.999000` 문구를 숫자 비교 실패로 재해석하지 않는다. validator/기준 변경0.
- C1~C3 raw histogram bin 중복0·drop0·개수일치, ceil(0.95N) p95를 독립 재계산했다.
  ratio1.002506194/0.999996908/0.999995720, p95 delta+8/+9/+8ms로 C 부분 PASS.
- 고정 camera[158,101] late20 effective p50는 GREEN2/B′1/B′2 모두395960.5/480000=82.4918%,
  stale p50는74863.5로 감소 미입증. `tinted_clip covered`는0이다.
  PT-d 원문의 tinted 하한11439에 대해 first GREEN11949/ GREEN2 11439/ B′1 **9229**/ B′2 14414다.
  **B′1 PT-d 미달도 보존한다.** 진단11099 역시 acceptance 증거가 아니다. 실행마다 원인 없이 animation 탓으로 면책하지 않는다.
  범위를 줄인 소스 수정은 없지만 수치가 다르므로 다음 work에서 실제 frame/key/covered 경로를 확인한다.
- dynamic API 실패주입/강제 rollback, 최종 입력, HD≥90%, GDI, 두 번째 장면, 사용자 승인 미검증 유지.

## 3. 다음 work 한 가지 — D2 clip 준비 내부 귀속 후 최소 비용 수리

새 계획 회차 없이 work가 아래 하나의 비용 가설을 구현·격리 실행·수리한다:
**남은 exclusive clip 준비24.7~25.5ms가 임시 heap 작업·full-buffer fill·mask 중 어디에서 발생하는가.**

1. 기존 opt-in QPC/marker와 source48개 build 경로를 재사용한다. `g1_mirror2x.c`,
   `g1_perf_sections.{h,c}`, `direct_draw_trace.c`, 관련 `tests/test_g1_mirror2x.py`만 단일 writer로 수정한다.
   clip 준비의 세부 exclusive bucket을 `temporary_alloc_free`, `buffer_fill`, `mask_prepare`로 나눈다.
   viewport 준비/복원은 remainder에 남긴다. clipped written HeapAlloc도 타이머로 감싼다
   (lap928은1296의 이 할당이 timer 밖이다). 기존 clip 합과 세 bucket+remainder를 같은 경계에서 검산한다.
   임시 할당 requested bytes와 실제 fill/mask bytes는 분리하며, lap928의4.15GB 합계를 고유 메모리량이나
   순수 memory-write bandwidth로 사용하지 않는다. 전체 QPC/기존 sections와 중복 차감0.
2. off/on·reset·early-return·실패·timer overlap을 실행 가능한 회귀로 잠그고 DLL 빌드한다.
   같은 save006/일정/미러범위에서 짧은 isolated diagnostic pair를 완주한다. acceptance에는 쓰지 않는다.
   source SHA/보호old bytes/20GiB/private game·prefix·display/maintenance I/O 비중첩/cleanup 규칙 유지.
3. 가장 큰 bucket이 확인되면 **동일 work에서 최소 수리→비계측 GREEN 재실행**한다.
   heap 지배가 확인되면 renderer가 소유한 임시 full replay2개+mask의 capacity 재사용이 후보이다.
   필요한 전체 sentinel fill, viewport/buffer 복원, mask 내용, visible-frame 검증, LUT pointer/digest key,
   tinted hooks·미러범위를 유지한다. 재사용은 fresh fill/검증 생략이나 negative cache가 아니다.
   OOM/부분할당/크기증가/실패시 원복·정확한 범위/연속호출의 잔존 bytes 회귀를 먼저 고정한다.
   fill/mask 지배이면 해당 루프의 범위/byte-identical 결과를 유지하는 최소 수리만 한다.
   구간이 안 갈리면 세 bucket/residual 수치를 middle에 남기며 무근거 새 최적화·strategy 대기를 만들지 않는다.
4. PT-d 수치는 고정 camera 창과 실제 writer/key/covered 경로를 함께 기록한다. 특히 B′1 9229 반례를
   덮거나 하한을 낮추지 않는다. 원인이 동일 구현의 추적 가능한 결함이면 고쳐 재실행한다.
5. 같은 source 비계측 GREEN→B′ 연속2→C3, 모든 시도 보존. PT-c≤52.0ms/경계안30개/기존 일정·coverage·
   PT-d·V1/V2/s/q/Scale2x·snapshot/input parity·C ratio≥.95/p95Δ≤16ms를 모두 확인한다.
   계측ON·성공만 선택·경계/validator 변경으로 통과시키지 않는다. source 결함 수리 반복은 PROMPT③대로다.
6. 문서 확정→lint/typecheck→전체Fast 완주→새 middle. 일반 비용/수치 HOLD는 work↔middle이며
   lap925 §6 조건 외 strategy 재호출 없음. G1 마일스톤 마감·G2/G5 재개·G3/G4 재개·커밋/게시 없음.

## 4. 근거와 종료

공유temp `20261004_lap929_middle_review/recalculate.py`와 `recalculation.json`(SHA256
`5a462d9e36396fc747a6c01a54a23ce75712e17b74d08d270976aa90b38f2e8f`, 입력790파일),
`supplement.json`, `original_pins.json`, `visual_contact_sheet.png`에 재계산/입력/관찰을 보존했다.
doctor·lint·typecheck·safety PASS. 문서 확정 후 fresh make check 결과는 STATUS에만 보강한다.
새 raw 충돌/원인불명3회 실패/마일스톤 경계는 발견하지 않았다. ESCALATE_SOL 생성 조건 없음.
판정은 **D1 수리 부분확인·P5-T HOLD(PT-c/PT-d)·G1 HOLD·D2 work 인계**이다.
