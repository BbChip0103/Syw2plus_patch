# 2026-09-21 | lap 430 | 목표 G2 (W16 P-K/P-L)

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-sonnet-5` / high / **work(실무)**.
- 가설 / 사용자 관찰: `docs/work/active/G2_UNIT_700_CORRUPTION_EXTENT_LAP428.md`(W16, lap428 middle
  발행)의 P-K. `unit+0x700`(K) 오염이 슬롯3565 tick10400에서 단독 write인지 블록 복사인지를
  `+0x6e0`~`+0x71c` 16 DWORD 연속 읽기 창으로 판별한다. lap429가 준비한 probe
  (`temp/Syw2plus_patch/g2_capacity/20260921_lap429_unit_700_corruption_extent_prep/
  movement_state_probe_pk.py`)를 그대로 실행(코드 변경 없음, 공유 디스크가 lap429 이후 313G로
  회복된 것을 `df -h /`로 먼저 확인).
- 예상 PASS / FAIL 조건: 판정식 (K1) n==2 표적쌍 / (K2) n>=3 연속구간 블록복사 / (K3) 산발 /
  (K4) 전이 비재현. (K2)면 P-L(값열 정적 대조)까지 같은 회차에 수행.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted): 저장소 소스 변경 **0**(probe는
  lap429가 이미 작성·컴파일 검증 완료, 이번 lap은 실행+분석만). uncommitted(LOOP_ALLOW_COMMITS=0).
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 원본
  `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`(실행 전/후 직접 재해시 일치,
  `source_unchanged=true`), 후보 `4331d9cd646c03a0102394727894beaf893e5b9aa3505c4ddb41eb26a4ef9bbe`
  (lap413~429와 동일 pinned marked-compat N=4001). 격리 사본
  `local/runtime/20260921_042518_819815_0`, display `:3847`(신규, 비중첩). fixture는
  op7 resource-only, 8owner, seed42 — lap421/423/425/427과 동일.
- 실행 명령 / 로그 / 캡처 경로 및 해시: `python3 movement_state_probe_pk.py`
  (동기 foreground, 셸 background 금지, INBOX 01:01 운영 규칙 준수). 산출물
  `temp/Syw2plus_patch/g2_capacity/20260921_lap429_unit_700_corruption_extent_prep/`
  (`samples.jsonl` 438표본, `run_summary.json`, `orchestrator.log`).
  `stop_reason=stop_tick_reached`, `final_tick=10493`(STOP_TICK=10500, fault tick11,928 불필요).
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN):
  - **(K2) 블록 복사 확정.** 슬롯3565 `s353(tick10399)→s354(tick10400)` 전이에서 **연속 3
    DWORD**가 같은 sample에서 동시에 바뀐다: `+0x6f8`(idx6) `0→0x11`(17), `+0x6fc`(idx7)
    `0→0x409a`(16538), `+0x700`(idx8) `0→0x57a0`(22432). 인접 `+0x6f4`(idx5)·`+0x704`(idx9)는
    불변. 기존 `K`/`sib`/`src` 계측값은 lap427/428과 정확히 일치(`K=22432`, `sib=16538`,
    `src=0` 불변) — 교차검증 불일치 0. `m`/`f688`은 다음 sample(`s355`)에서 변해 인과
    `K→m→f688` 재확인(변경 없음, 참고용). 기준 slot3562(owner4, 대조)는 동일 구간 window
    전부 `0` 불변. **n=3, 인덱스 연속구간(6,7,8) ⇒ 카드 §3 (K2) 성립.**
  - **P-L 정적 대조: 0건.** 값열 `[0x11, 0x409a, 0x57a0]`(3-DWORD)와 부분열
    `[0x409a, 0x57a0]`(2-DWORD, lap428이 이미 시도)를 핀된 `original.bin`/`candidate.bin`
    (`temp/Syw2plus_patch/g2_capacity/20260921_lap424_middle_review/`, sha256 각각
    `b56986e0…`/`4331d9cd…`으로 pin과 일치 확인)에서 image base `0x400000` 기준 전수
    바이트 탐색 — **원본·후보 어디에도 0건.** 카드 §3 P-L 규칙에 따라 "복사원은 정적 상수표가
    아니라 런타임 상태(bulk 라이브 blob 등)"로 결론짓고 여기서 멈춘다(런타임 메모리 전역
    스캔은 카드 범위 밖, 다음 카드 대상).
  - 판정: **FEASIBLE**(측정 자체는 계획대로 완결). 원인(복사원) 특정은 미해결로 다음 카드에
    이관.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: 이 lap은 **자기 결과이며 독립(다음 middle)
  검수는 아직 없다.** 계측 전용 준수 — `WriteProcessMemory` 0건, 카드 §4 금지 주소
  (`0x00414133`/`0x0043ee39`/`0x00422dc7`/`0x0040bc86~0x40bcfe`/`0x0040c1c2`/`0x48cba9`/
  `0x48c914`/`0x411ec0`/`0x413103`/`0x413120`) 패치 0건. 원본 직접 재해시 불변. targeted
  `pytest patches/population/test_g2_full_capacity_persistence_compat_v1.py
  patches/population/test_runtime_bridge_contract.py -q` → **6 passed**(113.64s). source 미변경이라
  통합 `make check` 생략(N22 근거: 이번 회차 source를 바꾸지 않았다). `checks/safety.sh check` →
  `SAFETY_PASS`. 카드 §8 stop 조건("K2로 확정되면 STATUS·`ESCALATE_SOL`에 올린다")에 따라
  `loop/ESCALATE_SOL` §17로 발행.
- 다음 한 가지: middle(Opus5/high)이 이 lap의 원시 `samples.jsonl`(438표본)로 (K2) 판정과 P-L
  0건을 독립 재계산해 ACCEPT/REJECT한다. ACCEPT 시 다음 표적은 "런타임 라이브 blob에서
  `0x11 40 9a 00 00 00 57 a0 00`(또는 DWORD 3개: 17/16538/22432) 값열의 발생 위치"를 실행 중
  프로세스 메모리에서 직접 스캔(이 카드 범위 밖 — 신규 카드 필요, `ESCALATE_SOL` §17에 발행
  근거 명시)한다. lap428·lap429가 실행증거 없음/제한실행이었고 이 lap430이 실행증거 회차이므로
  카드 §8의 "연속 2회" 경계는 이번 lap으로 해소된다.
