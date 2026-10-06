# 2026-09-29 | lap 765 | 목표 G5 (middle: v10 전체 독립 재검수)

- 실제 provider/model/effort / 지정 역할: Codex native session, middle(진단·계획·확인) 역할. 실제 served
  model ID는 이 surface가 노출하지 않아 `gpt-5.6-sol`이라고 주장하지 않는다. 게임 패치/제품 코드는 수정하지 않았다.
- 가설 / 사용자 관찰: lap756~764의 항목 (1) save/load와 항목 (2) 수확(V)·미니맵 paired raw가 일치하고,
  v9→v10 변경이 저장/로드 마지막 block-transfer hook 2곳+cave로 제한되며 v10 핵심 회귀가 PASS하면
  G5 A~H를 사용자 3단 판단에 다시 올릴 수 있다.
- 예상 PASS / FAIL 조건: PASS = 보호 원본에서 v10 결정적 재빌드·byte-exact 원복, 항목 (1)+(2) raw
  일치, 현재 source의 Fast PASS, v10 핵심 회귀가 기존 v8/v9 패턴과 일치. FAIL/HOLD = 필수 회귀의
  의미 지표 하나라도 예상 밖으로 어긋남. 이 경우 재시도하지 않고 work tier로 넘긴다.
- 변경 파일 / source fingerprint / 커밋: 제품 코드 0 변경. 이 기록, `docs/STATUS.md`,
  `docs/feedback/{INBOX,APPROVALS}.md`, `loop/ESCALATE_SOL`만 갱신. 시작 source fingerprint
  `2d7724f533c505d5d307196a2ad218e53a091aa3`, HEAD `a944d6ca5e95f4b525a09d3cf882cf8d894356fc`,
  커밋 없음(`LOOP_ALLOW_COMMITS=0`).
- 원본 / 후보 / 환경 / fixture: 보호 원본 SHA
  `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`; 원본에서 메모리 내 재빌드한
  v10 SHA `c3ceaa25dea98232234759a332b867d92a669f63a03c3f453d3199cc329ebfad`; 후보 길이 불변,
  restore byte-exact. fresh 회귀는 전체 게임 격리 사본, 새 Wine prefix/Xvfb, owner0/type2 55기
  synthetic fixture, 단일플레이에서 실행했다.
- 실행 명령 / 근거: `make doctor`; v10 `build_candidate`/`restore_candidate` 메모리 내 대조;
  lap756/757/760/764 raw JSON `jq` 재계산; `make check`; `checks/safety.sh check`; 기존
  `tools.g5_command_coverage_probe`를 프로세스 안에서 v10 모듈/SHA에 바인딩해 candidate 1회 fresh 실행.
  raw는 `/home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/
  20260929_lap765_middle_v10_coverage/probe-result.json`(SHA256
  `660f1d2ea595a9a63323c19fbf60cf30c65cb8dec692e964086d633b66d2cb31`).

## 측정값 / 판정

- 정적/패치 안전 PASS: 원본·후보 SHA 일치, raw 길이 불변, v9→v10 diff 171바이트가 핀된 hook 2곳·
  cave·section header 안에만 있음(관련 pytest PASS), 알 수 없는 후보 원복 거부 및 정확 후보 원복 byte-exact.
- 항목 (1) 증거 수용: v10 자체 save/load 50→50·stale command 0, 원본이 v10 save를 20기로 정상 로드,
  v10이 원본 save를 20+zero-tail로 정상 로드, 25→25·35→35 및 부대15 호출 PASS. 전부 source 불변,
  crash/timeout 0, cleanup PASS.
- 항목 (2) 증거 수용(제한 명시): 수확 V 원본20/v10 50 PASS; 미니맵은 정상 로비 UI 경로가 아니라
  격리 `0x97597c=1` 진단 조건에서 원본 pending/command 20/20, v10 50/50 PASS. 정상 game_type UI 접근성은
  계속 미검증이며 제품 정상경로 PASS로 확대하지 않는다.
- Fast PASS: `make check` **1134 passed, 5 skipped**(712.57s), ruff/compileall/mypy/context PASS;
  `SAFETY_PASS`. skip 5건은 pinned stock/ESL reference 부재. `make doctor`는 원본 SHA와 도구/라이브러리를
  확인했으나 활성 runtime manifest가 없어 runtime.ok=false였고, 이를 runtime PASS로 쓰지 않는다.
- fresh v10 회귀 부분 PASS: plain/ALT/Ctrl/Shift full drag 모두 50/50, double-click 50/50, 51번째 거부,
  move/stop/hold/patrol 버튼·단축키 전부 50/50, alive/cleanup/source 불변 PASS.
- **예상 밖 FAIL/HOLD:** 같은 fresh run에서 Shift 단일 추가가 `2→0`, Shift 제거 시퀀스가 `0→1`
  (`removed_anchor1=false`, `kept_anchor2=false`)로 나왔다. 과거 승인 패턴 `2→3` 및 `2→1`과 충돌한다.
  probe의 `status=COMPLETE`와 exit 0은 의미 기준 PASS가 아니다. 현 run은 original paired가 없어 제품
  회귀와 클릭 좌표/타이밍 하네스 오류를 구분할 수 없다.

## 종합 / 다음 한 가지

G5 v10 전체 2단 판정은 **HOLD**다. 항목 (1)+(2)는 위 제한으로 수용하지만 (B) Shift 회귀의 새 충돌
때문에 A~H 최종 PASS, 사용자 milestone 재상정, G1 재개를 하지 않는다. 실행 사본 `game/` 810MB는
휴지통으로 옮겼고 output/manifest/prefix/log/JSON/캡처는 보존했다.

다음 work tier 한 가지: 현재 `tools/g5_command_coverage_probe.py` 그대로 original20과 v10 50을 각각
fresh paired 1회 실행해 Shift add/remove를 먼저 대조한다. 원본도 같은 실패면 전용
`tools/g5_shift_click_add_probe.py`의 안정된 클릭 계약과 비교해 coverage 하네스만 최소 수리하고 paired
재실행한다. 원본 PASS·v10 FAIL이면 v10의 저장/로드 hook 실행 여부와 무관한 인게임 선택 상태 오염을
귀속한 뒤 최소 수리한다. 어느 경우든 새 middle이 raw를 재검수하기 전 G5를 마감하지 않는다.
