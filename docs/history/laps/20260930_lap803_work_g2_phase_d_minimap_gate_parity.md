# 2026-09-30 | lap 803 | G2 Phase-D 미니맵 gate parity

- 날짜/lap/목표: 2026-09-30 / 803 / G2 ESL2608 Phase-D 첫 항목인 미니맵 gate parity.
- 가설: G2 pool/supply 후보가 미니맵 라우터 gate 또는 `0x4516A0` 호출 경로를 바꾸면 후보별 runtime 수리/검증이 필요하고, 바이트가 같으면 이 항목은 원본 parity 정적 판정으로 닫을 수 있다.
- 변경파일: `analysis/memory_maps/g2_esl2608_phase_d_minimap_gate_parity_lap803.md`, `docs/history/laps/20260930_lap803_work_g2_phase_d_minimap_gate_parity.md`, `docs/STATUS.md`, `docs/feedback/INBOX.md`. 제품 EXE·원본·참고 저장소·runtime·probe는 변경하지 않았다.
- 원본SHA/후보SHA: normal baseline `cade60b2451519ec4e305d91279b1c377cf797c813a939c5b54c2e9b30b176a3`, normal candidate `83c7df80a3273d95d58e7a493866bbb40ad705d10120bc05db660400961fad60`; fixed_start baseline `f5f816eeb3d8b531ff030f4b43b2f2338ccf0d2257a5684b034e1f8dc8ee1973`, fixed_start candidate `1bdcadf9edeccc16d92696e580a60fc71f13a13b6bba22cafb8c9f50e749262f`.
- 실행명령: 각 EXE `sha256sum`; `objdump -Mintel -D --start-address=0x41c430 --stop-address=0x41c495`; `objdump -Mintel -D --start-address=0x41e420 --stop-address=0x41e480`; read-only Python byte-slice SHA 대조; `python3 checks/context_limits.py`.
- 수치: 네 파일 모두 `0x41c430..0x41c494` 101바이트 SHA `5982cbaa5a1e25e8e5b8abd31c199c9d0c29943cc1e6fefdfffeeab8a33ade37`, `0x41e420..0x41e47f` 96바이트 SHA `5b75237642db6e5bd9eff69fbc8191388c55aeef5681252c20109b2107b340a4`; `0x41c450` gate와 `0x41e43d→0x41e464` router/hit-test 호출 바이트 일치.
- 판정: **PASS(정적 parity)** — `MINIMAP_GATE=ORIGINAL_PARITY/STATIC_ONLY`. 실교전·정상 game-type 미니맵 명령 효과·고슬롯 초상화는 미검증이며 G2 완료/배포/사용자 승인으로 승격하지 않는다.
- fixture/환경: runtime 없음, 게임/Wine/Xvfb 미실행, 입력 EXE SHA 확인만 수행.
- 다음행동: Phase-D 다음 단일 항목인 실교전과 고슬롯 초상화 4-way 중 실교전부터 fresh paired 측정한다. 멀티·최종 새 이름 EXE·사용자 승인은 이후다.
