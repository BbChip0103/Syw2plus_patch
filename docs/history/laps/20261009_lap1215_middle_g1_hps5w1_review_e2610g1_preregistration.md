# 2026-10-09 | lap 1215 | G1 middle — H-PS5W1 독립 검수 · 다음 work H-E2610G1-0(G1 DLL을 ESL 2610에서) 사전등록

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5-5`, middle(중간계획·컨펌) 1 lap. 게임 run 0, 제품 C·하네스·테스트 변경 0, 커밋 0.
- 입력: `loop/ESCALATE_SOL`(lap1214 work 검수 요청, SHA256 `22506dd9…`) → byte 일치 보존 `docs/history/laps/20261009_lap1215_preserved_lap1214_escalate_sol.txt` 뒤 삭제. INBOX 최신 사용자 지시 = **2026-10-09 ESL 2610 기준 전환**(루프는 G1 계속, G1의 2610 전환 시점은 middle이 정함). APPROVALS 새 반려·시험 결과 없음. `loop/STOP` 없음.
- 원본 SHA: `[ESL]Syw2plus/[HQ]Syw2plus 2002.exe` `b56986e0…08a8ac` 직접 재계산 MATCH. 2610 정본 `patch_history/[ESL]Syw2plus 2610/[ESL]Syw2plus 2610.exe` `c5530cf4fd5f9429…3938d` 직접 재계산 MATCH(INBOX 값과 같음).

## 1. 독립 재계산(저장소 밖 새 스크립트, work의 `ana.py`·`s2x.py`·`ng5.py`·`leafdiff.py`를 쓰지 않음)

공유 temp `20261009_lap1215_middle_review/`: `recalc_lap1215.py`(`368dc980ffd2`) → `recalc_lap1215.json`(`d16ebd26dd18`), `ps7_v2s_lap1215.py`(`24bc595de579`) → `ps7_v2s_lap1215.json`(`efbc614756c9`), `mutate_lap1215.py`(`1d1c776f3c91`) → `mutations.json`(`6253eaf6652c`).

- **source 동일성:** 7 run의 `bridge/` 사본 `g1_mirror2x.c`(`cd34fd3c6208`)·`g1_scratch_bltfast.h`(`fcc0650cabf8`)·`g1_mirror2x.h`(`effed26e623d`)·`direct_draw_trace.c`(`db7b34097dbd`)가 현재 트리와 같다(on1·off1·PON·NON 대조).
- **M1 PS5(trace `mirror2x_present`를 `program_state`로 나눔):** on1 680·on2 714 present stale min/중앙/max 0/0/0, off1 728 present 4,684/5,044/5,044(마지막 5,043). mask dump 10개: on 전부 0, off 전부 5,044. off 10개 dump stale 교집합 = 합집합 = **5,044**. 그 5,044 화소는 on1·on2의 10 dump에서 **50,440/50,440 전부 값 1(covered·일치)**, 0(uncovered)·2(stale) 없음.
- **PS7:** on 0/0/0(149·160 present), off 1,398 고정(159). **PS3**(M1 264~265 present) stale 0, PS9 0.
- **호출 지점(present 사이 계수 증분을 상태별로 귀속):** on1 PS5 `0x4048D2` 6,120·`0x4B6D66` 1,358, **PS7 `0x4048D2` 596**, PS3·PS9 0. 합 8,074 = 마지막 `scratch_bltfast_calls`·`recorded`·`flush_applied`. on2 PS5 6,426+1,426·PS7 640(합 8,492). rejects·overflow·other 0, adopts 1·skipped_record 0. off 계수 전부 0. → work 수치 일치. 정정 1(경미): work 기록의 사이트 수치 `0x4048D2` 6,716은 PS5 6,120 + PS7 596의 합이다(PS5 전용 아님).
- **성능:** PS5 elapsed p95 on 15/15 · off 14, present 간격 p95 21/20 · 19. PS7 elapsed p95 16/15 · 15. +1 ms ≤ +2 ms.
- **안전:** 모든 lane(on1·on2·off1·NON·NOFF) present 행에서 `fallback`·`hresult`≠0·`success`≠1·`hd_mask_outside_diff_subpixels`·`scale2x_palette_violations`·`viewport_restore_failures`·`cache_clip_verify_failures`·`clip_replay_mismatches`·`identity_key_mismatches`·scratch rejects/overflow/other 0회, `dropped_count`·`aggregate_output_dropped_count`·`primary_present_dropped` 최대 0.
- **캡처 내용(PS5):** baseline `ps5.png`(on1·on2·off1 모두 `b179c67a…`)를 독자 Scale2x로 2배해 4화소 블록 비교. 이전 stale 5,044 화소에서 on(on1·on2 후보 PNG 같은 SHA `50d4e19d…`) **Scale2x 블록 5,044/5,044**, nearest 블록 4,139, 리터럴 좌상=원본 4,874(96.6%). off(`c0879f56…`) nearest 블록 **5,044/5,044**(= 내용이 원본과 같음), Scale2x 블록 4,139. 전체 화면 Scale2x 블록 on 99.391%·off 99.202%, 좌상=원본 on 94.491%·off 94.527%. → work 수치 전부 일치.
- **캡처 내용(PS7, 보강):** on1 대 off1에서 바뀐 블록 357개 전부 on이 Scale2x와 일치(357/357). stale 1,398 중 나머지는 nearest와 Scale2x가 같은 화소라 화면 차이 없음. PS7에 Scale2x 아닌 블록 902개(nearest 387 + 둘 다 아님 515)는 on·off 같은 기존 잔여(이번 변경 무관, 미귀속).
- **save006 pair:** PON·POFF 모두 `status` PASS·`scene_state_equal` true·input_effect PASS·minimap parity PASS(effect PASS)·V2/V2s/V2q/Scale2x gate PASS(V2s `tag_status/production` PASS). 판정 leaf(`status`·`effect`·`_equal`·`verdict` 끝) 202개 차이 0.
- **NG5:** NON PS3 6,034 present stale 0·p95 6, NOFF 6,022·stale 0·p95 8. NON PS5 733 stale 0(NOFF 700, 5,044), PS7 0(NOFF 1,398). PS3 래퍼 호출 0(래퍼는 상태 검사 **전에** `calls`를 세므로 0 = PS3에서 그 vtable BltFast 호출 자체가 없음 — work의 "이유 미확인"을 이 코드 순서로 답함).

## 2. 코드 검토

- 래퍼(`mirror_scratch_blt_fast`): 화면 안 건드림, 사각형만 큐, 원본 정확히 1회. 채택(`g1_mirror2x_scratch_bltfast_adopt`): 뒤 버퍼 `[0xE5D438]` 일치·trace record 없음일 때만 vtable 복제, BltFast 한 칸만 교체.
- **사전등록 "Wine 비동기 → 비교 전 Lock" 요구 충족:** flush는 `g1_mirror2x_copy_present`가 source를 `Lock(DDLOCK_WAIT|DDLOCK_READONLY)`한 뒤, 화소 루프 전에 실행된다. Lock이 wined3d CS를 비우므로 큐의 BltFast 결과가 반영된 뒤 diff한다(on 50,440/50,440 일치가 실측 근거).
- **사전등록 이탈 2(수용):** (a) W1-0 "목적 사각형 합집합 ≥90%"는 직접 기록 안 됨 → on dump에서 이전 stale 화소 100%가 covered·일치로 대체 입증. (b) "원복·버전 불일치 거부"는 복제 vtable을 프로세스 수명 동안 유지(원복 없음). 뒤 버퍼 주소·record 여부 검사와 끔 env가 있고, 기존 trace의 vtable 복제와 같은 방식이다. Windows 실제 ddraw에서의 vtable 교체 안전성은 기존 trace와 같은 미검증 위험으로 남긴다.
- **변이(저장소 밖 사본, 독립 8종):** RED 4(끔 env 무시·뒤 버퍼 주소 검사 제거·y 클립 제거·상태 3 허용), **생존 4**: m1 flush 상태 검사 제거(큐는 5·7에서만 차므로 상태 전환 present 한 번만 다름, 준동등), m7 flush를 `s3_overlay_at_present` 뒤로(둘 다 화소 루프 전, 준동등), **m2 `has_record`여도 vtable 교체(trace record 표면의 복제 vtable을 덮어 trace hook 상실), m3 flush 끝 큐 reset 제거(같은 사각형 재처리 후 64칸에서 overflow → 새 글자 stale)** — m2·m3는 테스트 공백(제품 결함 아님, 현재 코드는 올바름).

## 3. 판정

- **H-PS5W1 `PASS(partial, 기술·격리)` 수용.** 불일치 0, 정정 1(사이트 수치 상태 귀속, 판정 영향 0), 이탈 2 수용, 테스트 공백 2.
- **측정식 정정 수용:** 사전등록(lap1213 §5)의 "후보 2×2 좌상 = 원본 ≥99%"는 middle의 사양 오류다. Scale2x 출력은 대각 가장자리에서 좌상이 원본과 다른 것이 정상이라 정상 HD 화면도 94.5%다. "내용 불변"은 off nearest 블록 100%(내용 = 원본)와 on Scale2x 블록 100%(화질 = HD)로 정확히 입증된다. 이 정정은 기준 완화가 아니라 기준 정의 수정이다(같은 화소에서 더 엄격한 4화소 일치).
- partial 사유: 격리 Wine만, 호출 지점 7곳 중 5곳(`0x405A06`·`0x4B7369`·`0x4D1338`·`0x4D1E27`·`0x4D77EA`) 미관측, 상태 허용 5·7뿐, 실제 Windows 미검증.
- 가시 효과: PS5 지도 목록·좌측 이름·PS7 글자가 nearest → Scale2x. 재스테이징은 지금 하지 않는다(다음 묶음 때, 아래 §4 2610 결과와 함께 판단).

## 4. G1의 ESL 2610 전환 시점 결정

INBOX 2026-10-09 사용자 결정은 정본을 공식 ESL 2610으로 바꿨고, G1 전환 시점은 middle에 맡겼다. **지금 착수한다(가능성 probe부터).** 근거:
- 사용자가 실제로 플레이할 EXE는 이제 2610이다. HQ2002 위 G1 증거는 그대로 유효하지만, 사용자 G1 시험이 2610에서 돌면 지금 DLL이 거기서 켜지는지가 사용자 마일스톤의 직접 전제다.
- INBOX의 정적 조사가 위험 5개(① `_inmmserv.exe` 없을 때 MessageBoxW 대기 ② 창모드 HQCDD 공존 ③ `.kills`/`.idle` 오버레이의 `0x4664D0` 호출 = 패널 반환주소 화이트리스트 밖 ④ 선택 배열 `0x899028`→`0x1604004` ⑤ `Data`→`ESLData`)를 이미 지목했고, 실행 수단도 있다: 별도 2610 세션이 만든 `tools/esl2610_runtime.py`(`[ESL]Syw2plus` + 2608 overlay + 2610 overlay + EXE, SHA 고정, `runtime_env.prepare` 재사용).
- PS5W1 남은 항목(미관측 호출 지점·다른 메뉴 상태)은 작은 잔여라 2610 probe보다 우선할 이유가 없다.

주의 — 동시 작성자: 별도 2610 세션(G2·G6, 이 루프 밖)이 오늘 `tools/esl2610_runtime.py`·`tests/test_esl2610_runtime.py`·`patches/esl2610/`·`tools/g6_shift_click_probe.py`·`analysis/esl2610/`를 작성 중이다(17:39 수정, untracked). 단일 작성자 규칙에 따라 G1 work는 이 파일들을 **읽기·import만** 한다.

## 5. 다음 work 사전등록 — H-E2610G1-0: 현재 G1 DLL을 ESL 2610에서 켜기(가능성 판정)

**가설:** INBOX 정적 조사대로 DLL 계약·훅 바이트가 2610에서 같으므로, 현재 트리 G1 DLL(팩 끔·기본 env)은 2610 EXE에서 1600×1200 미러로 타이틀→대기실→인게임까지 안전 0으로 동작한다. 깨지는 곳이 있으면 위 위험 ①~⑤ 중 어느 것인지 실측으로 귀속된다.

**구성:** 게임 = `esl2610_runtime.prepare(2610 EXE bytes, runtime_root, bridge=…)`(EXE SHA `c5530cf4…` 검사, 다르면 중단). baseline·candidate lane 역할은 HQ2002 경로와 같게 두고 EXE만 2610으로 바꾼다. 팩 끔·`--hd-source scale2x`. 격리 game 사본·prefix·빈 Xvfb, run마다 `game` 사본만 삭제.

| 단계 | 할 일 | PASS 조건 |
|---|---|---|
| E0-0 테스트 공백 | `tests/test_g1_scratch_bltfast.py`에 단언 2개: (a) `has_record`면 vtable을 건드리지 않고 반환(lap1215 변이 m2), (b) flush 끝에서 큐 reset(m3). 저장소 밖 사본에서 m2·m3 RED, 트리 GREEN. 제품 C 변경 0. | RED→GREEN |
| E0-1 하네스 | `tools/g1_saved_scene_probe.py`에 `--esl2610`: 두 lane 게임을 `esl2610_runtime.prepare`로 만들고, 선택 배열 읽기를 `esl2610_runtime.SELECTION_ENTRIES_VA`·`SELECTION_CAPACITY`로 바꾼다. `esl2610_runtime.py`·`runtime_env.py`·`patches/esl2610/`는 수정 금지(필요하면 BLOCKED로 보고). 호스트 테스트 RED→GREEN. | 테스트 RED→GREEN, 플래그 없으면 기존 동작 byte 동일 |
| E0-2 부팅 probe | `--esl2610 --new-game-path --new-game-start` 1 run(필요 시 하네스·시작 결함 수리 뒤 재실행, 최대 3 cycle). 관측: (a) 시작 시 MessageBox(A/W)·`_inmmserv.exe` 대기 여부(probe.log·캡처) (b) `mirror2x_install` active·`set_display_mode` 1600×1200 (c) 상태 순서 PS9→PS7→PS5→PS3 도달과 2610 메뉴 좌표가 하네스 클릭과 맞는지 (d) PS3 present: stale·covered·안전 7종·`hd_mask_outside` 0 (e) 훅 설치 실패·old bytes 불일치·primitive verify 실패 수 (f) 패널 반환주소 거부·`0x4664D0` 관련 reject 계수(③) | 두 lane PS3 도달, candidate 훅 설치 실패 0·안전 7종 0 |
| E0-3 인게임 | E0-2 PASS면 `--esl2610 --new-game-path --new-game-start --new-game-act --new-game-play` 1 run. | 입력 효과 두 lane 같음, PS3 stale·안전 0, p95를 HQ2002 NG5(lap1214 NON 6 ms)와 나란히 기록 |

**결론 규칙:**
- E0-2·E0-3 PASS → `FEASIBLE`. 다음 middle이 2610 전환 범위(사용자 시험판을 2610용으로 묶을지, HQ2002 pair 기준선 유지 여부)를 정한다.
- 훅 old bytes 불일치·설치 거부 → `NOT_FEASIBLE(현재 DLL)`. 어느 주소인지 기록하고, 다른 버전 오프셋을 추측 적용하지 않는다(주소 근거는 `analysis/memory_maps/`에 남기는 middle 몫).
- 시작이 MessageBoxW 등으로 멈추면, 스텁의 기존 MessageBoxA 처리와 같은 방식의 최소 수리를 이 회차에 시도할 수 있다(구현 우선). 3 cycle 뒤에도 PS9에 못 가면 `BLOCKED`.
- 2610 고유 화면(`.kills`/`.idle` 오버레이 등)에서 stale·reject가 나오면 위치·계수만 기록한다(수리는 다음 회차).

**하지 않는 것:** G1 미러 로직·validator·gate 변경, 팩 켬, 시험판 재스테이징, G2/G5/G6/G7 접촉, 별도 2610 세션 파일 수정, 2610/원본 EXE·`patch_history`·`260921_temp` 쓰기.

**검사:** 테스트 RED→GREEN, `make lint`·`make typecheck` 뒤 `make check` 1회, SAFETY. 별도 세션의 untracked 파일 때문에 `make check`가 실패하면 그 파일·실패를 기록하고 그 파일은 고치지 않는다. 장기 run은 PID·`.exit` 파일로 끝까지 기다린다(`pgrep -f` 자기 일치 금지).

**우선순위 예외:** 사용자 업스케일 결과나 G1 시험 결과가 INBOX에 오면 그것이 최우선이다.

## 6. 검증

- 이번 회차 변경: 문서(STATUS 압축·이 기록·INBOX 메모·ESCALATE_SOL 보존본)와 공유 temp 재계산 스크립트·결과뿐.
- 전체 `make check` SKIP(source 변경 0, lap1214 full PASS 2138 그대로). focused·SAFETY·CONTEXT 결과는 STATUS에 보강한다.
- STATUS 압축: 원문 130줄·SHA256 `d1b8643b71b79e948161651d35a99fef23f79dc03c162fc358ebcd1b2be36bf9`를 `docs/history/20261009_status_lap1215_precompaction.md`에 byte-exact 보존.

## 7. 다음 한 가지

work H-E2610G1-0(§5). 사용자 업스케일·G1 시험 결과가 오면 그것이 최우선.
