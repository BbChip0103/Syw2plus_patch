# 2026-09-25 | lap 572 | 목표 G2

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5-5`/high(INBOX 2026-09-23 strategy 교체 지시) / strategy major direction. 게임 실행 0, 제품 source 변경 0, 커밋 0.
- 가설 / 사용자 관찰: §124 경계. W45R ACCEPT 뒤 남은 G2 축 중 최종 후보를 정하는 S3(F4 통합)가 혼합 144k보다 먼저여야 한다. 144k를 곧 대체될 후보에 쓰지 않기 위해서다. F4 15곳은 `a10024de` 위에 바이트 충돌 없이 얹힌다.
- 예상 PASS / FAIL 조건: 읽기 전용 probe 단언 A1~A5 모두 PASS면 정적 `FEASIBLE`. 하나라도 FAIL이면 S3 `BLOCKED(composition)`으로 두고 혼합 144k를 `a10024de`에서 먼저 연다.
- 변경 파일 / source fingerprint / 커밋: 신규 `docs/work/active/G2_STRATEGY_S3_F4_INTEGRATED_W46_LAP572.md`, 신규 probe `docs/history/laps/probes/20260925_lap572_strategy_f4_on_a10024de_overlap.py`, 이 기록, `loop/ESCALATE_SOL` §125, STATUS·INBOX 갱신, S5 제출문 부록, STATUS 압축 스냅샷 `docs/history/20260925_status_lap572_precompaction.md`. 커밋 없음(uncommitted).
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 원본 `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac` 전후 불변(sha256sum 2회). 후보 `a10024de…2d68`은 메모리에서만 재생성했고, F4 단독 `1893ff50…53ae1`도 메모리에서 재현했다. 결합 메모리 SHA `dfdc91adb88a732d96dff96f78648f03406003bffce1b22a7e5836317f963883`. Wine/Xvfb 미사용, fixture 없음.
- 실행 명령 / 로그 / 캡처 경로 및 해시:
  - `python3 docs/history/laps/probes/20260925_lap572_strategy_f4_on_a10024de_overlap.py` → exit 0. 사전 고정 단언 A1 원본 SHA, A2 후보 재생성, A3 F4 old bytes 15/15 존재, A4 후보 diff 5,912B와 겹침 0, A5 F4 단독 SHA 재현이 모두 True다. 파일 쓰기는 없다.
  - lap570 raw 재확인: `seed_receipts.json` `7b77af47…`, `t0_positions.json` `04653a7c…`, `samples.jsonl` `3bf57033…`(638행), `save_load_result.json` `63ae5320…`. 캡처 없음.
- 측정값 / 판정:
  - lap571 검수 동의(PASS): save `16061→16061`, pre-load `16368`(307 tick), load `16369→16061`. 풀 1,687/1,688/1,687, 차집합 `{(2313,526601,7,0)}`, `post_load == pre_save`, 8 owner `(used,reserved,count)` 복원.
  - Q9 해석 결정(strategy, 번복 가능): 제외 범위는 커뮤니티 배포 EXE(원본 폴더에 `조선의반격 ESL 2601 (멀티용).exe` 등이 실재)다. F4 통합 후보의 격리 실행은 허용된다.
  - S3 정적 `FEASIBLE`. 신규 위험 R-W: 브리지 `runtime_bridge.c:102,210,227`와 W26 `read_owners_full`이 `used`를 int16으로 읽어 상위 워드 오염을 못 본다. W46 F2/F3로 닫는다.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: 결합 후보 실행 0. 이것은 정적 증거일 뿐 런타임 증거가 아니다. G2 PASS와 사용자 3단 승인은 없다. S4 "8인" 정의와 Q10 `(다)` 제외는 그대로 사용자 전권이다. Fast(문서 반영 뒤): `make check` **835 passed/494.73s** + Ruff/compileall/mypy/`CONTEXT_PASS`(rc0, 496s), 별도 `checks/safety.sh check`=`SAFETY_PASS`, probe 파일 Ruff PASS. 이것은 Fast일 뿐이며 24k/144k 증거가 아니다.
- 다음 한 가지: work W46 결합 후보 `dfdc91ad…` 혼합 24k + 판별형 저장/로드 fresh foreground 정확히 1회(계약 `G2_STRATEGY_S3_F4_INTEGRATED_W46_LAP572.md` §4). 계획 회차 없이 바로 착수한다.
