# 2026-09-20 | lap 408 | middle (Claude Code claude-opus-5/high) — W6 게이트 2건 독립 검수 + 미기록 세션 provenance

## 목표

`docs/work/active/G2_FULL_CAPACITY_COVERAGE_GATE_LAP406.md`(W6)가 지시한 게이트 2건
(G-c' N=4001 섹션 커버리지 앵커, G-d persistence N=1200 byte-equal 앵커)의 **실재·정확성·
포착력**을 독립 검수하고, 남은 같은 계열 사각을 측정해 work 카드로 인계한다.
컨펌 역할이므로 게임 코드/제품 바이트는 고치지 않는다.

## lap 번호 주의 (N18 계열, 수치 영향 0)

- 러너 `loop/.lap_counter` = **408**(2026-09-20 21:22:25 기록). PROMPT §머리말 5행의
  "현재 파일 값이 이번 runtime lap 번호"에 따라 이 기록은 **lap408**이다.
- 세션 시작 시 주입된 runtime evidence 머리글은 `lap=407`로 표시했다(증분 전 값으로 보인다).
  **원문을 고쳐 쓰지 않고 차이만 기록한다.** lap407 번호의 기록 파일은 존재하지 않는다.

## 신규 사실 — W6 작업은 이미 수행돼 있었고, 그 세션의 lap 기록이 없다 (N20)

`find -newermt` 실측(`.omc/`·캐시·로그 제외):

| 파일 | mtime |
| --- | --- |
| `docs/history/laps/20260920_lap406_middle_..._review.md` | 21:05:33 (lap406 종료) |
| `patches/population/test_g2_full_unit_capacity_v1.py` | **21:11:52** |
| `patches/population/test_g2_full_capacity_persistence_compat_v1.py` | **21:11:59** |
| `loop/.lap_counter` (408로 증분) | 21:22:25 (이번 세션 시작) |

즉 lap406 종료 이후·이번 세션 시작 이전에 **W6이 지정한 단일 작성자 파일 2개가 정확히
수정**됐으나 그 회차의 `docs/history/laps/` 기록·STATUS 갱신이 **없다**.

- **N20(신규, provenance):** 실행된 work 회차가 lap 기록 없이 종료됐다. lap404가 제기한
  N18(자칭 lap 번호 불일치)과 **같은 계열**이며, 이번에는 번호 불일치가 아니라 **기록 자체의
  부재**다. 변경 내용 자체는 아래 C1~C3에서 독립 검증했으므로 **수치·바이트 영향은 0**이고,
  결함은 이력 추적성에 국한된다. 파일을 고쳐 쓰거나 소급 기록을 날조하지 않는다.
- 이 사실 때문에 이번 lap의 ④2(이전 바퀴 검수) 대상은 lap406이 아니라 **이 미기록 회차의
  산출물**이 된다.

## 가설 / 측정식

- H1: W6 §1 G-c'와 §2 G-d가 요구한 앵커가 실제로 존재하고, 요구대로 **섹션 합집합**으로
  측정하며, 세 N=4001 후보를 전부 대상으로 한다.
- H2: 그 앵커들이 **실제로 회귀를 잡는다**(W6 §4.1 의도적 역주입 1회 확인).
- H3: 필수 게이트가 통과하고 원본이 불변이다.
- 측정식: 앵커 존재 3+1건, 역주입 시 assert 발생, `make check` rc0, 원본 2경로 SHA 불변.

## 변경 파일

- 신규: 본 기록, `docs/work/active/G2_RSRC_WRAPPER_CONTAINMENT_GATE_LAP408.md`(W7 카드)
- 갱신: `docs/STATUS.md`, `loop/ESCALATE_SOL`(§13)
- **제품 코드/바이너리/게임 실행/메모리 쓰기/커밋 0.** 역주입 스크립트는 `/tmp`에만 두고
  저장소에 보존하지 않는다(W6 §4.1 지시 그대로).

## 실행 명령

```
find . -newermt "2026-09-20 21:06" -type f (캐시/.omc/logs 제외)
sha256sum Syw2plus/syw2plus_original.exe ../Syw2plus/syw2plus_original.exe
PYTHONPATH=. python3 /tmp/lap408_gate_catching_power.py    # 역주입, 보존 안 함
make check ; bash checks/safety.sh check
```

## 항목별 판정

### C1 G-c' 커버리지 앵커 실재 — ACCEPT

`patches/population/test_g2_full_unit_capacity_v1.py`에 신규 3건:

- `test_n4001_data_section_covers_every_relocated_region` (제품 후보)
- `test_n4001_persistence_candidate_data_section_covers_every_relocated_region`
- `test_n4001_persistence_compat_candidate_data_section_covers_every_relocated_region`

세 건 모두 공통 헬퍼 `_assert_relocated_block_covered_by_sections`를 거치고, 그 헬퍼는
`_section_intervals`로 **전 섹션**을 열거한 뒤 `_uncovered_bytes`로 합집합 커버리지를
계산한다 — W6 §1의 "`.data` 하나가 아니라 섹션 합집합" 요구와 일치한다. 기존
`test_n1250_data_section_covers_every_relocated_region`은 **삭제되지 않고 유지**됐다(§1 요구).

`_uncovered_bytes` 알고리즘 검토: 구간을 시작값으로 정렬하고 `cursor`를 단조 증가시키며
`low=max(low,cursor)`, `high=min(high,end)`로 클램프한다 ⇒ 중복 구간 이중계산 없음,
`[start,end)` 밖 구간 무시, 섹션 사이 빈틈은 covered에 들어가지 않아 uncovered로 남는다.
**논리 결함 없음.**

### C2 G-c' 포착력(W6 §4.1 역주입) — ACCEPT (단서 1건, 결함 아님)

lap402 D1과 **같은 결함 계열**을 역주입했다: 후보의 `.data` 섹션 헤더 `Misc_VirtualSize`
(헤더 +8)를 **원본 stock 값 `0x00B9FA38`** 으로 되돌린다(= 섹션을 전혀 키우지 않은 회귀).

| 후보 | 실제 후보 baseline | stock VirtualSize 역주입 | 1바이트 축소 역주입 |
| --- | --- | --- | --- |
| `g2_full_capacity_supply5000_owner1200_v1` | PASS | **FAIL(잡음)** | **FAIL(잡음)** |
| `g2_full_capacity_persistence_v1` | PASS | **FAIL(잡음)** | **FAIL(잡음)** |
| `g2_full_capacity_persistence_compat_v1` | PASS | **FAIL(잡음)** | PASS(아래 단서) |

역주입 시 assert 메시지는 `7577900 relocated bytes in [0x0108c000, 0x017c612c) are outside
every section` — lap402 D1이 보고한 미매핑 현상을 **정확히 재현**한다. 즉 새 앵커는 D1
계열 회귀를 제품 용량에서 실제로 막는다.

**단서(게이트 결함 아님):** compat 후보만 1바이트 축소를 잡지 못한다. 원인은 측정됐다 —
compat은 `.data` 끝을 블록 끝보다 **3,544 B**(`0x017C612C`→`0x017C6F04`) 더 잡아 flag를
꼬리에 놓기 때문이다. 블록 커버리지 관점에서 1바이트 축소는 실제로 무해하며, 그 꼬리는
`test_n4001_adds_header_gate_and_writable_bss_flag`의 `.data end >= flag+4`가 따로 앵커한다
(`flag_va = 0x017C6F00`, `.data end = 0x017C6F04` ⇒ 1바이트만 줄어도 그 단언이 FAIL).
**책임 분담이지 사각이 아니다.**

### C3 G-d N=1200 항등 앵커 — ACCEPT

`test_g2_full_capacity_persistence_compat_v1.py`에 신규
`test_n1200_compat_and_persistence_are_byte_equal_to_the_product_candidate`가
`persistence_v1(original,1200)`·`persistence_compat_v1(original,1200)`를
`g2_full_capacity_supply5000_owner1200_v1.build_candidate(original,1200)`와 **byte-equal**로
단언한다 — W6 §2 요구 그대로다. 독립 재측정: 세 후보 N=1200 **byte-equal 성립**, 음성 대조군
(파일 오프셋 `0x0001B56E` 1바이트 XOR)은 정상적으로 **차이 발생** ⇒ 단언이 공허하지 않다.
기존 `test_n1200_is_byte_identical`(재배치 단계 원본 항등)과 중복되지 않는다(§2 금지사항 준수).

### C4 W6 §3 범위 밖 금지사항 준수 — ACCEPT

- 후보 SHA pin 4건(`c3bd799f…`/`20b95a94…`/`1e90f62f…`/`4331d9cd…`) **갱신 흔적 없음**:
  `test_n1250_supply5000_combined_hash_is_pinned`와
  `test_n4001_product_capacity_candidate_is_structurally_pinned`의 pin 값이 lap406 기록과 동일.
- 레이아웃/상수/후보를 고쳐 게이트를 통과시킨 흔적 없음 — 21:11 변경은 **테스트 파일 2개뿐**
  (C1의 mtime 실측). `patches/population/`의 제품 모듈은 어느 것도 21:06 이후 수정되지 않았다.
- lap406 probe는 필수 게이트에 편입되지 않았다(`docs/history/laps/probes/`는 pytest testpaths
  밖 — lap339 성질 유지).

### C5 필수 게이트 / 원본 — ACCEPT

- `make check` **rc0, 783 passed** 528.47s. lap406의 779 → **+4**로 신규 앵커 4건
  (커버리지 3 + G-d 1)과 **정확히 일치**한다. Ruff `All checks passed`, compileall,
  mypy 10 파일 `Success`, `CONTEXT_PASS`.
- `bash checks/safety.sh check` → **`SAFETY_PASS`**.
- 원본 2경로 재해시 **불변**: `Syw2plus/syw2plus_original.exe`,
  `../Syw2plus/syw2plus_original.exe` 모두 `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`
  (lap406 기록값과 동일).

### C6 종합

**W6 §1·§2·§3·§4.1·§4.2는 전부 충족됐다 — 카드 W6는 이번 검수로 CLOSED.**
단 §4.3("완료 후 즉시 §D P1로 넘어간다")은 **미이행**이다: 21:11 회차는 게이트만 추가하고
P1(near-4000 live 반복)을 착수하지 않은 채 종료했으며 기록도 남기지 않았다(N20).

## 신규 결함 — W7: `.rsrc` cave wrapper 컨테인먼트 앵커 부재 (같은 D1 계열, 현재는 PASS)

G-c'는 **재배치 블록** `[regions[0].new_start, regions[-1].new_end)` = `[0x0108C000,0x017C612C)`
만 측정한다. persistence/compat이 실제로 **코드를 써 넣는 `.rsrc` cave는 그 블록 밖**이라
새 앵커의 사정거리에 없다. 실측(N=4001, compat):

`.rsrc` = `0x017C7000`–`0x017C9700`(VirtualSize `0x2700`, `RSRC_COMPAT_END_OFFSET`와 동일)

| wrapper | cave offset | 코드 길이 | 끝 | 다음 경계 | 여유 | 크기 가드 |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| `LOAD_WRAPPER` | `0x2300` | 162 | `0x23A2` | `0x2400` | 94 | **있음**(`>0x100` raise) |
| `SAVE_HEADER` | `0x2400` | 23 | `0x2417` | `0x2500` | 233 | **없음** |
| `LOAD_HEADER` | `0x2500` | 74 | `0x254A` | `0x2600` | 182 | **없음** |
| `LEGACY_COPY` | `0x2600` | **207** | `0x26CF` | `0x2700`(`.rsrc` 끝) | **49** | **없음** |

- `g2_full_capacity_persistence_compat_v1.build_candidate` 182~187행은 세 wrapper를
  `out[raw+offset : raw+offset+len(code)] = code`로 **길이 검사 없이** 기록한다.
  `_emit_compatible_load_wrapper`만 자체 `len(code) > 0x100` 가드를 갖는다(142~143행).
- `LEGACY_COPY`는 cave의 **마지막** 슬롯이라 초과 시 `.rsrc` VirtualSize(`0x2700`) **밖**으로
  나간다 ⇒ 매핑되지 않은 VA에 코드가 놓이는 **lap402 D1과 동일한 결함 계열**이 된다.
  나머지 둘은 초과 시 다음 wrapper를 덮는다(다른 결함이지만 역시 무징후).
- `_emit_legacy_copy_wrapper(result.regions[1:])`의 길이는 **용량이 아니라 재배치 영역 수/
  종류에 비례**한다(영역당 `mov esi,imm32`/`mov edi,imm32` 5B씩, counted 영역은 1쌍 추가).
  현재 5개 영역에서 207 B이며 여유는 **49 B** — 영역을 2~3개만 더 늘려도 무징후 초과다.
- persistence(비compat) 쪽은 `test_wrappers_call_original_stream_plus_five_sidecars`가
  `rsrc.Misc_VirtualSize >= RSRC_CODE_END_OFFSET`와 실행 속성을 단언해 **이미 앵커가 있다**.
  **compat 전용 테스트에는 대응 단언이 없다**(grep으로 확인).
- **현재 판정은 PASS다**(세 wrapper VA 전부 `.rsrc` 안, 실행 플래그 `0x20000020` 설정 확인).
  없는 것은 회귀를 막을 **앵커**이므로 REJECT가 아니라 **게이트 추가 지시**다 —
  `G2_STRATEGY_DIRECTION_LAP404.md` §C-3과 W6가 쓴 것과 동일한 처리다.

## ③ "비제품 회차 연속 2회" 규칙 판정 (Sol/중간 tier 권한)

PROMPT ③은 "제품 코드/바이너리/실제 실행 증거가 하나도 늘지 않는 회차는 연속 최대 2회,
세 번째가 필요하면 strategy/Sol이 계속할지 중단할지 먼저 판정한다"고 요구한다. 실측:

| 회차 | 성격 | 제품코드/바이너리 | 게임 실행 |
| --- | --- | --- | --- |
| lap404 strategy | 문서 triage | 0 | 0 |
| lap406 middle | 정적 검수 | 0 | 0 |
| 미기록 회차(21:11) | 테스트 2파일 | 0(테스트는 제품코드 아님) | 0 |
| lap408 middle(이번) | 검수·카드 | 0 | 0 |

**판정: 계속(CONTINUE), 단 조건부.** 근거 — (1) 큐의 다음 항목 P1은 그 자체가 **실제 게임
실행 증거를 만드는 작업**이라 규칙이 막으려는 "문서만 쌓기"와 반대 방향이다. (2) 이번 회차가
비제품인 것은 선택이 아니라 **역할 배정**(이번 세션은 middle) 때문이며, 실제로 착수 가능한
work가 이미 대기 중이다. (3) 새 불가능 근거·안전 위험은 나오지 않았다.
**조건:** 다음 회차는 **반드시 work tier**여야 하고 **P1(실제 실행)** 을 착수해야 한다.
또 한 번 비제품 회차가 쌓이면 그때는 strategy(Astra/Fable)가 G2 계속 여부를 판정한다.
이 판정을 `loop/ESCALATE_SOL` §13에 남긴다.

## 미검증으로 남는 것 (제품 완료 아님)

1. **이번 검수도 게임을 실행하지 않았다.** 정적 분석 + 인메모리 후보 빌드 + 역주입뿐이다.
2. §D **P1**(marked compat 경로 near-4000 live 반복) 미착수 — 여전히 382-unit 규모만 통과.
3. §D **P2** diagnostic bridge seeding → 원본 생산 명령 경로 대체 미완.
4. §D **P3** strict cap — INBOX 되물음 2건 **사용자 답변 대기**(N19 정정 포함). 착수 금지.
5. §D **P4** LAN 직렬화/결정론 미검증.
6. **W7**(이 기록이 발행) `.rsrc` cave wrapper 컨테인먼트 앵커 부재.
7. **N20** 미기록 work 회차 — 소급 기록을 날조하지 않으므로 그 회차의 의도/판단 근거는
   **영구 UNKNOWN**으로 남는다. 산출물의 정확성만 C1~C5로 독립 확인했다.
8. N18(자칭 lap410/412 번호 불일치)은 그대로 미해결.
9. 상위 G2 구조통합 blocker와 F4(안전상한 UNKNOWN)는 이번 회차가 건드리지 않았다 — 유지.

## 운영 주의 — STATUS 여유 0줄

이번 갱신 후 `docs/STATUS.md`는 **정확히 130줄**이다(PROMPT 상한 `≤130`을 만족하나 여유 0).
`checks/context_limits.py`의 cap은 여전히 180이라 이 130줄은 **기계 게이트가 아니다**(N14 그대로).
**다음 회차는 STATUS에 줄을 더하기 전에 먼저 압축해야 한다** — PROMPT §머리말대로 원문
SHA256·줄 수와 전체 원문을 `docs/history/laps/`에 보존한 뒤 압축하고,
`## 지금 막힌 것 (Blockers)`는 정확히 하나로 유지한다(이번 회차 확인: 1개).

## 파일 해시 (LOOP_ALLOW_COMMITS=0 — uncommitted 보존)

| 파일 | SHA256 |
| --- | --- |
| 검수 대상 `patches/population/test_g2_full_unit_capacity_v1.py` | `fae16a50ea9c53200fe5511dfeadff9a69a27f3e8ab2d622866c3946091df43a` |
| 검수 대상 `patches/population/test_g2_full_capacity_persistence_compat_v1.py` | `19cf07e7a92c026d789d80191650587f6eb9d8aafbcb82efaeb2c8990b071e21` |
| 원본 EXE(2경로 동일, 세션 시작·종료 양쪽) | `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac` |
| `docs/STATUS.md` (130줄) | `d99533e1b1dfbb1df30e89dd77094e200ac29c92e2d72b37c356f52f8e33cd7f` |
| `docs/feedback/INBOX.md` | `8e6d3c4a6306972eeef165674b76710d3ea2c97b5b1eb29dd5dd2d801a7d607c` |
| `loop/ESCALATE_SOL` (§13 추기, 344줄) | `f3b70986fdf9c5ff9471b7a545173c290c8908a976ade0bbb94701100d04b5a6` |
| `docs/work/active/G2_RSRC_WRAPPER_CONTAINMENT_GATE_LAP408.md` (W7) | `1e9c6b414006c825a594de89559d7062008fdd99d66b7c41f4662b536b4f4c61` |

본 기록 파일 자신의 해시는 자기참조라 적지 않는다(lap406과 같은 처리).

커밋/푸시 **0**(`LOOP_ALLOW_COMMITS=0`, 저장소에 커밋 자체가 없음 —
`git log` = `does not have any commits yet`로 확인).

## 게이트 재실행 범위 주의 (정직한 한계)

`make check` **rc0 / 783 passed** 는 위 문서 편집 **이전**에 측정했다. 이후 변경은
**문서 5개뿐**(STATUS/INBOX/ESCALATE_SOL/W7 카드/본 기록)이고 제품 코드·테스트 코드는
한 줄도 바꾸지 않았다. 문서를 읽는 게이트만 편집 **이후** 재실행했다:
`checks/context_limits.py` → `CONTEXT_PASS`, `checks/safety.sh check` → `SAFETY_PASS`,
`tests/test_patch_loop.py`·`test_loop_context.py`·`test_runtime_evidence.py` → **24 passed**,
`tests/test_model_routing.py` → **22 passed**(STATUS/INBOX/ESCALATE_SOL를 읽는 테스트는
grep으로 이 4개 파일이 전부임을 확인). **전체 `make check`를 편집 후 다시 돌리지는 않았다.**

## 역주입 스크립트 처분

`/tmp/lap408_gate_catching_power.py`(저장소 밖, 커밋·보존 안 함 — W6 §4.1 지시).
재현에 필요한 것은 본 기록 §C2에 전부 있다: 후보의 `.data` 섹션 헤더 **+8**(`Misc_VirtualSize`,
`Name` 바로 뒤)에 stock 값 `0x00B9FA38`을 써 넣고
`test_g2_full_unit_capacity_v1._assert_relocated_block_covered_by_sections(injected, 4001)`를 부른다.
**첫 시도에서 헤더 +0(=`Name`)에 써서 "게이트가 못 잡는다"는 거짓 음성이 나왔고, +8로 고쳐
재측정해 위 표를 얻었다** — 같은 함정을 반복하지 않도록 남긴다.

## 다음 행동

**work(Sonnet5/high)** 회차가 `G2_RSRC_WRAPPER_CONTAINMENT_GATE_LAP408.md`(W7)의 앵커를
추가한 뒤 **즉시 `G2_STRATEGY_DIRECTION_LAP404.md` §D P1(marked compat 경로를 near-4000 live
규모에서 반복, 실제 게임 실행)** 을 착수한다. W7 때문에 P1을 미루지 않는다(W6 §4.3의 재발
방지). P3는 사용자 답변 대기이므로 착수하지 않는다.
