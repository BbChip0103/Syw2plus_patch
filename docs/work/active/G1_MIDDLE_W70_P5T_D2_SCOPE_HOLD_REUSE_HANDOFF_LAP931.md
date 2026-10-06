# G1 P5-T D2 — 독립 검수·타이머 범위 HOLD 및 work 수리 인계 (lap931)

중간 tier solo. 제품/source/tests/probe/validator/raw/baseline 변경·게임 실행·커밋0.
실제 provider Codex, 시스템 표기는 GPT-6이며 정확한 모델 ID/effort는 이 세션에 노출되지 않았다.
다른 모델로 전환하거나 역할 모델 접근을 검증했다고 주장하지 않는다. 현재 사용자 지정 middle 역할을 따른다.
현재 실행 큐는 STATUS만 따른다. 이 문서는 진단과 조건부 work 수리 계약이며 제품/계획 승인이 아니다.

## 1. 독립 확인된 결과

- lap930 6 pair를 읽고 5 build×48 입력/current MATCH를 확인했다. `d2_diag_r2`는 원복한
  historical `rep stosb`이며 mirror source만 다르다. 6 DLL·12 trace·manifest·PNG SHA MATCH.
  scroll 5 pair의 snapshot50개를 다시 decode해 각5tick 전필드 baseline/candidate parity PASS.
  기존 입력502파일의 SHA를 기록했다. 보호 EXE/save006 및 tinted hook old bytes MATCH.
  모든 lane cleanup/game_removed=true·prefix process0·game 경로 부재를 확인했다.
- PS3 present5755개 V1 위반0. 현행 source 5 pair의 PNG25쌍 V2/V2s/V2q 재계산 MATCH/PASS,
  active Scale2x PASS. B′2 drag 원본800×600/후보1600×1200를 직접 나란히 관찰했다.
  old nearest BLOCKED는 기존 same-frame 진단이며 새 화면 결함으로 귀속하지 않는다.
  이 캡처는 최종 입력 효과/동일tick 화면의 새 승인 증거가 아니다.

| 비계측 실행 | DOWN PT-c ms | RIGHT PT-c ms | PT-d tinted covered |
|---|---:|---:|---:|
| GREEN | 52.551724 | 51.379310 | 11524 |
| B′1 | 53.896552 | 52.379310 | 9569 |
| B′2 | 57.000000 | 50.620690 | 9314 |

각 키30개 seq/sim_tick/covered−stale를 원문과 대조했고 observation tick 경계 안이다.
PT-c≤52.0ms 및 B′ 연속2 조건 미충족, PT-d 하한11439에 B′1/B′2 미달이다.
late20 effective p50=395960.5/480000=82.4918%, stale p50=74863.5, tinted_clip covered0.
stale 감소·전체HD≥90%·tinted_clip 수용은 미입증이다.
이름 `C3`는 20초 performance pair **1회**다. histogram 중복0·합계/meta 일치·drop0,
ratio0.9974653168·p95Δ+11ms PASS지만 현행 source의 C1/C2/C3 세 회를 대체하지 않는다.

## 2. 구현과 검수 전제의 범위 불일치 — 승격 사유

`G1_MIDDLE_W70_P5T_D2_REVIEW_LAP930.md` 항목1은 clip whole와 세 bucket의 동일 호출 경계를 요구한다.
실제 `g1_mirror2x.c:1342`에서 상위 timer 차분을 누적하고 1343에서 시작값을0으로 만든다.
1348의 clipped `written = clip_prepare_alloc(width*height)`는 alloc bucket으로 측정되지만
상위 timer는 **성공 뒤1351에서야** 다시 시작한다. 마지막 frees 앞1395에서 시작값을 덮으므로
이 할당은 성공/실패 모두 상위 clip 합에서 누락된다. 세 helper끼리 중첩이 없다는 사실과 별개다.
따라서 clip−세 bucket의 양수0.34%를 검증된 exclusive remainder로 승인할 수 없다.
이것은 해시 전사 오류가 아니라 재현 가능한 계측 구현 범위 결함이다. 기존 raw는 고치지 않는다.

누적 값 자체는 원문과 일치한다: clip32136220 QPC ticks, fill26655802(82.9463%),
alloc/free5265389(16.3846%), mask106235(0.3306%), 산술차108794 ticks.
동일30표본/29간격의 DOWN fill20.777614ms·alloc/free4.149441ms·mask0.048690ms,
RIGHT fill21.445948ms·alloc/free4.283069ms·mask0.051928ms. fill 지배 단서는 수용한다.
`rep stosb` ticks/byte는 원본 대비1.4583% 증가한다. 두 실행만으로 통계적 열등을 확정하지 않지만
채택 근거가 없어 원복한 결정을 지지한다. bytes는 호출별 누적 쓰기/요청이며 고유메모리량이 아니다.
사용자의 근거 충돌 중단 지시를 적용해 `loop/ESCALATE_SOL`을 남긴다. P5-T/G1 HOLD 유지.

