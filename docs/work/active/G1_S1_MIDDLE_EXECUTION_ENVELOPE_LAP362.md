# lap362 middle — S1 원본 단일-load 결선 봉투

2026-09-12 / Codex 현재 세션 / 정확한 모델 ID는 노출되지 않아 주장하지 않음 /
사용자 지정 high·middle(진단·계획·확인). 게임 코드·하네스·tests hands-on 수정과
게임/Wine/Xvfb/입력/PNG 실행은 0이다. `docs/MODEL_ROUTING.md`의 현재 middle 선택은
Claude Code `claude-opus-5`뿐이라는 차이를 공개하며, 다른 모델을 실행했다고 쓰지 않는다.

## 0. 판정

**기술 범위 ACCEPT 초안 / 세션 STOP — work 발효 전 재검수 필요. 실제 run 허가는 0회다.** lap361 §2의 CLI trigger
미결선과 trigger 반환 뒤 시작하는 wait deadline은 현행 코드에서 재현됐다. 반면 pre
`selected_index==1`은 보호 원본의 PS35 진입 사슬이 선택 WORD를 먼저 1로 초기화하므로 정상
UI 사건으로 구성 가능하다. slot1 strict-interior click은 이 값을 유지하면서 동일 사건에서
load handler로 들어간다. 실제 pre 값·click delivery·open/load는 실행 전까지 UNKNOWN이며,
관측 불일치는 완화하지 않고 NO_RUN/UNKNOWN으로 닫는다.

이 판정은 event-boundary orchestration의 구현 범위만 승인한다. S1 수집 성공, 두 run 결정성,
Stage B, WM_CLOSE, G1 제품 합격, M1 종료/M2 이동 및 사용자 마일스톤 승인이 아니다.

## 1. 입력과 PASS/FAIL 기준

- runtime counter `362`; 메시지의 `lap=361`보다 `loop/.lap_counter`를 우선했고 쓰지 않았다.
- 보호 원본: `local/runtime/20260912_191422_3558862_0/game/syw2plus_original.exe`,
  SHA256 `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`.
- fixture: 같은 private copy의 `save/save000.dat`, 3,093,902 bytes, SHA256
  `1c703551888f5c85a1fa2fb7b43d28309eb0b88e4bbf6e859f1a98b629e719da`.
- 현행 SHA: `tools/runtime_env.py=ba0a7beb657ce6c7a174d9323c4254f2d696b74277a974e15a5216d272b7372c`,
  `tools/s1_load_evidence.py=fffc644495b442627a8166125365caa6270999ff06bead52d2b1e1a8ad90fa65`,
  `tests/test_s1_load_evidence.py=7508e5c1fe3b6110336d3b1457381f4d208d632f361ff8c842309b18ad6cb8c7`.
- ACCEPT 조건: trigger 결손·deadline 범위를 독립 재현하고, 원본 주소/old bytes로 pre slot1과
  click→load를 비순환 연결하며, 한 command의 전체 deadline·종료·artifact·실패 분류를 수치화한다.
- BLOCKED 조건: slot1 pre 상태가 별도 load click 없이는 만들 수 없거나, 허용된 private helper만으로
  load 사건을 exact-once 구성할 수 없거나, 시간/종료 소유권이 분리되지 않는 경우다.

## 2. lap361 세 지점 독립 검수

### 2.1 trigger 결선 — CONFIRMED MISSING

`tools/runtime_env.py:5320..5357`의 `g1-s1-load-evidence --pid` 생산 분기는 private prefix
소유 PID와 manifest를 검사하고 `runtime_driver.read`만 만든다. 마지막
`g1_s1_load_evidence(...)` 호출에는 `trigger`가 없다. `:3366..3383`은 이 경우 read 0회로
`EVENT_TRIGGER_MISSING/UNKNOWN`, `trigger_invocations=0`을 기록한다. 현재 CLI는 load 수집이 아니다.

### 2.2 deadline — CONFIRMED INCOMPLETE

`tools/s1_load_evidence.py:235`의 pre snapshot과 `:252` trigger가 끝난 뒤 `:273`에서
`started=monotonic()`을 만들므로 현행 `timeout`은 PS3 polling만 제한한다. manifest 검사,
private copy 준비, launch, PS9→PS35, pre, trigger, post, cleanup을 포괄하는 상한은 없다.
`G1_S1_PS3_WAIT_SECONDS=G1_R1_PS35_STAGE_BUDGET` alias도 load 실측치가 아니므로 계승하지 않는다.

### 2.3 pre slot1과 click→load — STATIC ACCEPT, RUNTIME UNKNOWN

보호 원본을 `objdump -D -Mintel`로 재유도했다.

