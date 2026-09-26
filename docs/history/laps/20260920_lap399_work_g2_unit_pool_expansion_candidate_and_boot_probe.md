# 2026-09-20 | lap 399 | 목표 G2 (전역 UnitStruct 풀 확장 실행 스파이크, W3)

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-sonnet-5` / high, 실무(work) 역할.
- 가설 / 사용자 관찰: W3(`docs/work/active/G2_UNIT_POOL_EXPANSION_SPIKE_LAP397.md`)를 재조사 없이 즉시 구현한다.
  §B-1~B-3에 따라 pool/existence/age 3영역 재배치 + 상수4개 + fixup을 적용한 실행 가능한 후보 EXE를
  만들고, 격리 실행으로 S-1(정상 구동)부터 확인한다.

## 신규 안전 발견 1 — 작업카드의 권고 N=1300은 안전하지 않다 (구현 착수 전 차단)

바이트 산술로 확인(재현 가능, 아래 명령):
`unit_pool` 새 끝(`base_preserving_storage_layout_v1.layout(n).regions[0].new_end`)이 N=1300에서
`0x008c0270`이며, 이는 B-3이 **명시적으로 건드리지 않기로 한** 세 지점의 원본 주소를 모두 넘어간다:
`unit_age`끝(`0x0089a388`, slot-환산 1217.36) / `category_slot_list_a` base(`0x0089b008`, 1219.06) /
`category_slot_list_b` base(`0x0089c2ca`, 1221.61)와 base+span(`0x0089d58c`, 1224.17). `existence`/`age`는
B-1이 재배치해 자리를 비우지만 `category_slot_list_a/b`와 FO-3의 WORD[1600] gap(`0x0089a388..0x0089b008`,
lap398)은 재배치 대상이 아니므로, N=1300이면 이 스파이크가 건드리지 않기로 선언한 영역을 pool의 성장
자체가 물리적으로 침범한다(S-6 위반 가능성). 재현:
```
python3 -c "from patches.population.base_preserving_storage_layout_v1 import layout; \
print(hex(layout(1300).regions[0].new_end))"  # 0x8c0270 > 0x89b008 (catA_base)
```
**대응:** 이 지점들을 넘지 않는 `N=1210`을 채택했다(안전 상한은 FO-3 gap 기준 `N<=1217`). 10칸만
증명하면 되는 스파이크의 목적(S-2 slot>=1200)에는 충분하다. 이 발견은 W3 §B-1의 "재배치 3영역만"
전제와 §B-3의 "active/catA/catB는 건드리지 않는다" 전제가 N=1300에서는 상호 모순임을 보인 것으로,
`docs/work/active/G2_UNIT_POOL_EXPANSION_SPIKE_LAP397.md`의 N=1300 권고를 대체(철회 아님, N 선택만 정정).

## 구현 — `patches/population/g2_unit_pool_expansion_v1.py` (신규)

- B-1: `base_preserving_storage_layout_v1.build_layout_artifact`(lap382-388 ACCEPT)를 그대로 위임.
- B-2: 4상수(`0x00442FAC/B1/D1`, `0x0044317D`) old bytes 원본과 바이트 단위 확인 후 교체.
- B-3: `.text` capstone 재스캔(핀 손전사 아님)으로 pool/existence/age 리터럴 사이트를 자체 수집,
  FO-4(`0x00421349`/`0x0048F4B4`)·B-2 4사이트 하드 제외, 나머지에 region별 균일 delta 적용.
  각 site는 명령 바이트 안에서 old_value의 4바이트 LE 인코딩이 **정확히 1회** 나타나는지 확인 후
  교체(모호하면 추측하지 않고 `BuildAbortedError`).
- 안전장치: 원본 SHA 확인 없이는 아무것도 안 함, N<1200 거부, 출력 길이 불변 확인, pool 사이트는
  "bucket 0"(필드 오프셋 < elem_size)이 아니면 중단(레지스터 dyanmic 슬롯 접근이 아닌 하드코딩
  슬롯 리터럴로 의심 → FO-4류 오탐 방지, 이번 실행에서 outlier **0건** 확인).

## 검증 (make check 범위, 게임 미실행)

- 신규 pytest 13건 전부 PASS: N=1200 항등(패치 결과가 원본과 **바이트 단위 완전 일치**, 최강 회귀
  앵커) / N=1210 길이·해시 안정 / FO-4·B-2 사이트 generic 스캔에서 제외됨 / N=1210에서 FO-4 두 사이트
  바이트 불변 / PE 구조 유효 / 원본 bytes 객체 비변형 / N<1200 거부.
- **독립 교차검증(신규):** 이 모듈이 자체 재스캔한 사이트 수가 **두 개의 별도 이전 probe**와 정확히
  일치한다 — pool disp **986**(lap397 A4)·pool imm 28(=30-FO4제외 2, W3 §B-3)·existence disp
  32/imm 2·age disp 2/imm 3(원시, 1건은 B-2와 중복이라 제외)(W3 §B-3, `tools/g2_unit_pool_xrefs_evidence.json`
  계보). 서로 다른 구현이 같은 수를 내어 카운트 결함 가능성을 크게 낮춘다.
- `make check` rc0 **728 passed** 199.87s(신규 13건 포함, 715→728)+Ruff/compileall/mypy10+`CONTEXT_PASS`,
  `checks/safety.sh check` **`SAFETY_PASS`**. 원본 `b56986e0…c9c08a8ac` 불변(읽기만).
- 후보 산출물: `/tmp/g2_unitpool_n1210_candidate.exe`, SHA256
  `303c78f81f816ed82e495fa4545cc23af3fa7200344eb029b4e9f31cabe96522`, 길이 1,032,192B(원본과 동일).

## 실행 시도 — S-1 부분 착수, BLOCKED (신규 안전 발견 2)

`tools/runtime_env.prepare()`로 격리 사본+전용 Wine prefix 생성(run_id
`20260920_012749_2958612_0`, `local/runtime/`, gitignore 대상). 후보를
`game/g2_unit_pool_n1210.exe`로 배치, `patches/population/runtime_driver.py`의
`SUPPORTED_EXECUTABLES`에 정확한 SHA256으로 신규 항목 등록(기존 `supply5000.exe` 패턴과 동일).
전용 Xvfb `:250`(기존 세션 미충돌 확인), `wine explorer` + `wine <exe>`로 기동, `state()`로
`PS`(WORD@`0x4ED818`) 폴링.

**관측:** 후보 EXE가 크래시 없이 로드되고 30초간 `PS=40`에서 **정지**(변화 없음, tick=0 유지).
원본 smoke 계약(`tools/runtime_env.py::smoke`)은 title-click 전 `PS==9` 도달을 기다리므로 이 상태는
"준비 완료"가 아니다.

**대조 실험(신규 안전 발견 2, 결정적):** 원본과 **바이트 단위 동일**한 EXE를 `control_renamed_original.exe`
로만 이름을 바꿔 동일 harness로 기동했더니 **동일하게 PS=40에서 20초+ 정지**했다. 즉 PS=40 정지는
**이 패치의 결함이 아니라 파일명 의존 동작**(가설: 게임이 자기 모듈 파일명을 확인하는 구식 복사방지/
등록 검사, 또는 `_inmm` 사설 registry가 특정 exe 이름을 기대)이다. 두 실행 모두 크래시 0, 메모리
읽기 정상(PlayerStruct 8명 필드 전부 0으로 정상 파싱), 종료 시 프로세스/디스플레이 잔류 0
(`stop` op으로 정상 종료, `ps -ef`/`/tmp/.X11-unix/X250` 확인).

**판정:** `S-1` **BLOCKED**(패치 검증 불가가 아니라, 파일명 제약이라는 **새 필요 입력**이 드러남).
패치 자체가 원인이 아님을 대조군으로 분리했으므로 이 발견은 `NOT_FEASIBLE` 근거가 **아니다** —
다음 회차가 원래 파일명 `syw2plus_original.exe`로 후보를 배치하고 실행하면(원본 파일명 유지, SHA만
다름) S-1을 재시도할 수 있다. `runtime_driver.SUPPORTED_EXECUTABLES`는 파일명이 키이므로, 원래
파일명으로 후보를 등록하려면 그 딕셔너리 구조를 "파일명→기대SHA 1개" 대신 "파일명→허용SHA 집합"으로
바꾸거나, `syw2plus_original.exe`를 다른 파일명으로 두고 후보만 그 이름을 쓰는 실행 스크립트를 새로
만들어야 한다(둘 다 이 세션 예산 밖, 다음 회차로 넘김).

원시 로그: `local/runtime/20260920_012749_2958612_0/driver_out/`(control run의 `wine.log`/
`trace.jsonl`/`session.json`/`exit.json` 보존; 후보 run은 동일 출력 디렉터리를 재사용해 로그가
control run으로 덮였다 — **provenance 사각**으로 기록. 후보 run의 관측은 이 lap 기록 본문의 폴링
로그(대화 turn, t+5s~t+30s 전부 `ps=40`)로만 보존됨, 파일 산출물 아님).

## 변경 파일

- 신규: `patches/population/g2_unit_pool_expansion_v1.py`,
  `patches/population/test_g2_unit_pool_expansion_v1.py`.
- 수정: `patches/population/runtime_driver.py`(`SUPPORTED_EXECUTABLES`에 2항목 추가:
  `g2_unit_pool_n1210.exe`, `control_renamed_original.exe`).
- 커밋 없음(`LOOP_ALLOW_COMMITS` 미설정, uncommitted로 보존).

## 원본 SHA / 후보 SHA / 환경

- 원본 `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`(읽기만, 불변 확인).
- 후보(N=1210) `303c78f81f816ed82e495fa4545cc23af3fa7200344eb029b4e9f31cabe96522`.
- 격리 사본/전용 prefix: `local/runtime/20260920_012749_2958612_0/`(git 제외).
- fixture: save000 미사용(이번 회차는 부팅까지만; save 로드 전 단계에서 BLOCKED).

## 측정값 / 판정

- 패처 정확성(정적): PASS(항등 회귀 + 2건 독립 카운트 교차검증 + FO-4/B-2 제외 검증).
- N=1300 안전성: **FAIL**(대체 N=1210 채택, 근거 위 §1).
- S-1(정상 구동 후 save 로드): **BLOCKED**(파일명 의존, 패치 결함 아님 — 대조군으로 분리).
- S-2~S-6: 미착수(선행 조건 S-1 미충족).

## 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태

- 이 lap의 정적 결론(N=1300 위험, 패처 카운트, 패치 자체는 PS=40 원인이 아님)은 **다음 새 middle
  세션(Opus5/high)의 독립 검수 대기**. work는 자기 결과를 최종 승인하지 않는다.
- `loop/ESCALATE_SOL` §9의 F4(전비 5000 16-bit 랩) 판정은 **여전히 열려 있음**(우선순위 변경으로
  후순위 유지, 철회 아님) — 이 lap은 그것과 무관한 독립 트랙.
- lap385/388 저장포맷 통합 blocker, lap389 owner-transfer NO_GO는 이 lap이 건드리지 않음(그대로 유지).
- 사용자 마일스톤 승인 대상 아님(임의 PASS로 바꾸지 않음).

## 다음 한 가지

**파일명 제약을 해소하고 S-1을 재시도한다.** 구체적으로: (a) `runtime_driver.SUPPORTED_EXECUTABLES`를
파일명당 다중 허용 SHA로 확장하거나, 후보를 정확히 `syw2plus_original.exe`라는 이름으로 배치하는 새
격리 실행 경로를 만들고(원본은 별도 이름으로 보존해 안전하게 구분), (b) PS==9 도달까지 대기 후
`G1_R1_CLICK_POINT`/`G1_S1_LOAD_BUTTON_POINT`(1600×1200 좌표계이므로 1024×768 스톡 해상도용
`(184,560)` 조합과의 정합을 먼저 확인) 클릭으로 save000을 로드해 PS3 도달(S-1)을 확인한다.
(c) S-1 PASS 후 `layout(1210).regions[1].new_start`(새 existence base)를 이용해 slot 1200~1209의
existence/age/pool 슬롯을 직접 read로 관측(S-2), 이후 S-4/S-5(사망/재사용)를 자연 시뮬레이션 또는
직접 개체 생성 트리거로 확인한다. 실패 가설은 이번 회차로 1회 소진(파일명 가설, 대조군으로 확정됨) —
다음 회차는 재조사 없이 (a)를 바로 구현한다.
