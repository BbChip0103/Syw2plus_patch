# 2026-10-07 | lap1152 | G1 middle — H-TR3 독립 검수·수용, G1 사용자 시험 재요청(lap1151판), H-OS1 사전등록

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5-5`, high / middle(진단·계획·확인) 1 lap. 게임 실행 0, 게임 코드·하네스·테스트 변경 0, 커밋 0.
- 입력: `loop/ESCALATE_SOL`(lap1151 work). 원문을 byte 일치로 `docs/history/laps/20261007_lap1152_preserved_lap1151_escalate_sol.txt`(SHA256 `9a541596db72…`, cmp 일치)에 보존한 뒤 삭제했다. 그 밖 입력은 lap1151 기록과 lap1150 사전등록 §6이다. INBOX 새 사용자 지시 없음(마지막 = lap1151 처리 메모), APPROVALS 새 반려·사용자 G1 시험 결과 없음(lap1136 요청 대기, 비차단), `loop/STOP` 없음.
- 원본 SHA: `[ESL]Syw2plus/[HQ]Syw2plus 2002.exe` `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac` 직접 재계산 MATCH. pair 두 lane `private_exe_sha256 == source_exe_sha256 ==` 재계산값.
- fixture: 재실행 없음. lap1151 raw만 재계산했다(save006 `616b7997…`, 비합성, pair 1회).
- 가설(검수 대상): H-TR3 — 현재 트리(lap1135판 뒤 기본 켬 가시 수리 H-TM1·H-SC2 추가)의 단일 `_inmm.dll`(`8a3837fb9ef9…`)이 사용자 시험 경로(save006 pair)를 통과하고, 독립 재조립 DLL과 타임스탬프 외 같다.
- 마일스톤 경계: 사용자 시험판 교체·전달이라 root 전달용 새 `loop/ESCALATE_SOL`을 만든다(§5).

## 1. 출처

- source SHA 12자리 6/6이 lap1151 TR3-0과 같다: `g1_briefing_compose.h` `fa26be35c0b2`·`g1_mirror2x.c` `e3c6a1bcd754`·`g1_mirror2x.h` `a6eda22ba8a0`·`direct_draw_trace.c` `d3e372e276a7`·`Makefile` `de73c1045595`·`tests/test_g1_briefing_compose.py` `c19dd4548436`.
- `tools`·`tests`·`checks`·`patches`·`Makefile` 아래에 `logs/gates/lap1149-work-full-check.log`보다 새 파일 0개 → lap1149 full PASS 1823 뒤 source 변경 0.
- pair 로그 `logs/gates/lap1151-tr3-pair.exit` = 0. 디스크 여유 70G, `local/runtime/lap1151_tr3_pair/*/game` 0개.

## 2. 독립 재계산 (새 스크립트, work 스크립트 재사용·import 없음)

공유 temp `20261007_lap1152_middle_review/`:

| 파일 | SHA256 |
|---|---|
| `recheck_lap1152.py` | `6025617e3df3…` |
| `recheck_lap1152.json` | `0d1a1c1cf708…` |
| `selection_delta_lap1152.py` | `a171a83d00f1…` |
| `selection_delta_lap1152.json` | `bdefb50f228b…` |
| `rebuild_lap1152.py` | `754a01b9301a…` |
| `rebuild_lap1152.json` | `a638f4adb092…` |
| `rebuild/_inmm.dll` | `c6d6066eca92…` |
| `sel_lap1151_base_top_cand_bottom_half.png` | `d1f94a37b6f6…` |
| `sel_lap1151_nearest_diffmask_half.png` | `e76fe6c9009e…` |

**판정 불일치 0, 정정 1(§3).**

| 항목 | 재계산 | work 값 | 판정 |
|---|---|---|---|
| pair-result SHA / status / scene_state_equal / execution_source.unchanged | `ade828bbbcd9…` / PASS / true / true | 동일 | 일치 |
| input_effect / minimap parity | PASS 7/7 / PASS | 동일 | 일치 |
| V2·V2s·V2q·Scale2x gate | 전부 PASS | 동일 | 일치 |
| loaded V2s 단일 흑 / Scale2x 기준 / 설명 안 됨 | 1,912 / 2,205 / 36 | 1,912 / — / 36 | 일치 |
| **PNG에서 직접 계산한 nearest-2x 차이**(5 tag) | loaded 202,901·selection 267,169·drag 164,026·minimap 169,331·production 156,341 | 기록값 5/5 같음 | 일치 |
| 캡처 크기 | baseline 800×600, candidate 1600×1200(5/5) | 창 1600×1200 scale 2 | 일치 |
| V2s 비설명(5 tag) / production raw | 36·252·198·226·200(≤2,000) / FAIL 2,821 | production 비설명 200·raw 2,821 | 일치 |
| 후보 trace mirror present / 안전 7종 present / hresult≠0 | 1,191 / 0 / 0 | 1,191 | 일치 |
| 후보 `trace_close` / `mirror_validator` / `scale2x_validator` | FAIL / BLOCKED / PASS — lap1135 pair와 같은 값(아래 키 비교에서 변화 없음) | 공개 3건 | 일치 |
| 후보 prefix `inmm_unit_ticks.jsonl` | **없음**(baseline prefix `drive_c/`에만 있음) | 동일 | 일치 |
| 두 lane `game` 디렉터리 / cleanup | 없음 / ok | 동일 | 일치 |
| 스테이징 | 정확히 4파일, SHA = 기록, `_inmm.dll` = `pair/bridge/_inmm.dll`, `.bat` 2개 = lap1135 스테이징 byte 동일 | 동일 | 일치 |

## 3. 정정 1 — "lap1135 대비 기타 비교 키는 전부 같다"는 부정확(장면 변동, 판정 영향 없음)

- lap1135 pair-result(`56f4ae7f…`)와 스칼라 잎 4,200개를 경로·시각·SHA류를 빼고 비교했다. 값이 다른 잎 **178개**, 키 집합 차이는 AI 그룹 member_ids 배열 길이뿐이다. 바뀐 잎은 sim tick·AI 그룹 상태·자원·`nearest_equal_ratio`(5 tag)이고, status·gate·equal 류 키는 하나도 바뀌지 않았다.
- 5 tag nearest 차이가 모두 늘었다(loaded 192,299→202,901 … **selection 109,995→267,169**). 독자 Scale2x 기준 차이도 selection 14,140→181,485.
- 원인 확인(캡처 직접 열람·차이 마스크): lap1151 baseline selection 캡처에는 회오리 기술 효과가 있고 **선택된 유닛이 다르다**(baseline 체력 1619/4290·다른 초상화 vs candidate 655/750). 차이 마스크도 회오리·초상화·명령 칸·유닛 위치에 몰려 있다. candidate 화면 자체(HUD·자원 막대·월드)는 정상이다. baseline lap1135↔lap1151 논리 프레임 차이도 tag마다 4,823~29,825 px로, 같은 세이브여도 lane 진행이 run마다 다르다.
- 판정: 두 lane의 시뮬레이션 위상 차이(기존 backlog "lane 위상 경합")로 클릭이 다른 유닛을 집은 것이다. 제품 미러 결함이 아니다. input_effect 선택 효과는 두 lane 모두 true이고, nearest 비율은 gate가 아니다. backlog에 "selection tag 두 lane 선택 대상 불일치(lap1151)"를 추가한다.

## 4. 독립 재조립 → 스테이징 DLL 대조: 타임스탬프 마스크 일치

- 현재 트리 소스 복사 → bridge 변환이 트리 대비 유일 차이인지 검증(manifest 원본 입력 62개 SHA = 트리, `runtime_bridge.c` SHA = manifest = bridge 사본, 그 밖 소스 62개 = bridge, Makefile `SRCS` 앞 `runtime_bridge.c`·`inmm_stub.c` `supply_probe` 2줄) → 같은 변환 적용 → mingw `make` rc 0.
- 재빌드 457,256 B(스테이징과 같은 크기). 다른 바이트 **6개**: 136·137(COFF TimeDateStamp), 216·217(OptionalHeader CheckSum), 347140·347141(export 디렉터리 TimeDateStamp). 허용 필드는 스테이징 DLL PE 헤더에서 직접 계산했다 → **타임스탬프·체크섬을 가리면 스테이징 DLL과 동일**. lap1150 재조립(`9f0404fb35e5…`)도 같은 6바이트 위치다. pair bridge DLL = 스테이징(차이 0).
- 문자열: `INMM_STUB_NO_UNIT_TICKS`·`SYW2_G1_BRIEFING_COMPOSE`·`SYW2_G1_PRIMARY_READBACK`·`SYW2_G1_BAR_COPY`·`SYW2_G1_PAUSE_SNAPSHOT` 각 1회.
- 기본 켬 확인(`g1_mirror2x.c:720-729`): 새 두 수리 env `SYW2_G1_BRIEFING_COMPOSE`(⑥)·`SYW2_G1_KEYED_COPY`(⑤)는 값이 정확히 `"0"`일 때만 꺼진다. `.bat` 2개에 이 env가 없으므로 사용자 판에서 6개 수리 모두 켜진다.
- 스크립트 경미 결함(내 쪽): 비교 대상 `pair/candidate/_inmm.dll`은 존재하지 않는 경로라 `mismatch`에 들어갔다. 판정 대상 아님.

## 5. 안내문 열람 → 판정 → 수용, 사용자 시험 재요청, root 전달

- 안내문 `G1_1600x1200_시험판_읽어주세요_20261007_lap1151.txt`(`d577283c3848…`, UTF-8 73줄) 전문을 읽었다. lap1135판 대비 diff는 제목·대체 문구(12:53판 `6cbb12ac…`와 00:21판 `94213374…` 둘 다 대체, 옛 판 결과면 판 표시 요청)·추가 수리 ⑤⑥(위치·입력 불변)·기존 ①~④ 유지·브리핑 +4~6 ms 공개(Wine 측정, 실제 Windows 미측정)·DLL SHA 줄뿐이다. ⑤ 문구 "등록된 사용자가 없을 때 뜨는 사용자 등록 창"은 lap1142 정적 확정(`0x466480`←PS9 팝업, 빈 사용자 목록이면 타이틀 진입 즉시 뜸)과 맞다. ⑥은 lap1149·1150과 맞다. 과장 표현 없음.
- **H-TR3 `PASS(partial, 기술·격리)` 수용.** 불일치 0, 정정 1(§3, 장면 변동). 이것은 G1 사용자 합격도 G1 마감도 아니다.
- APPROVALS lap1136 항목에 "lap1151판으로 대체" 메모를 달고 새 사용자 시험 요청(lap1152)을 올린다.
- root 전달용 `loop/ESCALATE_SOL`: 스테이징 4파일을 `260921_temp`의 **새 폴더**(권장 `G1_1600x1200_시험판_20261007_lap1151/`)에 복사하고 SHA 4개를 대조한다. 기존 두 폴더(00:21판·12:53판)는 덮어쓰지 않는다. 옛 폴더 정리는 root·사용자 결정이다.

## 6. 다음 work 사전등록(Sonnet) — H-OS1: PS7 접속방식·PS5 혼자하기 대기실 글자·버튼 모서리 stale 귀속 → 조건부 수리

**근거.** 새 게임마다 반드시 지나는 두 메뉴 화면이 현재 미러 HD 최저 축이다: PS7 98.166%(stale 약 8,800 논리 px/present)·PS5 98.801%(lap1108·1110, 2/2 결정적). lap1109 독자 Scale2x 비교로 위치는 글자·버튼 테두리(목록 글자·버튼 글자·확인/취소 버튼 테두리)로 확정했고(공유 temp `20261007_lap1109_middle_review/ng_a_ps7_stale_mask.png`·`ng_a_ps5_stale_mask.png`), 눈에 보이는 nearest 블록은 PS7 799·PS5 2,427 HD px로 작다. 단서: 같은 run `textout_iat_metrics` 호출 11,950 중 `reject_target` 4,699, `rect_solid_465E80` 1,869 중 `reject_target` 1,620(run 누계, 상태 미분리). 즉 기존 hook이 호출은 보지만 대상 판정에서 거부하는 경로일 가능성이 높다. 가시 효과는 작다는 점을 미리 공개한다(사용자 시험 결과가 오면 그것이 우선).

- **OS1-0 진단 확장(TDD):** `--screen-watch-state`에 5·7 추가(`g1_screen_watch.h` 파서 한 자리 분기 + 하네스 choices + `--new-game-path` 분기가 `layer_drift`/`screen_watch` 계열을 후보 lane에 전달하는지 확인·배선). 가능하면 TextOutA·`0x465E80` `reject_target`을 program state별(5·7·그 밖)로 나눈 진단 계수 추가(옵트인 또는 요약 키, 기존 키 불변). 테스트 RED→GREEN.
- **OS1-1 귀속(격리 1~2 run):** `--new-game-path` + `--layer-drift --screen-watch --screen-watch-state 7`(그다음 5), 표본 3개 = 위 mask에서 stale인 픽셀 중 (PS7) "IPX 대전" 버튼 글자 부근(≈340,170)·목록 첫 줄 글자(≈260,218)·확인 버튼 테두리(≈560~650,548~580), (PS5) 목록 글자(≈500,160)·"전장카드" 버튼 글자(≈345,128)·1P 이름(≈45,48). 정확한 픽셀은 mask에서 가장 가까운 stale 픽셀로 고른다. PASS = 표본 3개 중 2개 이상이 같은 writer EIP·호출 스택. 상태별 `reject_target` 거부 사유(대상 표면/DC)를 함께 기록한다.
- **OS1-2 조건부 수리(1회 한도):** (a) 기존 TextOutA/`0x465E80` hook의 대상 거부가 원인이면 그 대상(예: 메뉴 화면이 쓰는 별도 표면·DC)을 화면 좌표와 1:1인 경우에만 받아들이는 최소 확장, (b) 미후킹 단일 함수면 H-TM1 선례 diff 미러, (c) wined3d/GDI 내부·다수 writer면 수리하지 않고 BLOCKED 보고. 수리는 기본 켬 + `=0` 끔 env(이름은 구현자 재량, 기존 선례 형식).
- **측정식:** 켬 2 run·끔 1 run에서 PS7·PS5 정착 HD min(현재 98.166/98.801)과 캡처 독자 Scale2x 판별 nearest 블록(현재 799/2,427). PASS = 둘 다 HD min ≥99.5 그리고 nearest 블록 ≥80% 감소, partial = 개선됐으나 미달, FAIL = 무변화. 끔은 현재 값 재현.
- **비회귀:** PS9 타이틀 HD 100, `--new-game-start --new-game-act --new-game-play`(NG5 플래그) PS3 HD min ≥99.9·안전 7종 0·dropped 0. 수리가 PS3에서도 실행되는 경로(TextOutA 대상 판정 등)를 바꾸면 save006 full pair 1회 추가(이전 결과와 gate 동일).
- **중단:** 실패 가설 2회 또는 60분이면 멈추고 근거를 남긴다. 공통: 디스크 ≥20GiB(현재 70G), run 뒤 game 사본 삭제, 원본/참고 쓰기·커밋·`260921_temp` 금지. 끝나면 lap 기록 → `make lint`·`typecheck` → `make check` 1회 → ESCALATE_SOL(middle 검수).

backlog 추가: selection tag 두 lane 선택 대상 불일치(§3, lane 위상). 기존 backlog(STATUS)는 유지한다.

## 7. 검사

- 결과는 STATUS 검증 줄에 보강한다(safety·context).
- 전체 `make check` SKIP: 이번 회차는 문서·공유 temp 스크립트만 바꿨다. C·하네스·테스트 source는 lap1149 full PASS 1823 그대로다(§1).

## 다음 행동

root: `loop/ESCALATE_SOL`에 따라 lap1151 묶음 시험판 4파일을 `260921_temp` 새 폴더로 전달하고 SHA를 대조한다. 그 뒤 work(Sonnet) H-OS1(§6). 사용자 G1 시험 결과가 오면 최우선이다.
