# G6·G7 middle 착수 계획 — 첫 work H-G6a(Shift+클릭 루프 개수 한정) handoff (lap976)

- 작성: 2026-10-05, lap976 middle(Claude Code `claude-opus-5-5`, high). 게임 실행·source 변경·commit 0.
- 근거: 사용자 지시 INBOX 2026-10-05 03:01 KST(G6·G7 최우선), DESIGN G6/G7, `analysis/memory_maps/g6_g7_local_player_slot_bugs_20261004.md`.
- 역어셈블 근거(공유 temp, 이번 lap 직접 생성): `temp/Syw2plus_patch/20261005_lap976_middle_review/`
  `orig_41DC40.txt`·`orig_41DD10.txt`·`port_41DC40.txt`·`orig_local_writers.txt`·`orig_local_callers.txt`·`orig_xref_b63fc4.txt`.

## §1 이번 lap 독립 확인 (원본 SHA `b56986e0…a8ac`, 이식판 normal SHA `0e28ef57…d257` = 배포본·test pin 일치)

1. `0x41DC64..0x41DC78`: 스택 배열 `[esp+0x30]`을 칸 수(원본 0x14, 이식판 0x32)만큼 **0으로 초기화**한다. 그래서 빈 칸 = 유닛 id 0.
2. `0x41DD48..0x41DD6E`: 전역 선택 배열(원본 `0x899028`, 이식판 `0x18A6004`)에서 비어 있지 않은 칸만 압축 복사, 개수 → `[esp+0x10]`.
3. `0x41DD70..0x41DDE7`: 두 번째 루프가 `edi < 0x14`(이식판 `0x32`)로 **칸 수 전체**를 돈다. 각 칸에서 `0x40F560`(owner 조회)
   ≠ `[0xB63FC4]`이면 `[esp+0x28]=1`(`0x41DDB3`). 빈 칸은 id 0의 owner(원본 `0x66B81E`, 이식판 `0x112E08E` 첫 행)와 비교된다.
4. `0x41DE40`: `[esp+0x28]==1`이면 추가 중단(`0x41E06A`). → local=0(1P)이면 id 0 owner가 0이라 통과, local≥1이면 선택이 꽉 차지 않은 한 항상 중단.
   선택 0개에서 Shift+클릭도 같은 이유로 중단된다(예측).
5. Shift+드래그 루프 `0x41DF59..0x41DFB5`는 빈 칸(`word[esi]==0 && word[esi+2]==0`)을 건너뛴다 → 정상 예측(대조군).
6. 이식판의 이 함수 diff는 스택 크기(0x98→0x270)·칸 수(0x14→0x32)·배열 주소뿐이고 owner 조회는 G2 풀 `0x112E08E`로 재배치됨. 결함 동일.
7. G7: `[0xB63FC4]` 직접 쓰기는 teardown `0x41CA85`(`mov [0xB63FC4],0`) 하나. 그 외는 `0x43AF40(&0xB63FC4)`(DPID표 `0x632CA0[0..7]`에서
   `0x439B90` 자기 DPID 위치 검색) 호출 5곳 `0x4219B5`·`0x439751`·`0x4B771D`·`0x4B774C`·`0x4B9653`. `0x4B771D` 직전에 `0x632E0C→0x632C9C` rep movsd.
   로드 `0x440FF0`가 이 값을 복원한다는 근거는 없음(분석 문서와 일치, 런타임 미확정).

판정: **G6 = FEASIBLE**(정적 원인·수리 지점 확정, 런타임 재현만 남음). **G7 = 런타임 관측 먼저**(복원 대상 범위 미결).

## §2 첫 work 가설 H-G6a (Sonnet work 1 lap, 한 가지 변경)

이식판(배포 normal/fixed_start 두 lane) 위에 새 패치 모듈 `patches/selection/g6_shift_click_count_bound.py`(이름은 work 재량)를 얹는다.
- 지점: 두 번째 루프 머리 `0x41DD82` old bytes `66 8B 06 B9 6C E3 61 00`(8바이트, `mov ax,[esi]; mov ecx,0x61E36C`) → `jmp cave` + `90 90 90`.
- cave(예: `.g5code` 0x18A78DB 이후 0-run 안, 권장 `0x18A7C00`. 0-run은 미참조 증명이 아니므로 기존 port의 모든 cave/tail/scratch 범위와 비중첩·xref 0을 테스트로 증명):
  `cmp edi, dword [esp+0x10]` / `jge 0x41DDE9` / `mov ax, word [esi]` / `mov ecx, 0x61E36C` / `jmp 0x41DD8A`.
  - 개수 0이면 루프 본문 0회, bx·bp·`[esp+0x28]`은 루프 전 초기화 그대로(0).
  - 끝 검사 `cmp edi,0x32; jl` 은 유지(개수≤50이라 도달 전 cave가 종료).
- 입력 가드: 이식판 SHA(normal `0e28ef57…`, fixed_start `703deaf4…`) 아니면 거부, old bytes·cave 0 확인, 정확한 rollback(출력→입력 byte-identical), diff 범위 = 지점 8바이트 + cave뿐.
- 원본 기반 G6 후보는 만들지 않는다(원본은 재현 대조만). 원본/참고/배포 EXE 쓰기 금지, 후보는 run 사본에만.

## §3 재현 절차 (격리 사본/prefix/Xvfb, 기존 하네스 재사용)

