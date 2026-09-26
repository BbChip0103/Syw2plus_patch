# W6 — 전면 재배치 커버리지/항등 게이트 보강 (lap406 middle 발행)

- 발행: 2026-09-20 lap406 middle(Claude Code claude-opus-5/high). 게임 코드 변경 0.
- 근거: `docs/history/laps/20260920_lap406_middle_g2_full_capacity_runtime_review.md` §C3, §C2.
- 이 카드는 `G2_STRATEGY_DIRECTION_LAP404.md` §C-3의 "게이트가 없으면 REJECT가 아니라
  게이트 추가를 work에 지시한다"를 그대로 집행한다. **REJECT가 아니다** — 두 불변식 모두
  현재 실측으로는 성립하며, 없는 것은 회귀를 막을 **앵커**다.
- 담당: work(Claude Code claude-sonnet-5/high). 단일 작성자 파일은
  `patches/population/test_g2_full_unit_capacity_v1.py`와
  `patches/population/test_g2_full_capacity_persistence_compat_v1.py`.

## §1 결함 — 제품 용량 N=4001에 커버리지 앵커가 없다

`test_n1250_data_section_covers_every_relocated_region`은 **N=1250만** 강제한다.
실제 런타임/제품 후보는 **N=4001**(`20b95a94…`, `1e90f62f…`, `4331d9cd…`)이다.
lap402가 REJECT 사유로 삼은 D1은 "블록의 99.24%가 어떤 섹션에도 매핑되지 않음"이었고,
그 결함은 **용량에 따라 다른 값으로 계산되는 `.data` VirtualSize 한 줄**에서 나왔다.
따라서 N=1250 하나만 통과시키는 앵커는 D1 계열 재발을 제품 용량에서 막지 못한다.

lap406 실측(현재는 PASS, 게이트만 없음):

| 후보 | 블록 | 블록 크기 | 섹션 밖 바이트 |
| --- | --- | ---: | ---: |
| N=1250 + supply5000 | `0x0108C000`–`0x012CE012` | 2,367,506 | 0 |
| N=4001 + supply5000 + owner1200 | `0x0108C000`–`0x017C612C` | 7,577,900 | 0 |
| persistence sidecar N=4001 | 동일 | 7,577,900 | 0 |
| persistence compat N=4001 | 동일 | 7,577,900 | 0 |

### 요구 G-c'(필수)

재배치 블록 `[regions[0].new_start, regions[-1].new_end)` 의 **전 바이트**가 후보 자신의
어떤 섹션 `[VA, VA+VirtualSize)` 안에 있음을 **N=4001에서도** pytest로 강제한다.
`.data` 하나가 아니라 **섹션 합집합**으로 측정한다(persistence 후보는 `.rsrc` 꼬리에
wrapper를 놓으므로 단일 섹션 가정을 굳히지 않는다). 세 N=4001 후보
(`g2_full_capacity_supply5000_owner1200_v1`, `g2_full_capacity_persistence_v1`,
`g2_full_capacity_persistence_compat_v1`)를 전부 대상으로 한다.

기존 N=1250 테스트는 **삭제하지 말고 유지**한다.

## §2 결함 — persistence 합성의 N=1200 항등 앵커가 없다

`test_n1200_has_no_compatibility_header`는 `compatibility_header is False`만 본다.
lap406이 측정한 실제 불변식은 더 강하다: **N=1200에서 두 persistence 후보는
supply5000+owner1200 제품 후보와 byte-equal**이며, 원본 대비 차이는 용량과 무관한
상수 편집 **7바이트뿐**이다(`0x0001B56E`/2B owner 250→1200, `0x0001B579`/2B 및
`0x0003FFD4`/3B supply 1500→5000).

### 요구 G-d(필수)

`persistence_v1(original, 1200)` 와 `persistence_compat_v1(original, 1200)` 가
`g2_full_capacity_supply5000_owner1200_v1.build_candidate(original, 1200)` 결과와
**byte-equal**임을 단언한다. 즉 N=1200에서 wrapper/sidecar/헤더 바이트가 **0**임을 강제한다.
(재배치 단계 자체의 원본 항등은 `test_n1200_is_byte_identical`이 이미 강제하므로 중복 금지.)

## §3 범위 밖 — 하지 말 것

- 게이트를 통과시키려고 레이아웃/상수/후보 SHA를 바꾸지 않는다. 현재 후보 SHA 4건은
  lap406이 byte-equal로 재현했다(§C2). 이 카드는 **테스트만** 추가한다.
- 기존 pin(`c3bd799f…`, `20b95a94…`)을 갱신하지 않는다. 값이 바뀌면 그것은 회귀다.
- N19(되물음 1 수치 정정)와 묶지 않는다. strict cap은 사용자 답변 대기(§D P3)다.
- `docs/history/laps/probes/`의 lap406 probe를 필수 게이트에 편입하지 않는다
  (lap339: probe 경로는 어떤 필수 게이트도 실행하지 않으며 그 성질을 유지한다).

## §4 완료 조건

1. 신규 테스트가 **추가 전 실패 → 추가 후 통과**를 보이지 않아도 되는 성질(현재 PASS)이므로,
   대신 **의도적 역주입으로 게이트가 실제로 잡는지 1회 확인**하고 그 관찰을 기록한다
   (역주입본은 커밋/보존하지 않는다).
2. `make check` rc0, `SAFETY_PASS`, 원본 2경로 재해시 불변.
3. 완료 후 즉시 카드 §D **P1(marked compat 경로를 near-4000 live 규모에서 반복)** 으로
   넘어간다. 이 카드 때문에 P1을 미루지 않는다.
