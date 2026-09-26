# 2026-09-20 | lap 391 | 목표 G2 (lap390 W1 독립 검수)

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5` / high, 중간(middle) tier
  — 진단·계획·확인만. 게임 코드 hands-on 수정 없음. `loop/.lap_counter=391`
  (러너 runtime evidence 헤더는 `lap=390`을 실었으나 PROMPT §서두에 따라 **파일 값 391**을 채택).
- 검수 대상: lap390 work(`claude-sonnet-5`/high) 카드 W1 —
  `20260920_lap390_work_g2_ledger_wrap_reachability.md`, 판정 `NOT_FEASIBLE`(이 fixture 한정).
- 가설 / 질문: lap390의 보고 텍스트를 믿지 않고, 같은 `samples.jsonl`에서 M1~M4와 lap389의
  위반 7건을 **독립 재계산**하면 같은 값이 나오는가. 그리고 **M1이 애초에 유효한 랩 검출기인가**.
- 예상 PASS / FAIL 조건(실행 전 고정): 신규 probe가 rc0 `failures=[]`이고 lap390이 보고한
  모든 수치를 재현하면 ACCEPT. 하나라도 어긋나면 REJECT + scoped 수리 handoff.

## 변경 파일 / SHA / 커밋

- 신규 read-only probe 1개(메인 레포):
  `docs/history/laps/probes/20260920_lap391_middle_g2_ledger_wrap_review_probe.py`
  SHA256 `3121b5e1372e6618a6e7e220c2ec9e7387dc5fcb5147e3b9d8d0ae4f3df93af9`
- 외부 보존(temp, 메인 레포 밖):
  `…/temp/Syw2plus_patch/g2_capacity/20260919_owner_transfer_cap/lap391_middle_ledger_wrap_review/probe_output.json`
  SHA256 `2616be2a41a3c3251906e696a4dbd897dceafb844c0753f90027515575d71749`
- **제품코드 변경 0 / 바이너리 변경 0 / 게임 실행 0 / 커밋 0.**
  uncommitted(`LOOP_ALLOW_COMMITS=0`, 사용자 커밋 허용 없음).
- 원본 EXE `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac` **불변**
  (재해시 실측). 원본/참고/공유 저장소 쓰기 0.

## 실행 명령

```
python3 docs/history/laps/probes/20260920_lap391_middle_g2_ledger_wrap_review_probe.py
  → rc0, failures=[]
