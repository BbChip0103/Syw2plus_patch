# 2026-10-09 | lap 1209 | G1 middle — H-TR15 검수 · H-SIG0(기존 서명 stale 쌍봉 위치·writer 귀속) 사전등록

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5-5` / high / 중간 계획·컨펌(middle). 게임 run 0·source 변경 0·커밋 0.
- 입력: `loop/ESCALATE_SOL`(lap1208 work → middle). 원문 byte 일치 보존 `docs/history/laps/20261009_lap1209_preserved_lap1208_escalate_sol.txt` SHA256 `098e3d247875a046ae4ac42c001da9cef5c56163f8ac6984e322a25a31e9cf89`, 보존 뒤 삭제.
- 원본 SHA: EXE `[ESL]Syw2plus/[HQ]Syw2plus 2002.exe` `b56986e0…08a8ac` MATCH(읽기만). 환경 `.venv/bin/python -I`. fixture 없음. 사용자 업스케일 결과: 아직 없음(INBOX 14:10 이후 새 항목 0).

## 1. 가설(검수)

lap1208 H-TR15 수치가 독립 재현된다: 새 summary 경우가 현재 소스에서 GREEN, 변이 i15에서 RED이고, C 제품 소스는 그대로다.

## 2. 독립 재계산

새 스크립트 `temp/Syw2plus_patch/20261009_lap1209_middle_review/recalc_lap1209.py`. 이 스크립트는 저장소 파일을 읽기만 한다. lap1208은 변이를 저장소 안에서 직접 수정했다가 되돌렸지만, 이 스크립트는 메모리에서 변이를 만들어 임시 디렉터리에서 빌드한다. `_OVERFLOW_FIXTURE`는 테스트 모듈을 import하지 않고 `ast`로 꺼냈다. 결과 `recalc_lap1209.json` SHA256 `b9810e6ddea751317e93032a1eb66b799907398c79eacbcf905990d7397ac501`.

| 변이 | 내용 | 결과 |
|---|---|---|
| original | 현재 소스 | GREEN |
| i15 | 578줄 `< TRACE_MAX_EVENTS` → `< TRACE_MAX_EVENTS - TRACE_RESERVED_EVENTS` | **RED**(새 summary 단언, fixture 85줄) |
| swap_names | serialize/event_limit 이름 교환 | RED(기존 단언) |
| no_summary_exempt | summary 상한 면제 제거 | RED(새 단언) |
| overflow_guard_minus2 | `trace_overflow` 보호 `MAX−1` → `MAX−2` | RED(기존 단언) |
| le_max | `<` → `<=` | GREEN(동등) |
| lt_max_minus_1 | `< MAX − 1` | GREEN(동등) |

- 생존 2개는 테스트 공백이 아니라 **동등 변이**다. `trace_overflow`는 `g_event_count >= MAX−1`이면 마커를 내지 않고 반환한다. 그래서 MAX−1과 MAX에서는 scope 이름이 관측되지 않는다. 이름이 관측되는 마지막 경계는 MAX−2이고, 이번 경우가 바로 그 경계를 고정한다. lap1208 기록 "MAX−1은 별도 단언 안 함"과도 맞는다.
- C SHA `27c8ee22…` 실행 전후 동일. 테스트 파일 SHA `d6370d70…`는 lap1208 기록과 일치한다.
- 게이트 대조: `logs/gates/lap1208-work-full-check.log` SHA256 `580a1e999ab7…` 일치, `2042 passed, 5 skipped in 811.79s`, `.exit` 0, lint·typecheck·CONTEXT_PASS. `lap1208-work-safety.log` `605d29f0…` = `SAFETY_PASS`·`exit=0`. 통과 수 2042가 lap1200과 같은 것은 정상이다. 새 테스트 함수를 만들지 않고 기존 함수의 fixture에 단언만 더했기 때문이다.
- focused 재실행: `tests/test_g1_presentation_trace.py` 19 passed/15.81s.

## 3. 판정

**H-TR15 `PASS(partial, 기술·호스트)` 수용.** T15-1·T15-2·T15-3 모두 PASS다. 판정에 영향을 주는 불일치 0, 정정 0, 보강 2(동등 변이 2개를 근거로 설명함, 저장소 밖 변이 재현). 실게임 증거는 아니다. backlog lap1201 i15는 닫는다.

## 4. 진행 규칙 판정(③ 연속 무증거 회차)

lap1207 middle(문서), lap1208 work(테스트 단언), 이번 lap1209 middle(문서)은 모두 제품 코드·실게임 증거가 늘지 않은 회차다. middle은 컨펌 역할로서 G1을 계속하기로 판정한다. 근거는 두 가지다. G1은 사용자 최우선이고, 사용자 업스케일 결과 대기는 비차단이다. 다만 **다음 work는 반드시 실게임 증거를 내야 한다.** 게임 run 0 backlog(`key_wrap_mismatches`, `mirror_blend_clip` 검사 순서)는 이번에는 고르지 않는다.

## 5. 다음 work 사전등록 — H-SIG0: 기존 서명 stale 쌍봉 위치·writer 귀속

**배경:** 사용자에게 보일 수 있는 일시 stale 결함이다. PS3 약 13.1 s와 약 14.9~15.5 s에 240~277 px 쌍봉이 나오고, 그 뒤에 ≤100 px 꼬리가 붙는다. 약 1/3 run에서 나온다. 키 경로가 없던 DLL(lap1192 T0)에도 있었으므로 키 경로보다 앞선 문제다. 관측 run은 lap1192 X2 255·T0 259, lap1194 Y3 245/242, lap1196 P0 277, lap1187 "15.5 s 선택 군집"(18~305)이다. 이 결함은 지금까지 측정식에서 **제외만 해 왔고** 위치·writer는 UNKNOWN이다(lap1187 §4, lap1195 §5, lap1197 (a)).

**가설:** 이 쌍봉은 `--new-game-act`의 선택·드래그 시점에 미러가 따라가지 못한 화면 writer가 1~수 present 동안 남긴 stale이다. 위치를 확정하면 기존 hook(`0x4662DE`·`0x467CCF`·wined3d 스레드 등)으로 귀속되는지, 아니면 새 미후킹 writer인지 가릴 수 있다.

**구성:** 현재 트리 DLL, 기본 env(팩 끔, `SYW2_G1_HD_PACK` 미설정). 명령은 lap1194 F0 구성과 같다: `PYTHONPATH=. .venv/bin/python tools/g1_saved_scene_probe.py --runtime-root local/runtime/lap<N>_sig0_<label> --artifact-root <공유 temp>/run_<label> --hd-source scale2x --new-game-path --new-game-start --new-game-act --new-game-play --new-game-play-keys RIGHT,DOWN,LEFT,UP,RIGHT,DOWN,LEFT,UP --new-game-play-hold 20 --new-game-play-dwell 56`. 템플릿은 `temp/Syw2plus_patch/20261009_lap1194_work_hdb2/scripts/run.sh`(팩 인자 `-`)다. 하네스 검사상 `--stale-mask`에는 `--hd-source scale2x`가 필요하고 `--census-only`와 함께 쓸 수 없다(`g1_saved_scene_probe.py` 7024줄). 격리 game 사본·prefix·빈 Xvfb를 쓴다. run이 끝날 때마다 `game` 사본만 지운다.

| 단계 | 할 일 | PASS 조건 |
|---|---|---|
| SIG-0 위치 | 위 명령에 `--stale-mask 250-313`을 더한다(PS3 ordinal 64개 = dump 상한). middle이 lap1194 Y3 raw(`run_Y3/candidate/trace_raw.jsonl`, `mirror2x_present` program_state 3, 0-based)로 이 창을 확인했다: ord 262(13.08 s) 245·ord 299(14.93 s) 242·ord 304~306(15.18~15.27 s) 79/75/18이 모두 창 안에 있다(스크립트 `20261009_lap1209_middle_review/ordinal_check.py`). 각 run의 trace로 대응을 다시 확인하고, 창이 어긋나면 다음 run에서 범위를 고친다(기록). 최대 6 run을 돌리고, 서명 run(12.5~16 s에 `stale_pixels` ≥150 present가 있는 run)이 2개 나오면 멈춘다. 측정식은 `mirror2x_present`의 `stale_pixels`(PS3 present, 1 s 간격 군집)이다. | 서명 run ≥1, 그 present들의 stale mask에서 stale 픽셀 연결 성분의 bounding rect(800×600 좌표)·면적 합이 metrics stale 값과 일치, 화면 영역(지도·하단 패널·미니맵·커서·선택 상자 등) 분류 |
| SIG-1 귀속 | SIG-0에서 가장 큰 성분 안의 3점을 `--layer-drift --screen-watch --drift-samples X,Y;X,Y;X,Y`로 같은 명령에 건다. 최대 6 run, 서명 run 1개가 나오면 멈춘다. | 서명 present에서 표본점 쓰기 hit ≥1. EIP·스레드를 기존 hook 또는 새 함수(objdump 호출처)에 귀속 |
| SIG-2 정리 | 새 스크립트로 raw 재계산, 캡처 열람 | 수치 일치, 안전 7종 0, 원본 SHA 불변 |

**결론 규칙(③ 60분 / 실패 가설 2회):**
- 6 run에서 서명 0 → `NOT_REPRODUCED`(빈도 상한을 기록하고 backlog는 유지, 추가 run 금지).
- 서명 run이 있으나 mask 창이 어긋남 → 하네스 ordinal 대응을 수리하고 재실행. 이것은 추적 가능한 하네스 결함이므로 반복한다.
- SIG-1에서 hit 0 → writer UNKNOWN과 그 근거를 기록한다(표본점이 성분 밖이었는지, 쓰기 없이 생긴 stale = cover 쪽 위상인지).
- 제품 C 수리는 하지 않는다. 귀속 결과를 보고 다음 middle이 수리(H-SIG1)를 사전등록한다.

**하지 않는 것:** 제품 C 변경, 팩 켬, 시험판·사용자 전달, G2~G5 접촉. 하네스를 고치면 테스트 RED→GREEN과 `make check` 1회를 함께 한다. 하네스 변경이 0이면 focused 테스트와 SAFETY만 한다. 장기 run은 세션이 끝까지 기다린다(PROMPT ③ 장기 실행 규칙).

**우선순위 예외:** 사용자 업스케일 결과나 G1 시험 결과가 INBOX에 오면 그것이 최우선이다(H-HDU3는 middle이 사전등록).

## 6. 검증

- 이번 회차 변경: 문서(STATUS·INBOX 메모·이 기록·ESCALATE_SOL 보존본·STATUS 압축 원문)와 공유 temp 재계산 스크립트뿐이다. 전체 `make check` SKIP(source는 lap1208 full PASS 2042 그대로). focused·SAFETY 결과는 STATUS에 보강한다.
- STATUS 압축: 압축 전 전문 130줄·SHA256 `09a907b2d5db142511aa85b54de19a6bba1acd154d0d9694276f20332926d6b5` → `docs/history/20261009_status_lap1209_precompaction.md` byte-exact.

## 7. 다음 한 가지

work H-SIG0(§5). 사용자 업스케일·G1 시험 결과가 오면 그것이 최우선이다.
