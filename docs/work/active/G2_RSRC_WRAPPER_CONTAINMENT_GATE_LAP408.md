# W7 — `.rsrc` cave wrapper 컨테인먼트 앵커 (lap408 middle 발행)

- 발행: 2026-09-20 lap408 middle(Claude Code claude-opus-5/high). 게임 코드 변경 0, 게임 실행 0.
- 근거: `docs/history/laps/20260920_lap408_middle_g2_w6_gate_verification.md` §W7.
- 처리 방식은 `G2_STRATEGY_DIRECTION_LAP404.md` §C-3과 동일 —
  **REJECT가 아니다.** 현재 실측은 PASS이고, 없는 것은 회귀를 막을 **앵커**다.
- 담당: work(Claude Code claude-sonnet-5/high).
  단일 작성자 파일: `patches/population/test_g2_full_capacity_persistence_compat_v1.py`.

## §0 선행 — W6는 CLOSED

W6(`G2_FULL_CAPACITY_COVERAGE_GATE_LAP406.md`)의 G-c'·G-d는 lap408이 독립 검수해
**충족 확인**했다(`make check` 783 passed = lap406 779 + 신규 4건, 역주입 포착 확인).
W6는 다시 열지 않는다. **이 카드는 W6가 닫지 못한 인접 사각 하나만 다룬다.**

## §1 결함 — 커버리지 앵커가 `.rsrc` cave에 닿지 않는다

W6가 추가한 G-c'는 **재배치 블록** `[regions[0].new_start, regions[-1].new_end)`
= `[0x0108C000, 0x017C612C)` 만 측정한다. 그런데 persistence/compat이 실제로 **코드를
써 넣는 곳은 `.rsrc` cave**이고, 그 cave는 블록 **밖**이라 새 앵커의 사정거리에 없다.

lap408 실측(N=4001, compat). `.rsrc` = `0x017C7000`–`0x017C9700`(VirtualSize `0x2700`):

| wrapper | cave offset | 코드 길이 | 끝 | 다음 경계 | 여유 | 크기 가드 |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| `LOAD_WRAPPER` | `0x2300` | 162 | `0x23A2` | `0x2400` | 94 | **있음**(`>0x100` raise) |
| `SAVE_HEADER` | `0x2400` | 23 | `0x2417` | `0x2500` | 233 | **없음** |
| `LOAD_HEADER` | `0x2500` | 74 | `0x254A` | `0x2600` | 182 | **없음** |
| `LEGACY_COPY` | `0x2600` | **207** | `0x26CF` | `0x2700`(`.rsrc` 끝) | **49** | **없음** |

`g2_full_capacity_persistence_compat_v1.build_candidate` 182~187행은 세 wrapper를
`out[raw+offset : raw+offset+len(code)] = code` 로 **길이 검사 없이** 기록한다.
`_emit_compatible_load_wrapper` 만 자체 가드를 갖는다(142~143행).

**왜 지금 문제인가:** `LEGACY_COPY`는 cave의 마지막 슬롯이라 초과하면 `.rsrc`
VirtualSize **밖**으로 나간다 ⇒ **매핑되지 않은 VA에 코드가 놓이는 lap402 D1과 동일한
결함 계열**이 되고, 무징후다. 그 길이는 용량이 아니라 **재배치 영역 수/종류에 비례**한다
(영역당 `mov esi,imm32`/`mov edi,imm32` 5B씩, counted 영역은 1쌍 추가) — 현재 5개 영역에서
207 B, 여유 **49 B**. 영역을 2~3개만 더 늘려도 조용히 넘친다.

비교: persistence(비compat)에는 이미 앵커가 있다 —
`test_wrappers_call_original_stream_plus_five_sidecars`가
`rsrc.Misc_VirtualSize >= RSRC_CODE_END_OFFSET`와 실행 속성을 단언한다.
**compat 전용 테스트에만 대응 단언이 없다.**

## §2 요구 G-e (필수)

`test_g2_full_capacity_persistence_compat_v1.py`에 N=4001 기준으로 다음을 pytest로 강제한다.

1. **cave 내 컨테인먼트.** 네 wrapper(`LOAD_WRAPPER`, `SAVE_HEADER`, `LOAD_HEADER`,
   `LEGACY_COPY`) 각각에 대해 `offset + len(emitted_code) <= RSRC_COMPAT_END_OFFSET`.
   길이는 **실제 emit 함수의 산출물**에서 얻는다(상수 재기입 금지 — 동어반복이 된다).
2. **상호 비중첩.** 네 wrapper의 `[offset, offset+len)` 구간이 서로 **겹치지 않는다**.
3. **섹션 매핑.** 네 wrapper의 시작 VA와 **끝 VA(포함)** 가 모두 후보 자신의 `.rsrc`
   `[VA, VA+VirtualSize)` 안이다. 시작만 보지 말 것 — 시작만 보는 단언은 §1의 초과를 놓친다.
4. **실행 속성.** `.rsrc` `Characteristics & RSRC_EXECUTE_CODE_FLAGS == RSRC_EXECUTE_CODE_FLAGS`.

## §3 완료 조건

1. **역주입 1회 확인(W6 §4.1과 같은 방식).** 예: `_emit_legacy_copy_wrapper`가 50 B 이상
   더 긴 코드를 내도록 일시 개조하거나 `RSRC_COMPAT_END_OFFSET`를 일시 축소해
   **새 단언이 실제로 FAIL하는지** 1회 관찰하고 그 관찰을 기록한다.
   **역주입본은 커밋/보존하지 않는다**(`/tmp`에서만).
2. `make check` rc0(현재 783 passed 기준 + 신규분), `SAFETY_PASS`, 원본 2경로 재해시 불변
   (`b56986e0…08a8ac`).
3. 신규 테스트가 현재 후보에서 통과할 것.

## §4 범위 밖 — 하지 말 것

- **게이트를 통과시키려고 wrapper 배치/오프셋/`RSRC_COMPAT_END_OFFSET`/후보 SHA를 바꾸지
  않는다.** 현재 배치는 PASS이며 이 카드는 **테스트만** 추가한다.
  후보 SHA pin 4건(`c3bd799f…`/`20b95a94…`/`1e90f62f…`/`4331d9cd…`)이 바뀌면 그것은 회귀다.
- persistence(비compat) 쪽 기존 앵커를 건드리거나 중복 작성하지 않는다.
- W6·lap406 probe를 다시 열지 않는다. `docs/history/laps/probes/`를 필수 게이트에 편입하지
  않는다(lap339 성질 유지).
- N19/되물음(strict cap)과 묶지 않는다 — **사용자 답변 대기**(§D P3)다.

## §5 완료 직후 (미루지 말 것)

이 카드를 닫는 즉시 `G2_STRATEGY_DIRECTION_LAP404.md` §D **P1 — marked compat
(`4331d9cd…`) 경로를 near-4000 live 규모에서 반복(실제 게임 실행)** 을 착수한다.

lap408 판정(기록 §③)에 따라 **다음 회차는 실제 실행 증거를 만들어야 한다.** W6 때
게이트만 추가하고 P1을 미룬 채 기록 없이 종료한 일(N20)을 반복하지 않는다.
P1을 착수하지 못하는 사유가 생기면 그 사유를 lap 기록에 남긴다.