make check                → rc0, 715 passed 148.29s + Ruff/compileall/mypy10 Success + CONTEXT_PASS
checks/safety.sh check    → SAFETY_PASS
```

probe는 lap390의 스크립트를 **import하지 않는다**. 핀/주장값을 손으로 전사해 상수로 박고
`samples.jsonl` 원문에서 전부 재계산한 뒤 대조한다.

## 측정값 / 판정

fixture: 9/19와 동일 `samples.jsonl`, SHA256 `76903a8dcc094fa7c477ffc76048240fbca38cf78b126599a906c3a05f0e7180`,
146 samples, tick 10020→34185, 8 owner, cap 전 sample 균일 5000.

| 지표 | lap390 주장 | lap391 독립 재계산 | 판정 |
|---|---|---|---|
| sample 수 | 146 | 146 | 일치 |
| M1 signed16 음수 | 0 | 0 | 일치 |
| M2 단일 owner used 최대 | 5,003 / owner1 / tick33185 / sample140 | 동일 4-튜플 | 일치 |
| M3 roster0+used점프 | 0 | 0 | 일치 |
| M4 전역합 첫 | 40,000 (tick10020) | 40,000 | 일치 |
| M4 전역합 끝 | 35,427 (tick34185) | 35,427 | 일치 |
| `used>cap` 위반(lap389) | 7건 | 7건, sample 140~146 | 일치 |
| per-owner used 범위 8행 | 표 참조 | 8/8 전부 일치 | 일치 |

**판정: ACCEPT.** lap390 W1의 `NOT_FEASIBLE`(이 fixture 한정)은 독립 재계산으로 재현된다.
이것은 **관측 단위 승인일 뿐이며 제품/런타임/마일스톤 승인이 아니다.**

## 신규 증거 (lap390이 하지 않은 것)

- **V1 — M1 검출기 유효성을 바이트로 확인.** lap390은 "값을 signed16으로 재해석"했다고 적었으나,
  `patches/population/runtime_driver.py:144`의 샘플러는 이미 `used=i16(0x200C)`,
  `i16 = struct.unpack_from("<h", …)` 즉 **부호있는 word**로 읽는다. 따라서 lap390의 재해석 단계는
  **항등(identity)** 이고(그래서 `used_min == used_signed16_min`이 8/8 성립), 추가 디코드가 아니다.
  다만 결론에는 유리하다 — 실제 랩은 JSON에 **직접 음수로** 드러나므로 M1=0은 유효한 음성이다.
  probe가 `'<h'`의 부호확장(40000→-25536)까지 실증해 fail-open을 닫았다.
- **V2 — M3의 사각을 gap-proof 검사로 대체.** lap390의 M3은 **엣지 트리거**(roster count 0으로의
  *전이*)라 sample 간격(중앙값 167 tick) 안에서 패배가 일어나면 놓칠 수 있다. lap391은 레벨 검사를
  추가했다: **per-owner roster count 최소값 = {0:112, 1:136, 2:145, 3:144, 4:144, 5:112, 6:133, 7:138}**.
  어떤 owner도 0에 근접조차 하지 않는다 ⇒ 이 trace 구간에서 패배 owner가 **존재하지 않으므로**
  `FUN_00444EF0`(패배 owner 일괄흡수)는 sample 사이에서도 발화할 수 없다.
  **lap390의 M3보다 엄격히 강한 근거이며, W1의 NOT_FEASIBLE을 보강한다.**
- **V3 — 여유 수치 고정.** 관측 최대 5,003 대비 signed16 상한 32,767까지 여유 **27,764**
  (관측 최대의 **5.5배**). 동시에 **전역합 peak 40,000 > 32,767**은 그대로다 ⇒
  **F4의 산술 전제는 살아 있다.** W1은 "이 fixture에서 도달하지 않았다"를 보였을 뿐,
  "원리적으로 도달 불가"를 보이지 않았다. 이 구분을 합격기준 판정에서 뭉개면 안 된다.
- **V4 — 샘플링 한계 명시.** 연속 관측이 아니라 166~167 tick 간격 표본이다. 한 gap 안에서 발생하고
  치유된 일시적 랩은 원리적으로 비가시다. V2가 이 사각을 실질적으로 막는다(패배 0건).

## 정정 / provenance (수치 영향 0, 완화 아님)

- **N16(신규, lap391 확정) — lap390 기록의 fixture SHA가 틀렸다.**
  `20260920_lap390_work_g2_ledger_wrap_reachability.md` 본문은 `samples.jsonl`의 SHA256을
  `d7bf3e1f73892b5d3ab4065dec5dd821bc2d43d71f4daadb9105a9bc2bdafdfe`로 적고
  "`independent_analysis_v1`의 `source.sha256`와 일치 확인"이라고 주장한다. **둘 다 사실이 아니다.**
  - 실측 `samples.jsonl` = `76903a8dcc094fa7c477ffc76048240fbca38cf78b126599a906c3a05f0e7180`.
  - `independent_analysis_v1/analysis.json`의 `source.sha256` = **`76903a8d…`** (일치 주장과 반대).
  - `d7bf3e1f…`는 같은 JSON의 **`cost_evidence.sha256`**(유닛 타입/비용표 핀)이다 — 다른 개체.
  - **lap390이 실제로 실행한 기계 산출물 `output.json`의 `input.samples_jsonl_sha256`은
    `76903a8d…`로 올바르다.** ⇒ 분석 자체는 올바른 파일을 읽었고 **수치 영향 0**.
    결함은 **손 전사된 서술 1줄 + 거기 딸린 거짓 교차검증 주장**에 국한된다.
  - 성격: STATUS provenance 회귀 **(c) "손 전사 JSON의 SHA 무효"의 재발**이자 lap385 §R5가 고친
    "부르지 않은 것을 불렀다고 적음"과 같은 계열이다. 기계 산출물이 살아 있어 복구 가능했다.
  - **처리:** lap390 기록 원문은 **고쳐 쓰지 않는다**(⑤ 원문 보존). 이 정정을 정본으로 둔다.
    STATUS에 N16으로 1줄 등재한다.
  - **재발 방지 제안(승인 대기, 착수 안 함):** lap 기록의 fixture SHA는 손 전사 대신 해당 lap의
    기계 산출물 필드를 그대로 인용하도록 템플릿(`docs/history/LAP_TEMPLATE.md`)에 명시.
    N14와 묶지 않는다.

## 회귀 / 남은 위험 / 승인 상태

- W1은 **CLOSED(ACCEPT)**. 새 수리 체인 없음.
- **F4 합격기준 판정은 여전히 미결**이고 middle 권한 밖이다(`loop/ESCALATE_SOL` 유지·갱신).
  lap391의 V3이 그 이유를 강화한다: 관측이 랩을 못 봤다는 사실은 (b) 기준을 불필요하게 만들지 않는다.
- 랩 트리거 fixture(`FUN_00444EF0` 반복 유도)는 **새 게임 실행/새 fixture 생성**이므로 승인 대기.
  V2가 보인 대로 현 fixture는 패배 owner가 0이라 이 경로를 원천적으로 다루지 못한다.
- 독립 검수: 이 기록 자체는 다음 회차(또는 승격 작업자)가 위 probe를 재실행해 확인한다.
- implementation-unchanged-streak: 제품코드/바이너리 변화 0이므로 **2**로 증가.
  다음 회차는 측정 가능한 제품 변화 또는 구체 blocker가 필요하다 — 다만 그 전제인 F4 합격기준이
  Astra/사용자 판정 대기라 middle이 단독으로 다음 제품 카드를 열 수 없다.

## 다음 한 가지

**F4 합격기준 판정(Astra/사용자) 대기 — middle 권한 내 새 독립 work 카드 없음, STOP.**
승격 작업자가 이어서 볼 것은 `loop/ESCALATE_SOL` §5(lap391 추가분).
