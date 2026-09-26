# 2026-09-12 | lap 286 | G1 S1 저장 레이아웃 work 결과 middle 독립 검수

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5` / high / middle tier(진단·계획·확인). 게임 코드 hands-on 수정 0.
- 가설 / 사용자 관찰: lap284 work의 static save-layout 모델이 work probe의 하드코딩 목록·윈도우·문자열 휴리스틱에 의존하지 않는 **다른 추출 경로**로도 같은 상수·계수·roster 수를 낳는가.
- 예상 PASS / FAIL 조건: PASS=독립 유도한 상수항/면적계수/네 fixture roster 수가 work와 전부 일치하고, save 함수가 무시한 callee 중 fwrite에 도달하는 것이 하나도 없다. FAIL=수치 불일치 또는 숨은 쓰기 발견 시 상수를 맞추지 말고 blocker로 보고한다.

## 랩 번호 정정 (기록용, 수정 아님)

`loop/.lap_counter`=286이고 `loop/PROMPT.md`는 이 값을 이번 lap 번호로 쓰라고 지시한다.
직전 세션은 러너 로그 `logs/laps/2026-09-12/lap-0285.log`에서 돌았지만 자신을 `lap284 work`로
기록해 기록 lap 번호가 러너보다 하나 뒤진다. 이번 기록은 PROMPT 계약대로 286을 쓴다.
러너 전용 상태인 `.lap_counter`는 읽기만 했고 쓰지 않았다.

## 변경 / 근거

- 신규 probe: `docs/history/laps/probes/20260912_lap286_middle_save_layout_review_probe.py`
  (`f424662f…cc631fdf`)
- 신규 출력: `logs/lap286/middle_save_layout_review.json` (`def7fa09…455e17585`)
- 게임 코드·하네스·comparator·producer·회귀 테스트·PASS 규칙·baseline/golden 변경 0. 원본/fixture 쓰기 0. 커밋 0(`LOOP_ALLOW_COMMITS=0`).
- 원본 EXE SHA `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac` 검수 전후 동일.

## 독립 추출 경로가 work와 다른 점

1. save 함수 범위를 `0x440FF0` 가정 대신 **자기 `ret`+앞선 분기 목적지 폐포**로 끊는다.
2. layer 본문을 "다음 layer 주소"가 아니라 **각 함수 자신의 경계**로 끊는다.
3. mode/repeat/element를 `"mov ebx,0x5"`·`sar` 문자열 개수가 아니라 **디코딩한 fwrite 인자 push와 감소되는 루프 레지스터**에서 읽는다.
4. save 함수가 무시하는 모든 callee를 깊이 3까지 **전이적으로** fwrite 도달 검사한다.
5. 페이로드를 호출 순서대로 재생해 bulk 파일 오프셋과 PlayerStruct 오프셋을 가정하지 않고 계산한다.

## 실행 / 수치

- 실행 명령: `.venv/bin/python docs/history/laps/probes/20260912_lap286_middle_save_layout_review_probe.py`
- exit 0, `failures=[]`. 같은 명령 재실행 출력 **바이트 동일**(결정성).
- lap284 work probe 재실행도 `logs/lap284/work_save_layout_probe.json`과 **바이트 동일**(SHA `7381b5f7…a5cbfb81`), exit 0.
- save 함수 실측 경계: entry `0x00440C20`, 마지막 명령 `0x00440F5A`(ret). 직접 fwrite **22**, layer **28**(중복 없음), nested helper **3**, roster **1**.
- 독립 유도 수치 — literal `1,249,942` + helper `118,360` + 고정 layer `32,400` = **상수항 `1,400,702`**, **면적계수 `30.5` B/타일**. work의 컴포넌트 합과 정확히 일치.
- 면적계수 30.5 내역: elem2 full 4개(8) + elem1 full 16개(16) + repeat5 full 1개(5) + quarter 6개(1.5). fixture 두 면적의 차분에서도 `(3,093,902−1,982,062−(375−147)×1880)/(32,400−10,000)=30.5`로 독립 확인.
- 네 fixture: save000/006 `180×180` prefix `2,388,902`, save011/012 `100×100` prefix `1,705,702`. roster 나머지가 `0x758`의 정수배 — **375 / 558 / 147 / 149**. work와 전부 일치.
- 호출 순서 재생으로 계산한 오프셋이 work와 일치: save000/006 bulk `1,455,954`, player0 `2,259,634`, roster `2,388,902`; save011/012 bulk `772,754`, player0 `1,576,434`, roster `1,705,702`.
- owner 히스토그램(=record 수 합치와 일치): save000 `0:124, 1:1, 2:123, 3:124, 5:3`; save006 `0:95, 2:92, 3:95, 5:104, 6:97, 7:75`. **work가 다루지 않은 save011/012까지 확장**: save011 `0:144, 1:3`, save012 `0:145, 1:4`.
- 네 fixture 모두 **owner id가 8 이상인 unit record 0개**. 기존 G3 저장 포맷 blocker와 같은 방향의 보강 관찰이다(반증 아님).
- 무시된 callee `0x440A80`(sprintf 래퍼), `0x440AC0`(슬롯 라벨 조립), `0x4AC3E0`(전역 알림 큐, 상한 5), `0x4DA9F2`(fopen), `0x4DA97C`(fclose) — **fwrite 전이 도달 0**.
- Fast: `make check` **292 passed in 44.86s**, Ruff/compileall/mypy 10 files, `CONTEXT_PASS`, exit 0. `checks/safety.sh check` → `SAFETY_PASS`. 신규 probe Ruff/py_compile exit 0.
- 게임/Wine/Xvfb/Stage B/PNG/원본 실행 **0**.

## 판정

**ACCEPT-WITH-CORRECTION (이 offline 카드 범위 한정).** 모델의 수치 주장은 독립 경로로 재현됐다.
정정 2건과 범위 한계 4건을 함께 남긴다. 제품 G1 증거·runtime 예산·마일스톤 승인은 아니다.

### 정정 1 — work probe의 디스어셈블 윈도우가 save 함수를 넘어선다

`SAVE_END = 0x440FF0`은 실제 save 함수 끝(`ret` at `0x440F5A`)을 지나 **다음 별개 함수
`0x440F60`**(저장 슬롯 헤더 `0x40`바이트를 fread로 읽어 문자열을 복사하는 루틴)까지 포함한다.
그래서 `0x4DA9F2`/`0x4DA97C`가 두 번씩, `0x4DA4A9`가 한 번 열거된다.
`0x4DA4A9`는 `0x4DA39F`(fwrite)와 시그니처가 같은 4인자 `(ptr,size,count,FILE*)` 루틴이지만
`0x440F60`의 읽기 경로에서 쓰이므로 **fread**다. work probe는 이 호출들을 무시하므로
**크기 모델에는 영향이 없다.** 그러나 경계가 근거 없이 넓고, 장래에 `0x4DA4A9`를 fwrite로
오인하면 조용한 드리프트가 된다. 상수 `SAVE_END`는 `0x440F5B`로 좁혀야 한다.

### 정정 2 — "네 크기를 정확히 재구성"은 두 번째 독립 검사가 아니다

`roster_records`는 나머지를 `0x758`로 나눠 **구한** 값이므로 `reconstructed == actual`은 항상
성립한다. 실제 반증력은 **나머지의 정수배 여부 4건**뿐이다. 강한 증거인 것은 맞지만
(4×약 1/1880), work 기록의 "정확히 일치"는 검사 2종이 아니라 1종으로 읽어야 한다.

### 남은 범위 한계 (이번 검수가 닫지 못함)

- 네 fixture가 **전부 정사각**이라 파일 오프셋 210/212의 width/height 배정은 구분되지 않는다.
- 네 fixture가 **전부 짝수 변**이라 halving layer의 기계 공식 `((w/2)*h)/2`(부호 있는 절단)와
  probe의 `(w*h)//4`를 구분할 수 없다. 홀수 변 지도에서는 두 식이 갈라진다.