## 3. 승격 검수 후 work 한 가지 — 임시 replay 두 개+mask capacity 재사용

승격 작업자는 위 timer 범위를 독립 확인하고 QPC 전체분해 승인을 보류한 채 아래 work 수리로 연결한다.
상위 strategy 재호출·새 목표/임계값·미러 범위 변경은 필요하지 않다.

가설: 매 호출 full buffer 할당/해제와 새 메모리의 첫 쓰기 비용 일부를 capacity 재사용으로 줄인다.
fill은 HeapAlloc 뒤 첫 전체 쓰기라 first-touch가 fill bucket에 포함될 수 있다(소스상 가능성).
page fault/raw allocation residency 증거는 없어 **원인 확정은 아니다**. 할당시간 감소만으로도
4.15~4.28ms/present 개선 여지가 있으나 실제 PT-c 회복/coverage 개선은 미보장이다.
mask 자체는0.05ms라 별도 mask 알고리즘 변경은 지지하지 않는다.
identity bind는 `g1_hd_asset.c:515` 이후 프레임·mask를 자체 메모리에 복사하므로 임시 capacity와
자산 key를 분리할 수 있다. 구현 가능성 FEASIBLE이며 새 문서·추가 계측만의 회차로 되돌리지 않는다.

1. work 단일 writer는 `g1_mirror2x.c`와 실행 가능한 회귀만 최소 수정한다. 계측 parent 범위는
   모든 clip alloc/free/fill/mask를 포함하고 original replay/bind를 제외하게 복구한다.
   timer overlap/off/reset/zero duration/alloc 실패는 모의 QPC·allocator로 실행해 확인한다.
2. renderer가 소유하는 임시 full replay2개와 mask capacity를 유지한다. 같은/작은 요청은
   재할당하지 않는다. growth는 필요한 새 메모리를 먼저 모두 확보한 뒤 capacity를 교체한다.
   부분할당/OOM이면 새 메모리를 정리하고 기존 capacity를 보존하며 현재 호출의 원래 실패 경로를 따른다.
   필요 bytes가 capacity보다 크면 오래된 버퍼를 사용하지 않는다. full2개 각각 G1_MAX_BUFFER,
   mask≤832×600 범위 이내, overflow/0/정확한 요청 끝·guard bytes를 검증한다.
3. **매 호출 기존 전체 bytes를 각각00/FF로 다시 채운다.** ROI fill/새 페이지의 선행 fill 생략·
   negative cache·sentinel 생략 금지. mask 전칸을 다시 써 residual byte를 소비하지 않는다.
   visible 비교·viewport/buffer 복원·LUT pointer+digest key·identity/Scale2x·writer 범위는 유지한다.
   original 예상 프레임/키/미러 버퍼를 scratch로 재사용하지 않는다.
4. 실행 회귀: 같은/작은/큰 크기의 연속 요청·서로 다른 stride/surface·00↔FF·mask shape 변경,
   첫/두번째/세번째 OOM·growth partial failure·실패후재시도·viewport 원복·detach/재설치 소유권.
   hook 원복 실패 시 살아 있는 hook이 쓰는 메모리를 해제하지 않는다. 무제한 heap growth 금지.
5. DLL 빌드→같은 save006·일정·전용game/prefix/display에서 실제 최소 수리 실행. 기존 marker로
   corrected clip/bucket을 짧게 비교하고 **같은 source 비계측 GREEN→B′연속2→C1/C2/C3**를 완주한다.
   30표본/observation tick·52ms·PT-d11439·V1/V2/s/q·Scale2x·state parity·성능 ratio≥.95/Δ≤16 유지.
   tinted coverage/stale/mismatch 반례를 함께 남긴다. capacity만으로 PT-d를 고쳤다고 주장하지 않는다.
   추적 가능한 구현 결함은 work가 수리→재실행하며 PROMPT③ 반복 원칙을 따른다.
6. 원본/과거raw/baseline 안전핀 보호·20GiB·maintenance I/O 비중첩·cleanup 유지.
   문서 확정 뒤 lint/typecheck/Fast 완주→다음 독립 middle. milestone 마감·G2/G5·G3/G4 재개0.

## 4. 근거/검사/종료

공유temp `20261004_lap931_middle_review/`의 `recalculation.json` SHA256
`7bb1cff438c43c59e9e567bcc7133a8403c3e5acbf32dcdc1cee5f9a34a07690`,
`supplement.json` SHA256 `ccf6dcdd471c58458fa17238b2532571077c2082ca092214f91d30c2bea54ef7`,
`original_pins.json` 및 독립 스크립트에 근거를 보존했다.
doctor top-level ok=true/original verified; default runtime manifest 부재는 새 runtime 승인 아님.
lint/typecheck·focused25 PASS. fullFast/새runtime는 사용자 근거충돌 중단 지시로 SKIP한다.
검사후 현재fingerprint PASS를 과거Fast로 대체하지 않는다. 마지막 safety/context·read-audit는 STATUS에 기록한다.
