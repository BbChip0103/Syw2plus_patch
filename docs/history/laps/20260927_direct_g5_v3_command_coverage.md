# 2026-09-27 | direct session | 목표 G5 — v3 명령 범위(command coverage) paired 검증

- 역할: 운영자 요청 직접 세션(루프 lap 아님). Claude Code claude-opus-5-5. 제품 EXE 변경 0, STATUS/INBOX/APPROVALS 미수정, 커밋 없음.
- 질문: G5 v3 후보(드래그 상한 20→50)가 이동·공격 말고 흔한 그룹 명령(미니맵 우클릭 이동, 순찰, 홀드, 정지, ALT/Ctrl 드래그)에서도
  원본 20기 대비 50기 전원에 적용되고 크래시가 없는가.
- 원본: `[ESL]Syw2plus/[HQ]Syw2plus 2002.exe` `b56986e0…c9c08a8ac`(7회 실행 전후 불변, `source_unchanged=true`).
  후보: `patches/selection/g5_selection_cap50_v3.py`로 재빌드 → `e5004764…de6977`(문서 값과 일치, 매 실행 private exe 재해시).
- 환경: `runtime_env.prepare` 격리 게임 사본+Wine prefix+Xvfb 1600×1200, 솔로 로비(시드 미고정), dense fixture(worker slot1198 기준
  owner0 type2 55기) + 9점 화면↔월드 보정(lap682 방식). 런타임 디렉터리 `local/runtime/g5cov-*`, 실행 후 `game` 사본 삭제.

## 도구

`tools/g5_command_coverage_probe.py`(신규, uncommitted, sha256 `6bdfcaed…513604`). lap682 흐름을 재사용하고 다음을 추가:
- 명령마다 전체 재드래그(12,40)→(788,470) 후 선택 수 읽기(원본 `0x899024`, 후보 `0x0108C000`, 후보는 legacy count도 기록).
- 선택 슬롯 전체를 `process_vm_readv` 1회로 벌크 샘플(첫 1.5초 10ms 간격): `+0x290` 명령, `+0x384` pending word, `+0x388` xy.
  판정값 = "입력 직후 해당 값을 보인 슬롯 수(입력 직전 값이 그 값이 아니었던 것만)" (`*_changed_to`).
  - 첫 두 실행(original-1/2, candidate-1)은 슬롯당 개별 읽기 100ms 간격이라 정지/홀드 pending(수명 <0.1초)을 놓쳤다 → 벌크·고속 샘플로 수정.
- 명령 버튼(패널 글자: S 정지, M 이동, A 공격, P 순찰, H 홀드)과 같은 글자 단축키 둘 다 시험.
- 목적지는 worker 단독으로 우클릭해 pending이 `0x1000003`(이동)인 타일만 사용(candidate-1/original-3 지도에서 밭 위 우클릭이
  `0x1000008`(수확/채집류)로 바뀌는 것을 발견해 추가).
- ALT/Ctrl/Shift 수정자: xdotool keydown + 드래그/클릭, 선택 수·슬롯·유닛타입 기록.
- 미니맵: 다이아몬드 영역(좌(5,553) 상(90,510) 우(177,553) 하(90,597), 800×600 좌표) 내부 우클릭/좌클릭/M+좌클릭.

## 실행 / artifact

`/home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/20260927_g5_command_coverage/{original-1..4,candidate-1..3}/`
(probe-result.json, probe.log, 단계별 캡처 PNG). 유효 판정에 쓴 쌍: **original-4 ↔ candidate-2, candidate-3**(고속 샘플, 이동 목적지 검증).
original-1/2는 느린 샘플이지만 같은 값 패턴(보조 근거). original-3은 목적지 검증 실패로 중단(FAIL, 지도 탓, 크래시 아님).
candidate-1은 목적지가 밭이라 이동이 `0x1000008`로 바뀌어 이동 판정 무효(그 대신 type8 명령이 50/50 도달한 근거).

## 측정값 (raw)

