# 2026-09-12 | lap 298 | 목표 G1 (load 연구 게이트)

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5` / high /
  **중간 tier(진단·계획·컨펌)**. 게임 구현 hands-on 0, 하위 세션·유료 CLI 실행 0.
  lap297 `ESCALATE_SOL`은 Sol 표식이었고 실제 Sol 호출은 없었다(MODEL_ROUTING의 middle=Opus5).
- 가설 / 사용자 관찰: lap284 §7이 "이 카드 다음(지금 열지 않음)"으로 남긴 가설 —
  타이틀 화면의 불러오기 좌표는 **게임 실행 없이 과거 타이틀 스크린샷 분석으로** 얻을 수 있다.
  lap297 Astra는 이를 middle이 "기존 로컬 캡처의 SHA·환경·화면 근거로 확인 가능한지" 판정하라고 요구했다.
- 예상 PASS / FAIL 조건:
  - PASS = (i) 캡처 좌표계와 클릭 좌표계가 같음을 소스로 증명하고, (ii) 하네스의 이미 검증된
    클릭 `(184,560)`이 탐지된 격자의 **정확히 한 셀**에 들어가며 그 셀이 `runtime_env.py`가
    부르는 이름(random-game)과 일치하고, (iii) 그때 이웃 셀인 불러오기의 bbox/중심이 나온다.
  - FAIL = 격자가 불규칙하거나, 클릭이 0개/2개 셀에 걸리거나, 라벨 대응을 소스로 못 묶는 경우.
    그 경우 좌표는 UNKNOWN으로 남기고 blocker로 반환한다(추측 좌표 금지).
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted): **전부 uncommitted**
  (`LOOP_ALLOW_COMMITS` 미설정, 기본 0). 게임 코드·하네스·검사·PASS 규칙 변경 **0**.
  - 신규 `docs/history/laps/probes/20260912_lap298_middle_title_load_ui_probe.py`
    `1d4f5d7ba9fba7f6d80b0b0a23fb8fefaf2561177895dd7a22a792a16e996e5c`
  - 추가 `docs/work/active/G1_RUNTIME_CONTRACT_MIDDLE_LAP284.md` §10 (새 문서 계보를 만들지
    말라는 lap297 Astra 요구에 따라 기존 runtime-contract 계보에 덧붙였다)
  - 갱신 `docs/STATUS.md` → `b3b089dea0475142fb6626c3f6d5e2604a48df05d53c6a9cdc7de2f3386e7443`
    (130줄). 압축 직전 원문(`260f0435…58f75f83`, 130줄)은
    `docs/history/laps/20260912_status_lap298_compaction.md`
    (`1cfef123…73341479`)에 먼저 보존한 뒤 압축했다.
  - 추가된 §10을 포함한 `…/G1_RUNTIME_CONTRACT_MIDDLE_LAP284.md`
    `d7d80e8cb6072a2c0f525a282dd1094eaee83c8a65111130e0c33bfad9a46e8a`
  - 삭제 `loop/ESCALATE_SOL` — lap297이 요청한 판정을 이번 바퀴가 수행했고, 이번 바퀴는
    승격 조건(필수 게이트 실패 / 근거 충돌 / 마일스톤 경계) 어디에도 해당하지 않는다.
    삭제 전 원문은 아래 부록 A에 바이트 그대로 보존했다(diff 일치 확인).
  - 불변 확인: `tools/runtime_env.py` `dd2ad043…8500190`,
    `patches/population/runtime_driver.py` `ae4ff939…4e4291b5`
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture:
  - 원본 EXE `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac` (재계산 일치)
  - 후보 SHA: **없음**(후보 빌드 0). 환경: offline, 게임·Wine·Xvfb·Stage B·runtime 예산·신규 PNG 캡처 0.
  - 활성 플레이어/지도/군대: 해당 없음(실행 0).
  - fixture(읽기 전용): `Syw2plus_re/Syw2plus/save/save000.dat` 3,093,902 B
    `1c703551…629e719da`, `save006.dat` 3,437,942 B `616b7997…9289a0d064` — §2 표와 재계산 일치.
    `local/fixtures/20260910/save011.dat`·`save012.dat`는 정적 대조 자료로만 유지.
  - 분석 입력(읽기 전용): 공유 temp의 `*_title_before_menu_*.png` **14장**,
    전부 단일 SHA `277a0b23b836e30508326efa0295aa0c35f09a6a9fc4f55fa2b121b09ce5b252`, 800×600.
- 실행 명령 / 로그 / 캡처 경로 및 해시:
  - `.venv/bin/python docs/history/laps/probes/20260912_lap298_middle_title_load_ui_probe.py`
    → `logs/lap298/title_load_ui_probe.json` `584e06e6e757fde534f2a4fe3041a3bfc3974b92153e0e695b0603be443e909a`
    exit **0**, `failures` **[]**, stderr **0 B**.
  - `make check` → `logs/lap298/make-check.log` (결과는 아래 측정값).
  - 파생 crop(기존 캡처를 자른 것이며 새 실행 캡처가 아니다), 공유 temp:
    `20260912_133000_lap298_title_r1c3_load.png` `5580e229…4da333b390`,
    `20260912_133000_lap298_title_r2c2_random.png` `185869c1…f01cbd174`.
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN):
  - **타이틀 메뉴 격자 = 4열×2행, 셀 100×36**, 열 좌변 21/134/247/360, 행 상변 488/542. **PASS**
  - 하네스 클릭 `(184,560)` → **정확히 한 셀** row2/col2. `runtime_env.py:606`이 같은 클릭을
    `"title random-game click (184,560)"`라 부르고 그 셀 crop의 라벨은 **임의게임**. 격자↔라벨
    대응이 소스 문자열로 독립 확인됨. **PASS**
  - **불러오기 = row1/col3, bbox `[247,488,346,523]`, 중심 `(296,505)`.** **PASS(위치·라벨 한정)**
  - 좌표계 동일성: `scrot -a content_crop` 크롭 + 클릭 `content_crop+(x,y)` + 800×600 게이트.
    캡처 픽셀 = 클릭 좌표. **PASS**
  - 탐지기 반증력: 셀 중심 8개가 각자 자기 셀로만 해석, 열 간극 `(127,560)`·격자 위 `(184,400)`은
    무해석. 한 덩어리 탐지는 통과 불가. **PASS**
  - 하네스 로드 경로 재측정: `runtime_env.py`의 `save` 참조 **0**, PS35 참조 **0**,
    PS 대기값 **{3,5,7,9}**. lap284 주장 재확인. **FAIL(로드 경로 부재 유지)**
  - Plan C 함정 봉인: 공유 temp의 800×600 `…_d1app2r3_21_load_screen.png`
    (`5e95ed92…d17e5879`)의 슬롯 문자열은 `Syw2plus_re/plan_c/src/ui/save_load_screen.cpp`
    (`f2232e91…90ff41ec`)가 만든다(`"[PLNC] "`/`"[ORIG] "`/`"저장된 정보가 없습니다."` 확인).
    **원본 좌표 출처로 REJECT.**
  - 슬롯 선택 UI·로드 후 상태 전이·클릭 효과: **UNKNOWN**(관측 0).
  - `make check`: 아래 "회귀" 항목에 기록.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태:
  - `make check` 2회 모두 **292 passed**, `MAKE_CHECK_EXIT=0`: 문서 편집 전 47.51s
    (`logs/lap298/make-check.log`), 최종 파일 상태에서 48.87s
    (`logs/lap298/make-check-final.log`). `checks/safety.sh check` **SAFETY_PASS**.
  - 남은 위험 (1): `(296,505)`는 **클릭 결과가 관측된 바 없다.** 위치와 라벨만 확정했다.
    Astra 결정2의 별도 evidence 종류, PS35→PS3 미도달 필드 선언, 봉투 (b)~(e)는 전부 미제출.
  - 남은 위험 (2): work tier가 같은 Plan C PNG를 재발견할 가능성이 높다. §10.3 봉인을
    카드 본문에 넣어 인계했다.
  - 남은 위험 (3): Plan C가 인용하는 `0x519A0C`/`0xB3AD74`/`0x1088B5C`는 원본 raw 파일 크기
    밖이다(`0x4D60B0`은 안). 섹션 virtual size 또는 다른 모듈 확인이 선행돼야 한다.
  - 독립 검수: **미완.** 이 절과 §10은 다음 새 middle이 검수한다. 자기 승인 아님.
  - 사용자 승인: 제품 승인 없음. 2026-09-12 01:03 실행 승인 범위는 그대로이며 확대 없음.
  - 이전 바퀴(lap297) 검수: 결정문서 `90cb9fcd…bb925cea`, `ESCALATE_SOL` `760a977e…4a8aa84c`
    재계산. Astra 결정1 문안이 lap284 §4 제안과 축소·확대 없이 일치함을 원문 대조로 확인.
- 다음 한 가지: work(Luna/high 또는 Sonnet5/high) 새 세션이 §10.5 카드 —
  lap296 §4.7.6 가드 수리를 먼저 끝낸 뒤, 원본 EXE에서 `FUN_004D60B0`을 직접 디스어셈블해
  저장/불러오기 대화상자 레이아웃을 **독립 재유도**한다. Plan C 값 복사는 실패다.

---

## 부록 A — lap297 `loop/ESCALATE_SOL` 원문 보존

원문 SHA256 `760a977ece02ed3c9a6ef1c7a6002802b35d2251d0a9894407292eb74a8aa84c`, 7줄.
lap297이 요청한 "새 middle이 세 상위 결정과 handoff 표를 독립 판정하고 work 범위 또는 구체
blocker 확정"은 이번 바퀴 §10에서 수행됐으므로 표식 파일은 해제한다. 아래가 삭제 전 원문이다.

```
lap=297
role=Astra major direction/master-plan
reason=load UI/명령/실행 봉투 근거 미확정; 게임 구현 및 runtime 실행 중단
handoff=docs/work/active/G1_ASTRA_RESEARCH_GATE_LAP297.md
next=새 middle이 세 상위 결정과 handoff 표를 독립 판정하고 work 범위 또는 구체 blocker 확정
preserve=lap296 §4.7.6 가드 수리 인계, 모든 기존 반려/미결, runtime/Stage B 예산 0
provider=사용자 지정 표식이며 실제 Sol/Opus 호출 또는 provider 변경 없음
```