- 기반: `tools/g5_esl2608_port_probe.py`(이식판 lane·G2 layout·`copy_overlay`)와 `tools/g5_shift_click_add_probe.py`(sparse·click-isolation 검증) 패턴.
- 자리 이동: ps5 대기실에서 `tools/x11_send_keys.py`로 방향키(RIGHT→DOWN→LEFT→UP 순 시도, 각 1회 뒤 0.5초)를 보내고
  `runtime_env._read_local_ready_state`의 `local_index`(=`[0xB63FC4]`)가 1 이상이 될 때까지. 사용한 키·횟수·전후 local·ready를 raw에 기록.
  `local_index`가 바뀌지 않으면 **하네스 BLOCKED**(제품 판정 아님)로 기록하고 화면 캡처와 함께 middle에 넘긴다.
- 게임 시작 뒤 ps3에서 local=k(≥1) 재확인. fixture는 owner=k, `SEED_TYPE`, ≥3타일 간격 sparse(op5, 합성 명시).
  `find_worker`/`live_fixture`의 owner 0 고정은 k로 매개변수화(기존 owner0 동작 byte/결과 불변 테스트).
- 각 유닛 plain click 단독 선택(정확히 그 slot 1개) 확인 뒤 Shift 단계 시작.
- 기록: 매 입력 뒤 선택 개수·slot 집합(원본 `0x899024`/20, 이식판·후보 `0x18A6000`/50), `[0xB63FC4]`, 유닛 0 owner byte, 캡처.

## §4 사전등록 PASS/FAIL

변형 3개 × lane: 원본 O(`b56986e0…`), 이식판 P(`0e28ef57…`), 후보 C(P+H-G6a, 새 SHA는 테스트 pin). 런타임은 normal lane, fixed_start는 정적 빌드·diff만.

| ID | 장면 | O@k | P@k | C@k | C@0(1P) |
|---|---|---|---|---|---|
| G6-1 재현 | A 클릭 → B~F Shift+클릭 5회 | 개수 1 유지(결함) | 1 유지(결함) | 1→2→3→4→5→6, 클릭 slot 합류 | 1→…→6 |
| G6-2 드래그 대조 | {A}에서 G·H만 덮는 Shift+드래그 | 증가 | 증가 | 증가 | — |
| G6-3 제거 | 선택된 유닛 Shift+클릭 | — | — | 개수 −1·그 slot 제거 | — |
| G6-4 상한 | 드래그로 50 선택 뒤 51번째 Shift+클릭 | — | — | 50 유지(거부)·크래시0 | — |
| G6-5 안전 | 전 단계 | 크래시0 | 크래시0 | 크래시0·개수≤50·선택 배열 범위 밖 쓰기0 | 동일 |

- G6-4는 owner=k 유닛 ≥51 필요(기존 port probe 100기 sparse fixture 패턴, owner=k).
- 정적: 패치 테스트 RED→GREEN(old bytes·SHA 거부·rollback·diff 범위·cave 비중첩·두 lane 빌드), `make lint`·`make typecheck` 후 full `make check`.
- **H-G6a PASS** = O·P에서 G6-1 결함 재현 + C에서 G6-1~G6-5 전부 충족. 1회 run씩, 이상치 있으면 같은 변형 1회 재실행.

## §5 반증·중단 조건

- (i) O 또는 P@k에서 G6-1이 정상 증가 → 정적 원인 가설 반증. 수리 후보를 제품으로 쓰지 않고 raw·capture와 함께 middle로.
- (ii) C@k에서 G6-1이 여전히 막힘 → cave 미실행 또는 다른 gate(`0x41DD40` 클릭 유닛 owner, `0x40F670` 0x2000 flag). 계수/트레이스로 원인 추적 후 수리·재실행(3회까지).
- (iii) 크래시·선택 개수>50·G6-2 퇴행 → FAIL, 원복 상태 확인 후 middle.
- 자리 이동 불가(§3) → 하네스 BLOCKED, G7 관측도 같은 전제라 함께 보류.

## §6 G7 다음 단계 (H-G6a 수용 뒤 work, 관측 전용 H-G7o)

같은 하네스로 P(이식판)에서 local=k 진행: 인게임 저장 → (a) 인게임 불러오기 / (b) 타이틀로 나가기 → 타이틀 불러오기.
각 단계에서 `[0xB63FC4]`·`0x632CA0[0..7]`·`0x632C9C`/`0x632F7C` 스냅샷 앞부분·카메라·패배 플래그·조종 가능한 owner를 기록.
사전 예측: (a) k 유지, (b) teardown 뒤 0 → 로드 뒤 0(1P 조종) 또는 패배. 관측 뒤에 middle이 수리 방식(G5SC 뒤 태그+local DWORD 복원 vs DPID표 재계산)과
함께 복원할 파생 상태를 정한다. 기존 세이브·1P 세이브·인게임 불러오기·G2/G5 sidecar 호환은 G7 합격 조건에 포함.

## §7 범위·비회귀

- G5 50 상한·G2 sidecar·1P 동작 비회귀는 §4로 확인. G2/G5 재개 아님(배포본 위 별도 패치).
- G1 uncommitted 변경·lap975 H-F handoff는 그대로 보존·보류. 같은 파일 단일 작성자.
- 게임 사본 정리(game만), prefix/manifest/output 보존, 커밋·게시·배포 금지.