| 명령 | 원본 raw (original-4, 20 선택) | 후보 raw (candidate-2 / candidate-3, 50 선택) | 판정 |
|---|---|---|---|
| 지면 우클릭 이동 | `+0x290`→3: 20/20, pending `0x1000003` 20/20 | 3: 50/50 · 50/50, `0x1000003` 50/50 · 50/50 | PASS |
| 미니맵 우클릭 이동 | 명령 없음(pending/xy 변화 0, 카메라 변화 없음) | 동일하게 명령 없음 | UNKNOWN |
| 정지(S 버튼/`s`) | pending `0x1000002` 20/20, 이동 중이던 18~20기 command 3→1 | `0x1000002` **20**/50 · **20**/50(버튼·단축키 4회 모두 정확히 20) | **FAIL** |
| 홀드(H 버튼/`h`) | pending `0x1000027` 20/20(command는 1 유지) | `0x1000027` **20**/50 · **20**/50(4회 모두 20) | **FAIL** |
| 순찰(P + 지면 클릭) | command 35(0x23) 20/20, pending `0x1000023` 20/20 | command 35 **20**/50, `0x1000023` **20**/50(candidate-1/2/3 6회 모두 20) | **FAIL** |
| ALT+드래그 | 20 선택, 전부 type2(일꾼 제외). 작은 드래그/클릭은 일반과 동일 | 50(c2)/47(c3, 화면 내 type2 전부) 선택, 일꾼 제외, legacy 0, 크래시 없음 | PASS |
| Ctrl+드래그 | 일반 드래그와 동일(20, 일꾼 포함, 추가 선택 아님) | 일반과 동일 50/48, 크래시 없음 | PASS |
| (참고) Shift+드래그/클릭 | 선택 추가(4+2→6, 1→2) | 추가(5→9, 8→13, 1→2), 전체 드래그 50 유지 | PASS |
| (참고) 명령 type8(밭 우클릭) | — | pending `0x1000008` 50/50(candidate-1) | 50 도달 |

모든 단계에서 게임 프로세스 생존(ps==3), fault/크래시 없음, cleanup 후 prefix 프로세스 0.

## 발견한 결함 (원인 추정)

**v3 청크 래퍼의 명령 타입 화이트리스트 `{1,3,4,7,8,9}`에 정지/홀드/순찰이 없다.** `0x004AE550` 진입 래퍼(cave `0x004E4D50`,
`g5_selection_cap50_v3.py` `_WRAPPER_ASM`)는 `word [esp+8]`이 그 집합에 없으면 원본 본문으로 바로 넘어가고, 원본 본문은 선택 배열의
처음 20개만 읽는다(`mov ebp,0x14` @`0x004AE5F4`). pending 하위 워드(이동 3, 공격 4와 같은 규칙)로 보면 정지=`2`, 순찰=`0x23`,
홀드=`0x27`이며 셋 다 집합 밖이다. 후보에서 셋 다 **정확히 20기**만 받는 것이 이 경로와 일치한다(일부 수신이면 20 경계가 아닐 것).
수정 방향(미실시): 화이트리스트에 2/0x23/0x27(및 아직 모르는 명령 타입)을 추가하거나, "알려진 비명령 opcode(0x52, 0x56, 0x19b,
0x19d-0x1a1, 0x1ae-0x1bc)가 아니면 청크"로 뒤집는다. gdb로 `word [esp+8]` 실제 값을 확인하는 것이 다음 검증이다(미실행).

## 검증 못 한 것

- 미니맵: 이 환경(격리 Wine, 솔로 로비)에서 미니맵이 계속 검은 다이아몬드로만 렌더되고, 우클릭·좌클릭·M+좌클릭 모두 원본에서도
  명령/카메라 이동이 없었다. 미니맵 자체가 비활성(렌더/입력)인지 좌표 문제인지 가리지 못함 → UNKNOWN. 원본에서 먼저 작동해야 비교 가능.
- 정지/홀드/순찰 수신 20기가 선택 배열 앞 20개인지 슬롯 단위로 대조하지 않음(수만 확인). 홀드/순찰의 이후 실제 행동(자리 고수, 왕복)은 미측정.
- ALT/Ctrl의 원래 기능: 설명서(ESL 요약·SYW2X)에는 "L-Alt 모든 유닛 상태바"(SYW2X 관전 기능)만 있다. 실험상 ALT 드래그는 일꾼을 빼고
  전투 유닛만 선택, Ctrl 드래그/클릭은 관측 가능한 차이 없음. Ctrl+숫자 부대지정·더블클릭 동일타입 선택은 이번 범위 밖.
- 공격은 이번에 재측정하지 않음(lap688/689 근거 유지). 멀티/네트워크 동기화 미실행. 각 명령 쌍은 원본 1(+보조 2), 후보 2회.

## 게이트

`ruff check tools/g5_command_coverage_probe.py` PASS. `bash checks/safety.sh check` → SAFETY_PASS. make check는 실행하지 않음(제품 코드 무변경, 신규 probe만).
