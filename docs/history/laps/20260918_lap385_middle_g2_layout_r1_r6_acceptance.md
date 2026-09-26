# 2026-09-18 | lap 385 | 목표 G2

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5`/high, 중간(middle) tier —
  진단·검수·확인. **게임 코드 hands-on 수정 없음, 게임 실행 없음, 커밋 없음.**
  `docs/MODEL_ROUTING.md` 2026-09-18T17:56 override와 일치.
- 가설: lap384 work가 `G2_STORAGE_LAYOUT_REPAIR_HANDOFF_LAP383.md`의 R1~R6을 실제로 닫았다면,
  각 항목을 **모듈 출력이 아니라 핀된 표/원본 바이트에서 독립 재유도**해도 같은 결론이 나오고,
  lap383이 주장한 수리 전 결함도 **국소 재구현으로 재현**된다.
- 예상 PASS / FAIL 조건: 독립 probe `failures=[]` + `make check`/`safety.sh` PASS + 원본 SHA 불변
  + lap384 기록 SHA 3종 일치. 하나라도 비면 REJECT.

## 변경 파일 / source fingerprint / 커밋

제품 코드 **무변경**. 이번 lap이 만든 것은 읽기전용 probe 2개와 문서뿐이다.

- 신규 probe `…/20260918_lap385_middle_g2_layout_r1_r6_acceptance_probe.py`
  SHA256 `7a4daa69e39166f7a4b806df22fd7a144be6793840f7ad0e168161e89adf8a07`
- 신규 probe `…/20260918_lap385_middle_g2_r5_launch_gate_reachability_probe.py`
  SHA256 `7afb887b856c7dca929c3a2d06c9b5e6ec68b814a8237eadbc1dfc0c4fb504bf`
- 갱신 `docs/work/active/G2_BASE_PRESERVING_STORAGE_OPUS_PLAN_20260918.md` (§3-5 범위 확정)
  SHA256 `1f89510e5ad94295d2e2b82f89fa7a198f57e77670a8173209fdb869c1d51788`
- 신규 `docs/work/active/G2_LAYOUT_ALIAS_EXPOSURE_HANDOFF_LAP385.md`
  SHA256 `9366a1be3602901aac1c0fc168244dcc27278459c9f10fc3793e5ee73fb0c17b`
- 두 probe는 lap339 확정대로 **필수 게이트 밖**이다(pytest testpaths·ruff 대상 밖). 참고로
  `ruff check` 수동 실행은 `All checks passed`.
- 갱신 `docs/STATUS.md`
- uncommitted (LOOP_ALLOW_COMMITS 기본0). 검수 대상 SHA는 lap384 기록과 **일치 확인**:
  - `base_preserving_storage_layout_v1.py` `7ae85ef50ae324a42a16f8cb251b05498f22f18a7d9f84d20cd361bf1a136cb2`
  - `test_base_preserving_storage_layout_v1.py` `88672c65a91185526296a81e25008b352756eda2bf6569ba8d3a4b3fc8ccee9a`
  - frozen `offline_storage_v1.py` `e9d84513f6a53e27135a7e19a546a8a72165804d1041f9a23719fc7cb249f8cc` **무변경**

## 원본 SHA / 환경 / fixture

원본 `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac` 불변(검수 전/후 확인).
게임 실행·활성 플레이어·지도·군대 **없음** — 이 카드는 순수 PE 레이아웃 계산기 검수다.
원본/참고/공유 저장소 쓰기 0, residue 0.

## 실행 명령 / 수치

- `python3 docs/history/laps/probes/20260918_lap385_middle_g2_layout_r1_r6_acceptance_probe.py`
  → **rc0 `failures=[]`** (31개 단언).
- `python3 docs/history/laps/probes/20260918_lap385_middle_g2_r5_launch_gate_reachability_probe.py`
  → **rc0 `failures=[]`** (CLI 진입점 11개 전수).
- `make check` → **rc0 `681 passed 128.54s`** + Ruff `All checks passed` + compileall +
  mypy 10파일 `Success` + `CONTEXT_PASS`.
- `bash checks/safety.sh check` → **`SAFETY_PASS`**.

## 항목별 판정 — R1~R6 전부 ACCEPT

독립 재유도 원칙: 핀된 여섯 영역 표를 probe 안에 **따로 전사**하고(모듈 상수 미사용),
수리 **전** 알고리즘을 국소 재구현해 lap383의 결함 주장을 먼저 재현한 뒤 수리를 판정했다.

| R | 판정 | 독립 근거 |
|---|---|---|
| R1 | ACCEPT | 수리 전 알고리즘 재구현으로 결함 **재현**: `map_va(0x66B790+0x758*1199, 100)` → `kind="region"`/`unit_pool`/`new_va=0x891CB8`인데 unit_pool 새 범위는 `[0x66B790,0x6995F0)`이고 `0x891CB8`의 **실제 새 주인은 `gap_after_active_slot_list`(`[0x778EC2,0xE8F5B8)`)** 였다 — lap383 주장과 블록 이름까지 일치. 현행은 `layout(1199)`/`layout(0)`/`layout(-1)`/`map_va(...,1199)` 전부 `ValueError`, `layout(1200)`은 정상 수락. |
| R2 | ACCEPT | 외래 블록 delta를 **모듈을 쓰지 않고** `cumulative_insert_below`로 재계산해 대조: N=4001 gap 4개 `5,265,880/5,277,084/5,299,492/5,305,094`, rsrc `5,308,416` — 5개 전부 `.delta` 필드 자체와 일치(N=9601/9904도 동일). 확장 시 delta 0인 외래 블록 **0개**. `RegionLayout.delta`는 주소 이동이 아니라 span 증가임을 소스에 명시(`NOT an address shift`). |
| R3 | ACCEPT | 32비트 경계를 **독립 이분탐색**으로 재유도 → 첫 초과 용량 **N=2,259,703**(lap383/lap384 값과 일치). 모듈은 2,259,702 수락·2,259,703 `OverflowError`. 소스에서 `IMAGE_BASE + 2**32` 형태는 **소멸**했다. |
| R4 | ACCEPT | 지정 temp 산출물 2개 실재·SHA 일치(`38a7148e…36cbc808`, `fb7f9e83…d11605b18`). 나아가 `.pelayout` 바이트를 **핀된 원본에서 재생성해 SHA 재현**했고, 독립 PE 파싱으로 파일 길이 불변·`.rsrc` RVA 이동량 `5,308,416`(독립 layout과 일치)·SizeOfImage가 새 `.rsrc` 끝을 덮음을 확인. 메인 레포 내 `.pelayout` **0건**. |
| R5 | ACCEPT (범위 명시) | 아래 별항 참조. |
| R6 | ACCEPT | 36개 probe를 독립 생성해 전수 확인: unmappable **정확히 1개**이고 그 주소가 `0x0066B78F`, 나머지 35개 전부 N=1200 항등. 테스트가 그 주소를 상수로 고정(blanket skip 소멸). |

### R5 — "실제 launcher 진입점"인지 엄밀 판정 (STATUS가 지정한 항목)

**정직한 범위:** lap384의 pytest는 `validate_original_source`를 **직접** 부른다.
`prepare()`/`check_runtime()`/CLI 자체를 부르지는 **않는다**. 따라서 "prepare 진입점을
실행했다"고 읽으면 **과대 주장**이다. 이번 lap이 그 빠진 고리를 정적으로 메웠다:

`runtime_main` 디스패치가 부르는 진입점 **11개 전수**에 대해 호출 그래프 도달성을 계산한
결과, Popen에 도달 가능한 진입점 **8개 모두에서 `validate_original_source`가 Popen보다
엄격히 먼저** 온다(`prepare` 0번째 호출 vs Popen 26번째, `smoke` 0 vs 12, `g1_baseline`
0 vs 45, `g1_r1_load_origin` 0 vs 18, `g1_r1_candidate_load_origin` 0 vs 29,
`g1_s1_original_load_evidence` 1 vs 3, `g1_presentation_trace` 1 vs 20, `check_runtime`
8 vs Popen 도달불가). 나머지 3개(`g1_s1_load_evidence`/`_manifest`/`_prefix_pids`)는
Popen에 도달하지 않는다. ⇒ **게이트는 모든 실행 경로에서 우회 불가**이므로 그 함수를
부른 것은 handoff §R5 (a)의 실질을 만족한다.

라이브 재현도 했다: 확장 artifact를 소스 EXE 자리에 놓으면 `RuntimeSafetyError`
(`SHA-256 mismatch`) 거부 + `Popen` **0회**. **대조군**으로 N=1200 artifact(원본과
바이트 동일)는 **같은 게이트를 통과**한다 ⇒ 게이트가 디렉터리가 아니라 **내용**을 본다는
증거다. 단, 이것이 증명하는 것은 "이 저장소의 launcher가 확장 artifact를 원본으로 받지
않는다"까지이고, **artifact가 어디서든 실행 불가**라는 주장은 아니다.

## 계획 §3-5 판정 (lap384가 이 tier에 넘긴 결정)

계획 문서 `G2_BASE_PRESERVING_STORAGE_OPUS_PLAN_20260918.md`에 **§3-5 절을 신설해 확정**했다.
요지: **Part A(`0x892410` 3중 alias 노출)는 이 카드에 남기고, Part B(PlayerStruct/bulk span)는
신규 별도 카드로 뺀다. descope 아님 — 계약 5번은 필수이고 §3 전체 계약은 OPEN이다.**

판정을 가른 이번 lap의 실측: 핀된 save `0x440F02`(length `0xE397C`, source `0x892410`)와
load `0x4412DC` 쌍이 정의하는 bulk 블록 `[0x892410,0x975D8C)`에 대해

- unit_pool은 bulk **아래**(추가 slot당 1,880 B) — 별도 roster 저장,
- existence/age/catA/catB/active_slot_list **5개는 bulk 안쪽**(추가 slot당 합계 14 B).

⇒ 확장은 `0x892410`을 밀어 올리는 **동시에** 고정길이 blob **내부를 불린다**.
N=4001이면 새 bulk start `0xD97DE8`, 필요 길이 `0xED2AA`. 둘 다 **하드코딩 push 즉시값**이고
현행 layout 모듈은 **둘 다 모형화하지 않는다.** Part B가 이름 붙이기가 아니라 두 번째
좌표계 모형화인 이유가 이것이다.

## 회귀 / 남은 위험 / 다음 한 가지

- 이 ACCEPT는 **layout 계산기 단위 승인**이다. 제품 승인도, 런타임 승인도, 마일스톤
  사람 승인도 **아니다**. G2 8인5000은 미완료(integration/lifecycle/economy/save/LAN 없음).
- lap379 Sol의 integration / automatic broad patcher / runtime NO-GO는 **유효**하며,
  이번 bulk 실측은 그것을 뒤집지 않고 **강화**한다. tail 참조 이전 부채 17,584 linear
  후보도 그대로다.
- **Astra 큐(승인 대기, 이번 lap은 막지 않고 독립 작업을 계속했다):** 고정길이 bulk blob이
  확장 대상 5개 영역을 품고 있으므로 layout mapper만으로는 저장 호환 확장이 원리적으로
  불가능하다(길이·주소 즉시값 fixup + 저장 포맷 변경 필수). G2를 이 경로로 계속할지 판정 요청.
  **새 불가능 증명이 아니다.**
- lap383 handoff는 이번 ACCEPT로 **소비**됐다. 신규 handoff
  `G2_LAYOUT_ALIAS_EXPOSURE_HANDOFF_LAP385.md`(Part A) 발행.
- 다음 한 가지: 다음 work(Sonnet5/high)가 Part A를 구현한다.
