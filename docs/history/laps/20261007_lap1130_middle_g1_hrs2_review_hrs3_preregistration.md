# 2026-10-07 | lap1130 | G1 middle — H-RS2 독립 검수·수용, H-RS3(PS29 `0x468BB0` 미러) 사전등록

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5-5`, high / middle(중간 계획·컨펌) 1 lap. 게임 코드 hands-on 수정 0.
- 입력: `loop/ESCALATE_SOL`(lap1129 work, 원문 byte 일치 보존 `docs/history/laps/20261007_lap1130_preserved_lap1129_escalate_sol.txt` SHA256 `73815e37917588f6…`, 보존 뒤 삭제), STATUS 다음 한 가지, lap1128 사전등록 §4. INBOX 새 사용자 지시 없음, APPROVALS 새 반려 없음(G1 사용자 시험 lap1104 대기, 비차단). `loop/STOP` 없음.
- 원본 SHA: `[ESL]Syw2plus/[HQ]Syw2plus 2002.exe` `b56986e018b4…` MATCH(읽기 전용 objdump만).
- fixture: 재실행 없음. lap1129 raw(`g7defeat` = lap982 orig `save001.dat` `57872666…`, new-game 경로)만 재계산.
- 가설(검수 대상): H-RS2 — PS26 primary 역읽기를 마지막 present 논리 프레임으로 대체하면 PS27 HUD가 복원되고 첫 PS27 stale 92,383이 0이 된다.

## 1. 출처·바이트 확인

- source SHA 6개 = lap1129 기록과 일치: `g1_primary_readback.h` `b33a5ffb4942`·`g1_mirror2x.c` `e628b15c7767`·`g1_mirror2x.h` `b0112c54aaec`·`direct_draw_trace.c` `20058edeb748`·`Makefile` `13ec7c1e0ccd`·`tests/test_g1_primary_readback.py` `0ac4b560ce13`.
- run 사본(a·b·off·ng의 `bridge/`) 4개 C/헤더 SHA = 현재 source(실행 판본 = 검사 판본).
- 마지막 source mtime 08:41:32 < `logs/gates/lap1129-work-full-check.log` 09:12:15(full PASS 1775 뒤 source 변경 0).
- run 종료 코드 a·b·off = 2: harness 전체 판정이 PS29 98.36%(기존 FAIL, H-RS3 대상)로 기준 미달이라 lap1125~1127과 같은 코드. H-RS2 판정 항목과 무관.
- `local/runtime/lap1129_hrs2_*`에 `game` 사본 0, 디스크 여유 136G.

## 2. 정적 대조(원본 objdump, lap1128 발췌 재사용)

- 호출 지점 `0x4C7EE6`: `push 0x10; push 0; push [0xE5D434]; push 0; push 0; push 1; mov ecx,0xE5BF18; call 0x469300` → 인자 (selector 1, x 0, y 0, source primary, rect NULL, flags 0x10 = WAIT). 바이트 `E8 15 14 FA FF` → 대상 `0x4C7EEB + 0xFFFA1415 = 0x469300` 일치.
- `0x469300`: thiscall·`ret 0x18`(스택 6인자), selector 1 → `[ecx+0x1520]`(후면 버퍼)로 BltFast. 반환값은 호출자(`add esp,0x400; ret`)가 쓰지 않는다.
- work wrapper `mirror_primary_readback_site`: thiscall·스택 6인자(같은 정리 규약), selector 1·source == `[0xE5D434]`만 가로채고 나머지는 원본 호출, colorkey flag(bit0)면 거부. **규약·조건 결함 0.**
- 같은 함수의 `0x4C8034` 호출(source = `[0xE5D438]`)은 훅 지점이 아니어서 영향 0.
- **서피스 훅 가정 오류 정정 확인:** lap1128 사전등록은 `hook_blt_fast`/`hook_blt`에서 잡는다고 했다. 실제 PS27 소스 `0x01E71780`은 caps 2076(BACKBUFFER|COMPLEX|FLIP) 플립 체인 버퍼라 vtable이 복제되지 않았다. attempt1 a·b·off 3 run 모두 `primary_readback_calls` 0·PS27 80.7535%로 재계산 확인 → 1차 실패 가설은 사실이고, 호출 지점 훅 교체가 맞다. 이 오류는 middle(lap1128)의 층위 가정 오류로 기록한다(정적 호출 지점·인자 해석은 맞았다).

## 3. 독립 재계산(새 스크립트, work 스크립트 미사용)

공유 temp `20261007_lap1130_middle_review/recheck_lap1130.py`(`3224e5a27ea6`) → `recheck_lap1130.json`(`256f0d5d418b`).

| 항목 | a | b | off | work 값 | 판정 |
|---|---|---|---|---|---|
| readback calls/converted/rejects | 1/1/0 | 1/1/0 | 1/0/0 | 동일 | 일치 |
| 반환 주소 | 5013227 = `0x4C7EEB` | 동일 | 동일 | 동일 | 일치 |
| dest hash = source hash = 직전 present(PS3) 소스 해시 | `0xA0DFD3A9` 3자 일치 | 동일 | 복사 0 | 동일 | 일치 |
| readback 직전 present 상태 | 3(사이 다른 상태 0) | 3 | 3 | — | 확인 |
| PS27 presents / 첫 stale / HD min | 1,095/0/100% | 1,116/0/100% | 1,148/92,383/80.7535% | 동일 | 일치 |
| PS27 p95 | 6ms | 6ms | 6ms | 동일 | 일치 |
| PS9 HD min | 100 | 100 | 100 | 동일 | 일치 |
| PS29 HD min(마지막 전환 present 제외) / 마지막 stale | 98.3596 / 478,002 | 동일 | 동일 | 98.36 / 478,002 | 일치(불변) |
| 안전(fallback·hresult≠0·V1 outside·palette·clip replay·viewport restore) present 수 | 0 | 0 | 0 | 0 | 일치 |
| dropped(event·present) | 0/0 | 0/0 | 0/0 | 0 | 일치 |
| RB-b ≤8 일치(배너 상자 제외) | 99.0961% | 99.0961% | 81.9717% | 99.0968/81.9865% | 정의 차이* |
| RB-b 하단 비검정 비율(후보 2× 표본/baseline) | 0.9988 | 0.9988 | 0.0010 | 0.9988/0.0005 | 정의 차이* |

\* 배너 상자를 포함 경계(`245:356, 270:531`)로, 비검정을 채널 max>0으로 셌다. work는 배타 경계·자체 임계(`nz`, baseline 72,277)를 썼다. 절대값 차이는 정의 차이이며 판정(≥99%, ±3%)은 같은 결과다. 수리 켬 비율 0.9988 일치.

- 캡처 SHA: a·b 후보 `19ce8ba99bfb`, baseline `f8e0cd5e2bd5`, off 후보 `c658e289fdc1` = lap1127 c27 결함 캡처 SHA(재계산 일치).
- **캡처 직접 열람:** 켬 `a/candidate/ps27.png`는 baseline과 같은 구도(상단 자원 3칸, "패배했습니다" 배너, 손 커서, 우측 로고, 하단 HUD·미니맵 팔각·F1~F11·초상 칸)를 2×로 보인다. off는 HUD 소실·상단 자원 아이콘 4× 확대(lap1127 결함)다.
- 비회귀 new-game(`ng/candidate/trace_raw.jsonl`): PS3 1,746 present min 100%, PS23 4,190 min 99.936%, PS5 98.719·PS7 98.166(기존 범주), PS9 100%, readback calls 0, fallback·V1·dropped 0, result `status` PASS → 일치.

## 4. 판정

- **불일치 0.** RB-a·RB-b·RB-c·RB-d 모두 PASS, off 결함 재현.
- **H-RS2 `PASS(partial, 기술·격리)` 수용.** PS27 HUD 소실(실제 가시 결함)은 수리됐다. 서피스 훅 가정 오류는 lap1128 middle 쪽 오류로 정정해 기록한다.
- 코드 검토 메모(비차단, 수리 불요):
  1. `g_last_frame`은 present마다 800바이트×`height`행을 복사한다. present 게이트가 정확히 800×600이라 현재 경로에서 과독·부분 프레임은 없다.
  2. 수리는 후면 버퍼 왼쪽 위 800×600에만 쓴다. HD 크기 후면 버퍼의 나머지 영역은 원본 역읽기 결과와 달라지지만 PS27 present는 그 영역을 읽지 않는다(work 공개와 같다).
- 공개 한계 유지: 승리 화면 UNKNOWN(같은 `0x4C7D00` → 같은 호출 지점이라 같은 수리 예상, fixture 없음) · PS22 역읽기 `0x41C7E5`(서피스 vtable 직접 호출, 호출 지점 훅 밖, 장면 미확인) · flip 분기 `0x4C7EC7` 미실행 · PS29 막대 98.36% 불변 · PS29 마지막 전환 present stale 478,002 backlog.
- **시험판 재스테이징: 보류.** 사용자 시험(lap1104 판본) 결과가 아직 없다. 판본 혼동을 막는 lap1107·1109 원칙도 있다. 그래서 H-RS3 수용 뒤 RS2+RS3(+보류 중 H-P35)를 한 판본으로 묶어 재스테이징할지 그때 정한다. 사용자 결과가 먼저 오면 그것이 최우선이다.

## 5. 다음 work 사전등록(Sonnet) — H-RS3: PS29 결과 표 막대 writer `0x468BB0` 미러

**정적 근거(원본 objdump, 이번 회차).**

- `0x468BB0`은 thiscall이고 `ret 0x28`(스택 10인자)이다. ecx(renderer `0xE5BF18`)는 쓰지 않는다. 키·클립 없는 행 단위 사각형 복사(`rep movsd`+`rep movsb`)다.
- 인자 디코드(호출 지점 `0x4B5493`의 push 순서와 함수 본문 대조):
  - arg0 `dst` = `[0xE5D42C]` = renderer+`G1_RENDERER_BUFFER`(0x1514)
  - arg1 `dst_pitch` = `[0xE5BF28]` = renderer+`G1_RENDERER_STRIDE`(0x10)
  - arg2 `src` = `[ecx*4+0x105CA70]+[0x105D1A4]`
  - arg3 `src_pitch` = `[0x105C5B4]`
  - arg4 `sx0`=0, arg5 `sy0`=0, arg6 `sx1`=n−1, arg7 `sy1`=0x11
  - arg8 `dx`=`[esi]`, arg9 `dy`=`[esi+4]`
- 따라서 폭은 `sx1−sx0+1`, 높이는 `sy1−sy0+1`(=18행, lap1126 "18행"과 일치)이다.
- 복사 의미: `dst + dy·dst_pitch + dx` ← `src + sy0·src_pitch + sx0`, 행마다 각 pitch만큼 진행한다.
- 호출 지점 바이트 `E8 18 37 FB FF`(대상 `0x4B5498 + 0xFFFB3718 = 0x468BB0`)이고 원본 안 호출처는 이 1곳이다(lap1128 확인).

**가설 H-RS3.** 원본 `0x468BB0` 호출 뒤 같은 사각형을 HD로 미러한다. 그러면 PS29 막대의 present당 stale +72가 0이 되고 PS29 HD min이 98.6% 이상이 된다.

**RS3-1 구현(구현 우선).**

- 호출 지점 훅을 `0x4B5493`에 둔다(H-RS2 `install_callsite` 패턴, 바이트 확인·detach 복원·`primitives_installed` 편입).
- wrapper는 thiscall·스택 10인자로 원본을 **먼저** 호출한다. 그 뒤 다음 조건을 모두 만족할 때만 미러한다.
  - `dst` == renderer 화면 버퍼
  - `dst_pitch` == renderer stride
  - 폭·높이 > 0
  - 목적지 사각형이 논리 800×600 안
  - src 읽기 가능
- 미러 방법(work 선택):
  - (a) src 사각형을 packed 임시 버퍼로 모아 기존 `transfer_block_copy_to_screen(renderer, dx, dy, w, h, packed)` 경로에 넘긴다.
  - (b) 같은 의미의 strided 순수 헬퍼를 둔다.
  - 어느 쪽이든 Scale2x/expected snapshot/covered 갱신 의미는 기존 block copy와 같아야 한다.
- env `SYW2_G1_BAR_COPY=0`이면 원본만 호출한다(기본 켬).
- trace 계수: `bar_copy_468bb0_calls`·`_mirrored`·`_rejects`·`_pixels`.
- 순수 헬퍼가 생기면 테스트한다(RED→GREEN): 조건 경계, 폭·높이 계산 `x1−x0+1`, 0/역전, 프레임 밖 거부, 거부 시 무쓰기.

**측정(격리).**

- g7defeat `--result-screen` 켬 2 run과 `SYW2_G1_BAR_COPY=0` 끔 1 run(결함 재현 대조)을 돌린다.
- 비회귀 1 run: new-game `--new-game-start --new-game-act --new-game-menu`. `0x468BB0` 호출 수를 공개한다.

**PASS(켬 2/2).**

- RS3-a: PS29에서 calls > 0, mirrored = calls − 공개된 rejects, rejects 사유를 공개한다.
- RS3-b: PS29 HD min(마지막 PS29→PS9 전환 present 1개 제외)이 ≥98.6%이고 기대값은 100% 근처다. present당 stale 증가 0. 탭 전환(병사·건물·자원) 뒤에도 같은 조건이다.
- RS3-c: PS27 HD min 100%(H-RS2 유지), PS9 100%.
- RS3-d: V1/안전 7종/fallback/hresult 0, dropped 0, scale2x PASS, 경과 p95 증가 ≤2ms. `result_tab_*.png`·`ps29.png`를 직접 열람하고 막대가 baseline과 같은 위치·길이인지 본다.
- 끔 run은 98.36%(+72/present)를 재현해야 한다.
- 비회귀: PS3 100%·PS23 99.936% 근처.

**FAIL/BLOCKED.**

- calls 0이면 호출 지점·상태를 다시 확인한다.
- stale이 남으면 남은 위치·writer를 공개하고 middle로 넘긴다.
- 실패 가설 2회 또는 60분이면 BLOCKED.

**공개만(판정 아님).**

- PS29 마지막 전환 present stale 478,002. 같은 run에서 원인 단서(전환 present의 writer 계수)가 보이면 기록한다.
- 막대 정체값 7,874 vs 면적 7,980 차이 106(lap1126 backlog).

**공통.**

- C·하네스 변경 뒤 lint·typecheck → 기록 freeze → `make check` 1회.
- 디스크 ≥20GiB(현재 136G), game 사본 삭제.
- 원본/참고 쓰기·커밋·시험판 재스테이징 금지.
- 사용자 G1 시험 결과가 오면 최우선이다.

## 6. 검사

- `checks/safety.sh check`·context 검사·focused 테스트(`tests/test_g1_primary_readback.py` 외 G1 mirror 계열)는 STATUS 검증 줄에 보강한다.
- 전체 `make check` SKIP. 이번 회차는 문서만 바꿨고, C·하네스·테스트 source SHA는 lap1129 full PASS 1775 그대로다.

## 다음 행동

work(Sonnet) H-RS3 구현·격리 실행(§5).
