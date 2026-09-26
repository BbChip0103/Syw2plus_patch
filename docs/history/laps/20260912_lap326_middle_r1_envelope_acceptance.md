# 2026-09-12 | lap 326 | 목표 G1 (M1)

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5` / high / 중간 tier(진단·계획·확인).
  게임 코드 hands-on 수정 0, 게임 실행 0, Wine/Xvfb/클릭 0, 커밋/푸시 0.
- 가설 / 사용자 관찰: lap325가 middle로 되돌린 두 미결(① 다이얼로그 도달의 비순환 판정식,
  ② x/y 두 store의 표본 일관성)은 **새 계측 기구 없이** 원본의 상태 전이 순서만으로 닫힌다.
- 예상 PASS / FAIL 조건: PASS = 원본 PE 바이트에서 (a) PS를 읽는 디스패처 폭/테이블, (b) PS=35를 쓰는
  유일 즉시 writer, (c) 그 writer와 origin store의 **무조건 선후 관계**를 재유도하고 probe failures=[].
  FAIL = 어느 간선이라도 조건부이거나, PS=35 즉시 writer가 1개가 아니거나, store 인구조사가 lap324와 불일치.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted): 전부 **uncommitted**(LOOP_ALLOW_COMMITS=0).
  - `docs/history/laps/probes/20260912_lap326_middle_r1_reach_ordering_probe.py`
    `70c9cc17db880b54802db7d7d8af565df3e52e5fa73b247bc9a58e1675f17bd8` (신규)
  - `docs/work/active/G1_R1_MIDDLE_ENVELOPE_LAP326.md`
    `a9c0890ff229f155db5eb4fc339195fe387120b6bd8cbab1e94dbf5dd77fb9ec` (신규)
  - `docs/history/laps/20260912_lap326_middle_r1_envelope_acceptance.md` (본 문서, 신규)
  - `docs/STATUS.md` 갱신 → 130줄, `112308f7d3c6a55e5a828c1ccd4bfc0d5d92e60ac3d70fb0f185f82006a5323d`.
    압축 전 원문(126줄, `0c64d66207bf2ea4d10232fb403ee3c0c5804e521cdd1a5284789353b46988c1`)은
    `docs/history/laps/20260912_status_lap325_compaction.md`에 먼저 보존했다.
  - `loop/ESCALATE_SOL`(lap325) 소비·삭제(원문은 아래 부록 A). 새 ESCALATE 생성 **없음**.
  - 게임 코드/하네스(`tools/`, `patches/`, `checks/`, `tests/`) 변경 **0**.
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture:
  원본 `Syw2plus/syw2plus_original.exe` = `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`
  (probe가 직접 해시, 불변). **후보 SHA 없음**(패치 생성 0). 환경 = 정적 읽기 전용 분석만.
  활성 플레이어/지도/군대/fixture = **해당 없음**(게임 실행 0).
- 실행 명령 / 로그 / 캡처 경로 및 해시:
  - `python3 docs/history/laps/probes/20260912_lap326_middle_r1_reach_ordering_probe.py`
    → rc0, `failures: []`, stdout SHA `1bff28d40b55e1488d3c071445cabb9cf280389cabb49b0a1126c56110cf0785`
    (연속 2회 byte-identical).
  - `make check` → 361 passed (57.02s), Ruff `All checks passed!`, compileall OK,
    mypy `Success: no issues found in 10 source files`, `CONTEXT_PASS`, exit 0.
  - `checks/safety.sh check` → `SAFETY_PASS`.
  - 캡처(PNG) **없음** — 화면 출력 작업이 아니다.
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN): **ACCEPT** — R1 봉투 수용, 두 미결 해소.
  1. 디스패처 `0x4233B8` = `0f bf 05 18 d8 4e 00` → PS는 WORD, 부호확장 분기. 점프테이블 `0x423738`
     35엔트리(인덱스 PS-1), PS=9→`0x423407`, **PS=34→`0x423411`**, PS=35→`0x42341B`.
  2. PS 즉시(imm16) store 71건 중 **값 35는 정확히 1건** = `0x4248E5`
     (`66 c7 05 18 d8 4e 00 23 00`), PS=34 핸들러 `0x4248E0` 말미.
     **fail-open:** PS 레지스터 store 33건은 값 미상이라 "유일 writer"라고 쓰지 않는다.
  3. **선후 관계(본 lap 핵심):** `0x423411 → 0x4248E0 → call 0x4A2FF0 → (꼬리 jmp) 0x493C40
     → push 8; call 0x4D6A00 → call 0x4D60B0 → x@0x4D632A, y@0x4D6348 → 0x4D6A23 tag → ret
     → 0x4248E5 PS:=35`. 모든 간선 무조건. `0x4A2FF0` 참조자 1(call, `0x4248E0`),
     `0x493C40` 참조자 1(jmp, `0x4A2FF5`), `0x4A3000` 참조자 1(call, PS35 핸들러 `0x4248F1`).
     ⇒ **PS==35 관측 시점은 세 store 전부의 뒤**이므로 게이트된 1회 read에 찢김 표본이 없다.
  4. **lap324 정정:** lap324는 E8-only 호출 그래프를 써 `0x4A2FF5`의 꼬리 `jmp`를 놓쳤고,
     그래서 origin store가 PS35 핸들러 **안**에서 일어나는 것으로 보였다. 수치·금지 범위 영향 없음,
     그러나 판정식의 방향이 바뀐다(관측 순서 보장이 **생긴다**).
  5. 직접 store 인구조사(절대 operand): `0x1088B5C` 출현10/store **1**(`0x4D632A`),
     `0x1088B5E` 출현11/store **1**(`0x4D6348`), `0x1088B60` 출현3/store **2**
     (`0x4D6A23`,`0x4D6A2F`, 둘 다 `0x4D6A00` 내부). lap324와 일치(독립 재유도, 승격 아님).
     x→y store 간격 = 직선 23바이트 `8bf88b86f4100000992bc2d1ffd1f82bf80fbfc183c014`.
  6. `0x4D6A00` 직접 호출자 2개는 인자가 다르다: `0x493C42`=`push 8`, `0x493D6B`=`push 0x3E8`
     (`68 e8 03 00 00` @ `0x493D66`). ⇒ `tag==8`은 이번 진입 경로의 2차 표지(필요조건 아님).
  7. 초기값: 세 전역은 `.data` raw 끝 `0x4F9000` 밖 = **BSS 0**. PS 파일 초기 WORD=40, 상위 WORD=0.
     ⇒ 사전 등록 예측 (P1): fresh run PS9 시점 pre는 `(0,0,0)`이어야 한다.
  8. 좌표계: `runtime_env.py:3413-3421`의 **이미 PASS한** 타이틀 입력이 변환을 고정
     (`root = content_crop + client`, 실증 `(184,560)`→PS9→PS7, content 800×600·root 1600×1200 강제).
     `(296,505)`는 같은 좌표계·같은 변환. 새 근거 불필요.
  9. A/B 산술 재유도: `(800-320)/2,(600-310)/2 = (240,145)` = A; `(640-320)/2,(480-310)/2 = (160,85)` = B.
     lap322 §14.3과 일치.
  10. `0xB92CC0`은 **WORD·다음 상태 요청**(`0x4257A7`=`0x140`, `0x4257C2`=`8`, PS9 핸들러 `0x4248CC`가 ax 기록).
      `player_offsets.md`의 "직전 프로그램 상태 (추정) byte" 행과 다르다 → 문서 정정은 별도 카드(수치 영향 0).
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태:
  - **실행 예산 여전히 0.** 본 판정은 Astra 발효 조건 4개 중 첫 번째(middle 봉투 수용)만 충족한다.
  - fail-open 유지: 계산/간접 writer 미배제(N2 계열), PS 레지스터 store 33건 값 미상,
    `0x4D60B0` 조기 반환 가능(→ post==pre==0 → UNKNOWN), **클릭이 '불러오기'를 고른다는 정적 증명 없음**.
  - 독립 검수: 본 문서는 자기 검수가 아니다. work 구현 후 **다른 새 middle 세션**이 실행 전 검수해야 한다.
  - 사용자 마일스톤 승인: **없음**. G1 제품 증거 0 유지. 마일스톤 종료/이동 0.
- 다음 한 가지: **work tier(Luna 또는 Sonnet5 / high)가 `G1_R1_MIDDLE_ENVELOPE_LAP326.md` §5의
  (F1)~(F8)+(P1)을 최소 변경으로 구현하고 `make check`와 합성 검사 4종을 통과시킨다. 실행은 하지 않는다.**

## 부록 A — lap325 `loop/ESCALATE_SOL` 원문 (본 lap이 소비)

```
lap=325
role=Codex gpt-6-astra/high major direction/master-plan
reason=R1 연구 방향은 조건부 허용하나 구성 확인 판정식과 x/y 표본 일관성 근거가 미정. 구현 근거 불명확으로 실행/재시도 없이 승격.
handoff=docs/work/active/G1_R1_SCOPE_DIRECTION_LAP325.md
next=새 middle(Sol 요청)이 독립 도달 판정·좌표계·표본 일관성·4실패모드·deadline·소유 종료·evidence 분리를 검증하고 봉투 수용/반려. 수용 후 work 구현/필수 검사와 새 middle 실행 전 독립 검수를 거쳐야 제한 1run 발효.
constraints=현재 runtime/게임/Wine/Xvfb/클릭 0; work 카드 0; Stage B/쌍/PNG 비교/W3 재pin/baseline/golden/INT3 금지; 게임 코드 수정/커밋/푸시/후속 모델 자동 호출 0.
approval=상위 범위 조건부 결정이며 middle 기술 수용·사용자 마일스톤 승인·제품 완료 아님. exit0은 승인/검증 통과 아님.
```

처리: 요청된 일곱 항목(도달 판정·좌표계·표본 일관성·4실패모드·deadline·소유 종료·evidence 분리)을
`G1_R1_MIDDLE_ENVELOPE_LAP326.md` §1~§5에서 심사해 **ACCEPT**했다. 반려 사유 없음, 새 ESCALATE 없음.
