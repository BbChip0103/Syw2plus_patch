# lap792 ESCALATE_SOL 원문 보존

# lap792 승격 요청 — G2 ESL2608 Phase C UI 계약 미확정

현재 세션은 G2 Phase C에서 실제 UI 생산까지는 fresh baseline으로 재현했지만,
생산 후 집결지 지정과 장수 UI 생산의 입력 계약을 특정하지 못해 네 조합 paired를
완주하지 못했다. 같은 가설을 더 반복하지 않고 work 결과와 raw를 보존한다.

승격 작업자가 이어서 검증할 것:

1. `tools/g2_esl2608_phase_c_production_probe.py`의 fresh private runtime 계약을
   유지한 채, HQ 선택 화면의 실제 집결지 버튼/단축키와 유효한 지도 좌표 입력을
   원본에서 먼저 확정한다. R 후보 `(704,503)` 및 오른쪽 클릭/좌표 `(560,330)`,
   `(450,300)`은 이번 raw에서 집결 필드 `+0x654/+0x656`를 바꾸지 못했다.
2. 새 게임에서 `+0x980` 장수 수가 0인 이유와 `장수7명` 계열의 실제 장수 생산
   fixture/UI 경로를 raw로 확정한다. 영웅 아이콘 후보 `(776,540)`은 생산·장수수
   변화를 만들지 않았고, `(738,540)`도 이전 baseline 재현에서 영웅이 생성되지 않았다.
3. 위 계약이 확정되면 normal/fixed_start × baseline/candidate 네 조합을 같은
   overlay/bridge로 fresh paired 실행한다. 생산 worker count/slot, HQ rally,
   장수 count/type/cmd/도착, source unchanged, cleanup을 모두 기록한다.

근거 raw:

- `temp/Syw2plus_patch/g2_esl2608_lap792/normal_baseline*/probe-result.json`
- 결과 SHA: `a8acdf47154ac3c81a7831b6a249c7abaa10c5e4219b1ee75bef58e5d459bf71`,
  `e21815a44497a4c9ac1b42b224c0c74c2db4d1a215eb983906ad30b7c064a752`,
  `a6b75fa37d790ff117f6e4a27ac7ab846f09ad753fe5f3857d2f31c51c53ce7c`,
  `9f713f04eee88c84a43879238ab0ee2a3032f8d51e8100163d320e3358ec579a`.
- 네 실행 모두 `source_data_unchanged=true`, `game_removed=true`, prefix 잔류 프로세스 0.