1. PS35 사슬은 `0x4248E0→0x4A2FF0→jmp 0x493C40→push 8→0x4D6A00`이다.
   `0x4D6A0F..0x4D6A19`가 load mode `0x3ED`를 넘겨 `0x4D6930`을 호출한다.
2. `0x4D6930`은 mode를 저장하기 전에 무조건 `0x4D5CA0`을 호출한다. old bytes
   `66 c7 81 9e 0f 00 00 01 00 c3`은 `WORD[this+0xF9E]=1; ret`다.
   그 뒤 `0x4248E5`가 PS WORD `0x004ED818`에 35를 쓴다. 따라서 PS35에서 읽는
   `WORD@0x01087216`의 정상 초기 선택은 1이다.
3. 이 offset의 쓰기는 해당 코드 창에서 초기화 `0x4D5CA0`, mouse strict-hit의
   `0x4D5FF8`, keyboard 증가/감소 `0x4D603A/0x4D607C`로 한정된다. 별도 preselection
   click은 필요하지 않다. 값이 실제로 1이 아니면 실행 전제 불일치로 처리한다.
4. origin `(240,145)`에서 rect1은 `[260,119,540,143]`; logical `(400,131)`은 strict
   interior다. `0x4D5F9D..0x4D5FF8`은 mouse 좌표를 검사해 `index+1=1`을 같은 WORD에 쓴다.
5. button 경로 `0x4D6740→0x4D5F10`은 선택된 child가 1을 반환하면 그 selected WORD를
   결과로 돌려준다. `0x4D6A40`이 이를 `di`로 받아 `0x4D6B5A`로 보내고,
   `esi=di-1=0`, mode `0x3ED`에서 `push esi; call 0x440FF0`으로 save000 load를 호출한다.
6. `tools/x11_mouse_click.py` 기본은 root 좌표로 motion 1회 뒤 button1 down/up 1쌍이며
   `--repeat` 기본 1이다. root 좌표는 `content_crop origin + (400,131)`, presentation
   scale을 곱하지 않는다. Plan C 좌표는 사용하지 않는다.

이는 정상 구성 가능성의 정적 근거다. 실제 origin/group/selected/input/open/PS3와 fixture
raw 변화는 하나도 관측하지 않았고 PASS로 승격하지 않는다.

## 3. Luna/high work 구현 봉투 — 실행 0회

한 바퀴에서 `tools/runtime_env.py`, `tools/s1_load_evidence.py`,
`tests/test_s1_load_evidence.py`만 수정한다. 원본 R1 command/artifact의 의미와 offline
`--post-json` 경로는 보존한다.

### 3.1 단일 소유 command와 fixture

- 새 command 이름은 `g1-s1-original-load-evidence`로 고정한다. source와 runtime-root를 받아
  기존 `prepare()`로 새 전체 private copy/prefix를 만들고, 그 command가 launch, 두 입력,
  collector, artifact, cleanup을 끝까지 소유한다. 기존 `--pid`는 외부 trigger 없는 진단 경로로
  남겨 `EVENT_TRIGGER_MISSING`을 계속 반환한다.
- source와 private copy의 EXE/save000 크기·SHA를 각각 기록하고 위 두 pin과 다르면
  **NO_RUN**이다. fixture는 group WORD 0 / 1-based slot1 / save000만 허용한다.
  symlink·기존 prefix/process/output·다른 display는 거부하며 새 fixture를 만들지 않는다.
- PS9에서 기존 원본 R1 입력 `(296,505)` 정확히 1회로 PS35에 진입한다. PS35 direct pre가
  `(ps,group,selected)==(35,0,1)`이고 origin/tag 및 8×6 read가 완전할 때만 load trigger를 만든다.
- trigger는 private outer window focus 뒤 root=`content_crop+(400,131)`에
  `x11_mouse_click.py`를 기본 repeat1로 정확히 한 번 호출한다. focus/click rc와 argv,
  logical/root 좌표, helper SHA, invocation count를 남긴다. 재클릭·자동 재실행은 없다.

### 3.2 고정 시간 계약

전체 hard deadline은 command 진입 직전 monotonic 시각부터 **150초**이며 늘릴 CLI option을
두지 않는다. 각 상한은 다음과 같고 남은 시간을 빌려 쓰지 않는다.

| 단계 | 상한 |
|---|---:|
| private `prepare()`/copy/prefix 및 pre/post SHA | 60초 |
| launch→PS9 | 40초 |
| 첫 입력→PS35 | 20초 |
| direct pre snapshot | 2초 |
| focus+load trigger callback | 5초 |
| PS3 WORD wait | 10초 |
| direct post snapshot/evaluate/artifact finalize | 3초 |
| owned cleanup reserve | 10초 |

