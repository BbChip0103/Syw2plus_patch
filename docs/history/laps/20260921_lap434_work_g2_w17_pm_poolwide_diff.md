# 2026-09-21 | lap 434 | 목표 G2

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-sonnet-5` / high / **work(실무)**.
  카드 `docs/work/active/G2_UNIT_700_WRITER_POOLWIDE_DIFF_LAP431.md`(W17)의 P-M+rider를
  §9(lap432 정정) 반영해 동기 1회 실행하라는 STATUS「다음 한 가지」를 수행했다.
- 가설 / 사용자 관찰: 카드 §9-A가 실행 전 고정한 판정식 — 축1 base rate `B`(전이 tick 제외
  창-변화 슬롯 수 중앙값)로 (L3)을 먼저 가르고, `B==0`일 때만 `|S|`로 (L1a/L1b/L1c/L2)로
  내려간다. 새 가설 추가 없음(카드 §3/§9 그대로), 스폰(alive_prev=False→alive=True) 슬롯은
  `S`/`B` 계산에서 제외.
- 예상 PASS / FAIL 조건: `B>=1` ⇒ (L3) 확정, 수리 금지·보고 후 정지. `B==0`이면 `|S|`로
  (L1a/L1b/L1c/L2) 분기. 판정 불가(전이 비재현)면 (L4).
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted): 메인 레포 소스 변경 **0**
  (N22, 이번 회차 source 미변경). 신규 파일은 전부 `temp/Syw2plus_patch/g2_capacity/
  20260921_lap434_unit_700_poolwide_diff/`(evidence, git 비대상): `movement_state_probe_pm.py`
  (lap430 `movement_state_probe_pk.py` 복사 + P-M 풀전역 창diff·rider 값열탐색 추가, 읽기 전용,
  `WriteProcessMemory` 0건), `recompute434.py`(독립 재계산), `samples.jsonl`(379표본),
  `poolwide_diff.jsonl`(76행), `poolwide_spawn_diff.jsonl`(2행), `rider_hits.json`(빈 배열),
  `run_summary.json`, `resource_receipts.json`, `orchestrator.log`. 커밋 0.
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 원본
  `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`(실행 전후 직접 재해시
  일치, 변경 없음), 후보(marked compat N=4001) `4331d9cd646c03a0102394727894beaf893e5b9aa350
  5c4ddb41eb26a4ef9bbe`(lap413~432와 동일 핀). fixture: op7 resource-only, 8 owner, seed42,
  격리 사본 `local/runtime/20260921_051938_1705248_0`, 전용 wine prefix, display `:3850`(비중첩,
  실행 전 `df -h /` 303~306G 확인·lock 없음 확인).
- 실행 명령 / 로그 / 캡처 경로 및 해시: `python3 movement_state_probe_pm.py`(동기 전경 실행,
  셸 background 미사용). 1차 시도는 title-click 전이(PS9→PS7) 타임아웃으로 실패(게임 부팅
  단계, P-M/rider 로직 도달 전 — 새 가설 아님, 기존 클릭 스텝의 산발적 타이밍 이슈). `bridge_build`
  잔여 디렉터리 삭제 후 2차 시도 성공. 로그
  `temp/Syw2plus_patch/g2_capacity/20260921_lap434_unit_700_poolwide_diff/orchestrator.log`.
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN): **(L3) 확정.**
  - 전이(슬롯3565 `+0x700` K `0→22432`)는 이번 run에서도 **정확히 재현**됐다(sample343,
    이번 run의 실제 tick=**10402** — tick 카운터가 표본 사이 10398→10402로 건너뛰어 정수
    10399/10400이 아예 표본화되지 않았다; lap427~431의 "10400"은 그 run들의 실측치였을 뿐
    보편 상수가 아니라는 뜻이며, 전이 자체의 정체성(같은 K/sib/idx6 값)은 불변이다). 창
    인덱스 6·7·8이 `0→{17,16538,22432}`로 동시 전이해 lap430/431/432와 **바이트 정확히 일치**
    (교차검증: `win`(idx6/7/8)과 기존 `K`/`sib` 계측이 이번 run에서도 100% 일치).
  - **P-M(신규 실행 증거):** dense 50표본 중 전이표본 제외 49표본에서 슬롯별 창-변화
    개수 분포 `{0:15, 1:16, 2:11, 3:7}`(0이 아닌 표본 34/49=69%), **중앙값 `B=1`**.
    `B>=1`이므로 카드 §9-A 판정식에 따라 **(L1)/(L2)로 내려가지 않고 (L3)에서 정지**한다.
  - 전이표본(sample343) 자체의 `|S|=2`(`{3565, 3604}`)는 배경 분포(0~3, 중앙값1) 범위
    **안**이다 — 전이가 "이례적으로 많은 슬롯"을 건드리는 사건이 아니라 배경 잡음과 통계적으로
    구별되지 않는다. 슬롯3604의 변화는 idx15(`+0x71c`, `131075→3`)로 3565의 idx6/7/8과
    **다른 오프셋·다른 값 성격**(작은 카운터류로 읽힘)이라 같은 원인으로 보이지 않는다
    (별도 배경 변화로 해석, 3565와의 인과 연결 주장 안 함).
  - **N47(신규):** N46(lap432, band_scan이 이 창을 안 본다)의 우려가 실측으로 **확정**됐다 —
    이 창은 실제로 상시 활동 중이며 "3565 국소" 전제(W14~W16)는 대조 슬롯 3562 하나로 지탱된
    것이었는데(lap431 C1) 이번 P-M은 3562와 무관하게 **풀 전역에서 배경 변화가 흔함**을 직접
    보였다. 3562가 우연히 조용한 슬롯이었을 가능성을 배제할 수 없다.
  - **rider(같은 회차, 값싼 곁가지) 결과: hit 0건, 원인은 결함(카드 위반 아님).** 정확 tick
    일치(`tick in {10399,10400}`)로 캡처를 트리거했으나 이번 run의 tick 진행이 10398→10402로
    건너뛰어 두 값 다 표본화되지 않아 `rider_ticks_captured=[]`. (L3) 판정에는 rider 결과가
    필요하지 않으므로(카드 §8: (L3)이면 수리 금지·보고, rider는 (L1)/(L2) 해석 보조용) 이
    회차의 필수 결론에는 영향 없음. 향후 재사용 시 `RIDER_TICKS`를 정확 tick 대신 전이표본
    탐지 기반(예: K 필드 전이 직후 첫 dense 표본)으로 바꿔야 함을 §「다음 한 가지」에 남긴다.
  - 검사: `pytest patches/population/test_g2_full_capacity_persistence_compat_v1.py
    patches/population/test_runtime_bridge_contract.py -q` → **6 passed**(54.24s). source
    미변경이므로 통합 `make check` 생략(N22). `checks/safety.sh check` → `SAFETY_PASS`. 원본
    직접 재해시(`hashlib.sha256`) 실행 전/후 모두 확인, 카드 §4 금지 주소 10곳 전부 미기록,
    `WriteProcessMemory` 호출 0건(코드 검토로 확인 — 이 probe는 `runtime_driver.read`만 import).
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: 이번 lap 자기 결과이며 **독립(다음 middle)
  검수는 아직 없다.** lap433 strategy가 실행 전에 종료 경계를 이미 고정했다 — "(L3)/(L1c) →
  수리 금지·보고 후 정지(카드 §8·§9-A 그대로). W14~W16 전제 재해석과 §14 항목3(풀 재배치
  안전성 재검토) 발동 여부는 strategy 판정 사항으로 예약한다"(`ESCALATE_SOL`§20). 이번 lap은
  그 경계를 그대로 따라 **수리를 시도하지 않고 여기서 정지**했다. 게임 실행 2회(1차 실패/2차
  성공), 제품 코드 변경 0, 커밋 0.
- 다음 한 가지: `loop/ESCALATE_SOL`§21로 (L3) 결과를 발행했다. 다음 middle이 이 원시
  `poolwide_diff.jsonl`/`samples.jsonl`을 독립 재계산(`recompute434.py` 재사용 가능)해 ACCEPT/
  REJECT를 낸 뒤, W17이 마지막 진단 카드였으므로(lap433 강제) **strategy가 §14 항목3(풀
  재배치 안전성 재검토 발동 여부)과 W14~W16 "3565 국소" 전제 재해석을 판정**한다. work 권한
  으로 새 진단 카드를 자체 발행하지 않는다.
