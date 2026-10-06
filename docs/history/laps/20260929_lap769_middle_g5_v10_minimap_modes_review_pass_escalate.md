# 2026-09-29 | lap 769 | 목표 G5 (middle: v10 미니맵 세 모드 독립 재검수)

- 실제 provider/model/effort / 지정 역할: Codex native session, middle(진단·계획·확인) 역할. 실제 served
  model ID는 이 surface가 노출하지 않아 `gpt-5.6-sol`이라고 주장하지 않는다. 게임 패치·probe·제품 코드는 수정하지 않았다.
- 가설 / 사용자 관찰: lap768의 진단 gate 조건에서 이동·공격(어택땅)·순찰 버튼 뒤 미니맵 좌클릭이
  원본20/v10 50의 선택 전원에게 같은 종류의 목적지/명령을 전달했다면, 사용자 추가 항목은 제한부 PASS로
  수용하고 기존 G5 v10 `PASS_WITH_LIMITS`를 사용자 3단 판단에 다시 올릴 수 있다.
- 예상 PASS / FAIL 조건: PASS = 원본20/v10 50 모두 선택 수·fixture·후보 SHA가 맞고 세 모드의
  `pending_xy`가 전원 변화하며 즉시/지연 command 신호가 원본과 대응, 크래시·trace fatal·원본 변경·cleanup
  실패가 없고 현재 source Fast가 PASS. FAIL/HOLD = 후보만 명령 종류/전달 수가 어긋나거나 패치/Fast가 실패.
  마일스톤 경계에서는 기술 판정만 남기고 `ESCALATE_SOL`로 넘긴다.
- 변경 파일 / source fingerprint / 커밋: 제품·패치·probe 0 변경. 이 기록과 `docs/STATUS.md`,
  `docs/feedback/{INBOX,APPROVALS}.md`, `loop/ESCALATE_SOL`만 갱신. Fast 시작 validation fingerprint
  `ad84f4db300f5f202550fc61a1cb082f46bef40f`, implementation fingerprint
  `67e10f6a68cf11f3cd2c1a4929e7a048e53aeeb0`, HEAD `a944d6ca5e95f4b525a09d3cf882cf8d894356fc`,
  커밋 없음(`LOOP_ALLOW_COMMITS=0`).
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 보호 원본
  `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`; v10
  `c3ceaa25dea98232234759a332b867d92a669f63a03c3f453d3199cc329ebfad`. lap768은 새 전체 game
  copy/Wine prefix/Xvfb, 1인 solo, 기존 맵, owner0/type2 55기 합성 fixture(기존 worker 1기 포함),
  원본 선택20·후보 선택50. 이번 lap은 보존 raw/capture의 독립 재계산이며 새 runtime 실행이 아니다.
- 실행 명령 / 로그 / 캡처 경로 및 해시: `make doctor`; lap768 JSON `sha256sum`+`jq` 재계산;
  원본/후보 attack 캡처 육안 대조; v10 임시 copy-only 재빌드·wrong-version/same-path/unknown-restore 거부·
  byte-exact 원복; `make check`; `checks/safety.sh check`; `checks/context_limits.py`. lap768 JSON SHA는
  원본 `af44986f629c78fcfe6b7819bd711c533afeeec1dd22deefcc099dd0e2baf88d`, 후보
  `145e281f0a7abc9c77b51782025ac875ad0b0d166f1fb365ac6341f7460e5c0d`. Fast 로그
  `logs/gates/full-test-20260929-lap769.output` SHA256
  `88bbd6101c1ddd54cc55350a6fd7eb3e7e5c202987c32aceccd6e00b435fd2bd`.
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN): 두 raw 모두 fixture receipt 55/55, source unchanged,
  PS9→PS3, gate `0→1`, LUT non-FF 16200, trace fatal 없음, alive/cleanup PASS. 선택은 원본20 unique20,
  v10 50 unique50. `pending_xy`는 이동·공격·순찰 모두 원본20/20, v10 50/50 변화. 이동 즉시
  `command=3`은 20/20 대 50/50. 공격 즉시는 기존 worker가 양쪽 모두 command1을 유지하고 나머지가
  `command=3` 19/20 대 49/50이며, transient pending low16=4가 양쪽 1기씩 관측돼 원본 parity다.
  순찰은 원본 즉시20/20 `command=35`, v10은 즉시49/50·지연50/50 `command=35`. 첫 원본 명령의
  exit1은 기존 artifact root 재사용 거부이며 새 `original-r2`에서 해소된 실행 래퍼 오류로 보존한다.
- 패치 / Fast 판정: 현재 보호 원본에서 v10 결정적 SHA·길이 불변, hook old/new bytes, copy-only,
  잘못된 버전·same-path·unknown restore 거부, exact restore PASS. `make check` 1136 passed·5 skipped
  (684.82s), ruff/compileall/mypy/context PASS; `SAFETY_PASS`. skip 5건은 pinned stock/ESL reference 부재다.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: 사용자 추가 미니맵 세 모드는 원본 parity로 PASS.
  G5 v10 2단은 `PASS_WITH_LIMITS`를 유지한다(A/B/C/D/F/H PASS, E 조건부, G `BLOCKED(env)` 수용).
  `0x97597c=1`은 격리 진단 write이므로 정상 로비 `game_type==3` UI 접근성, 실제 LAN 동기화, E 가림과
  기존 N/A/edge는 미검증이다. 작업 중 최신 사용자 사전 승인(18:4x)이 도착했다: lap769가
  `PASS_WITH_LIMITS`면 재질문 없이 G5 v10을 알려진 한계와 함께 3단 승인·종료하고 다음은 G1이며,
  G2 전체 점검은 G1 뒤로 순연한다. 기술 조건은 충족했지만 이 세션은 마일스톤 경계에서 직접 마감하지
  말라는 호출 지시를 따라 적용 판정을 승격 작업자에게 넘긴다.
- 다음 한 가지: 승격 작업자가 후보 SHA·이 `PASS_WITH_LIMITS`가 사전 승인 조건을 충족함을 확인해
  APPROVALS에 G5 v10 3단 승인·종료를 기록하고, 사용자에게 재질문하지 않은 채 `STATUS`의 다음 한 가지를
  G1(원본 구도 유지 1600×1200) 착수로 전환한다.
