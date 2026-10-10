# 2026-10-09 | lap 1201 | G1 middle — H-HDB5 검수 · 효과 갈래 마감 · H-HDA0(전체 팩 동시 실게임) 사전등록

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5-5` / high / 중간 계획·컨펌(middle). 게임 run 0·C/tools/tests 변경 0·커밋 0.
- 입력: lap1200 work `loop/ESCALATE_SOL`(원문 byte 일치 보존 `docs/history/laps/20261009_lap1201_preserved_lap1200_escalate_sol.txt` `fa029cfd04d25677`, 보존 뒤 삭제). `loop/STOP` 없음. INBOX·APPROVALS에 새 지시·반려·사용자 G1 시험 결과 없음. `loop/.lap_counter` = 1201.
- 가설: lap1200의 새 테스트 6개는 lap1199 생존 변이 4개만 잡는 좁은 테스트가 아니라, 같은 함수의 다른 변형에도 민감하다. `trace_event`의 `serialize` 분기는 판정·검증기 의미를 바꾸지 않는다.
- 측정식(사전 기록): 독립 변이(work와 다른 형태) RED 비율, 생존 변이는 동등/공백 분류, 검증기의 overflow 소비 방식, focused GREEN, SAFETY_PASS, 원본 SHA.

## 1. source 동일성

lap1200 기록의 파일 SHA256 앞 16자 4개(`direct_draw_trace.c 27c8ee2289a4b115`·`test_g1_blend_key.py 282a6063c6c3c278`·`test_g1_hd_pack.py 69b106639af03c5e`·`test_g1_presentation_trace.py a40c6b6255026784`)를 현재 트리에서 재계산했고 4/4 일치한다. lap1200 `make check` 뒤로 source 변경 0이다.

## 2. C 한 줄 검토(ESCALATE 작업 2)

`trace_event`(`direct_draw_trace.c` 562~581): 상한 분기(`g_event_count ≥ MAX − RESERVED`, summary 제외)는 그대로 `event_limit`이다. `trace_event_raw` 실패 분기는 `g_event_count < MAX`이면 `serialize`, 아니면 `event_limit`이다.
- **도달 범위:** summary가 아닌 이벤트는 상한 분기를 통과해야 raw에 오므로 항상 `g_event_count < MAX − 2`다. 따라서 raw 실패는 개수 상한 때문일 수 없고 `serialize`가 맞다. `else` 분기는 summary가 `g_event_count ≥ MAX`일 때만 가는데, 이때 `trace_overflow`는 `g_event_count ≥ MAX − 1`이면 아무것도 쓰지 않는다. 그래서 출력상 죽은 분기다(무해).
- **비활성·쓰기 실패 포함(공개 3):** `g_trace_enabled == 0`이면 overflow 줄도 못 쓴다(출력 0, 카운터만 증가 — 변경 전과 같다). `WriteFile` 실패는 "상한 아래에서 기록 실패"이므로 `serialize`로 불러도 된다. 이 이름은 "상한 아닌 실패"를 뜻한다는 해석을 수용한다.
- **2회 방출 제한(공개 4):** 변경 전에는 직렬화 실패도 `event_limit`이라는 잘못된 이름으로 같은 2칸을 썼다. 그래서 칸 소비는 같고 이름만 바로잡혔다. 퇴행이 아니다.
- **소비자:** `tools/check_g1_presentation_trace.py` 131·158줄은 `event == "overflow"`면 scope와 관계없이 오류다. `scope` 값을 읽는 python 소비자는 없다(`grep`, `g5_selection_upstream_trace.py`의 `event_limit`는 자기 summary 필드). → **판정·검증기 영향 0.**

## 3. 독립 변이(ESCALATE 작업 1) — 공유 temp `20261009_lap1201_middle_review/mutation_lap1201.py`(`69a13c92b4123b7f`)·`mutation_lap1201.json`(`1ef851549923068f`)

`/tmp` 사본(`tools`·`tests` 복사, `checks`·`docs`·`analysis`·`patches` 링크)에서 실행했고 저장소는 바꾸지 않았다. base focused 4파일 184 passed. 첫 실행 base 1 FAIL은 사본에 `analysis/` 링크가 빠진 탓이었다(`test_p4b_cache_layer_hooks…`가 `analysis/memory_maps/…lap863.md`를 읽음). 링크를 넣어 전체를 재실행했다. 저장소 자체는 같은 4파일 184 passed다.

| id | 변이(work와 다른 형태) | 대상 | 결과 |
|---|---|---|---|
| i01 | digest 비교를 tinted writer에서만 무시 | B5-1 | RED |
| i02 | remap 혼합 writer에서만 무시 | B5-1 | RED |
| i03 | `0x468360`에서만 무시(루프 마지막 writer) | B5-1 | RED |
| i04 | `0x466540`에서만 무시 | B5-1 | RED |
| i06 | level `(int16_t)`→`(int32_t)` | B5-3 | RED |
| i07 | level `(uint16_t)` | B5-3 | RED |
| i08 | digest 255 B | B5-3 | RED |
| i09 | 읽기 불가 표도 remap 유지 | B5-3 | RED |
| i11 | 함수 본문 끝에 `if (level==7) level=2` 추가 | B5-3 | RED |
| i12 | raw 실패 분기를 조건 없이 `serialize` | B5-5 | B5-5 생존 → 기존 순서 계약 테스트 2개 RED(`test_production_trace_writer_uses_bounded_serializer_and_exact_write`·`…rejects_failure_order_mutations`). 동작은 §2대로 동등 |
| i13 | 상한 분기를 `serialize`로 | B5-5 | RED |
| i14 | raw 실패에서 `++g_dropped_count` 제거 | B5-5 | RED |
| i15 | `serialize` 기준을 `< MAX − RESERVED`로 | B5-5 | **생존(focused 184 GREEN)** |
| i17 | clip7 `mirrored_calls`↔`mirrored_pixels` 접근자 교환(같은 writer 안) | B5-4 | RED |
| i18 | clip7 필드가 flip7 `key_level_rejects` 접근자 읽음 | B5-4 | RED |

- **RED 14/15**(i12 포함). B5-1은 4 writer를 각각 따로 구분한다(i03·i04: 한 writer만 망가뜨려도 RED). B5-3·B5-5의 소스 본문 추출은 본문 끝 줄 추가(i11)·형 변환 한 글자(i06·i07)에도 민감하다(공개 1 확인: 추출 실패는 RED 방향).
- **i15 생존 = 경미한 테스트 공백:** summary 이벤트가 `g_event_count == MAX − 2`일 때 직렬화에 실패한 경우에만 이름이 `event_limit`로 바뀐다(`MAX − 1` 이상이면 marker 자체가 안 나간다). 진단 이름 1칸 차이이고 판정 영향은 0이다. → backlog(경미)로 두고 이번 수리 대상은 아니다.
- work 재현(lap1200 `mutation_lap1199_rerun.txt`: RED 15·동등 4 / `mutation_lap1198_rerun.txt` 28/28)은 파일을 열람해 확인했다. 독립 변이가 같은 함수들을 더 넓게 덮으므로 재실행은 생략했다.

## 4. 판정

**H-HDB5 `PASS(partial, 기술·격리)` 수용.** 집계: 판정 영향 불일치 0 · 정정 0 · 새 경미 공백 1(i15). 제품 결함 0. 기본 켬·사용자 전달 아님.

**효과 갈래 마감(ESCALATE 작업 3):** lap1199 §6 판정을 유지한다. `0x467410`·`0x467E60`(level 0 무클립, 정상 속도 화면 안 관측 거의 없음)은 **명시 잔여(Scale2x 화질, diff 미러로 정확성 유지)**로 둔다. 효과(반투명) writer 9개(키 경로 7개 `0x4672E0`·`0x467580`·`0x467B00`·`0x467FD0`·`0x4685C0`·`0x4678C0`·`0x468360` + 잔여 2개) 갈래는 **마감**한다. 새로 관측되면 재개한다. 이것은 INBOX 19:3x 지시 안의 하위 갈래 마감이고, 사용자 마일스톤 경계는 아니다.

## 5. 다음 work 사전등록(Sonnet) — H-HDA0: 전체 팩 동시 실게임 확인 1회

**왜:** 지금까지 각 갈래는 자기 팩만 넣고 측정했다(`pack_hdf1` 909 MB·25,637파일 / 로고 `pack_logo` / 효과 `pack_hdb4` 413). 또 `pack_hdf1`의 imjin2 디렉터리(`cecc4681/`)는 lap1192 확장 이름 **이전**에 만들어졌다. 그래서 `.amb` 마커가 0이고, 충돌 이름 674개도 기본 이름 파일로 들어 있다. C는 기본 이름이 있으면 확장 이름을 보지 않는다. 그래서 이 팩을 그대로 합치면 충돌 프레임에 엉뚱한 그림이 쓰일 수 있다. 기본 켬·사용자 전달 전에 "모든 팩을 한 디렉터리로, 현재 도구 규약으로" 실게임 1회가 필요하다.

- **A-0(오프라인, 팩 구성):** 현재 `tools/g1_hd_convert.py`로 imjin2 계열 팩을 다시 만든다. 순서는 `extract`(fnt·char·지형 `.ytl` 디렉터리, lap1169·lap1167 방식) → 가장자리 복제 바이큐빅 stand-in → `convert` → `pack`이다. 여기에 효과 초안(lap1194·1198 `fnt/*`·`char/cannon2c*`)과 로고(`logo`, lap1188)를 같은 `cecc4681/`에 넣는다. 타이틀 계열 디렉터리 `296963d9/`·`84428eed/`·`e24d0e6d/`는 `pack_hdf1`에서 하드링크한다. 합격 조건: (a) 도구 `check` 위반 0, (b) **충돌 674 이름에 기본 이름 파일 0개**, `.amb` 마커와 확장 이름 존재, 남은 3(`char/bullk*`)은 공개, (c) 같은 경로에 다른 바이트가 오는 합치기 충돌 0(있으면 목록과 선택 규칙 공개). 산출물은 공유 temp `20261009_lap1202_work_hda0/pack_all/`에 두고, 파일 수·크기·manifest SHA를 기록한다.
- **A-1(실게임, 켬):** 같은 DLL(현재 트리 빌드)과 `SYW2_G1_HD_PACK=pack_all`로 (1) NG5 장기 스크롤(`--new-game-path --new-game-start --new-game-act --new-game-play --new-game-play-keys RIGHT,DOWN,LEFT,UP,RIGHT,DOWN,LEFT,UP --new-game-play-hold 20 --new-game-play-dwell 56`)과 (2) save006 pair를 각 1회 돌린다. 키 로그·trace를 켠다.
- **측정식(합격):** 안전 7종 0, 크래시 0, writer별 자기 검사 불일치 0(blend·shade·tinted·flip), `hd_pack_*_rejects`가 늘지 않음(개별 갈래 run 대비), `hd_pack_ext_hits` > 0이고 충돌 이름 키가 기본 이름 파일로 hit한 건 0, PS3 p95 ≤ 개별 갈래 최대 + 2 ms, identity cache 바이트 ≤ 128 MiB 한도(축출 정상), trace overflow 0(있으면 scope 공개), save006 pair = 기존 판정과 같음(W-1 gate·입력 효과·minimap parity). PS9·PS5·PS7 fullscreen hit = present 수(pal miss 0).
- **실패·중단:** 실패 가설 2회 또는 60분이면 멈춘다. 디스크는 run 전에 확인하고 **여유 7 GB 미만이면 시작하지 않는다**(팩 재생성 ~1~2 GB + game 사본 2.7 GB). 8 GB 미만이 되면 root 대상 ESCALATE_SOL로 확보를 요청한다. run 끝나면 game 사본은 삭제하고, 중간 추출물(`extract` 1배·바이큐빅 RGB)은 manifest·SHA 기록 뒤 지워도 된다(`pack_all`은 보존). 팩 합치기에서 실제 결함(잘못된 이름 hit 등)이 나오면 수리하지 말고 근거를 남긴 뒤 ESCALATE_SOL로 보낸다.
- **비목표:** 실제 업스케일 화질 평가(stand-in이다), `0x467410`·`0x467E60`, 기본 켬 전환, 사용자 전달.
- **그다음(middle 판단):** H-HDA0을 수용하면 HD 그림 경로 도구·엔진이 "사용자 업스케일러 결과를 받을 준비"가 된다. 사용자 시험판 재스테이징이나 업스케일러 실험 요청을 할지는 마일스톤 경계이므로 그 middle이 root 전달(ESCALATE_SOL)로 판단한다. stand-in 팩만으로는 사용자에게 보이는 화질 이득이 없다는 점을 함께 적는다.

## 6. 검사

- `checks/safety.sh check` **SAFETY_PASS**(로그 `logs/gates/lap1201-middle-safety.log` `605d29f0d0580010`, exit 줄 포함).
- focused 6파일(`test_g1_blend_key`·`hd_pack`·`hd_convert`·`mirror2x`·`rect_fill`·`presentation_trace`) **263 passed/30.85s**(로그 `logs/gates/lap1201-middle-focused.log` `a5bb3d17a1d9cdf3`). lap1200 work 수치와 같다.
- 전체 `make check`는 SKIP했다. 이번 회차는 문서와 공유 temp 스크립트만 바꿨고, source는 lap1200 full PASS(2042 passed) 그대로다.
- 원본 EXE `[ESL]Syw2plus/[HQ]Syw2plus 2002.exe` SHA256 `b56986e0…08a8ac` MATCH. 디스크 여유 11 GB.

## 다음 행동

work(Sonnet)가 H-HDA0(§5)을 진행한다. 사용자 G1 시험 결과가 오면 그것이 최우선이다.
