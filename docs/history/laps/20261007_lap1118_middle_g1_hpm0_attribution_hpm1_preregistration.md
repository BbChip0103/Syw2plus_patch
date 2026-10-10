# 2026-10-07 | lap1118 | G1 middle — H-PM0 FAIL 독립 재계산·귀속 + H-PM1(PS23 전환 writer census) 사전등록

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5-5`, high / middle(진단·계획·확인) 1 lap. 게임 실행 0, 제품 source·하네스·테스트 변경 0, 커밋 0.
- 입력: `loop/ESCALATE_SOL`(lap1117 work → middle 귀속 요청), STATUS 다음 한 가지, lap1117 기록, lap1116 사전등록 §7. INBOX 새 사용자 지시 없음, APPROVALS 새 반려 없음(G1 사용자 시험 lap1104 대기), `loop/STOP` 없음.
- ESCALATE_SOL 처리: 원문을 `docs/history/laps/20261007_lap1118_preserved_lap1117_escalate_sol.txt`로 byte 일치 보존(SHA256 `475d29319bb2bdea…`, `cmp` 일치)한 뒤 삭제했다.
- 원본 SHA: `[ESL]Syw2plus/[HQ]Syw2plus 2002.exe` `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac` 직접 재계산 MATCH(읽기만). 하네스 SHA `0dc53744…`는 lap1117 기록과 같다.
- fixture: lap1117 raw만 사용(새 게임 실행 없음). 새 게임 경로 PS9→PS7→PS5→PS3→Esc PS23, save 쓰기 없음.

## 1. 독립 재계산 (새 스크립트)

- 스크립트: 공유 temp `20261007_lap1118_middle_review/recalc_lap1118.py`(`ff8ca01c…`) → `recalc_lap1118.json`(`fe93ff7d…`), 캡처 비교 `capdiff.py`(`3943f6a9…`). trace SHA a `db2cad27…`·b `48dc9451…`(lap1117 기록과 일치).
- PS23 전환 present(전 present 대비):

| run | 저장 창 열림 | 저장 창 닫힘(복귀) | 다음 present | 정착 PS23 |
|---|---|---|---|---|
| a | seq 3641 stale 51,628·partial 0 | seq 5358 stale 95,366·partial 0·layer transfer 0·menu 0·frame 0 | 5359 covered 384,326→435,652(메뉴 패널 copy 53,320 중 51,326 재덮음) | 1,288 present HD 90.74~90.76% |
| b | seq 4865 stale 51,636·partial 0 | seq 6601 stale 95,336·같은 계수 0 | 6602 covered 384,537→435,868(51,331 재덮음) | 1,307 present HD 90.78~90.81% |

- **산술:** 손실 = 복귀 stale − 다음 present 재덮음 = 95,366 − 51,326 = **44,040**(b 95,336 − 51,331 = **44,005**). work 수치와 같다. PS3 복귀 뒤 a 217·b 218 present 전부 covered 480,000·HD 100%.
- present별 partial copy 크기: 메뉴 창 53,320 px(= 172×310), 저장 창 99,200 px(= 320×310), 둘 다 present당 1회(`0x466280` packed block → `transfer_block_copy_to_screen`).
- 정착 PS23 동안 stale 0인데 covered가 줄어든 이유(코드 확인): present가 `covered && expected != pixel`이면 stale로 세고 그 픽셀의 `g_covered`를 0으로 지운다(`g1_mirror2x.c` 1820~1831). 일시정지 중에는 월드 primitive가 다시 불리지 않으므로(PS23 present당 bbox 9/4·terrain 계수 0) 지워진 픽셀을 다시 덮을 writer가 없다. 그래서 stale 0·covered 감소로 고정된다(나머지는 nearest 2×로 표시).

## 2. 위치 확정

- 캡처 `pause.png` 대 `pause_return.png` 차이(같은 정지 장면, 다른 점은 HD 여부·커서): 논리 x240..313·x464..559(b 464..571) × y100..409. x464..485(b ~571)는 돌아가기 버튼 위 커서 위치 차이다. 차이 블록 중 `pause_return`이 2×2 균일(nearest)인 비율 a 96.2%·b 96.0%, `pause`는 6.3%·6.7% → 그 띠가 nearest 폴백이다.
- 크롭 열람: 메뉴 패널 HD x≈630..970·y≈200..815 → 논리 약 x314..485 × y100..409(172×310), 저장 창 논리 x240..559 × y100..409(320×310).
- **결론:** 빠진 영역 = 저장 창 사각형 − 메뉴 패널 = 좌우 두 띠 x240..313·x486..559 × y100..409(74×310×2 = 45,880). 손실 44,040과의 차 1,840은 저장 창 픽셀과 복원된 월드 픽셀 값이 우연히 같아 stale이 아니었던 픽셀이다(그 픽셀은 저장 창 HD가 남는 경미한 화질 차이, 판정 영향 없음).

## 3. 귀속 — 가설 1개

**H-PM1:** PS23 안 하위 화면 전환(메뉴↔저장 창) 첫 present에서 게임이 사각형 전체(저장 창 열림: 새 패널, 닫힘: 띠의 월드 배경 복원 + 메뉴 패널)를 **미러 경로 밖의 writer**로 다시 쓴다. 근거: 두 전환 present 모두 `partial_copy`·`layer_transfer`·`menu_copy`·`frame_copy` 증가 0, bbox +1뿐, 그 present에서 stale이 사각형 크기만큼 난다. 다음 present부터 per-present `0x466280` panel copy가 패널만 다시 덮고, 배경 띠는 다시 그려지지 않는다.
- writer 정체는 이 raw로 정할 수 없다(trace에 전환 writer 계수 없음). 후보(정적 확인 없음, census로 가른다): (i) 화면→버퍼 저장(save-under) 뒤 버퍼→화면 복원 복사(미후킹 함수), (ii) `0x466280`이 `transfer_block_copy_to_screen`의 **계수 없는 조기 return**(target==cache/panel bound·stride·`readable_bytes`)으로 빠진 경우, (iii) 기타 BltFast/memcpy.
- 부수 관찰(귀속 의무 없음, backlog): 저장 버튼·계속하기 클릭 직전 stale 308/309·101 px 1회와 그 뒤 covered −308/−101 고정 = 클릭 위치로 옮긴 소프트웨어 커서 영역으로 보인다(위치 미확정).

## 4. 판정

- **H-PM0 `FAIL(귀속)` 수용**, 원인 = 전환 프레임 미러 밖 writer + 일시정지 중 월드 재그림 부재로 인한 영구 coverage 감소(사용자 체감: 저장 창 닫은 뒤 메뉴 좌우 띠가 nearest 2× 화질, 겉모습·비율·위치 정상). 불일치 0. 제품 C 변경 없음 → G1 후보 DLL은 lap1106 H-P35 트리 그대로. 정정 0.
- 수리 가능성: writer가 정해지면 FEASIBLE로 본다(기존 H-B4/H-L/H-A diff·block 미러 방식). 지금은 writer 미확정이라 수리 사양을 쓰지 않고 census를 먼저 한다.

## 5. 다음 work 사전등록(Sonnet) — H-PM1: PS23 전환 writer census

- **PM1-0 진단 게이트(TDD, 진단 전용):** `g1_screen_watch.c`의 `g1_screen_watch_on_present`는 `program_state != 3`이면 바로 return한다(363줄) → PS23에서 무장·present 번호 갱신이 없다. 옵트인 env `SYW2_G1_SCREEN_WATCH_STATE`(값 `3` 또는 `23`, 없으면 3 = 현행 동작 불변)를 추가하고 하네스 `--screen-watch-state {3,23}`(`--screen-watch` 필수)로 넘긴다. 테스트 RED→GREEN, 기본 경로 byte 동작 불변(env 없을 때 기존 테스트 전부 통과).
  - 하네스 배선(확인한 결함): `--new-game-path` 분기(`tools/g1_saved_scene_probe.py` 6301~6311)는 `_run_lane`에 `layer_drift`·`screen_watch`·`screen_watch_cache`·`drift_samples`를 넘기지 않고, `new-game-path-result.json` lane 요약 키(6325~6327)에 `screen_watch`가 없다. 후보 lane에만 넘기고 요약에 `screen_watch`(경로·SHA·bytes)를 더한다. 기존 NG3~PM0 경로 불변.
- **PM1-1 census(격리 run 2회):** `--hd-source scale2x --new-game-path --new-game-start --new-game-menu --layer-drift --screen-watch --screen-watch-state 23 --drift-samples "260,250;530,250;400,380"`(A 왼쪽 띠·B 오른쪽 띠·C 메뉴 패널 대조). 옵션 조합이 parser나 런타임에서 안 되면 원인을 고쳐 다시 실행한다(하네스 결함은 수리 대상).
  - 측정: 저장 창 열림·닫힘 전환 present(trace seq와 watch `p` 대응)에서 A·B·C 쓰기 EIP·스택 return 4개·스레드·값, 정착 PS23 동안 A·B 쓰기 0인지, C의 per-present writer(예상 `0x4662DE`), raw dropped 0, PM0 수치 재현(복귀 손실 ≈44k).
  - **PASS(귀속):** 2/2 run에서 닫힘 전환의 A·B writer EIP가 같고, 그 함수 진입·호출처를 objdump로 적는다(인자 수·ret·source 버퍼). 그 writer가 쓰는 source가 화면에서 미리 저장한 버퍼면 그 저장 writer(열림 전환 때 A·B를 **읽는** 쪽은 DR 쓰기로 안 잡히므로, 버퍼 주소를 스택/인자에서 읽어 기록)도 적는다.
  - **수리 같은 회차 허용 조건(구현 우선):** writer가 (ii) `0x466280` 조기 return이면 그 조건을 고치고 counter를 붙여 PM0 재측정 2회(PASS = 복귀 뒤 PS23 HD ≥98.6%·전체 창 ≥90%·V1/안전 0·dropped 0·PS3 비회귀). (i)·(iii)이면 수리하지 않고 사양 근거(함수·인자·버퍼)를 middle에 넘긴다.
  - **BLOCKED:** PS23에서 무장 실패·hit 0이면 `a`/`k` 레코드와 함께 넘긴다. 60분 또는 실패 가설 2회.
- 공통: source를 바꾸면 lint·typecheck → 기록 freeze → `make check` 1회. 디스크 ≥20GiB(현재 165GiB 여유) 확인, 끝나면 game 사본 삭제. 원본/참고 쓰기 금지, 커밋 금지, 시험판 재스테이징 없음. 사용자 G1 시험 결과가 들어오면 그것이 최우선이다.

backlog(추가): 클릭 커서 영역 −308/−101 고정 coverage(§3 부수), 저장 창 동색 1,840 px 저장 창 HD 잔존. 나머지 backlog는 lap1116 §7 그대로.

## 6. 검사

- 기록 freeze 뒤 `checks/safety.sh check`·`checks/context_limits.py`. 결과는 STATUS에만 쓴다.
- 전체 `make check`는 SKIP한다. 이번 변경은 문서뿐이고 하네스·테스트·C source는 lap1117 full PASS(1738) 때와 같다(하네스 SHA `0dc53744…` 일치, 그 뒤 바뀐 source 0).

## 다음 한 가지

work(Sonnet): §5 H-PM1 — PM1-0 screen watch 상태 게이트(옵트인) → PM1-1 PS23 전환 writer census 2회 → 귀속(조기 return이면 같은 회차 수리·재측정).
