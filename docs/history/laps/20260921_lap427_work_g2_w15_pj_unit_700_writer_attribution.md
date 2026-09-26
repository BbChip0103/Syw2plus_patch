# 2026-09-21 | lap427 | 목표 G2

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-sonnet-5` / high / **work(실무)**.
  카드 발행자는 lap426 `claude-opus-5`/high/middle.
- 가설 / 사용자 관찰: W15 `docs/work/active/G2_UNIT_0x700_WRITER_ATTRIBUTION_LAP426.md` P-J.
  W14가 확정한 `unit+0x700`(K) 단독 표 밖 점프(0→22432, 슬롯3565, tick10400)가 (J1) 정당
  site(`0x40d79f`가 `[unit+0x388]`을 정상 복사)인지, (J2) 외부 write(그 4곳이 아님)인지,
  (J3) 이웃까지 더러워지는 블록 write인지 읽기 2개(`src=[unit+0x388]`, `sib=[unit+0x6fc]`)만
  추가해 판별한다. K 가드 상한을 lap426 유도값 `<3759`로 갱신.
- 예상 PASS / FAIL 조건: 판정식은 카드 고정(J1/J2/J3/J4). "PASS"는 네 판정 중 하나로 결론나고
  전이(K:0→22432)가 이번 run에서도 재현되는 것; "FAIL"은 60분/실패2회 안에 결론 못 내는 것.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted): 원본/후보 EXE 변경 0(이번 회차
  source 변경 없음, N22 근거로 통합 `make check` 생략, 표적 6 passed만 실행). 신규 파일은
  `temp/Syw2plus_patch/g2_capacity/20260921_lap427_unit_700_writer_attribution/`
  (`movement_state_probe_pj.py`, `samples.jsonl`, `run_summary.json`, `orchestrator.log`,
  `resource_receipts.json`, `bridge_build/`)뿐이며 레포 커밋 대상 아님(uncommitted).
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture:
  원본 `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`(불변, run 전후 재해시 일치),
  후보(marked compat, N=4001) `4331d9cd646c03a0102394727894beaf893e5b9aa3505c4ddb41eb26a4ef9bbe`
  (lap413/414/419~421/423/425와 동일 pin). 격리 사본 `tools.runtime_env.prepare()` +
  전용 Wine prefix + 빈 display `:3846`(lap425의 `:3845`와 겹치지 않는 새 display). 8 owner,
  seed42 chain goal, resource-only op7 fixture(rice/wood 1,000,000, 8/8 ok). fixture는 카드
  지시대로 lap421/423/425와 **동일**.
- 실행 명령 / 로그 / 캡처 경로 및 해시: `python3 movement_state_probe_pj.py`(동기 foreground,
  셸 backgrounding 없음 — INBOX 2026-09-21 01:01 운영 규칙 준수). run_dir
  `local/runtime/20260921_034154_3928975_0`. 476표본, `stop_reason=stop_tick_reached`,
  `final_tick=10494`(STOP_TICK=10500 이전 자연 종료, tick11,928 fault 불필요). 산출물
  `temp/Syw2plus_patch/g2_capacity/20260921_lap427_unit_700_writer_attribution/`
  (`samples.jsonl`, `run_summary.json`).
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN): **PASS — (J2)+(J3) 확정, 재현 확인(J4 아님).**
  슬롯3565 단일 변화점 `sample383/tick10400`: `K` `0→22432`(전이 재현, lap423/425/426과 일치).
  **같은 sample383에서 `sib`(`[unit+0x6fc]`)도 `0→16538`로 동시 점프**(런 전체에서 sib는 0 또는
  16538 두 값뿐, 이후 22432와 같이 tick10528까지 고정). **`src`(`[unit+0x388]`)는 런 전체 152
  생존표본 전부 `0`으로 불변**(22432가 된 적 0건). ⇒ (J1) 정당 site 가설은 **배제**(전이 순간
  `src≠22432`이므로 `0x40d79f`/`0x40f040`가 정상 값을 복사한 결과가 아니다). (J2) 외부
  write 확정(`src`는 정상인데 `K`만 표 밖으로 튐). (J3) 이웃 필드 동시 오염 확정(단일 스칼라
  store가 아니라 **블록/OOB write**가 `+0x6fc`와 `+0x700`을 같은 순간 함께 건드림 — 카드가
  정의한 저비용 판별자 그대로 성립). 대조 슬롯3562(owner4, ref_slot 자동발견, tick10347)는
  구간 내내 `K=0`/`sib=0`(src는 정상 범위 내 변동 0~851982) ⇒ 슬롯3565 국소 현상, 대조군
  오염 없음 재확인.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: **독립 검수 없음(work의 자기 결과,
  다음 middle 회차가 검수)**. 이 결과는 카드 §8의 중단 조건("(J2)가 확정되면 그것은 풀
  확장 회귀의 구조적 원인 후보이므로 STATUS와 `loop/ESCALATE_SOL`에 올리고 다음 상위 판정을
  받는다")에 해당해 `loop/ESCALATE_SOL` §14로 기록하고 이 회차는 카드의 "다음 표적"
  (잔존 1200-bound site 3곳의 `unit+0x700`/`+0x6fc` 착지 정적 평가)을 **착수하지 않았다**
  — 카드 §8이 실행/추가 조사보다 상위 판정을 먼저 요구하는 stop 조건이기 때문이다. 명령
  바이트 패치는 0건(계측 전용, 카드 §4 고정 주소 전부 미기록). P2 near-cap FAIL 기준은
  낮추지 않는다. `sib=16538`의 의미(어떤 배열/구조의 값인지)는 미해석 — 다음 정적 평가가
  풀어야 할 새 단서다.
- 다음 한 가지: **다음 middle 회차가 원시 `samples.jsonl`(476표본)로 이 판정(J2+J3)을
  독립 재계산해 ACCEPT/REJECT를 내린 뒤**, `loop/ESCALATE_SOL` §14가 요청한 상위 판정
  (잔존 1200-bound site 3곳을 `unit+0x700`/`unit+0x6fc` 착지 가능성으로 정적 평가할지,
  혹은 다른 OOB 발생원을 먼저 좁힐지)을 받는다. 이 카드(W15)의 실행 부분은 이 lap으로
  종료하고 재시도하지 않는다(성공 재현, 실패 예산 미소진 상태로 조기 종료).