합계는 150초다. `collect_load_event_boundary`의 event deadline은 pre 직전 시작하며
pre+trigger+PS3 wait+post를 모두 포함한다. PS3 wait는 그 안의 10초 sub-cap이다.
모든 subprocess timeout은 `min(stage remaining, total remaining before cleanup reserve)`다.
시간 초과는 해당 stage와 last raw를 보존한 `UNKNOWN`; 이 상한은 운영 안전값이지 성능 PASS가 아니다.

### 3.3 종료·artifact·실패 분류

- 새 run directory와 `s1_original_load_evidence.json`/log/source snapshot manifest만 새로 쓴다.
  실행 당시 두 Python 원문과 input helper를 별도 snapshot에 보존하고 path/size/SHA를 manifest에
  넣는다. 실제 argv, stage start/end/elapsed, fixture/EXE pre/post SHA, DISPLAY/WINEPREFIX/PID,
  input count/좌표, pre/wait/post raw/read address·width, cleanup 결과를 기록한다. overwrite 금지다.
- 종료는 owned child, 새 private prefix의 `wineserver -k/-w`, owned Xvfb만 다룬다.
  전역 kill/기존 session attach 금지. cleanup 실패는 원시 증거와 residue PID를 보존하고 UNKNOWN이다.
- 사전 SHA/ownership/freshness/geometry/slot/좌표 결측은 **NO_RUN**. trigger 예외·rc!=0·count!=1,
  timeout, 부분 read, PS35/pre 불일치, PS3 미도달, post group/slot 불일치, pre==post,
  fixture raw 불일치는 **UNKNOWN/FAIL**로 보존한다. PS3 단독·open 성공 추정은 PASS가 아니다.
- 수집 유효 PASS는 exact-once + PS35→PS3 + direct pre/post 변화 + post 8×6==pinned fixture +
  cleanup OK의 결합이다. scene 전체, S1 (A)+(B), 제품 G1과 구분한다.

### 3.4 회귀와 work 종료

합성 회귀는 (a) timer가 prepare 전 시작, (b) trigger 지연이 event/total deadline을 소비,
(c) pre slot!=1이면 trigger 0회, (d) root 좌표가 crop+(400,131)이고 scale 미적용,
(e) helper repeat1/exact-once, (f) stage별 timeout, (g) post/cleanup 실패 raw 보존,
(h) 새 artifact/snapshot overwrite 거부를 잠근다. 기존 21 targeted와 lap354 F1~F4도 유지한다.

work는 실제 게임을 실행하지 않고 targeted → lap354 probe → `make check` → safety만 실행해
편집 전후 SHA와 함께 반환한다. 다음 새 middle이 이를 독립 검수한 뒤에만 Astra가 실제 원본 n=1,
150초, save000 실행을 별도 발효하거나 반려한다.

## 4. 경계와 다음 한 가지

금지: 게임/Wine/Xvfb/클릭/PNG 실행, EXE/DLL/save/fixture/pin/reference/golden 변경,
과거 probe 재pin, timeout 확대, 재클릭, Stage B/P6/WM_CLOSE/G2~G4, 새 의존성, 커밋.
W3/N14와 역사적 lap331 identity UNKNOWN은 그대로 보존한다.

**다음 한 가지:** 새 middle/Sol 승격 작업자가 §5의 probe import provenance를 독립 해결하고
lap354 probe를 fresh 1회 통과시킨 뒤에만 §3을 work에 발효한다.

## 5. 필수 검증 예상 밖 실패와 STOP

기록 뒤 targeted `python3 -m pytest -q tests/test_s1_load_evidence.py`는 **21 passed**였다.
다음 필수 독립 검증을 저장소 root에서
`python3 docs/history/laps/probes/20260912_lap354_middle_lap353_s1_reader_review_probe.py`로
실행했으나 rc1 `ImportError`로 중단됐다. probe의 `from tools import runtime_env`가 현재
저장소가 아니라 형제 `Syw2plus_re/tools/__init__.py`를 선택했다. `PYTHONPATH`는 unset이었고,
probe는 계산한 `REPO`를 import 전에 `sys.path`에 넣지 않는다.

이 실패는 S1 계약 assertion의 FAIL이 아니라 실행 환경/import provenance 실패지만,
필수 검증의 예상 밖 실패다. 다른 argv/PYTHONPATH로 재시도하거나 Fast/safety를 계속하지 않았다.
§3 ACCEPT 초안은 **미발효**이며 다음 승격 작업자는 과거 lap360의 canonical probe argv/environment를
대조하고, 형제 저장소를 읽지 않는 명시적 repo-root import 계약을 정한 뒤 원본 probe를 수정 없이
fresh 1회 검증해야 한다. probe rc0/`failures=[]` 전에는 work 구현을 시작하지 않는다.
