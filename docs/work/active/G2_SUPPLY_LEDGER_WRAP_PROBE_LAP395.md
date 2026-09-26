# G2 work 카드 W2 — 정상 이전+재생산 장부 probe / 최대 단위비용 실측

발행: lap395 middle (Claude Code `claude-opus-5` / high), 2026-09-20 KST
수행: work tier (`claude-sonnet-5` / high 또는 Luna/high), **다음 work 회차**
상한: **한 work 회차 또는 60분 중 먼저 도달하는 시점, 실패 가설 2개**.

## 0. 왜 이 카드인가 (전제)

lap395가 lap394 Astra 반례를 독립 검수해 확정한 것:
- 전역합 불변식 무효, **cap≤4095 안전상한도 무효**, 안전상한 **UNKNOWN**.
- 이전 경로(`roster_add 0x43EE30`)는 supply cap `+0x2012`도 count cap `+0x2010`도
  **참조하지 않고** 오직 `cmp ax,0x4B0; jl`(배열 1200칸)만 건다.
- 남은 구조적 상한 `min(roster1200, 유닛풀) × 최대 단위비용`의 **최대 단위비용이 UNKNOWN**이다:
  비용표 `0x9B5238`과 type표 `0x66B81D`는 `.data` raw 끝 `0x4F9000` **바깥 BSS**라 정적으로 못 읽는다.
  실측 평균 31.66~34.42만 있고, 1200칸 손익분기 평균은 27.31이다.

⇒ 이 카드는 **추가 계획 회차가 아니라 측정**이다. 두 미지수를 실제 프로세스에서 읽어 닫는다.

## A. 합격/실패 측정식 (먼저 적는다)

| ID | 측정 | PASS 조건 | FAIL/UNKNOWN 조건 |
|---|---|---|---|
| M-a | 비용표 `0x9B5238`에서 실제 사용되는 unit type의 **최대 단위비용** `c_max` | 값이 읽히고 type 집합이 명시됨 | 읽기 실패 / type 집합 불명 → UNKNOWN |
| M-b | `min(1200, 유닛풀) × c_max` vs **32,767** | 부등호가 확정됨 | 미확정 |
| M-c | 정상 이전 1회 전후 `(used, count)` 쌍 — 양 owner | `used` 변화량이 양쪽 **동일 부호반대·동일 크기**, 즉 합 보존 | 불일치 → 이전 비보존(신규 결함) |
| M-d | 이전 직후 원 소유자의 **재생산 1회** | gate 통과 + `used` 증가 = 비용, 전역합 `Σused` **증가** 관측 | 재생산 불가 → 반례의 게임 내 비성립 근거 |
| M-e | 장부 `+0x200C` vs **실소유 유닛 비용합**(roster 순회 재계산) | 두 값 일치 | 불일치 → 별칭/우회 writer 존재 증거 |

M-b가 `>`이면 **어떤 uniform cap도 랩을 구조적으로 막지 못함**이 실측으로 확정된다.
M-b가 `<=`이면 **안전상한이 복구**되고 cap 결정 분기가 되살아난다. 어느 쪽이든 §7.6 질문이 닫힌다.

## B. fixture (명시 — 임의 축소 금지)

- 후보 아님. **원본 EXE** `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`
  또는 기존 5000 패치본 중 **하나를 택해 기록**한다(둘 다 M-a/M-b에 유효; cap은 M-a에 무관).
- 실행 봉투: 기존 격리 전체 게임 복사본 / 전용 Wine prefix / 빈 Xvfb display.
  기존 세션 접속·전역 pkill·다른 로그 정리 **금지**. cleanup 후 잔류 0 확인.
- 상태: 기존 `save000` 8 PlayerStruct 로드 경로(logical load-button `(316,372)` 1회, PS35→PS3)를 재사용한다.
  **새 생성 fixture를 만들지 않는다** — 새 생성/새 시나리오는 승인 대기 항목이다(ESCALATE_SOL §5).
- 읽기 수단은 기존 `process_vm_readv` 폴링 **그대로**. `process_vm_writev`/`ptrace`/`int3`/디버거
  **금지**(lap324 확정, 기구 제작 자체가 위반).

## C. 범위 경계 (반드시 지킨다)

- **바이너리 변경 0. 메모리 쓰기 0. 관측 전용.** 이전/재생산은 **게임 내 정상 조작**으로만 유도한다
  (capture/승선/charm 등 원본 경로). 원본 명령 우회로 만든 성공은 증거로 쓰지 않는다.
- M-c/M-d를 유도하지 못하면 **억지로 만들지 말고** `BLOCKED` + 누락 입력을 적는다.
  M-a/M-b는 이전 유도 없이도 독립 측정 가능하므로 **먼저 끝낸다**.
- `used>cap` 자체를 FAIL로 처리하지 않는다 — 원본 허용 상태다(lap389). 측정 대상은 **랩**이다.
- baseline/golden/안전 pin을 고쳐 통과시키지 않는다. 실패는 보존한다.

## D. 산출물

- 신규 read-only probe 1개 + `samples`/`output.json`을 공유 temp
  `…/temp/Syw2plus_patch/g2_capacity/20260919_owner_transfer_cap/lap<N>_work_ledger_wrap_probe/`에 저장,
  경로와 SHA256을 lap 기록에 남긴다. 캡처 PNG는 지정 temp에 `YYYYMMDD_HHMMSS_` 접두사로.
- `make check` + `checks/safety.sh check` + 원본 재해시 불변을 매 회차 기록.
- lap 기록은 `docs/history/LAP_TEMPLATE.md` 필드 전부. fixture SHA는 **기계 산출물 필드를 인용**한다
  (손 전사 금지 — N16 재발 방지).

## E. 판정 후 흐름

`FEASIBLE`이면 추가 계획 회차 없이 그 회차에서 실행까지 끝낸다.
결과는 **다음 새 middle이 독립 검수**한다. work는 자기 결과를 최종 승인하지 않는다.
M-b 결과는 `loop/ESCALATE_SOL` §9의 승격 판정에 직접 입력된다 — work가 cap 숫자나
합격 기준을 바꾸지 않는다.
