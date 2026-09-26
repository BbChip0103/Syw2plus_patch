# 2026-09-21 | lap 433 | 목표 G2 — strategy 판정: §18/§19 (가) 속도·계속 여부

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-fable-5` / (세션 기본, MODEL_ROUTING상 medium~high) / **strategy(큰 방향/master-plan)**. 게임 코드 직접 수정 없음.
- 가설 / 사용자 관찰: `ESCALATE_SOL` §18 항목1·§19 (가)가 strategy 판정을 요청했다 — W10(lap414)부터
  제품 코드 변경 0인 진단 사슬이 19 lap째이고, lap431(middle, 실행0)·lap432(middle, 실행0)로
  PROMPT ③ "실행 증거 없는 회차 연속 최대 2회"를 소진했다. 3회째(이번 lap433)는 규칙상
  strategy가 계속/중단을 먼저 판정해야 한다. 이번 세션이 정확히 그 판정 회차다.
- 예상 PASS / FAIL 조건: 판정문이 (i) W17 계속 + work 배정 또는 (ii) 경로 중단/전환 중 하나를
  결정 가능한 문서로 남기고, 종료 경계(어떤 결과에 무엇이 따라오는지)를 실행 전에 고정하면 완료.

## ④.2 이전 바퀴(lap432) 독립 검수 — ACCEPT

lap432 코드에 기대지 않고 이번 세션이 직접 재실행/재확인했다:

- `recompute432.py`를 원시 `samples.jsonl`(438줄,
  `temp/Syw2plus_patch/g2_capacity/20260921_lap429_unit_700_corruption_extent_prep/`)에 대해
  독립 재실행 → 저장된 `recompute432.out`과 **diff 0(완전 일치)**. 핵심 수치 전부 재현:
  창 변화점 2개(`s305/t10233 +0x70c 0→-1` 스폰, `s354/t10400` idx6·7·8 `0→{17,16538,22432}`),
  `win[8]==K`/`win[7]==sib` 불일치 0/438, `src` 비0 0/438, 가드-스킵 84건 `s354..s437` 연속,
  `(10+347349) mod 65536 = 19679` 일치, **`samples_without_band_scan = 124`(N46 핵심 수치) 재현**.
- 원본 `syw2plus_original.exe`를 `sha256sum`으로 **직접 재해시** →
  `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac` 불변.
- `checks/safety.sh check` → `SAFETY_PASS`. 디스크 여유 306G(81%) — lap429 blocker 해소 상태 유지.
- 표적 `pytest patches/population/test_g2_full_capacity_persistence_compat_v1.py
  patches/population/test_runtime_bridge_contract.py -q` → **6 passed**(별도 실행, 로그는 세션 기록).
- **이번 회차 source 미변경**(N22: 통합 `make check` 생략 근거 명시). 게임 실행 0, 제품 코드 0, 커밋 0.

## strategy 판정 (ESCALATE_SOL §20으로 발행)

**판정: (i) 계속 — 다음 회차는 work(Sonnet5/high 또는 Luna) 배정, W17(§9 반영) P-M+rider 동기 1회 실행.**
middle 권고 (i)를 인용하며, 판정 근거와 종료 경계는 §20 원문을 따른다. 요지:

1. 두 번 연속 실행0은 기술 blocker가 아니라 **역할 배정 불일치**였다(§19 운영 사실). W17은
   read-only 계측 1회짜리이고 (L1)/(L2)/(L3)/(L4) 어느 결과든 다음 단계가 강제 결정된다 —
   ③이 막으려는 "같은 추측 반복"의 반대 구조다.
2. **W17은 진단 사슬의 마지막 한 장이다(카드 §8을 strategy 차원에서 확정).** W17 이후 새 진단
   카드는 이 판정으로는 허용되지 않는다 — 필요하면 근거를 붙여 strategy로 다시 올린다.
3. **결과별 경계를 실행 전에 고정한다:**
   - (L1a) → 다음은 **수리 카드**(루프 bound). 수리 후보 1회 + 검증(동일 fixture에서 tick11,928
     fault 소멸 + stock 대조 무회귀) 1사이클 안에 fault가 제거되지 않으면 반복하지 말고
     strategy로 재승격한다.
   - (L1b)/(L2) → middle이 수리 표적을 판정하되, 표적을 못 좁히면 진단 반복 없이 strategy 승격.
   - (L3)/(L1c) → **수리 금지, base rate 보고 후 정지**(카드 §8·§9-A 그대로). 이 경우 W14~W16
     전제 재해석과 §14 항목3(풀 재배치 안전성 재검토) 발동 여부를 strategy가 판정한다.
   - (L4) BLOCKED → 근거 보존 후 strategy 승격(창 확대/즉석 가설 추가 금지 유지).
4. 범위 불변: 사용자 되물음 2건(pending 예약 (가)/(나), 장부 (B)/(C))과 F4 트랙(§5~§13)은
   사용자 답변 대기 그대로. G1/G4 잠정 중단·G3 포기 고정 유지. 목표 숫자 5000 불변.

- 변경 파일 / source fingerprint / 커밋: `docs/STATUS.md`, `loop/ESCALATE_SOL`(§20 추기),
  본 기록, `docs/history/laps/20260921_status_lap433_precompaction.md`(STATUS 보존).
  제품 소스 미변경. LOOP_ALLOW_COMMITS 기본 0 → uncommitted 보존.
- 원본 SHA / 후보 SHA: 원본 `b56986e0…c9c08a8ac`(직접 재해시 불변) / 후보 `4331d9cd…`(이번 회차 미사용).
- 실행 명령 / 로그: recompute 재실행 diff 0, safety `SAFETY_PASS`, targeted 6 passed. 게임 실행 0.
- 측정값 / 판정: lap432 검수 **ACCEPT**, strategy 판정 **(i) CONTINUE**(경계 고정).
- 회귀 / 남은 위험: (L3) 확률이 N46으로 상승 — 그 경우 진단 사슬 재해석 비용 발생. 실행0 3회
  경계는 이번 판정으로 소비했으므로 **다음 회차가 또 실행 없이 끝나면 안 된다**(work 배정 필수).
- 다음 한 가지: work가 W17 P-M+rider(§9 반영)를 동기 1회 실행한다.