- 파일 크기만으로는 layer별 full/quarter 배정이 유일하지 않다(full 하나와 quarter 하나를
  맞바꾸면 총계 30.5가 보존된다). 다만 이번 검수의 **함수 경계 기반 분류가 28개 전부 work와
  일치**하므로, 총계뿐 아니라 개별 배정도 두 경로에서 같은 답을 냈다.
- unit record의 owner 필드 `+0x8E`는 work에서 **상속한 가정**이며 이번에 재유도하지 않았다.
  히스토그램 합이 record 수와 같고 id가 전부 0..7이라는 점은 방증이지 유도가 아니다.

## 회귀 / 남은 위험 / 승인 상태

- 기존 blocker 전부 유지: S1/F2-R2 결정성, Stage B 0, runtime 예산 0, WM_CLOSE 결함,
  G3 저장 포맷 `0x1B5A4` 초과, tick 순환 의존, W2 매직 리터럴 드리프트.
- 이 ACCEPT는 **static 모델의 재현성**에 한정한다. runtime layer 값의 의미, save/load 값 동일성,
  로드 메뉴/PS35 경로, 제품 G1~G4는 전부 미검증이다.
- 사용자 마일스톤 승인 없음. 모델 컨펌과 사람 승인은 분리한다.

## 다음 한 가지

work tier(Luna/Sonnet5)가 정정 1을 반영해 `SAVE_END`를 `0x440F5B`로 좁히고, 회귀로
`0x4DA4A9`를 fwrite로 세지 않는다는 단언을 probe에 추가한다. 같은 카드에서 정정 2의 문구를
기록에 맞춘다. 게임 실행·하네스 로드 경로 구현·PASS 규칙 변경은 계속 금지.
