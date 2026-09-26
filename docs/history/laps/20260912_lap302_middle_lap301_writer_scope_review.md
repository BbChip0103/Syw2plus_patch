# 2026-09-12 | lap 302 | G1/S1 lap301 수리 probe 독립 검수 (writer 범위·후보 집합)

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5`/high, 지정 역할 **middle
  (진단·계획·컨펌)**. 게임 코드 hands-on 수정 없음. 제품 판정·마일스톤 승인 없음.
- 목표: lap300 §11 handoff의 T1~T4를 lap301 work가 실제로 수행했는지, 그리고 그 결과가 원본
  바이너리에서 **독립적으로** 성립하는지 확인한다. 승격/실행 허가/Stage B/runtime 예산은 범위 밖.
- 가설 / 예상 PASS·FAIL 조건: (a) lap301 probe가 기록된 SHA로 재현되면 결정성 PASS. (b) T1 앵커가
  §11이 지목한 주소에 실재하면 T1 PASS. (c) 원본 입력 fixture 경로·SHA가 맞으면 T2 PASS.
  (d) 내가 따로 뜬 objdump에서 화면 전역 writer가 lap301의 4개로 **전수**면 T3 ACCEPT, 더 있으면
  REVISE. (e) `logs/lap299/`가 불변이면 T4 PASS.

## 변경 파일 / source fingerprint / 커밋(없으면 uncommitted)

- 신규 `docs/history/laps/probes/20260912_lap302_middle_lap301_writer_scope_review_probe.py`
  SHA `b5343ec41713e14ecf4e2b99ebe2903786d350367b86daf6411cb7d487ebd0a6`.
- 신규 `logs/lap302/middle_writer_scope_review.json`
  SHA `5190920f1cfb14d9155c913abc3378d88e092c8a6e13f8a116174cc1948940d2`.
- 신규 `docs/history/laps/20260912_status_lap302_compaction.md`(STATUS 원문 보존,
  원문 SHA `2361a54f829ac3b0b8504787ba82c22fb01ae61957776aa20672e1a762bce23f`, 124줄).
- `docs/work/active/G1_RUNTIME_CONTRACT_MIDDLE_LAP284.md` §12 handoff 추가
  (갱신 후 SHA `1ac0ae34e8da8b2cc193b02a885762f5cb94e32e6a39bdab43af962e506f64a8`), 본 history,
  `docs/STATUS.md` 갱신(갱신 후 130줄, SHA `a63aa526ca9c932240d109b93fe99205582e282e41b32838eacfa1a009a36dd8`). 원본/참고 EXE·DLL/assets/`tools/`/`patches/`/하네스/comparator/PASS 규칙
  변경 0. **lap301 probe와 lap299/lap301 로그는 읽기만 했고 수정 0.**
  커밋 없음(`LOOP_ALLOW_COMMITS=0`).

## 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture

원본 EXE `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`(독립 재확인), 후보 없음.
읽기 전용 fixture `../Syw2plus/yfnt/saveloadtitle.spr` SHA
`7d154cdbf37dbea78c162ada870e656a039a224c5aa63ee52d86d8123c08a5c5`, header `[9,320,310,1]`(재확인).
offline Linux `.venv` + `/usr/bin/objdump`. 활성 플레이어/지도/군대 없음.
게임/Wine/Xvfb/Stage B/runtime/PNG/캡처 대조 **0**.

## 실행 명령 / 로그 / 해시

- `.venv/bin/python …/20260912_lap299_work_save_load_layout_probe.py` → exit0, stdout SHA
  `c312b42e3593c2af5bb47e9df9e1b624f8a55ea618a1cc70b7e6dc709caaf10a`
  = `logs/lap301/save_load_layout_probe.json`과 **바이트 동일**. 두 번 재실행 모두 동일.
- `.venv/bin/python …/20260912_lap302_middle_lap301_writer_scope_review_probe.py` → exit0,
  `failures=[]`, report SHA `5190920f…8940d2`.
- 독립 `objdump -d -Mintel -j .text --start-address=0x401000 --stop-address=0x4e4ae5` 전수 + PE
  헤더 직접 파싱.
- 검수 시작 시점 `make check` → **292 passed (47.54s)**, ruff/compileall/mypy/`CONTEXT_PASS`, log SHA
  `2a926ca33026e05a5b1725859d35ae2139e8ce529f94c3b530c9766f386f1731`;
  `bash checks/safety.sh check` → `SAFETY_PASS`, log SHA
  `bfa8f48349efc18774e6abb18c8c6b7cb6c9e785d3540862291a9c7c420d071e`.
- **문서/probe 추가 후 재실행:** `make check` → **292 passed (46.57s)**, ruff/compileall/mypy/
  `CONTEXT_PASS`, exit0, log SHA `4414c0745d6e9fc14284186ec242ff556700f8e92eef0bc64d1b69a0a244b754`;
  `bash checks/safety.sh check` → `SAFETY_PASS`, exit0, log SHA `bfa8f48349efc18774e6abb18c8c6b7cb6c9e785d3540862291a9c7c420d071e`.

## 1. 결정성과 T4 — ACCEPT

lap301이 기록한 두 SHA를 독립 확인했다. 소스 `a6f682eb…a428c7a0`, report `c312b42e…caaf10a`,
재실행 결과 바이트 동일. `logs/lap299/save_load_layout_probe.json`은 `8e735a9a…76d2bb0b`로 불변이라
T4의 로그 보존 요구는 충족.

## 2. T1 앵커 — ACCEPT (§11이 지목한 주소와 일치)

내 objdump에서 `sub ecx,0x1a`는 `0x004D6358`에 **정확히 1회**만 존재한다. §11이 적은 주소와 같다.
`add eax,0x18`은 3회(`0x4D6371`/`0x4D641E`/`0x4D64CD`), `add ecx,0x18`은 2회(`0x4D63AC`/`0x4D6456`).

**사각(기록만, 차단 아님):** lap301의 `contains_all`은 구간 내 **문자열 존재**만 본다. 위처럼 2~3회
나오는 앵커는 어느 발생인지 구별하지 못하므로, 슬롯 높이 계산이 다른 명령으로 옮겨가도 통과한다.
STATUS가 이미 적은 `type`/`owner` 값 드리프트 사각과 같은 부류다. lap302 probe는 같은 앵커를
**주소 고정**으로 다시 단언해 이 구멍을 덮었다.

## 3. T2 fixture — ACCEPT

경로가 참조 저장소가 아니라 원본 입력 `REPO.parent/Syw2plus/yfnt/`이고, pin된 SHA·헤더가 실제
파일과 일치함을 직접 계산해 확인했다.

## 4. 상대 레이아웃 모델 — 명령 단위로 독립 재유도 ACCEPT

lap299/lap300이 낸 모델을 이번에는 **중심식 명령 열**까지 직접 읽어 재유도했다.

```
0x4D625B  mov eax,[esi+0x10F0]        ; dialog_w  (= saveloadtitle.spr 320)
0x4D6310  mov edi,eax
0x4D6312  mov eax,ds:0xE5BF1C         ; screen_w
0x4D6322  sar edi,1 / 0x4D6324 sar ecx,1 / 0x4D6326 sub ecx,edi
0x4D632A  mov WORD PTR ds:0x1088B5C,cx   ; origin_x 저장 (16-bit)
0x4D6333  mov eax,[esi+0x10F4]        ; dialog_h (310)
0x4D633C  sar edi,1 / 0x4D633E sar eax,1 / 0x4D6340 sub edi,eax
0x4D6348  mov WORD PTR ds:0x1088B5E,di   ; origin_y 저장 (16-bit)
0x4D6351  movsx ecx,[0x1088B5E] / 0x4D6358 sub ecx,0x1a → [esi+0x40C]  ; slot0 y1
0x4D6345  add eax,0x14 → [ebx]=[esi+0x408]                            ; slot0 x1
0x4D6363  add edx,0x118 → [esi+0x410] / 0x4D6371 add eax,0x18 → [esi+0x414]
```

즉 `this+0x408` stride 16, 슬롯0 `(origin_x+0x14, origin_y-0x1A, +0x118, +0x18)`가 원본에서 그대로
나온다. **정정 1(수치 영향 0):** 실제 식은 `(screen-dialog)/2`가 아니라
`sar(screen,1) - sar(dialog,1)`, 즉 **각각 반으로 나눈 뒤 빼기**다. lap301은 전자로 적었다. 도달
가능한 5개 해상도와 dialog 320×310이 전부 짝수라 두 식의 값은 **5개 모두 동일**함을 계산으로
확인했다(probe `formulas_agree` 전부 true). 홀수 변 스프라이트로 바뀌면 갈라진다.

**정정 2(설계용):** 중심식이 화면 전역을 읽는 시점은 **클릭 시점이 아니라 다이얼로그 구성
시점**(`0x4D6312`)이고, 그 결과 origin은 `ds:0x1088B5C`/`0x1088B5E`에 16-bit로 **고정 저장**된다.
따라서 훗날 관측이 허가되면 관측 지점은 클릭이 아니라 구성 시점이며, 화면 전역보다 origin 두 워드가
직접적인 관측 대상이다.

## 5. T3 화면 전역 writer 전수 주장 — **REVISE** (lap301 4개는 전수가 아니다)

lap301의 정규식은 `mov (DWORD|…) PTR ds:0xe5bf1c/20,…` **절대주소 쓰기**만 잡는다. 내 전수
disassembly에서 절대주소 writer는 정확히 그 4개가 맞다. 그러나 같은 두 워드는 그래픽 객체
`0xE5BF18`의 `+4`/`+8`이고, **`this` 상대 쓰기**가 따로 존재한다.

- `FUN_004644A0`은 thiscall이다: `0x4644AD mov esi,ecx`, `0x4644B5 mov [esi],eax`(모드 값 저장),
  `0x4644C1 jmp [eax*4+0x464B68]`(8-way switch). 각 분기가 `mov [esi+0x4],…` / `mov [esi+0x8],…`를
  쓴다 → `this=0xE5BF18`이면 **정확히 `ds:0xE5BF1C` / `ds:0xE5BF20`**이다.
- 그 `this`가 실제로 `0xE5BF18`임을 호출 사슬로 확정했다:
  `0x423D52 mov ecx,0xE5BF18` → `0x423D63 call 0x464360` → `0x4643BE mov ecx,esi` →
  `0x4643C0 call 0x4644A0`. (`.text`의 `0xE5BF18` 참조는 1,066건이고 다수가 `mov ecx,0xE5BF18`
  형태의 thiscall이다.)

결론: 두 전역의 쓰기 지점은 **4개가 아니라 최소 20개**(절대 4 + 모드 분기 8×2)이며, lap301의
`unexpected screen global writer count` 게이트는 간접 경로에 대해 **fail-open**이다. §11이 모드 표를
"디스플레이 초기화에서만 불린다"고 적어 writer에서 제외한 전제도 문구로서 틀렸다 — 모드 표는
**writer이며**, 참인 주장은 writer 여부가 아니라 *호출 시점*에 관한 것뿐이다.

## 6. 후보 집합 — **REVISE** (A/B 두 개로 좁혀지지 않는다)

`FUN_004644A0`의 모드 인자는 `[esp+4]`로 들어오는 **런타임 값**이고 `eax-1 ∈ 0..7`의 8분기다.
분기가 쓰는 해상도는 `320x200`, `640x480`(×2), `800x600`(×2), `1024x768`(×2), `1280x1024` —
**5개**다. 따라서 정적으로 도달 가능한 화면 전역 값 집합은 lap301의 {A=800×600, B=640×480}이
아니라 {모드 표 5종} ∪ {`0x4324B8` 사후 640×480 복원} ∪ {`0x431B79` 지도 표면 `ebp`/`edi`}다.

이 정정은 **후보 A를 강화하면서 동시에 배타성을 없앤다.** 강화: 800×600이 이 두 워드에 들어가는
경로가 `0x464502`/`0x464509`(와 `0x464512`/`0x464519`)로 구체적으로 특정됐다. 배타성 상실: 같은
스위치가 나머지 4종도 똑같이 도달 가능하게 만든다. 그러므로 **lap300의 절대 좌표표 REJECT는
유지되고, lap301의 2후보 쌍에도 그대로 확장된다.**

부산물 — `320x200`에서는 다이얼로그가 화면 밖으로 나간다: origin `(0,-55)`, 슬롯0
`[20,-81,300,-57]`. lap301의 `slot_rects_inside_screen` 검사는 이 모드에서 **false**다. lap301은 두
후보에만 검사를 돌려 이 사실이 보고서에 없다. (해당 모드가 실제로 선택 가능한지는 미확인.)

## 7. 부수 확정 — lap300이 남긴 섹션 virtual size 선행 조건 해소 (ACCEPT)

PE 헤더를 직접 파싱했다: `.text` = `0x401000..0x4E4AE5`(vsize `0xE3AE5`) — lap301의 스캔 범위와
**정확히 일치**하므로 `.text` 범위 자체는 전수다. `.data`는 raw `0xD000`이지만 **virtual size
`0xB9FA38`** → `0x4EC000..0x108BA38`. 따라서 `0xE5BF18/1C/20`, `0x1088B5C/5E`, `0x519A0C`,
`0xB3AD74`가 모두 **이미지 안 .data의 BSS 확장부**에 있다. STATUS가 "원본 raw 크기 밖"으로 적어
둔 항목의 선행 확인이 이것으로 끝난다(주소 실재 확정이며 **좌표 출처 적격성과는 무관**, Plan C
봉인은 그대로 유지).

## 8. provenance 회귀 — ACCEPT-WITH-CORRECTION

T4의 로그 보존은 지켜졌으나 **소스는 제자리에서 덮어썼다**. 트리 어디에도 수리 전 lap299 소스가
없고(저장소에 커밋이 하나도 없어 복구 경로도 없다), 따라서 lap299 report `8e735a9a…`와 lap300의
바이트 동일 재현은 **더 이상 재현 불가능한 과거 값**이다. 또 새 report는 `"lap": 299`,
`"probe": …lap299….py`로 **자기 lap을 잘못 표기**한 채 `logs/lap301/`에 있다. 수치 영향 0, 감사
추적 영향 있음. 규칙 변경이나 과거 기록 정정은 하지 않고 사실로만 남긴다.

## 9. 새 사각을 만들지 않기 위한 설계 (W3 대응)

lap302 probe는 **뒤 바퀴가 고칠 것으로 예상되는 산출물의 SHA를 pin하지 않는다.** 결정성은 같은
세션에서 lap301 probe를 두 번 돌려 서로 비교하는 것만 단언하고, 보존된 lap301/lap299 로그 SHA는
report에 기록만 한다. 그래서 work가 lap301 probe를 다시 고쳐도 이 게이트가 W3처럼 영구 exit1이
되지 않는다. (W3 자체의 재pin은 여전히 Astra/사용자 결정 대기이며 이번 바퀴에서 건드리지 않았다.)

## 측정값 / 판정 요약

| 항목 | 판정 |
|---|---|
| 결정성(소스/report SHA, 2회 재실행) | **ACCEPT** |
| T1 앵커 존재(`0x4D6358` 유일) | **ACCEPT** (앵커 강도 사각은 기록) |
| T2 원본 fixture 경로·SHA pin | **ACCEPT** |
| T3 화면 전역 writer "전수 4개" | **REVISE** — 최소 20개, 간접 경로 fail-open |
| T3 후보 A/B 2개 제시 | **REVISE** — 도달 가능 5해상도, 절대 좌표 REJECT 유지 |
| T4 `logs/lap299/` 보존 | **ACCEPT** |
| T4 소스 provenance | **ACCEPT-WITH-CORRECTION** — 수리 전 소스 소실, lap 라벨 오기 |
| 상대 레이아웃 모델(명령 단위) | **ACCEPT** + 중심식 정정 2건(수치 영향 0) |
| 섹션 virtual size 선행 조건 | **ACCEPT**(해소) |
| 제품 G1~G4 증거 | **0** — 변화 없음 |

## 회귀 / 남은 위험 / 승인 상태

원본 SHA·보호 기준·안전 기준·PASS 규칙 변경 0. `make check` 292 passed, `SAFETY_PASS`.
제품 G1~G4 증거 0, 실제 입력/scene pair 0, Stage B 0, runtime 예산 요청 0, 사용자 마일스톤 승인 없음.
어느 해상도가 다이얼로그 구성 시점에 살아 있는지는 **offline 결정 불가**이며 이 기록은 그 실행을
허가하지 않는다.

## 다음 한 가지

§12 handoff 참조: work tier가 (i) lap301 probe의 writer 열거를 간접 경로까지 넓히고 (ii) 후보를
2개에서 도달 가능 5해상도로 교정하며 (iii) lap 라벨 오기를 바로잡되 **과거 기록은 정정하지 않는다.**
