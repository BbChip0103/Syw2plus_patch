# lap661 ESCALATE_SOL 보존본

- 원문: `loop/ESCALATE_SOL` 39줄, SHA256 `3fd7a25f047d9daa6b4c7cebda3be457d2158315a626971a5a62589710d46c33`

- 처리: lap659 항목은 2026-09-26 04:47 운영자 make check 완주(909 passed)로 해소. lap660 항목은 lap661 strategy가 부대지정 재배선 계약을 확정(`docs/history/laps/20260926_lap661_strategy_g5_control_group_rewire.md`)한 뒤 전문을 여기 보존하고 파일을 해제했다.

---

# lap659 escalation — G5 lap658 독립 컨펌 중 필수 Fast 중단

## 승격 사유

`make check`가 현재 source에서 909개를 수집한 뒤 51%의 `tests/test_g2_unit_pool_xrefs.py` 진입 시 약 600초(로그 599923ms)에 SIGTERM되어 exit 143으로 끝났다. assertion 실패는 관측되지 않았지만 필수 게이트가 완주하지 않았으므로 lap658을 2단 PASS로 승인할 수 없다. 사용자 지시대로 현 회차에서는 재시도하거나 억지로 마감하지 않았다.

## 보존된 확인 결과

- 보호 원본 SHA: `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac` (`make doctor` verified, side effects false).
- 구현/테스트 SHA는 lap658 기록과 일치: builder `5551373a…f223`, builder test `a8929fd3…19d9`, probe `8c5fe285…73f1`, probe test `ab18449c…52d1`.
- `/tmp` 새 재빌드 후보 SHA `6c8f73ba…b25`는 lap658 보존 후보와 `cmp=0`; end `0x0108C0CC`, END sites 14.
- targeted G5 검사는 9 passed. lap658 raw JSON 재해시 및 직접 판독은 candidate fixture55/selection50/move_selection50/movement_nonzero50/cleanup ok/source unchanged, paired original selection20/move20/cleanup ok/source unchanged와 일치.
- 캡처 육안 대조에서도 후보는 원본보다 많은 선택 윤곽을 보이나, UI/부대지정/save-load 제품 축 증거로 승격하지 않는다.

## 승격 작업자가 이어서 검증할 한 가지

1. `logs/laps/2026-09-26/lap-0659.log`의 exit143이 테스트 실패가 아니라 호출 환경의 600초 종료 경계인지 먼저 확인한다.
2. 장기 실행 규칙에 맞는 충분한 동기/monitor 시간으로 현재 source의 `make check`를 한 번 완주한다. nonzero면 exact failing test/output을 보존하고 무변경 재시도를 반복하지 않는다.
3. Fast PASS일 때만 lap658의 단일 경계/후보 SHA/fresh 50·원본20/restore 근거를 selected middle model로 독립 컨펌한다. 이후 UI·Ctrl+숫자 부대지정·save/load는 별도 work-tier 실행 카드로 넘긴다.

상세: `docs/history/laps/20260926_lap659_middle_g5_end_bound_review_blocked.md`.

# lap660 escalation — G5 UI/control-group/save-load 20-entry consumer remains

## 승격 사유

Fresh private candidate execution proved the remaining G5 product path fails: drag selected 50 unique units, but Ctrl+1 stored group1 count 50 while the live selection and recall were both capped at 20. After save/load, group1 count and first ID remained but recall again returned 20. This is a required runtime verification failure, not a harness timeout; do not claim G5 product PASS or retry the same candidate unchanged.

## 보존된 확인 결과

- Candidate `6c8f73ba5626a978abaa09bb56adc46ee5da39bdd16d05c71285ce10d8f20b25`; protected original `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac` unchanged.
- Artifact `/home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/20260926_lap660_g5_candidate_ui/probe-result.json`, SHA `c28f3ec3a6df00564e9d567742c740b0b784c38e28f7674be8061c5a96d5fce2`; candidate cleanup/source checks pass; private game copy was trashed after run.
- Raw measurements: drag `50/50`; Ctrl+1 stored `group1_count=50`, then recall `selection_count=20`; `save001.dat` exists, 2,499,822 bytes, SHA `3bf4ea95c2f8f203244284151722d4d158b832ba5f602cfc75e42e697b2c854b`; load retains group metadata but recall remains 20.
- Targeted pytest `9 passed`; `bash checks/safety.sh check`=`SAFETY_PASS`; no source write, commit, or protected runtime write.
- Static original disassembly at `0x00445D30` uses `[ebp+0x16]` as 10×20 group storage and count at `+0x336`; original/accepted candidate builder explicitly leaves `control_group_fields` and `command_packet` unchanged. Simple immediate widening would write past the PlayerStruct group area.

## 승격 작업자가 이어서 검증할 한 가지

Strategy/middle must independently map the minimal safe rewire of the group save/recall function to the reserved candidate side-table `0x0108C100` (10 groups × 50 × 4 bytes), including group counts, caller frame/loop bounds, and save/load serialization. Only after that bounded patch is approved should a work session implement it and fresh-run candidate plus paired original20 for UI/recall/save/load. G5 remains incomplete; user milestone approval is absent.
