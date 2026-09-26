# 2026-09-18 | lap 388 | 목표 G2

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5`/high, **중간 tier(middle)**
  — 진단·계획·확인. 게임 코드/제품 코드 hands-on 수정 0건(이번 lap이 만든 파일은 읽기전용 probe
  1개와 문서뿐). `docs/MODEL_ROUTING.md` 2026-09-18T17:56:55+09:00 override 준수.
  `loop/.lap_counter` = **388**(러너 전용, 읽기만 함).
- 과업: STATUS "다음 한 가지" — lap386(Part A)+lap387(Part B)의 §3-5 구현을
  **독립 재유도로 1회 검수**. Astra `GO_FINISH_CURRENT_LAYOUT_CONTRACT_ONCE`
  (`g2_capacity/20260918_post_layout_major_decision.json`) 범위를 벗어나지 않는다 —
  alias별 후속 카드/새 추론 엔진/code operand fixup/runtime 착수 없음.

## 검수 방법 (독립성 확보 방식)

핀된 사실을 **probe 안에 따로 전사**하고 기대값을 전부 로컬 전사본에서 재계산했다.
검수 대상 모듈은 **답을 읽기 위해서만** import했고 기대값 유도에는 쓰지 않았다.
전사 출처: Astra 결정 JSON의 `bulk_equations` 원문(`newBULKstart=0x892410+1880*d`,
`newBULKlength=0xE397C+14*d`, `newBULKend=oldBULKend+1894*d`, PlayerStruct 8×`0x3ABC`)과
lap380/lap381 구조표(6영역 base/elem/count). 자체 누적삽입 함수 `cumulative_below()`를
따로 구현해 모듈의 `running_delta`와 무관하게 새 주소를 재유도했다.

probe: `docs/history/laps/probes/20260918_lap388_middle_g2_layout_part_ab_acceptance_probe.py`
→ **rc0, `failures=[]`**. 검사 N 스윕 = 1200/1201/1500/2400/4001/9601/9904/40000/123457.

## 판정: **ACCEPT** (layout 계산기 단위 승인일 뿐 — 제품/런타임/마일스톤 승인 아님)

| | 검사 | 결과 |
|---|---|---|
| G1 | 원본 EXE 바이트에서 ground fact 재확인 | PASS(아래 신규 증거) |
| G2 | BULK start/length/end가 Astra 3식과 9개 N에서 일치 | PASS |
| G2b | N=1200 identity `0x892410`/`0xE397C`/`0x975D8C` | PASS |
| G3 | 두 alias가 **일반 mapper**에서도 같은 값으로 떨어짐 | PASS |
| G4 | N=4001 `0xD97DE8`/`0xED2AA` 바이트 일치 | PASS |
| G5 | PlayerStruct base/end/stride/count + 자체 재유도 | PASS |
| G6 | sidecar 5개 fit·unit_pool 제외·per-slot 14B | PASS |
| G7 | `mapped_offset` 의미론(동일블록 항등/교차보정/거부) | PASS |
| G8 | 회귀(N=1200 artifact 항등·SHA거부·축소거부·suffix) | PASS |
| G9 | **반증력 검사**(틀린 구현 2종을 재현해 probe가 잡는지) | PASS |

### 이번 lap의 **신규 증거** — 핀을 바이트로 승격

lap385~387은 `BULK_OLD_LENGTH=0xE397C`와 `0x892410`을 **전사된 핀**으로 사용했다.
이번 lap이 원본 EXE(`b56986e0…c9c08a8ac` 재해시 확인)를 직접 파싱해
save site `0x440F02`(파일 오프셋 `0x40F02`)와 load site `0x4412DC`(`0x412DC`)
**양쪽 모두** ±`0x40` 창 안에서 두 즉시값 `0xE397C`·`0x892410`의 리틀엔디언 4바이트가
**실재함을 실측**했다(섹션표 재파싱으로 VA→오프셋 변환). 4/4 present.

- **fail-open(정직하게 남긴다):** 이 검사는 **바이트 창 존재성**이지 명령어 디코딩이 아니다.
  두 즉시값이 그 창에 실재함은 확정했으나, 그것이 정확히 `push`/`fread`의 해당 피연산자라는
  **명령어 수준 해석은 lap385 §3-5의 주장 그대로 두었고 이번 lap이 재디코딩하지 않았다.**

### G3 — 이번 검수의 핵심 교차검증

`bulk_state_base`/`bulk_end`가 세 property 안에서만 맞는 게 아니라
**모듈이 그 주소를 알지 못하는 일반 경로 `map_va()`** 에서도 같은 값이 나온다:
- `map_va(0x892410, n).new_va == bulk_state_base(n)` — `0x892410`은 `unit_pool`의 반개구간
  **배타적 끝**인 동시에 그 위 foreign gap의 **포함적 첫 바이트**인데, 두 해석이 모든 N에서
  같은 새 주소로 수렴한다(alias의 정합성).
- `map_va(0x975D8C, n).new_va == bulk_end(n)` — old BULK end는 모듈에 상수로 들어 있지 않은
  주소인데도 일반 사상 결과가 `start+length`와 정확히 일치한다. 즉 "품은 영역 5개" 모형이
  모듈 자신의 기하와 **독립적으로 자기정합**이다.

### G5 — PlayerStruct 이동률 1892의 독립 재유도

PlayerStruct base `0x956770` 아래의 성장 영역은 unit_pool(1880)+existence(2)+age(2)+catA(4)
+catB(4) = **1,892 B/slot**이며 `active_slot_list`는 **위에** 있다. probe가 이를 따로 계산해
모듈의 `new_base`와 전 N에서 일치시켰고, 관측된 이동률 집합은 정확히 `{1892}`였다.
이는 BULK start의 1880·BULK end의 1894와 **모두 다른 세 번째 비율**이라, 비율 혼동이
있었다면 즉시 드러난다(G9-ii로 반증력도 확인: 1880 적용 시 `0xE5C148` vs 정답 `0xE64494`).
span은 전 N에서 `8*0x3ABC` 불변, `[new_base,new_end)` ⊂ mapped BULK, host block은 항상
`gap_after_category_slot_list_b`.

### G7 — `mapped_offset`이 naive 차분이 아님을 수치로 고정

N=4001에서 `mapped_offset(0x892410, 0x956770)` = `0xCC6AC`, naive 차분 = `0xC4360`,
**보정량 = 33,612 = (2+2+4+4)×2801** — 사이에 낀 네 성장 영역과 정확히 일치. 즉 bulk-relative
PlayerStruct 오프셋은 확장 시 실제로 달라지며 모듈이 그것을 바르게 계산한다.

## 게이트 실측

- `make check` → **rc0, `715 passed in 117.53s`** + Ruff `All checks passed!` + compileall +
  mypy 10파일 `Success` + `CONTEXT_PASS`.
- `bash checks/safety.sh check` → **`SAFETY_PASS`**.
- 원본 `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac` **불변**.
- frozen `offline_storage_v1.py` `e9d84513…9f8cc` **무변경**.
- 검수 대상 SHA가 lap387 기록과 **동일**함을 확인(다른 산출물을 검수하지 않았다):
  모듈 `1469752c1bb060ed3f16aa4a11d50e5f824fc659c0b7db9485e5ce6711f0c1bd`,
  테스트 `5c220a73aeba818bd89ed2d8eb167daedca6bd46c276301e677f3e5f0bd70c70`.
- 외부 temp artifact도 lap387 기록과 동일: `.pelayout` `38a7148e…36cbc808`(원본에서
  **재생성해 SHA 재현**, 길이 불변), mapping JSON `010224184bc9…7d02987f6d`.
  JSON의 기계값 bulk `new_start=14253544(0xD97DE8)`/`new_length=971434(0xED2AA)`/
  `new_end=15224978(0xE85092)`, player_struct `new_base=15090836(0xE64494)`/
  `new_end=15211124(0xE81A74)` — 전부 probe 독립 산출값과 일치.
- 게임 실행 0회, 원본/참고/공유 저장소 쓰기 0건, 커밋 0건(LOOP_ALLOW_COMMITS 미설정).

## 계약 판정

- **§3 계약 5번 = CLOSED (계산기/모듈 단위)**. bulk-relative span·count/endpoint alias·
  PlayerStruct span이 전부 절대 주소 재계산이 아니라 기준점 상대 유도로 구현됐음을 독립 확인.
  `BULK_OLD_LENGTH`/`PLAYER_STRUCT_BASE`는 **입력 ground fact**(핀, 이번 lap이 바이트 확인)이고
  *성장·새 주소*는 전부 유도값이므로 계약 5번 위반이 아니다 — 이 해석을 명시해 후속 lap의
  재논쟁을 막는다.
- 계약 1·2·3·4·6·7은 lap383~385 검수 계보에서 이미 ACCEPT. 따라서 **§3 전체 계약은
  계산기 단위로 CLOSED**이며, 이 레이아웃 카드는 **여기서 종결**한다(Astra 지시대로 재수리
  체인 없음). handoff `G2_LAYOUT_ALIAS_EXPOSURE_HANDOFF_LAP385.md`는 **소비됨**.
- **`native_route_judgment`는 변경 없음(NO_GO 유지).** 이 ACCEPT는 "현재 artifact에서
  bounded native slot>=1200 lifecycle/save 마일스톤을 낼 수 없다"는 Astra 판정을 **뒤집지
  않으며 근거를 강화**한다: 계약 5번이 닫혔다는 것은 곧 확장이 길이·주소 **두 하드코딩 push
  즉시값의 fixup과 저장 포맷 변경**을 반드시 요구함을 계산기가 수치로 확정했다는 뜻이다.
  lap379 Sol의 integration/broad-patcher/runtime NO-GO도 유효하다.
- **G2 8인5000은 미완료.** lifecycle/economy/save/LAN 증거 0건. 이 카드 종결은 제품 승인도
  런타임 승인도 마일스톤 승인도 아니다. `4001/9601/9904`는 공학 테스트 값이지 최종 용량이 아니다.

## 남은 사각 (전부 수치 영향 0, 수리 카드 발행하지 않음 — Astra `not_allowed`)

- **N15:** STATUS lap387 항목이 `bulk_length` 유도를 "regions[1:5] delta 합"으로 적었으나
  실제 코드는 `regions[1:]`(sidecar **5개**)다. `regions[1:5]`(4개) 해석이면 N=4001 길이가
  `0xEBCC8`이 되어 핀 `0xED2AA`와 **불일치**한다(G9-i로 확인). 코드가 옳고 STATUS 문구가
  드리프트였다 — 이번 lap이 STATUS를 정정했다.
- **N16:** 저장소 테스트 `test_player_struct_layout_is_derived_via_mapped_offset_not_reused_old_span`
  은 구현이 실제로 호출하는 `mapped_offset`에 대조하므로 **순환**이다. `mapped_offset` 자체의
  공통 오류는 잡지 못한다. 이번 lap의 G5(독립 `cumulative_below` 재유도)가 그 구멍을 메웠다.
- **N17:** 저장소 `mapped_offset` 테스트는 동일블록 항등 + 사상불가 거부만 본다. "검증만 하고
  naive 차분을 돌려주는" 구현은 그 둘을 **통과**한다. 이번 lap의 G7(교차보정 33,612 실측)이
  구현이 실제로 옳음을 확인했다. 테스트 공백은 기록만 한다.
- **N18:** Astra `scope`가 artifact 산출물로 이름 붙인 "mapped-field-minus-mapped-base offsets"가
  mapping JSON에 **명시 필드로는 없다**. 다만 유도 가능하며(`15090836-14253544=837292=0xCC6AC`,
  G7 실측값과 일치) 값 자체는 이미 정확하다. 기록만 한다.
- **N19:** `bulk_length`는 `regions[1:]`라는 **인덱스**로 "blob 안쪽 5영역"을 고른다. 장래에
  `REGIONS`에 영역이 추가/재정렬되면 조용히 어긋난다. 이번 probe의 G6이 개수 5와 합계 14를
  매 N에서 확인하므로 현재 상태는 안전. 리팩터 제안은 하지 않는다(범위 밖).

## 이번 lap이 만든 파일 (전부 uncommitted — LOOP_ALLOW_COMMITS 미설정, 해시로 이력 보존)

- `docs/history/laps/probes/20260918_lap388_middle_g2_layout_part_ab_acceptance_probe.py`
  `529ef563edb489f0696ce62f7aa8453618285d07cf068bd290435f203c4d3201` (읽기전용 probe, 재실행 rc0 재현)
- `docs/history/laps/20260918_lap388_middle_g2_layout_part_ab_acceptance.md` (이 파일)
- `docs/reports/20260918_G2_LAYOUT_CARD_CLOSURE.md`
  `68569d8cf1b8bb556e4f2b803f5d8ef8a07afe898d2d6e0d06f1a0eeec2230ed`
- `loop/ESCALATE_SOL` `32ac39ba52f256c2a404cf53cc74360ae0ea321bd4b6db858a1d28b850bac066`
- `docs/STATUS.md` 갱신 `7016ba3a5b7129f14b6bd3d29e1861ef58a54421ab4b5d75a0b8d7d262b20d72`
  (129줄, PROMPT의 130줄 상한 이내, `## 지금 막힌 것` 정확히 1개, `CONTEXT_PASS` 재확인)

제품 코드(`patches/**`)·원본·참고·공유 artifact **변경 0건**. 2026-09-18 19:31 KST.

## 다음 한 가지

**이 레이아웃 카드는 종결됐고, 같은 경로의 다음 work 카드는 middle 권한 밖이다.**
Astra 결정 JSON이 (a) alias별 후속 카드를 `not_allowed`로 막았고, (b) "G2를 이 경로로
계속할지는 Astra 판정 사항"이라고 명시했으며, (c) `native_route_judgment`가 다음 runtime을
`None authorized`로 두었다. 따라서 이번 세션은 `loop/ESCALATE_SOL`을 발행하고 종료한다.
승격 작업자가 이어서 판정할 것은 리포트 `docs/reports/20260918_G2_LAYOUT_CARD_CLOSURE.md`와
`loop/ESCALATE_SOL`에 적었다.
