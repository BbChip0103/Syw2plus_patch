# Sol 승격 — lap1273 G1 사용자 마일스톤 경계

## 요청된 판정

현재 큐는 `docs/STATUS.md`의 lap1272 공식2613 HD 시험판에 대한 Windows 사용자 확인이다. 이 세션의 hands-on 범위는 ①~⑥을 읽고 해당 경계에서 멈추는 것이다. 기술 검수 PASS를 G1 완료나 사용자 승인으로 바꾸지 말고, 새 격리 런·동일 SHA 재검수는 반복하지 않는다.

## 보존된 기준

- 전달판: `../260921_temp/G1_1600x1200_시험판_20261011_1272_2613_HD_변형/`
- 공식 EXE SHA256: `818721a5e8539f9ed97090a6d64cfdba429d46ec9caaa5671528005b22f5b724`
- 전달 DLL SHA256: `205b89b2c6ff3ae530ed3cbb705b644ea454404a0efee37de3980a85da36c28c`
- manifest SHA256: `151148f2b5ffd6e4ad12013ce32de53c94e78d894a52d83f7271a19283656707`; 39,942 payload 항목 재해시 MATCH, txt0.
- raw result SHA256: `013a7f184e215004f4b6ea33c19019a6c94a6107663a2dcead4167efd662f6a4`; 상세 `docs/history/laps/20261011_lap1272_work_htrvar_official2613.md` 및 `../temp/Syw2plus_patch/20261011_lap1272_official2613/`.
- 네 격리 lane의 wrapper/PS3 및 cleanup은 PASS, fresh Codex sol scoped review PASS. Newgame HD-key reject1은 기존 `tree_plus` key와 일치하나 원인 UNKNOWN. mirror validator는 BLOCKED(oracle minimum 약0.6237/0.5273). 이를 화면 parity PASS로 확대하지 않는다.
- 미검증: 사용자 Windows 실행, 실제 1600×1200 화면·입력 대응, G1 마일스톤 승인. Wine display-only 실행은 Windows 확인을 대신하지 않는다. G2 pool/8인 부하 및 G9 행동도 이 결과의 범위 밖이다.

## 이어서 할 일

1. 현재 승인/반려와 STATUS를 확인하고, 전달판에 대한 사용자 Windows 실행·해상도·화면 구성·입력 대응 결과를 기다린다.
2. 결과가 도착하면 기존 미검증 범위와 분리해 기록한다. PASS/FAIL은 관찰된 사용자 결과만으로 판단하고 raw reject/mirror BLOCKED를 보존한다.
3. 새 실패가 구체적으로 보고되면 그 실패 경로만 최소 재현·수리한다. 사용자 G1 마일스톤 판단 전에는 완료 처리나 다음 마일스톤 이관을 하지 않는다.

근거 인덱스: `docs/STATUS.md`, `docs/feedback/INBOX.md` lap1272 전달 사전결정, `docs/feedback/APPROVALS.md` 2026-10-11 전달 기록, 위 lap1272 기록.
