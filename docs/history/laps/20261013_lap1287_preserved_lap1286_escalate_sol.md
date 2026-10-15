lap1286 hands-on work — G1→G5 milestone priority boundary; stop before implementation

PROMPT ①–⑥를 확인했다. 이 세션의 hands-on work 역할에서는 사용자의 새 지시를 무시하지 않되, G1 시험판 전달 뒤 사용자 결과/마일스톤 판단이 미결인 상태에서 종결 처리하지 않았다. 2026-10-13 23:15 INBOX의 새 사용자 지시가 G5 100기 선택 재개를 최우선으로 지정했으며 STATUS의 다음 항목도 H-G5ON2614다. 기존 DESIGN/STATUS에는 G5가 공식 ESL 지원으로 종결됐다는 계약이 남아 있어 G1→G5 전환은 PROMPT의 마일스톤 경계 승격 조건에 해당한다. 구현·런타임 작업 전에 fresh Sol이 우선순위 경계와 실행 범위를 판정해야 한다.

보존된 상태/근거:
- G1 H-HDSINGLE writer 수리는 lap1283 fresh middle에서 PASS(scoped, 기술). root가 같은 source의 전달 직전 `make check`를 exit0, 2203 passed/9 skipped, fingerprint MATCH로 마치고 2026-10-13 21:17 시험판 `260921_temp/G1_1600x1200_시험판_20261013_2613_HD_원본형식/`을 전달했다. Windows/DxWnd/사용자 화질·G1 마일스톤 결과는 아직 미확인이다. 제품 완료나 사용자 승인으로 기록하지 않는다.
- 최신 사용자 지시: 23:15, H-G5ON2614. 2614에서 비활성 100기 선택만 켜는 최소 사본 패치, 꺼진 원본과 비교해 선택/UI/이동·공격·정지/Shift/부대지정/세이브로드/크래시를 확인한다. 현 단계에서 코드를 만들지 말고 Sol 판정 뒤 지정 work 역할이 실행한다.
- HDSINGLE 관련 기존 미커밋 구현·테스트와 evidence는 그대로 둔다. `tools/g1_hd_convert.py` SHA256 `cab166cb4710ef3ea9072abc29c1b65c22c6577ce07fe2e84f853bc211a1830b`; `tools/inmm_stub/g1_hd_asset.c` `5e074325e411411d88f1dc22ebb3af87c8c05bf9cb3519106483bf99e06d91db`; `tests/test_g1_hd_convert.py` `06a1012b23f6192f96e2b14248772838cf85999bd58cba33132134ba8e198c8e`; `tests/test_g1_hd_native_reader.py` `3facee6fc60a6b9767691ac7db81d155075fd66dd5c3893014ec288b8bd6e576`. No source/test/runtime files changed in lap1286.
- Runtime opening evidence: HEAD `27dad8128791b70770dbabc6f21342eea76ef53c`, source fingerprint `c74e1f94bfcbfb9e7f2ca2328d222d8cd838cb23`, `head_match=no`, `source_match=no`; old lap569 full-test is source-mismatched and not current proof.
- INBOX was 361 lines (>350). Exact original archived before compaction at `docs/history/20261013_inbox_lap1286_precompaction.md`, 361 lines, SHA256 `3ae725dc4c9349dd13d016f6c59ac84a09dc9de8d9be466701fceb4f708e61c4`. A later 2614 input fact appeared during the compacted edit; the 291-line compacted snapshot SHA256 `ae3f84986c06100d4021fe6f9d2013950a34f3f01124e6a4edb502006ae8cb92` is preserved at `docs/history/20261013_inbox_lap1286_compacted_snapshot.md`. All original nonblank lines remain in order; current INBOX adds two provenance pointers. STATUS/INBOX/APPROVALS now remain below PROMPT limits.

승격 작업자가 이어서 할 일:
1. Fresh Sol role로 새 H-G5ON2614 지시와 G1의 미결 Windows/user milestone을 대조해 우선순위/경계 판정을 기록한다. G1 결과를 임의 PASS로 만들거나 G5를 이미 사용자 승인된 구현으로 간주하지 않는다.
2. 재개 승인 범위가 확정되면 work에서만 2614 원본/사본 SHA, 2613 대비 선택 관련 차이와 실제 비활성 스위치를 확인하고 주소 근거를 남긴다. 사용자 지시대로 스위치만 사본에 패치하며 변형 EXE·원본은 수정하지 않는다.
3. 100+ fixture에서 꺼진 2614와 후보를 비교해 드래그 수, UI, 이동/공격/정지, Shift, Ctrl+숫자 저장/호출, save/load, crash를 기록한다. 멀티 동기화는 단일 실행으로 합격 처리하지 않고 위험/미검증으로 보고한다. 관련 회귀→격리 실게임 검증을 우선하고 전체 `make check`는 사용자 전달 직전만 수행한다.
4. 이전 G1 변경·raw·미결 user result, mirror BLOCKED/tree_plus UNKNOWN을 보존한다. 새 결함이나 충돌이 확인되면 해당 범위만 다시 승격한다.

lap1286 판정: milestone boundary에 따른 ESCALATE_SOL. 제품 수정/테스트/게임 실행/전달/커밋 없음. G1 사용자 판정 미완료, G5 실행 대기.
