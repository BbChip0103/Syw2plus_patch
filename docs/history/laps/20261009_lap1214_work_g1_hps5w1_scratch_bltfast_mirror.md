# 2026-10-09 | lap 1214 | G1 work — H-PS5W1: 복제되지 않은 뒤 버퍼 BltFast(글자 스크래치) 미러

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-sonnet-5-5`/high, work(실무) 1 lap. 제품 C·테스트 변경 있음(제품 동작 변경 1: 메뉴 목록 글자 미러), 커밋 0.
- 입력: STATUS "다음 한 가지"(work H-PS5W1), lap1213 middle 사양 §5. INBOX 새 사용자 지시 없음(마지막 = lap1213 처리 메모), APPROVALS 새 반려·시험 결과 없음, `loop/STOP`·`loop/ESCALATE_SOL` 없음(시작 시 확인).
- 가설: PS5 영구 stale(지도 목록 92.9% + 좌측 이름)은 뒤 버퍼 `[0xE5D438]`의 **복제되지 않은 vtable BltFast**(글자 스크래치 `[0x104F810]`, flags `0x11`)가 미러 밖에서 글자를 쓰기 때문이다. 그 슬롯을 감싸 사각형을 기록하고 present에서 expected 대비 diff하면 stale이 0이 되고 글자가 HD로 나온다.
- 사전등록 PASS/FAIL(lap1213 §5): 호출 ≥1·반환 주소 ⊂ 7곳 / 켬 PS5 stale ≤504 2/2·끔 5,044±1 / 내용 불변 / 안전 7종 0 / p95 ≤ +2 ms / save006 pair PASS·NG5 비회귀. 감소 <50% = FAIL.
- 원본 SHA: `[ESL]Syw2plus/[HQ]Syw2plus 2002.exe` `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac` 직접 재계산 MATCH. 모든 run `source_unchanged` true 2/2, `game` 사본 삭제(잔존 0). 팩 끔·기본 env·`--hd-source scale2x`, 격리 game 사본·prefix·빈 Xvfb, fixture 없음(새 게임 대기실).

## 0. 변경 파일(모두 uncommitted; 같은 파일들에 lap1099~1212 미커밋 변경이 이미 있다)

- 신규 `tools/inmm_stub/g1_scratch_bltfast.h`(`fcc0650cabf8`): 순수 헤더 — `g1_scratch_bltfast_state_accepts`(5·7만), 호출 지점 7곳 표와 `site_index`(없으면 7), `g1_scratch_bltfast_rect`(원본 사각형 크기를 `(x,y)`에 놓고 800×600으로 clip, src 없음·빈 사각형·원점 밖 거부), 64칸 제한 큐(`push` 초과분은 `overflow`로 세고 버림, `reset`은 overflow 유지).
- `tools/inmm_stub/g1_mirror2x.c`(`cd34fd3c6208`): env `SYW2_G1_SCRATCH_BLTFAST_MIRROR`(기본 켬, 정확히 `0`이면 끔). `mirror_scratch_blt_fast`(stdcall 래퍼): 화면을 건드리지 않고 사각형만 큐에 넣고 원본을 정확히 1회 호출. `g1_mirror2x_scratch_bltfast_adopt(back, has_record)`: 뒤 버퍼가 `[0xE5D438]`이고 trace 기록이 없을 때만 vtable 복제(BltFast만 교체), 같은 객체·복제 vtable이면 재설치 안 함. `scratch_bltfast_at_present`: `rect_blt_heal_at_present` 바로 뒤, present의 화소 루프 앞에서 큐의 사각형마다 expected 스냅샷을 before·이미 잠긴 뒤 버퍼를 after로 `g1_overlay_blt_apply_tiled`(바뀐 화소만 expected/covered/HD 갱신). 추가 Lock 없음. 계수 calls·recorded·rejects·site_calls[7]+other·adopts·adopt_skipped_record·overflow·flush_applied·flush_pixels.
- `tools/inmm_stub/g1_mirror2x.h`·`direct_draw_trace.c`(`effed26e623d`·`db7b34097dbd`): 접근자와 present 행 필드 `scratch_bltfast_*`, 기본 present 경로에서 `g1_mirror2x_scratch_bltfast_adopt(source, source_record != NULL)`를 `copy_present` 앞에서 호출. `Makefile`(`200847934803`): 의존 헤더 추가.
- 신규 `tests/test_g1_scratch_bltfast.py`(`65c0ef4cbe8e`, 6개: 게이트·사각형 gcc 픽스처, 큐 경계 gcc 픽스처, 래퍼 구조(원본 1회·Lock 없음), 채택 구조, present 순서, 계수 노출). RED(헤더·심볼 부재 6 failed) → GREEN 6 passed. 변이 6종 중 5 RED(원본 2회·flush 제거·상태 3 허용·x 경계 제거·큐 off-by-one), 생존 1(재채택 가드 제거)은 단언 추가 후 RED로 닫음.

## 1. 실행·측정 (공유 temp `20261009_lap1214_work_hps5w1/`, 스크립트 `scripts/run.sh`·`chain1.sh`·`chain2.sh`·`ana.py`·`s2x.py`·`ng5.py`·`leafdiff.py`)

M1 = `--new-game-path --new-game-start --stale-mask 300-309 --stale-mask-state 5`(lap1212와 같은 명령). 끔 = `SYW2_G1_SCRATCH_BLTFAST_MIRROR=0`. trace는 `mirror2x_present` 이벤트, `program_state`로 장면을 나눴다(lap1213 정정 1 방식).

| run | PS5 present | PS5 stale min/p50/max | mask dump 10개 stale | PS7 stale | PS5 elapsed p95 / gap p95 ms |
|---|---|---|---|---|---|
| **on1** 켬 | 680 | 0 / 0 / 0 | 전부 0 | 0 | 15 / 21 |
| **on2** 켬 | 714 | 0 / 0 / 0 | 전부 0 | 0 | 15 / 20 |
| **off1** 끔 | 728 | 4,684 / 5,044 / 5,044 | 전부 5,044 | 1,398 | 14 / 19 |

- **W1-0 (귀속 확인):** 켬 두 run `scratch_bltfast_adopts` 1·`adopt_skipped_record` 0(뒤 버퍼는 trace 기록 밖 = 복제 안 된 vtable), 래퍼 호출 8,074(on1)·8,492(on2) 전부 사각형 기록·거부 0·`other_site_calls` 0. 반환 주소는 7곳 중 **`0x4048D2` 6,716·`0x4B6D66` 1,358**(on1)에만 나온다(on2 7,066·1,426). 나머지 5곳은 이 장면에서 0 호출. 끔 run 호출 0·stale 5,044 재현. lap1213 정적 귀속 "복제되지 않은 vtable의 글자 스크래치 BltFast" **확인**.
- **W1-2 감소:** PS5 stale 5,044 → **0**(100% 감소, 2/2), 목표 ≤504 초과 달성. 끔 5,044±1 재현(전 present 4,684~5,044). 보너스: PS7 1,398 → 0(켬 2/2, 끔 1,398). PS3 stale 0 불변.
- **W1-2 내용 불변(측정식 정정 1건):** 사전등록은 "이전 stale 화소에서 후보 2×2 좌상 = 원본 캡처 ≥99%"였다. 켬 캡처 `ps5.png`의 리터럴 값은 **4,874/5,044 = 96.6%**(on1·on2 같음)다. 이 식은 Scale2x 출력에 맞지 않는다 — Scale2x는 대각 가장자리에서 좌상 화소가 원본 화소와 다른 것이 정상이고, 같은 캡처의 **전체 화면 좌상=원본 일치도 94.5%**라 어떤 정상 HD 화면도 이 식으로는 99%가 안 나온다(끔은 nearest라 100%인 것이 자명). 정확한 기준 = 원본 캡처(`baseline/ps5.png`)를 독립 구현 Scale2x로 2배한 것과의 4화소 블록 일치: stale였던 5,044 화소에서 켬 **5,044/5,044 = 100%**(on1·on2), 끔 4,139/5,044 = 82.06%(nearest). 전체 화면 블록 일치 켬 99.391%·끔 99.202%. 캡처 열람: 지도 목록 글자·좌측 이름이 정상으로 매끈, 깨짐·누락 없음.
- **안전·성능:** 안전 7종(fallback·dropped·hresult·violations·verify/restore 실패) 켬 모든 run 0, `scratch_bltfast_rejects` 0·`overflow` 0. PS5 present 경과 p95 켬 15/15 대 끔 14(+1 ms) → ≤+2 ms 충족, present 간격 p95 켬 21/20 대 끔 19(+1~2). 켬 비용 = present당 큐 사각형 diff(추가 Lock 0).
- **W1-3 비회귀:**
  - **save006 pair:** PON(켬)·POFF(끔) 모두 `status PASS`·`scene_state_equal` true, 판정 leaf **200개 전부 동일**(차이 0, `leafdiff.py`), 안전 수치 차이 0. 기존 상태 그대로: `owner0_hq_type` UNKNOWN·`mirror_validator` BLOCKED(기존 하네스), production `v2s_raw` FAIL은 켬·끔 둘 다 같다(W-1 gate 아님, 공개 진단 — lap1202 PA는 PASS·PD는 FAIL이던 run 간 변동 값).
  - **NG5** (`--new-game-act --new-game-play` 8방향 키 hold 20 dwell 56): NON(켬)·NOFF(끔) `status PASS`, PS3 present 6,034(켬)·6,022(끔) stale 0·covered_min 480,000·p95 6(켬) 대 8(끔) → 비회귀. NG5 안에서도 래퍼 호출은 PS5·PS7 구간 8,693뿐(site `0x4048D2` 7,229·`0x4B6D66` 1,464, 인게임(PS3) 구간 래퍼 호출은 계수상 없음; 이유는 미확인 — PS3 뒤 버퍼가 trace 기록이 있는 다른 객체일 가능성은 추정이고 측정 안 함).

## 2. 판정

**H-PS5W1 `PASS`(사전등록 기준, 측정식 정정 1건 공개)**: PS5 stale 5,044→0(2/2)·끔 재현, PS7 1,398→0 부가, 내용은 독립 Scale2x와 100% 일치, 안전 0, p95 +1 ms, pair 200 leaf 동일·NG5 비회귀. partial 사유: 격리 Wine 2 lane만(실제 Windows 미검증), 호출 지점 7곳 중 5곳(`0x405A06`·`0x4B7369`·`0x4D1338`·`0x4D1E27`·`0x4D77EA`)은 이 장면에서 0 호출이라 런타임 미관측, 상태 허용 목록은 5·7뿐(다른 메뉴 상태·PS3 인게임 글자 스크래치 호출은 일부러 열지 않음), 시험판 재스테이징 미실행(가시 효과 = 지도 목록 글자 화질).

## 3. 검사

- `make lint`·`make typecheck` 통과, `tests/test_g1_scratch_bltfast.py` 6 passed, C 빌드(mingw) 새 경고 0(기존 `control_executor.c`·`asset_hook.c` 경고만). 전체 `make check`는 기록 freeze 뒤 1회, 결과는 STATUS 검증 줄에 보강한다.
- 로그 `logs/gates/lap1214-chain1.log`·`lap1214-chain2.log`(+`.exit`), 공유 temp `run_<label>.log`·`.exit`·`disk_*`. 후보 DLL 해시(하네스가 run마다 재빌드, 타임스탬프 때문에 서로 다름): on1 `41aab9b5f5e7`·off1 `e61f7619777c`·on2 `958c8f70d079`·PON `7d50f392f89c`·POFF `f0256ab44579`·NON `b7fa14599ede`·NOFF `28d82b1e1626`.

## 4. 한계·위험

- 래퍼는 사각형만 기록하고 present에서 diff하므로, present 사이에 같은 자리에 두 번 그려 중간 상태가 사라지는 경우 최종 상태만 반영된다(그게 화면에 나가는 상태라 기대 동작).
- 큐 64칸 초과분은 버려진다(`overflow` 계수 0이라 이 장면은 충분하지만, 글자 줄이 더 많은 화면은 stale로 남을 수 있다).
- 되돌리기: env `SYW2_G1_SCRATCH_BLTFAST_MIRROR=0`. 한 번 채택한 vtable 복제는 프로세스 수명 동안 유지(원래 vtable로 복원하지 않음; 모든 슬롯이 원본과 같고 BltFast만 래퍼).
- 위험(미관측): Windows의 실제 DirectDraw 객체는 래퍼 설치 방식이 같은 vtable 교체다(기존 trace와 같은 방식). 실제 Windows 미검증.

## 다음 행동

middle(Opus): raw 독립 재계산(새 스크립트로 M1 켬 2·끔 1 PS5/PS7 stale·호출 지점 분포·캡처 블록 일치·pair leaf·NG5 p95), 측정식 정정(리터럴 좌상 일치 → 독립 Scale2x 블록 일치) 수용 여부, `PASS` 수용 뒤 backlog 재정렬(남은 5곳 호출 지점·다른 메뉴 상태 허용·재스테이징 묶음 판단). 사용자 업스케일·G1 시험 결과가 오면 그것이 최우선.
