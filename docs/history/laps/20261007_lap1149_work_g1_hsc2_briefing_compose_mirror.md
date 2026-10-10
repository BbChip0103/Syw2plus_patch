# 2026-10-07 | lap1149 | G1 work — H-SC2: PS20 브리핑 합성 호출 지점(`0x4B23B5`→`0x4D4620`) diff 미러

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-sonnet-5-5`, high / work(실무) 1 lap. C·테스트 변경 있음(제품 동작 변경 1: PS20 브리핑 합성 미러), 커밋 0.
- 입력: STATUS "다음 한 가지"(work H-SC2), lap1148 기록 §4 사양. INBOX 새 사용자 지시 없음(마지막 = lap1148 처리 메모), APPROVALS 새 반려·사용자 시험 결과 없음(lap1136 재요청 대기), `loop/STOP`·`loop/ESCALATE_SOL` 없음(시작 시 확인).
- 가설: PS20 stale writer는 게임이 매 present `0x4D4620`으로 뒤 버퍼 `[0xE5D438]`에 하는 키 BltFast/Blt이고(vtable 미복제 → hook 밖), 호출 지점을 감싸 뒤 버퍼를 전/후 diff하면 PS20 정착 HD min ≥98.6을 만들 수 있다.
- 사전등록 PASS/FAIL(lap1148 §4): 켬 min ≥98.6·<90 0%·초상화 3칸 stale ≈0 & 끔 min 89.43 재현 = `PASS(partial, 기술·격리)`. calls 0 또는 개선 0 = 반증.
- 원본 SHA: `[ESL]Syw2plus/[HQ]Syw2plus 2002.exe` `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac` 직접 재계산 MATCH(읽기만, objdump로 `0x4B23AA..0x4B23B5` = `mov eax,[0xE5D438]; mov ecx,0x61E370; push eax; call 0x4D4620` 재확인). 모든 run `source_unchanged` true·cleanup ok·`game` 사본 삭제(잔존 0).
- fixture: 없음(타이틀에서 시작, 비합성).

## 0. 변경 파일(모두 uncommitted; 같은 파일들에 lap1099~1148 미커밋 변경이 이미 있다)

- 신규 `tools/inmm_stub/g1_briefing_compose.h`(`fa26be35c0b2`): 순수 게이트 `g1_briefing_compose_accepts(state, dest, back_buffer, width, height, pitch, bpp)` — 상태 20·dest==뒤 버퍼·비 NULL·8bpp·pitch 800..2048·(height 600 & width ≥800 또는 1600×1200).
- `tools/inmm_stub/g1_mirror2x.c`(`e3c6a1bcd754`): `G1_BRIEFING_COMPOSE_SITE 0x4B23B5`·`_FUNC 0x4D4620`·`G1_BACK_BUFFER_VA 0xE5D438`, env `SYW2_G1_BRIEFING_COMPOSE`(기본 켬, 정확히 `0`이면 끔), `mirror_briefing_compose_site`(thiscall 인자 1, `ret 4`): 게이트 통과 시 뒤 버퍼 Lock(WAIT) → 800×600 논리 영역을 before로 복사(`g1_bar_copy_pack`) → Unlock → 원본 `0x4D4620` 정확히 1회 → 다시 Lock(WAIT, wined3d 큐 동기화) → `g1_overlay_blt_apply_tiled`(H-TM1 방식, 바뀐 화소만 HD 미러) → Unlock. 설치(`install_callsite`, old bytes `E8 66 22 02 00`)·detach·installed 판정, 계수 calls·mirrored·changed pixels·rejects(+reject gate/lock/surface 이유별, 마지막 dest·geometry).
- `tools/inmm_stub/g1_mirror2x.h`·`direct_draw_trace.c`(`a6eda22ba8a0`·`d3e372e276a7`): 접근자와 present 행 필드 `briefing_compose_4d4620_{calls,mirrored,rejects,pixels}`·`briefing_compose_reject_{gate,lock,surface}`·`briefing_compose_last_{dest,geometry}`. `Makefile`(`de73c1045595`): 의존 헤더 추가.
- 테스트 신규 `tests/test_g1_briefing_compose.py`(`c19dd4548436`, 3개: 게이트 gcc 픽스처·호출 지점/설치/detach 계약·계수 노출). RED(헤더 부재) → GREEN. 기존 `g1_bar_copy.h`·`tests/test_g1_bar_copy.py`는 lap1131 산출물 그대로.

## 1. 구현 중 발견 — 사전등록 정정 1건

첫 run(`on_a`·`on_b`·진단 `d1`)에서 wrapper calls = PS20 present 근사지만 mirrored 0·rejects 전부(`reject_surface` 4,351/4,351): **뒤 버퍼 `[0xE5D438]`의 잠금 geometry = 1600×1200 pitch 1600 8bpp**(`briefing_compose_last_geometry [1600,1200,1600,8]`). 사전등록 §4는 800×600 논리 영역 가정이었다. 이것은 present 게이트의 `menu_shape`(1600×1200 BACKBUFFER 표면의 왼쪽 위 800×600 = 논리 프레임; `g1_present_contract.h`)와 같다. 게이트에 1600×1200을 허용하고 before/after 모두 왼쪽 위 800×600만 다뤘다(stride = lock pitch). 첫 3 run은 수리 전 DLL이라 판정 근거에서 제외하고 `on_a`=거부 상태 재현 기록으로만 둔다(PS20 HD min 89.43 = 끔과 동일).

## 2. 실행·측정 (공유 temp `20261007_lap1149_work_hsc2/`, 명령 `scripts/run_sc2.sh <name>`)

공통: `--hd-source scale2x --title-button scenario --scenario-start --scenario-play --scenario-briefing-dwell 65 --stale-mask 700,1750,2650,3350,4350 --stale-mask-state 20`. 켬 = 기본, 끔 = `SYW2_G1_BRIEFING_COMPOSE=0`. 요약 `scripts/sc2_summary.py`·`sc2_calls.py`(새 스크립트, numpy/scipy).

| run | PS20 정착 present | HD min / p50 | <98.6 / <90 | stale max | wrapper calls / mirrored / rejects | 변경 화소 합 |
|---|---|---|---|---|---|---|
| **on1**(켬) | 3,621 | **100 / 100** | 0% / 0% | **0** | 3,318 / 3,318 / 0 | 55,021,644 |
| **on2**(켬) | 3,561 | **100 / 100** | 0% / 0% | **0** | 3,271 / 3,271 / 0 | 52,883,581 |
| **off1**(끔) | 4,644 | 89.43 / 98.218 | 67.0% / 7.1% | 50,735 | 4,344 / 0 / 4,344(gate) | 0 |
| on_a·d1(거부 상태) | 4,729·4,625 | 89.43 / 98.219·98.218 | 66.2·67.3% / 7.0·5.9% | 50,735 | reject_surface 전부 | 0 |

- stale mask 5 dump(present 약 1,860·2,910·3,810·4,510 부근): 켬 on1·on2 **전부 stale 0·성분 0**(on1 4 dump·on2 4 dump, 끔은 7,385·8,819·1,286·18,494·50,735 + 초상화 3칸 15,949·16,134·15,579 재현). 끔 = lap1145~1148과 같은 수치(결정적 재현).
- 다른 상태 비회귀(켬 on1/on2, 끔과 동일): PS15 100/100, PS9 100/100, PS3 99.686/99.686(stale 0, covered_min 478,491 — lap1145와 동일), PS1은 미러 present 0.
- **calls 대 PS20 present(SC2-1)**: wrapper calls는 PS20 present의 91.6%(on1 3,318/3,622)로 사전등록 ±2%를 벗어난다. 원인은 trace로 확정: PS20 **첫 304 present**(on2는 291)에서는 호출이 없고(`0x4D3EF0()!=1` 구간, 본문 준비 전) 그 뒤 모든 present가 호출 1회씩(calls 증가 present 3,318 = PS20 present − 304). PS20 밖 calls 0(on1·on2·off1·d1 전부). 호출 없는 304 present에서도 HD 100(정착 min 100)이라 화질 영향 없음 → 기준 해석 정정으로 PASS 처리(숨기지 않음).
- 안전: hresult 0·fallback 0·viewport_restore_failures 0·cache_clip_verify_failures 0·scale2x_palette_violations 0·dropped_count 0(on1·on2·off1), 두 lane `source_unchanged` true.
- **공개 비용**: PS20 present 간격(trace `ts_ms`) 켬 p50 18 / p95 22(on1)·23(on2) / p99 25·27 ms, 끔 14 / 17 / 22 ms → **+4 ms(p50)·+5~6 ms(p95)**(사전등록 +2 ms 초과 → 공개). 원인 추정(미측정): 매 present Lock 2회·480 KB before 복사·800×600 전체 타일 diff. 초당 약 55 present 유지, 브리핑은 정적 화면(입력 지연 영향 UNKNOWN). 최적화(변화 영역만 diff·Lock 1회) 후보는 backlog.
- `scenario_state_sequences_match`: 켬 2/2 true, 끔·거부 4/4 false(candidate 첫 상태 150 vs baseline 16 — lap1145 r1·r2, lap1147 m1·on1에서도 동일하게 false였던 기존 표본 차이, PS20 이후 `[20,1,3]` 동일). 이 값으로 인과를 주장하지 않는다.
- 캡처 열람(`on1/candidate/scenario_ps20_dwell.png`·`off1/...`): 초상화 3칸·본문 글자·버튼 모두 정상, 깨짐·이음새 없음, 켬은 초상화·배경이 Scale2x로 매끈(끔은 nearest 블록).

## 3. 판정

**H-SC2 `PASS(partial, 기술·격리)`**: PS20 브리핑 정착 HD min 89.43 → **100**(켬 2/2), <90 구간 7.1% → 0%, stale 50,735 → 0, 끔 재현, PS9/15/3 비회귀, 안전 0. 정적 귀속(`0x4D4620` 키 합성이 writer) 런타임 확인. partial 사유: 렌더러 잠금 그리기·GDI(`GetDC` 글자) 블록은 stale 0으로 별도 잔여 없음을 확인했으나 present 간격 +4~6 ms 비용, 합성 `0x41C362`(dest `[0x104FB2C]`) 경로 미측정, 시험판 DLL 재스테이징 미실행, 실제 Windows 미검증.

## 4. 검사

- `make lint`·`make typecheck`·C 빌드(mingw, 경고 0) 통과, `tests/test_g1_briefing_compose.py` 3 passed. 전체 `make check`는 기록 freeze 뒤 1회(결과는 STATUS 검증 줄).
- 로그 `logs/gates/lap1149-sc2-{on_a,on_b,d1,on1,on2,off1}.log`·`.exit`(on_b·d1은 chain 중단으로 exit 파일 일부 없음/비정형, 결과 JSON은 있음). 결과 JSON SHA 12자리: on1 `c5c426a8876f`·on2 `b33de7e90f4d`·off1 `37bdaa810d05`·d1 `8a8f183e1040`, 후보 trace on1 `4456ed0e9731`·on2 `27f20c832ec7`·off1 `d423dad385a5`·d1 `b972f55e2343`, on1 후보 DLL `29519743c515`.

## 5. 한계·위험

- 판정은 격리 Wine 2 lane 시나리오 제1장 브리핑 1종(체류 65초). 다른 장 브리핑(초상화 수·확대 애니메이션 `0x4D3960` 경로 `Blt KEYSRC`)은 같은 함수라 기대되나 미관측.
- 켬 비용(+4~6 ms)은 브리핑 화면에서만(상태 20 게이트). 인게임(PS3)·메뉴 경로에는 영향 0(PS3 present 간격 비교는 안 함 — 호출 0이라 기대 0).
- 되돌리기: env `SYW2_G1_BRIEFING_COMPOSE=0` 또는 `restore_hook` 경로(detach 테스트로 계약 고정, 동적 강제 rollback은 기존 wrapper와 같은 수준).

## 다음 행동

middle(Opus): raw 독립 재계산(새 스크립트로 on1/on2/off1 PS20 HD·calls·mask·간격) → `PASS(partial)` 수용 여부, +4~6 ms 비용 처리(수용/최적화 work), 재스테이징 묶음 판단(H-TM1·H-SC2 = 가시 수리 2건 누적). 사용자 G1 시험 결과가 오면 그것이 최우선.
