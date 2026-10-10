# 2026-10-07 | lap1136 | G1 middle — H-TR2 독립 검수·수용, G1 사용자 시험 재요청(lap1135 묶음판), H-TI0 사전등록

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5-5`, high / middle(진단·계획·확인) 1 lap. 게임 실행 0, 게임 코드·하네스·테스트 변경 0, 커밋 0.
- 입력: `loop/ESCALATE_SOL`(lap1135 work). 원문을 byte 일치로 `docs/history/laps/20261007_lap1136_preserved_lap1135_escalate_sol.txt`(SHA256 `b34e95fa82ca…`, cmp 일치)에 보존한 뒤 삭제했다. 그 밖의 입력은 lap1135 기록과 lap1134 사전등록 §7이다. INBOX 새 사용자 지시 없음, APPROVALS 새 반려 없음(G1 사용자 시험 lap1104 대기, 비차단), `loop/STOP` 없음.
- 원본 SHA: `[ESL]Syw2plus/[HQ]Syw2plus 2002.exe` `b56986e018b4…` 직접 재계산 MATCH. pair·vs 4 lane 모두 `private_exe_sha256 == source_exe_sha256 ==` 재계산값.
- fixture: 재실행 없음. lap1135 raw만 재계산했다. save006(`616b7997…`, 비합성) pair, `victory-poke`(합성 트리거 `[0xB63238]=1`) new-game.
- 가설(검수 대상): H-TR2 — 현재 트리로 만든 단일 `_inmm.dll`(`6cbb12ac…`)이 사용자 시험 경로(save006 pair)와 수리 경로(승리 배너·결과 표)를 모두 통과하고, 독립 재조립 DLL과 타임스탬프 외 같다.
- 마일스톤 경계: 사용자 시험판 교체·전달이라 root 전달용 새 `loop/ESCALATE_SOL`을 만든다(§6).

## 1. 출처

- source SHA는 lap1135 §0과 같다: `g1_mirror2x.c` `1213c4abb660`, `g1_bar_copy.h` `ff12d6299246`, `g1_saved_scene_probe.py` `8c22de763922`, `test_g1_victory_poke.py` `5d383d080cf0`.
- `tools`·`tests`·`checks`·`patches`·`Makefile` 아래에 `logs/gates/lap1133-work-full-check.log`보다 새 파일은 0개다. lap1133 full PASS 1786 뒤 source 변경은 0이다.
- pair bridge 소스 대 현재 트리: 다른 것은 `Makefile`(SRCS 앞 `runtime_bridge.c`)과 `inmm_stub.c`(`supply_probe_poll` 2줄)뿐이고, 브리지 전용 파일은 `runtime_bridge.c`·`supply_bridge_build.json`이다. 하네스 supply-bridge 변환과 같다(lap1104 정정 2와 같은 구조).
- `local/runtime/lap1135_tr2_*`에 `game` 사본 0개. 디스크 여유 123G.

## 2. 독립 재계산 (새 스크립트, work 스크립트 재사용·import 없음)

공유 temp `20261007_lap1136_middle_review/`:

| 파일 | SHA256 |
|---|---|
| `recheck_lap1136.py` | `9421528804096ca1…` |
| `recheck_lap1136.json` | `aae909044396992…` |
| `rebuild_lap1136.py` | `307f23c6319e8e52…` |
| `rebuild_lap1136.json` | `1fd45e5f5141f62e…` |
| `rebuild/_inmm.dll` | `18fb03e7df950920…` |

**판정 불일치 0, 정정 0.**

| 항목 | 재계산 | work 값 | 판정 |
|---|---|---|---|
| pair-result SHA / status / scene_state_equal | `56f4ae7f…` / PASS / true | 동일 | 일치 |
| input_effect / minimap parity | 7/7 PASS / PASS | 동일 | 일치 |
| V2·V2s·V2q·Scale2x gate | 전부 PASS | 동일 | 일치 |
| loaded V2s 블록 / Scale2x 기준 / 설명 안 됨 | 1,876 / 2,179 / 96 | 동일 | 일치 |
| **PNG에서 직접 계산한 nearest-2x 차이 픽셀**(5 tag) | loaded 192,299·selection 109,995·drag 151,613·minimap 158,814·production 151,722 | 기록값과 5/5 같음 | 일치 |
| 캡처 크기 | baseline 800×600, candidate 1600×1200(5/5) | 창 1600×1200 scale 2 | 일치 |
| V2s unexplained(5 tag) | 96·27·146·167·186(≤2,000) | — | 기록 |
| 후보 trace mirror present / 안전 7종 present | 1,192 / 0 | Scale2x 1,192/1,192 | 일치 |
| 후보 prefix `inmm_unit_ticks.jsonl` | **없음**(baseline prefix에는 `drive_c/inmm_unit_ticks.jsonl` 있음) | 동일 | 일치 |
| 두 lane `game` 디렉터리 / cleanup | 없음 / ok | 동일 | 일치 |
| vs result SHA | `5d23537f…` | 동일 | 일치 |
| vs 두 lane poke | before 0·readback 1·consumed(ps 3), states 3→25→29 | 동일 | 일치 |
| vs 후보 criteria | 12/12 true | 12/12 | 일치 |
| vs 후보 연속 상태 구간(마지막 PS3부터, seq 순) | 3(264)→25(1,084)→29(1,153)→9(298) | 창 기준 PS25 1,060·PS29 419 present | 정의 차(창 vs 구간), 판정 영향 없음 |
| PS25 HD min / readback 증가·반환 | 100 / calls 1·converted 1·`0x4C7EEB`(5013227) | 동일 | 일치 |
| PS29 본문(마지막 전환 present 제외) HD min / bar 증가 | 100 / calls 2,714 = mirrored 2,714 | 동일 | 일치 |
| PS29 마지막 present stale | 479,004(전환 1개, lap1133·1134 공개와 같음) | — | 기존 공개 |
| PS9(확인 뒤) HD min · 안전 · hresult≠0 · dropped | 100 · 0 · 0 · 0/0 | 동일 | 일치 |

공개(기존 종류): pair 후보 `mirror_validator` BLOCKED·`trace_close` FAIL(run_id 불일치)은 `--candidate-no-present-trace` 모드 진단이다. lap1101/1103과 문자 그대로 같은 종류이고 pair gate 밖이다. production tag `v2s_raw_status` FAIL은 W-1 결정(2026-10-06) 뒤 공개 진단이다(gate = unexplained 186 ≤2,000 PASS).

## 3. 시도 1 baseline 경합 판정 — 확정: 하네스 write→readback 경합(제품 무관)

- 시도 1 baseline lane: poke before 0, **readback 0**, 하네스가 FAIL로 즉시 반환했다(`victory poke readback 0 != 1`).
- 그런데 같은 lane trace의 상태 열은 `…2(14)→3(4)→24(1)→25(16)`이다. poke 직후 원본 게임이 승리 준비 PS24 → 배너 PS25로 넘어갔다. 즉 **쓰기는 성공했고**, 게임 루프가 하네스의 readback 전에 플래그를 소비했다.
- 하네스가 FAIL 반환 뒤 결과 화면을 걷지 않았으므로 PS25에 머문 채 끝났다(16 레코드). 후보 lane은 같은 시도에서 readback 1·PASS였다.
- 결론: work 가설(경합)을 **trace 근거로 확정**한다. 시도 2(같은 명령)를 근거로 쓰는 것은 정당하다.
- 하네스 경미 결함 1건으로 기록한다(`_victory_poke_window`, `tools/g1_saved_scene_probe.py:2684-2691`): readback 0을 곧바로 FAIL로 본다. 수리 방향(backlog, 비차단): readback 0이면 짧은 시간 안에 PS24/25 진입을 관측했는지로 "소비됨"을 판정한다. 기준 완화가 아니라 관측 순서 수리다.

## 4. 독립 재조립 → 스테이징 DLL 대조: 타임스탬프 마스크 일치

- 현재 트리 복사 → 위 §1 변환을 하나씩 검증한 뒤 적용(manifest 원본 입력 61개 SHA = 트리, `runtime_bridge.c` SHA = manifest = bridge 사본, 그 밖 소스 동일) → mingw `make` rc 0.
- 재빌드 448,133 B(스테이징과 같은 크기). 다른 바이트 **7개**: `0x88·0x89`(COFF TimeDateStamp), `0xd8·0xd9·0xda`(OptionalHeader CheckSum), `0x53404·0x53405`(export 디렉터리 TimeDateStamp). 허용 필드 위치는 work 기록이 아니라 스테이징 DLL의 PE 구조에서 직접 계산했다. 7개 모두 그 안에 있다 → **타임스탬프를 마스크하면 스테이징 DLL과 동일**.
- vs bridge DLL(`c3b142c6…`)도 같은 방식으로 6바이트, 모두 같은 필드 안이다. lap1135 TR2-3의 `.edata` 판정은 맞다.
- 문자열: `INMM_STUB_NO_UNIT_TICKS`·`SYW2_G1_PRIMARY_READBACK`·`SYW2_G1_BAR_COPY`·`SYW2_G1_PAUSE_SNAPSHOT` 각 1회.
- 기본 켬 확인(`g1_mirror2x.c:677-682`): 세 env는 값이 정확히 `"0"`일 때만 꺼진다. `.bat`(lap1103판 byte 동일)에 이 env가 없으므로 사용자 판에서 네 수리는 켜진다.

## 5. 안내문·캡처 열람

- 스테이징은 정확히 4파일, SHA가 lap1135 기록과 같다(`_inmm.dll` `6cbb12ac…`, `.bat` `2da323e8…`·`29a35d2e…`(CRLF), 안내문 `f6593f5c…` UTF-8).
- `guide_diff.txt`(`4f958cb8…`)는 lap1134 §7 ①~⑤ 변경만 담고 있다. 나머지 줄은 lap1103판 그대로다. 본문 3줄의 "켜는 스위치 3개 + .bat이 1개 더함"과 파일 목록 "환경변수 4개"는 서로 맞는다.
- 안내문은 옛 판 대체·추가 수리 4개(위치·입력 불변)·합성 조건 측정·사용자 확인 전임을 밝힌다. 과장 표현은 없다.
- 캡처 `vs/candidate/vs_ps25.png`(1600×1200)를 직접 열람했다. 상단 자원 막대·하단 HUD(미니맵 틀·F1~F11·명령 패널)·중앙 "승리했습니다!" 배너가 정상이다. H-RS2 결함 모양(4분면 확대·HUD 소실)은 없다.

## 6. 판정 → 수용, 사용자 시험 재요청, root 전달

- **H-TR2 `PASS(partial, 기술·격리)` 수용.** 불일치 0, 정정 0. 시도 1 경합은 trace로 확정했고 하네스 경미 결함 1로 기록한다. 이것은 G1 사용자 합격도 G1 마감도 아니다.
- APPROVALS lap1104 항목에 "lap1135 판으로 대체" 메모를 달고, 새 사용자 시험 요청(lap1136)을 올린다.
- root 전달용 `loop/ESCALATE_SOL`: 스테이징 4파일을 `260921_temp`의 **새 폴더**(권장 `G1_1600x1200_시험판_20261007_lap1135/`)에 복사하고 SHA를 대조한다. 기존 `G1_1600x1200_시험판_20261007/`(lap1103판)은 덮어쓰지 않는다. 옛 폴더를 둘지 치울지는 root·사용자가 정한다(안내문이 옛 판 대체를 밝힘).

## 7. 다음 work 사전등록(Sonnet) — H-TI0: 타이틀 인트로(PS40/60/180) 화면 관측·G1 범위 판정 근거

**근거(이번 재계산 부산물).** lap1135 두 후보 trace에서 PS9 앞 상태는 40→60→180이다. 이 구간에는 `mirror2x_present`가 0이고, `set_display_mode`가 640×480×16 ↔ 800×600×8로 여러 번 바뀐다(PS40 5회·PS60 4회·PS180 2회). 즉 후보에서 인트로는 미러 경로 밖이다. 사용자가 그동안 보는 창 크기와 그림은 측정된 적이 없다.

**목표.** 측정·관측만 한다(수리 없음). 원본 lane과 후보 lane에서 인트로 구간의 창 크기·표시 내용을 관측해, G1 범위에서 (A) 원본 구성 그대로라 수리 불필요인지, (B) 후보에서 깨짐·잘림·창 크기 튐이 있는지를 가른다.

- TI0-0 출처: source SHA가 §1과 같은지 확인한다. 하네스 옵트인 추가는 허용한다(예: 인트로 구간 주기 캡처, 테스트 RED→GREEN). 제품 C 변경은 금지다.
- TI0-1 격리 1쌍(원본·후보, 기존 `--new-game-path` 경로처럼 타이틀까지 자연 진행): PS40/60/180 각 구간에서 적어도 2장씩 캡처하고, X 창 크기(`xwininfo` 등)·`set_display_mode` 열·상태별 지속 시간을 기록한다.
- 측정식: 상태별 {지속 초, 모드 열, 창 크기, 캡처 SHA}. 후보 캡처가 원본 캡처의 nearest-2x 또는 같은 크기 표시와 같은 구도인지 레이아웃 비교(차이 픽셀 비율은 기록만).
- PASS(관측): 세 상태 모두 관측·캡처 성공, 안전·크래시 0. 판정 문구는 (A)/(B)/UNKNOWN 중 하나로 쓰고 근거 캡처를 남긴다.
- FAIL/BLOCKED: 인트로가 하네스 시작 전에 지나가 관측이 안 되면, 그 사실과 타이밍을 기록하고 BLOCKED로 보고한다. 실패 가설 2회 또는 60분이면 멈춘다.
- 공통: 디스크 ≥20GiB(현재 123G), run 뒤 game 사본 삭제, 원본/참고 쓰기·커밋·`260921_temp` 금지. **사용자 G1 시험 결과가 오면 그것이 최우선이다.**

backlog 추가: 하네스 victory-poke readback 경합(§3). 기존 backlog(STATUS)는 유지한다.

## 8. 검사

- 결과는 STATUS 검증 줄에 보강한다(safety·context).
- 전체 `make check` SKIP: 이번 회차는 문서·공유 temp 스크립트만 바꿨다. C·하네스·테스트 source SHA는 lap1133 full PASS 1786 그대로다(§1).
- STATUS 압축: 원문 126줄 `db587955…`를 `docs/history/20261007_status_lap1136_precompaction.md`에 byte-exact 보존한 뒤 lap1125~1134 줄을 포인터로 바꿨다.

## 다음 행동

root: `loop/ESCALATE_SOL`에 따라 lap1135 묶음 시험판 4파일을 `260921_temp` 새 폴더로 전달하고 SHA를 대조한다. 그 뒤 work(Sonnet) H-TI0(§7). 사용자 G1 시험 결과가 오면 최우선이다.
