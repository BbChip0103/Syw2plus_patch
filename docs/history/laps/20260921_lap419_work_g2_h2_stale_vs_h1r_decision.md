# 2026-09-21 | lap 419 | 목표 G2

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-sonnet-5`/high, work(실무). 카드
  `docs/work/active/G2_POOL_FAULT_H2_STALE_REFERENCE_LAP418.md`(W11 P-D) 실행.
- 가설 / 사용자 관찰: lap418이 H1("잔존 1200-bound 순회가 슬롯≥1200 초기화/수명주기를 건너뛴다")을
  기전 부재로 기각한 뒤 남긴 두 가설 — **H2**(slot 3565가 손상 순간 stale/사망/재할당 상태) vs
  **H1r**(3565는 계속 생존·owner/type 불변인데 `+0x692`만 외부에서 덮임, 즉 wild write). lap416
  `movement_state_probe.py`를 복사해 (a) 3565를 생존여부와 무관하게 매 샘플 전 필드 기록,
  (b) `max_abs`를 무조건 갱신 + 분포 히스토그램 기록(N31 정정 흡수), (c) tick 11,860~11,928 매tick
  샘플(폴 간격 0.02s, stall 판정은 샘플수 대신 벽시계 6.0s로 전환해 오탐 방지)로 바꿔 재실행.
- 예상 PASS / FAIL 조건: 손상 최초 tick에 3565가 사망/재할당이면 H2, 계속 생존·owner/type 불변인데
  `+0x692`만 튀면 H1r. 어느 쪽도 아니면 추측 수리 없이 사실만 기록.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted): 저장소 소스 변경 **0**(이번 회차에
  source를 바꾸지 않았다). 변경은 `temp/Syw2plus_patch/g2_capacity/20260921_lap419_fault_h2_stale/`
  아래 probe 스크립트 사본(`movement_state_probe.py`, lap416 run2 사본에서 3곳만 수정)과 산출물뿐.
  uncommitted, 커밋 없음.
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 원본
  `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`(실행 전후 재해시 일치,
  `source_unchanged=true`), 후보(marked compat) `4331d9cd646c03a0102394727894beaf893e5b9aa3505c4ddb41eb26a4ef9bbe`.
  격리 신규 사본 `local/runtime/20260921_014414_2903790_0`, 신규 display `:3843`, 신규 wine prefix.
  fixture는 lap413/416과 동일: op7(원본 SetResource) resource-only, 8 owner(7 AI), goal
  `_custom_game_chain_inject_g2_eight_seed42`, N=4001. `op=6` 직접 주입 없음.
- 실행 명령 / 로그 / 캡처 경로 및 해시: `python3
  temp/Syw2plus_patch/g2_capacity/20260921_lap419_fault_h2_stale/movement_state_probe.py`
  (foreground, 직접 대기, 총 wall ~370초). 산출물
  `temp/Syw2plus_patch/g2_capacity/20260921_lap419_fault_h2_stale/`
  (`orchestrator.log`, `samples.jsonl` 994줄, `run_summary.json`, `resource_receipts.json`,
  `findings.json`).
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN): **H1r 지지, PASS(probe 완주·결론 확정).**
  - fault: 이전 lap413/414/416과 동일하게 tick **11,928**에서 정지(`fault_seen_at.tick=11928`,
    `sample_count=994`, stall 6.0s+3.0s 확인 후 정상 종료 exit0).
  - 슬롯 3565는 dense 구간(tick 11,855~11,928) **전 tick**에서 `alive=True, type=76, owner=4`로
    **불변**(사망·재할당 0회). 반면 `+0x692`(move)는 tick **11,915**부터 정상 드리프트대(±44~50)와
    돌발 이상값 3종(**19579 / -26278 / -6599**) 사이를 tick마다 번갈아 오간다(단조 증가/고착이 아니라
    진동): 11915=19579, 11917=-26278, 11918=-6599, 11919=19579, 11920=-26278, 11921=-6599,
    11923=**0(정상 복귀)**, 11924=19579, 11925=-6599, 11926=**0**, 11928=19579(stall).
  - N31 정정 확인: hi밴드 `max_abs`가 이상 구간 밖에서도 **44~50**(0 아님)로 기록돼 "매치 내내 정확히
    0"이 아니라 정상 드리프트가 존재함을 재확인. lo밴드는 전체 994샘플에서 `max_abs=0`(전 구간 이상
    없음), 전체 실행에서 이상 발생 슬롯은 **{3565} 단 하나**.
  - ⇒ **판정식 매칭: H1r 지지 조건("손상 tick에도 3565가 계속 살아 있고 owner/type이 불변인데
    `+0x692`만 튄다")을 정확히 충족한다. H2는 기각한다(사망/재할당 관측 0).**
  - 절대주소 계산(다음 probe 대상): `POOL_BASE(0x0108C000) + 0x758*3565 + 0x692`
    = unit base `0x016F0478`, move field VA **`0x016F0B0A`**.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: 게임코드/제품모듈/커밋 **0**. 격리 실행,
  잔류 프로세스 0(`:3843` lock 없음), 원본 2경로 재해시 불변. targeted
  `patches/population/test_g2_full_capacity_persistence_compat_v1.py
  patches/population/test_runtime_bridge_contract.py -q` **6 passed**(기준선 유지), `checks/safety.sh
  check` → `SAFETY_PASS`. source 변경 0이므로 `make check`(기준선 786) 재실행하지 않음. 이 결론은
  `inmm_stub.c`/`ai_shadow.c`/`sfx_hook.c`/`control_executor.c` stub 채널에 근거하지 않는다(N21).
  **이번 lap은 work 자기 결과이며 독립(다음 middle) 검수는 아직 없다.**
- 다음 한 가지: H1r이 확정됐으므로 다음 카드는 `0x016F0B0A`(slot 3565 `+0x692`) 인근에 tick
  11,915~11,928 구간에서 **쓰는 주체**를 추적한다(예: 이웃 슬롯의 인덱스 off-by-N, 보조 인덱스/테이블
  오버런, 다른 유닛의 경로 갱신 루프가 잘못된 stride/index로 3565 구조체를 침범). `0x00414133`
  fault 명령과 `roster_add 0x0043ee39`는 계속 패치 금지. 이 실행 회차로 PROMPT③의 "연속 최대2회
  제품0" 카운터는 리셋된다(실제 게임 실행 완료).
