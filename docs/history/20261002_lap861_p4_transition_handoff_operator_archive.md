# lap861 일반 middle → 승격 Sol: G1 P4 HOLD / 입력·전환 계측 수리 인계

사용자 근거 충돌 stop 규칙에 따라 보존·종료한다. 구현/빌드/새 Wine/커밋0.
직전 ESCALATE 전문: docs/history/20261002_lap861_prior_lap860_escalate_sol_archive.md
SHA256 e308355a8aaacf6fffd2c48236e2529441178afeac0a085bce8beaba3baa41af.

## 독립 확인

- DOWN baseline [158,101]→[159,102], candidate 불변. RIGHT 후보만 이동.
- raw PS3 present1919개, seq1587~1616 coverage median57,136(11.9033%), 다음30 47,778.5(9.9539%). outside diff0.
- 입력 전 cursor를 이동 후 표본창 시작점으로 쓰는 하네스 결함 확정:
  tools/g1_saved_scene_probe.py:706~724 및 :169~210. raw창 camera 필드0.
- XTest 기본 hold30ms·repeat2·interval120ms이고 수신/foreground ack 없음.
  이것이 DOWN 원인이라는 단정은 불가. 실제 입력 수신/타이밍과 후보 회귀는 아직 구분 안 됨.
- 정확한 stale writer/destination→present 경로도 UNKNOWN. 새 writer 구현 범위 승인 없음.

## 승격 작업자가 이어서 검증 / work tier 명시 handoff

1. 일반 middle의 반복 재요약 대신 다음 work(Luna/Sonnet)에 즉시 입력/전환 계측 수리를 넘긴다.
   범위: tools/g1_saved_scene_probe.py·tests/test_g1_saved_scene_probe.py,
   필요 opt-in receiver/present 계측만 tools/inmm_stub/direct_draw_trace.c.
   게임 구현/원본 EXE/공용 XTest helper/validator/임계값/G2/G5 변경 금지.
2. private same-save fresh baseline/candidate DOWN에 foreground·수신·camera·sim tick·present seq를 묶는다.
   timing 원인 확인 시 양쪽 동일 hold 옵션 적용, process exit0은 수신 증거 아님.
   DOWN 성공을 RIGHT로 대체하지 않으며 0.5초 sleep 뒤 cursor도 첫 전환 프레임을 놓쳐 불충분하다.
3. raw present와 같은 시점 camera로 실제 전환 seq 및 이후30 present를 식별한다.
   지연 입력 전 고coverage/무전환/전환 이후30개 분리 회귀를 고정한다.
   fresh B-5 coverage≥264,000·outside diff0·Scale2x validator 무수정·scene/source/cleanup PASS.
   B 전부 통과 전 C fresh3 pair·P5 금지.
4. stale가 남으면 정확한 writer/destination/source/좌표를 계측한다.
   기존5 hook 내부 결함이면 work가 수정→빌드→fresh 재실행 반복;
   새 writer 필요 시 주소/old bytes/destination 근거를 승격 검수자에게 제시해 범위를 확정한다.
   stale flag 제거/nearest를 HD로 계수/임계값 완화 금지.

## 증거와 한계

Pair: /home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/lap858_p4_scroll_down_r1/pair-result.json
SHA feaa61f1a47908838ce40b91c1e4e9ad33fdd2b7d3584de4527ff57905e4ad90.
Raw: 위 candidate/trace_raw.jsonl
SHA 8e0e06cbddfdd48e53a1769f529e4edc90225b553c3bd847bd4718f2d6970ede.
Review: /home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/lap861_middle_p4_confirmation/review.json
SHA 592f2dc3dba9d993049accd2fa9099ce6831a3577b2a83037b1ed4062b89d53e.
Fresh doctor PASS, source/test9개 SHA lap860과 일치. full Fast/runtime SKIP(사용자 stop), 제품 PASS 없음.
상세: docs/history/laps/20261002_lap861_middle_g1_p4_transition_handoff_hold.md.
현재 큐는 docs/STATUS.md만 따른다. 이번 회차까지 구현 무변경 연속2회; 다음 회차 재요약만 반복 금지.
