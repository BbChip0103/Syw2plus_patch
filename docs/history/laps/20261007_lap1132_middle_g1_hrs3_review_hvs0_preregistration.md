# 2026-10-07 | lap1132 | G1 middle — H-RS3 독립 검수·수용, H-VS0(승리 화면 HD) 사전등록

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5-5`, high / middle(중간 계획·컨펌) 1 lap. 게임 코드 hands-on 수정 0.
- 입력: `loop/ESCALATE_SOL`(lap1131 work). 원문은 byte 일치로 `docs/history/laps/20261007_lap1132_preserved_lap1131_escalate_sol.txt`(SHA256 `154ffabf5fba…`)에 보존한 뒤 삭제했다. 그 밖의 입력은 STATUS 다음 한 가지와 lap1130 사전등록 §5다. INBOX 새 사용자 지시 없음. APPROVALS 새 반려 없음(G1 사용자 시험 lap1104 대기, 비차단). `loop/STOP` 없음.
- 원본 SHA: `[ESL]Syw2plus/[HQ]Syw2plus 2002.exe` `b56986e018b4…` 직접 재계산 MATCH(읽기 전용 objdump만).
- fixture: 재실행 없음. lap1131 raw만 재계산했다(`g7defeat` = lap982 orig `save001.dat` `57872666…`, new-game 경로).
- 가설(검수 대상): H-RS3 — 원본 `0x468BB0` 호출 뒤 같은 사각형을 기존 block copy로 HD 미러하면 PS29 막대 stale +72/present가 0이 된다.

## 1. 출처·바이트 확인

- source SHA 6개 = lap1131 기록과 일치:
  - `g1_bar_copy.h` `ff12d6299246`
  - `g1_mirror2x.c` `1213c4abb660`
  - `g1_mirror2x.h` `d3af97ed6adf`
  - `direct_draw_trace.c` `5ee7c6e90021`
  - `Makefile` `f6b0a382c75a`
  - `tests/test_g1_bar_copy.py` `c26bd8d51192`
- run 사본(a·b·off·ng의 `bridge/`) C/헤더 4개 SHA = 현재 source(실행 판본 = 검사 판본).
- 마지막 source mtime 09:20:12 < `logs/gates/lap1131-work-full-check.log` 09:45:19. full PASS 1778 뒤 source 변경은 0이다.
- `local/runtime/lap1131_hrs3_*`에 `game` 사본 0, 디스크 여유 131G.

## 2. 정적 대조(원본 objdump, 이번 회차)

- 호출 지점 `0x4B5493` 바이트 `E8 18 37 FB FF` → 대상 `0x468BB0`. 원본 안 호출 앞에 `n = [edi+0x106261C]`가 0이면 건너뛴다(`jbe 0x4B5498`).
- push 순서(마지막 push = arg0) = 사전등록 디코드와 일치:
  - arg0 dst `[0xE5D42C]`, arg1 dst_pitch `[0xE5BF28]`
  - arg2 src `[ecx*4+0x105CA70]+[0x105D1A4]`, arg3 src_pitch `[0x105C5B4]`
  - arg4 sx0 0, arg5 sy0 0, arg6 sx1 n−1, arg7 sy1 0x11
  - arg8 dx `[esi]`, arg9 dy `[esi+4]`
  - ecx = `0xE5BF18`
- `0x468BB0` 본문 전체 디코드:
  - 폭 = arg6−arg4+1, 높이 = arg7−arg5+1이다. 높이 ≤0이면 바로 return한다.
  - 시작 주소: dst = arg0 + arg9·arg1 + arg8, src = arg2 + arg5·arg3 + arg4.
  - 행마다 `rep movsd`+`rep movsb`로 복사하고, 각 pitch만큼 진행한다.
  - 끝은 `ret 0x28`(스택 10인자)이다.
- work wrapper `mirror_bar_copy_site` 검토:
  - thiscall·스택 10인자로 같은 정리 규약이다.
  - 원본을 먼저 호출하고, 그 뒤 renderer·dst·dst_pitch 일치, 포함 사각형, 800×600 안 목적지, `src_pitch ≥ sx0+폭`, source 읽기 가능을 확인하고 나서 packed 버퍼를 `transfer_block_copy_to_screen`에 넘긴다.
  - **규약·조건 결함 0.**
- 코드 검토 메모(비차단, 수리 불요):
  - `mirrored` 계수는 `transfer_block_copy_to_screen`(void)에 넘긴 횟수다. 실제 쓰기 횟수가 아니다(그 함수의 조기 return — panel/cache 대상·버퍼 미준비 — 은 세지 않는다). 이번 run은 stale 0이라 판정 영향이 없다. 다음에 계수를 손볼 때 "넘김"과 "쓰기"를 구분하면 된다.
  - 원본 함수는 폭 ≤0을 거르지 않지만(높이만 검사), wrapper는 역전·0 폭을 거부한다. 이 차이는 미러 쪽만 보수적이라 안전하다.

## 3. 독립 재계산(새 스크립트, work 스크립트 미사용)

공유 temp `20261007_lap1132_middle_review/recheck_lap1132.py`(`ea77be86b157`) → `recheck_lap1132.json`(`e0f11fbea3f3`).

| 항목 | a | b | off | work 값 | 판정 |
|---|---|---|---|---|---|
| `0x468BB0` calls/mirrored/rejects | 2,646/2,646/0 | 2,682/2,682/0 | 2,692/0/0 | 동일 | 일치 |
| 미러 픽셀 합 | 4,439,232 | 4,511,808 | 0 | 동일 | 일치 |
| calls 발생 상태 | PS29만 | PS29만 | PS29만 | — | 확인 |
| 호출당 픽셀(present 단위 평균) | 18×k, k=1..112 | 동일 | — | — | 확인* |
| PS29 present / 본문(마지막 전환 제외) | 1,121/1,120 | 1,136/1,135 | 1,137/1,136 | 1,120/1,135/1,136 | 일치 |
| PS29 본문 HD min / stale max | 100/0 | 100/0 | 98.3596/7,874 | 동일 | 일치 |
| PS29 본문 stale 증가 이벤트 | 0 | 0 | 333 | 동일 | 일치 |
| PS29 첫 / 마지막 stale | 0/478,002 | 0/478,002 | 72/478,002 | 동일 | 일치 |
| PS27·PS9·PS35·PS3 HD min | 100 | 100 | 100 | PS27·PS9 100 | 일치 |
| PS29/PS9/PS27 p95 | 13/12/6 | 13/12/6 | 12/12/6 | 동일 | 일치 |
| 안전 8종(fallback·hresult·outside·palette·clip replay·viewport mutation/restore·identity invalid) present 수 | 0 | 0 | 0 | 0 | 일치 |
| dropped(event·present) | 0/0 | 0/0 | 0/0 | 0 | 일치 |
| readback calls/converted(H-RS2 유지) | 1/1 | 1/1 | 1/1 | 동일 | 일치 |

\* 막대 4개는 present마다 한 칸씩 자라며, 매 호출이 현재 막대 전체(폭 k × 18행)를 다시 복사한다. 그래서 off의 stale +72/present는 새로 자란 열 4×18이다.

- 비회귀 new-game(`ng`):
  - present 수: PS3 1,747(min 100%), PS23 4,284(min 99.9356%), PS5 98.7194, PS7 98.166, PS9 100
  - bar calls 0, readback calls 0
  - 안전·dropped 0
  - 모두 work 값과 일치한다.
- **캡처 직접 열람:** `a/candidate/result_tab_soldiers.png`(1600×1200)와 `a/baseline/result_tab_soldiers.png`(800×600)를 열었다. 빨강·보라 막대의 위치·길이, 라벨 "1", 탭·확인 버튼, "패배했습니다." 문구가 같은 구도다.
- 2× 표본과 baseline의 채널 차 >8 픽셀 수는 켬·끔 동일(ps29 10,017·병사 10,084·건물 10,091·자원 10,146)이다. 즉 가장자리 Scale2x와 원본의 차이일 뿐이다.
- **새 관찰(정정·공개):** 켬(a)과 끔(off) 후보 HD 캡처 차이는 ps29 2 px, 병사·건물 탭 1 px(논리 (310,227)), 자원 탭 0 px다. 막대는 행마다 한 색인 가로 띠라서 Scale2x 내부 결과가 nearest와 같다. 따라서 **H-RS3의 가시 효과는 거의 0이고, 효과는 HD coverage 계측의 정확성(PS29 98.36→100%)에 있다.** lap1126 "가시 차이 약 274 px"는 이 캡처 쌍에서 재현되지 않는다(비교 대상 정의 차이로 보이며, 판정 영향 없음). 실제 가시 결함 수리는 H-RS2(PS27 HUD 소실)다.

## 4. 판정

- **불일치 0.** RS3-a·b·c·d 모두 PASS이고, off에서 결함이 재현됐다.
- **H-RS3 `PASS(partial, 기술·격리)` 수용.** 결과 화면(패배 fixture)의 PS27·PS29는 HD coverage 결함이 아니다.
- 공개 한계 유지:
  - PS29→PS9 전환 마지막 present stale 478,002 1개(켬·끔 동일, writer 미귀속)
  - 막대 정체값 7,874 vs 면적 7,980 차이 106
  - 승리 화면 UNKNOWN
  - `0x41C7E5`(PS22) 역읽기와 flip 분기는 미커버
- **시험판 재스테이징: 보류하되 시점을 정한다.** 사용자 시험(lap1104 판본) 결과가 아직 없고, H-RS3는 가시 효과가 거의 0이다. H-RS2는 패배 화면 약 8초 동안만 영향을 준다. 그래서 다음 H-VS0 검수(lap1134 예정) 뒤 middle이 RS2+RS3(+VS0 결과, +보류 중 H-P35)를 한 판본으로 묶어 스테이징한다. 사용자 결과가 먼저 오면 그것을 최우선으로 처리한다.

## 5. 다음 work 사전등록(Sonnet) — H-VS0: 승리 화면 HD(PS24→결과 표)

**정적 근거(원본 objdump, 이번 회차; 발췌는 공유 temp에 남기지 않고 아래 주소로 재현한다).**

- 승패 판정은 `0x41CA05`의 `call 0x4C4040`이 정한다.
  - 반환 1이면 `[0x892FE8]=1`, `[0x4ED818]=0x18`(PS24, 승리)로 간다(`0x41CA47`).
  - 반환 0xFFFF이면 `[0x4ED818]=0x1A`(PS26, 패배)로 간다(`0x41CA62`).
- `0x4C4040`:
  - word `[0xB93988]==1`이면 별도 경로로 간다(멀티로 추정, 미확인).
  - 그렇지 않을 때 word `[0x8929D2]==1`이면 **즉시 1(승리)**, word `[0x8929D4]==1`이면 즉시 0xFFFF(패배)를 반환한다.
  - 둘 다 아니면 `0x4C3DC0(ecx=0xB3CB20)` 정상 판정으로 간다.
- `[0x8929D2]=1`을 쓰는 곳은 원본 `.text` 직접 주소 참조 기준으로 `0x48F4D7` 하나다(색인·memset 쓰기는 이 검색 밖). 이것은 명령 실행기 `0x48F250`(`arg−0x1AE`로 0..14 switch, 표 `0x48F640`)의 **case 9 = 명령 0x1B7(439)** 이다. case 10 = 0x1B8 → `[0x8929D4]`(패배)다.
  - `0x48F250`은 명령 큐 처리기(`0x4AE913`, 큐 `0x8931E8`, 실행 tick 일치 시)에서만 호출된다.
- 명령 0x1B7을 넣는 곳은 즉치값 `push 0x1B7` 검색 기준으로 `0x48EDC3` 하나다(`0x4AC189`의 같은 값은 `0x4AA840` 일련 id 등록 호출 인자라 제외(문자열 id로 추정)). 위치는 `0x48EC30`(ecx=`0xB631E8`, `0x41C853`에서 매 tick 호출) 안이다.
  - dword `[0xB631E8+0x50]` = **`[0xB63238]`이 1이면 0으로 되돌린 뒤** `0x4AE550`으로 명령 0x1B7(플레이어 `[0xB63FC4]`)을 큐에 넣는다.
  - 같은 패턴의 이웃 플래그가 `+0x38..+0x60`에 있고 명령 0x1B4..0x1B9에 대응한다. 치트 플래그 묶음으로 추정한다.
- `[0xB63238]`의 원본 쓰기 지점은 직접 주소 참조 0건이다(색인 쓰기로 추정). 즉 **채팅 치트 등 네이티브 입력 경로는 UNKNOWN**이다.
- 승리 쪽 배너 준비는 `0x424DE0` → `0x4C7CA0` → `0x4C7D00(1)`이다(lap1128). 같은 함수 안의 PS26 역읽기 호출 지점 `0x4C7EE6`을 지나므로 **H-RS2 수리가 그대로 적용될 것으로 정적으로 예상**한다. 결과 표 막대는 같은 `0x4B5493` 호출 지점을 쓸 가능성이 높다(런타임 UNKNOWN).

**가설 H-VS0.** 승리 경로에서도 PS24 이후 배너 화면과 결과 표가 H-RS2+H-RS3로 HD 100%(막대 포함)를 유지한다. 수리를 끄면 패배 경로와 같은 결함(HUD 소실·막대 stale)이 재현된다.

**VS0-0 fixture(구현 우선, 정적 조사 ≤15분).**

- (선택) `[0xB63238]=1`을 쓰는 네이티브 입력(채팅 치트 문자열 표 등)을 15분 안에 찾으면 그 입력을 하네스로 실제로 입력해 쓴다.
- 못 찾으면 **선언된 합성 트리거**를 쓴다. new-game 경로(`--new-game-start`)로 PS3에 들어간 뒤, 기존 하네스 poke 기능(g6 `slot0_owner_poke`와 같은 방식, readback 확인 필수)으로 dword `[0xB63238]=1`을 1회 쓴다.
  - 그 뒤는 게임 자체 경로가 처리한다: 명령 큐 → `0x48F250` case 9 → `[0x8929D2]` → `0x4C4040` → PS24.
  - baseline·candidate 두 lane에 같은 poke를 한다.
  - fixture 이름은 `victory-poke`로 기록하고 "합성 트리거, 승리 조건 미충족 상태에서의 강제 승리"를 공개한다.
- 하네스 `--result-screen`의 상태 대기(27→29)를 승리 상태(PS24→PS25 예상→결과 표)로 일반화한다. 실제 상태 번호는 trace로 확정해 기록한다. 테스트 RED→GREEN.

**측정(격리).**

- 켬 2 run과 끔 1 run(`SYW2_G1_PRIMARY_READBACK=0`+`SYW2_G1_BAR_COPY=0`, 결함 재현 대조)을 돌린다.
- 결과 표 탭 클릭(병사·건물·자원)과 확인은 패배 경로와 같게 한다.

**PASS(켬 2/2).**

- VS0-a: poke readback 일치. 실행 뒤 `[0xB63238]`이 0으로 되돌아간 것(게임이 소비)과 PS24 도달을 관측한다.
- VS0-b: 승리 배너 상태의 HD min 100% 근처(≥98.6)다. readback calls ≥1, converted = calls − 공개 rejects, 반환 주소 `0x4C7EEB`.
- VS0-c: 결과 표 상태의 HD min(마지막 전환 present 제외) ≥98.6%, bar calls > 0 = mirrored, 본문 stale 증가 0, 탭 전환 뒤도 같다.
- VS0-d: 안전 8종·fallback·hresult·dropped 0, scale2x PASS, 경과 p95 증가 ≤2ms다. 승리 배너·결과 표 캡처를 baseline과 나란히 열람한다(HUD·문구·막대 위치·길이).
- 끔 run은 결함을 재현해야 한다(배너 상태 HD 저하 또는 막대 stale). 재현이 안 되면 "승리 경로는 결함 없음 또는 다른 경로"로 공개하고 middle에 넘긴다.

**FAIL/BLOCKED.**

- poke 뒤 30초 안에 PS24가 안 오면 `[0xB93988]`·`[0x8929D2]`·큐 처리를 확인한다.
- 승리 경로에서 readback·bar 호출 지점이 다르면 위치·writer를 공개하고 수리 없이 middle로 넘긴다.
- 실패 가설 2회 또는 60분이면 BLOCKED.

**공개만(판정 아님).**

- 승리 경로의 마지막 전환 present stale(패배 경로 478,002와 비교)
- PS24/PS25 경과 p95

**공통.**

- C·하네스 변경 뒤 lint·typecheck → 기록 freeze → `make check` 1회.
- 디스크 ≥20GiB(현재 131G), game 사본 삭제.
- 원본/참고 쓰기·커밋·시험판 재스테이징 금지(재스테이징은 다음 middle 몫).
- 사용자 G1 시험 결과가 오면 최우선이다.

## 6. 검사

- focused 테스트(`tests/test_g1_bar_copy.py`·`test_g1_primary_readback.py`·`test_g1_frame_copy.py`) **12 passed/0.15s**(로그 `logs/gates/lap1132-middle-focused.log`).
- `checks/safety.sh check`·context 검사는 STATUS 검증 줄에 보강한다.
- 전체 `make check` SKIP: 이번 회차는 문서만 바꿨고, C·하네스·테스트 source SHA는 lap1131 full PASS 1778 그대로다.

## 다음 행동

work(Sonnet) H-VS0 fixture·하네스·격리 실행(§5) → middle(Opus) 검수 뒤 RS2+RS3(+VS0) 묶음 시험판 스테이징.
