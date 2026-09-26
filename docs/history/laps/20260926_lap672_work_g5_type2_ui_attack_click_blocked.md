# 2026-09-26 | lap 672 | 목표 G5

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-sonnet-5` / high (Codex 401로 임시 전환, `loop/env.local.sh`); 지정 역할 work, middle 없이 STATUS/INBOX 08:55 지시 + lap671 자체 "다음 한 가지" (a) 수행.
- 가설 / 사용자 관찰: lap671이 근본 원인을 확정(worker=type31은 domain 공격권한 없음, SEED_TYPE=2는 있음)했으나 실제 UI 클릭 경로(드래그 선택→'A'+좌클릭)로 type2 유닛이 공격을 수행하는지는 아직 검증되지 않았다. 08:55 지시: 일꾼을 빼고 type2 fixture만 드래그해 확정된 화면→월드 변환으로 적 type2 중심을 A+좌클릭/우클릭 → `+0x290==4`·`+0x38C==적 uid` 확인.
- 예상 PASS / FAIL 조건: 원본에서 type2 공격자 1기가 UI 클릭만으로 `command==4`·`pending_target_uid==적 handle`에 도달하면 PASS → candidate50 paired로 이관. 도달 못하면 원인(선택/좌표/게이트/타이밍)을 좁혀 다음 work에 넘긴다.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted): 신규 `tools/g5_type2_ui_attack_probe.py`, `tests/test_g5_type2_ui_attack_probe.py`(제품 EXE 미변경, read-only 진단). 커밋 0(LOOP_ALLOW_COMMITS=0, 전체 저장소 uncommitted).
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 보호 원본 `b56986e0…c9c08a8ac` 6회 실행(run1~r6, 모두 원본-only) 전부 불변. 후보 미실행(원본 PASS 없이는 candidate 진행 금지, lap671 §다음 (a)(b) 순서 준수). 격리 Wine/Xvfb 1600×1200, PS3 solo owner0; 매 실행 owner0 type2 공격자 1기 + owner1 type2 목표 1기를 기존 worker 인접 좌표에 신규 spawn(op5 stock-layout diagnostic).

## 반복 요약 (6회 실행, 실패 2회 초과로 BLOCKED 판정)

1. **run1**: 첫 시도 — 계산된 화면 좌표로 tight drag-box(±24px) 단일 선택 시도 → 선택 0(드래그가 클릭/드래그 임계값 미만이라 끝점 단일클릭으로 처리되어 유닛을 놓침).
2. **run2**: tight drag-box를 y-스윕 단일 좌클릭으로 교체 → dy=-8에서 **일꾼(1198)이 잘못 선택됨**(공격자 아님). 원인: 보정용 우클릭 이동 명령을 받은 일꾼이 보정 종료 후에도 계속 이동 중이라 마지막 보정 목적지 근처(공격자와 인접)를 배회하며 클릭에 우연히 걸림.
3. **run3**: 일꾼을 먼 좌표로 "주차"(우클릭+idle 대기)한 뒤 재시도 → 일꾼 오염은 해결됐으나 **선택 자체가 y=0~-72 전 구간에서 0건**. 스크린샷 확인 결과 계산된 화면 x좌표가 실제 유닛 위치보다 ~58px 어긋나 있었다 — 어파인 역변환을 일꾼이 아닌 **다른 유닛(공격자)의 위치에 적용할 때 수평 오차도 존재**함을 발견(수직 오차만 가정한 lap668~671의 전제가 이 경우엔 불충분).
4. **재설계**: 정밀 단일 클릭 선택을 포기하고, 이미 검증된 넓은 드래그 사각형(`DRAG_START`~`DRAG_END`)을 **보정 이전(공격자 스폰 전)**에 일꾼만 선택하도록 순서를 바꾸고, 보정 완료 후 공격자/목표를 스폰한 뒤 **같은 넓은 드래그를 재사용**(일꾼이 섞여 들어와도 무관 — 판정은 공격자 슬롯 필드만 직접 읽음)하도록 스크립트를 재구성.
5. **run4**: 재구성된 스크립트로 `PASS_TYPE2_UI_ATTACK` 획득 — 그러나 세부 로그 검사 결과 **자율 AI 교전(auto-aggro) 오염 의심**: 공격자의 `command=7`·`pending_target_uid`가 op8 호출·공격 클릭 이전부터 이미 목표와 일치했고, op8 자체는 `order_slot_not_alive`로 **거부**됐다(그런데도 필드는 이미 일치 — 즉 클릭/주문이 아니라 스폰 후 자동교전이 원인일 가능성). `command=7`은 기존 `attack_observation()`의 엄격한 `command==4` 기준도 충족하지 못한다.
6. **오염 방지 계측 추가**: 스폰 직후(어떤 입력도 가기 전) 공격자 상태를 즉시 스냅샷하는 `attacker_state_immediately_after_spawn`을 추가하고, op8 판정을 `order_result.ok and raw_return==1`(실제 주문 수락)로 강화, 자동교전 감지 시 상태를 `INCONCLUSIVE_AUTO_AGGRO`로 명시 분리.
7. **run5**: `auto_aggro_before_input=False`(자동교전 미발생, run4가 우연/타이밍 의존적 현상이었음을 확인) — 그러나 y-스윕(수직만, 10칸) 전 구간 미스, `FAIL_TYPE2_UI_ATTACK`. 관측: 특정 y오프셋에서 `pending_target_uid`가 **공격자 자신의 handle**로 나타남(자기 자신을 클릭했을 때의 기본값으로 추정) — 계산된 화면 x좌표가 여전히 실제 목표 위치에서 벗어나 있음을 재확인.
8. **2D 스윕 확장**: X_SWEEP_OFFSETS(0,±24,±48) × Y_SWEEP_OFFSETS(0~-72, 10단계) = 50칸 그리드로 확장.
9. **run6**: 50칸 전수 미스, `FAIL_TYPE2_UI_ATTACK`. 추가로 **op8도 이번엔 다른 사유로 거부**(`order_slot_dead_or_uninitialized`, tick≈567~575) — lap671의 type2-domain-probe(스폰 직후 즉시 op8 호출, tick 낮음)와 달리 이 probe는 보정·드래그·50칸 스윕 등으로 실행 시간이 길어 **op8 호출 시점의 tick이 훨씬 높다**. op8 거부 사유가 실행마다 다른 것(`order_slot_not_alive` vs `order_slot_dead_or_uninitialized`)은 슬롯/유닛 상태가 시간 경과에 따라 변하고 있다는 신호일 수 있다(원인 미확정).

- 실행 명령 / 로그 / 캡처 경로 및 해시: `PYTHONPATH=. python3 tools/g5_type2_ui_attack_probe.py --runtime-root local/runtime/g5-lap672-type2-ui-attack[-r2..-r6] --artifact-root .../g5_lap672_type2_ui_attack[_r2.._r6]`. 각 실행 `probe-result.json`·캡처 PNG 보존(공유 temp). 정적 회귀 `PYTHONPATH=. pytest -q tests/test_g5_type2_ui_attack_probe.py` → 4 passed. `make check`(`.venv`, 세션 내 완주 대기) → **926 passed in 652.62s**, ruff/compileall/mypy/`CONTEXT_PASS` 모두 PASS(로그 `logs/gates/lap672_make_check.log`). `checks/safety.sh check` → `SAFETY_PASS`.
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN): **BLOCKED** — UI 클릭 경로로 type2 유닛의 실제 공격 명령(`+0x290==4`)을 아직 재현하지 못했다. 확인된 것: (a) 넓은 드래그 재사용으로 공격자 slot을 선택에 포함시키는 것은 안정적으로 동작, (b) 일꾼-기반 보정 이후 다른 유닛 위치에 어파인을 적용하면 수평·수직 모두 오차가 커 50칸 그리드 스윕으로도 목표 스프라이트 히트박스를 못 맞췄다, (c) 자동교전은 가능하지만 결정적이지 않다(run4는 발생, run5는 미발생 — 조건 미상), (d) op8 raw 주문도 이 실행 흐름에서는 시점에 따라 거부 사유가 달라 신뢰하기 어렵다.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: 새 진단 도구 1개(+수정 반복)만 추가, 제품 EXE/보호 원본 0 변경. `source_unchanged=true`(6회 모두). `cleanup.ok=true`(6회 모두, game/prefix 사본 직후 삭제로 디스크 21GB→37GB 복구). G5 제품 PASS·2단 검수·사용자 승인 없음. candidate50은 원본 PASS 없이 착수하지 않음(lap671 순서 준수).
- 다음 한 가지: 클릭 정밀도 문제를 근본적으로 우회한다 — 목표 스프라이트의 정확한 화면 좌표를 **어파인 역변환으로 추정하지 말고**, (a) op8을 스폰 직후 tick 낮을 때 바로 호출해 raw 주문 성공을 재확인(`order_slot_*` 거부 사유의 시간 의존성 원인 규명 우선), (b) UI 클릭은 스폰 직후 바로(보정 생략하거나 보정을 공격자 자신에게 적용) 시도해 수평 오차 누적을 줄인다. 두 가설 모두 실패하면 STATUS/INBOX에 BLOCKED로 보고하고 strategy(Opus5/Astra)에게 다른 hit-test 접근(예: 실제 렌더 좌표를 메모리에서 직접 읽기)을 요청한다.
