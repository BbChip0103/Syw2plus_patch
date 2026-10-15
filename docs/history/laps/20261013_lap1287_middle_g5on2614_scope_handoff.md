# 2026-10-13 | lap1287 | G5 H-G5ON2614 경계 확인 / work handoff

- 지정 역할: fresh middle(진단·계획·확인), 계약 Codex sol/high. surface Codex App outside tmux; 실제 model/effort launch argv는 노출되지 않아 추정하지 않았다. 게임/하네스 hands-on 수정·subagent 호출 없음.
- 목표/가설: lap1286 G1→G5 경계를 확인한다. INBOX23:15 명시 사용자 지시가 과거 G5 공식지원 종결·재개 금지를 해당 범위에서 대체한다. G1 완료 승인과 G5 착수 권한은 독립이다. **범위 판정 CONFIRMED, 제품 검증 SKIP.**
- 종료 조건: 최신지시·이전인계·입력SHA 확인, 최소 work handoff, 기존변경/원문보존, 문서·안전검사 후 ESCALATE_SOL로 root 인계. 스위치 추측구현·마일스톤 마감 없음.
- 순서: PROMPT① 합격조건→② AGENTS/최신INBOX/APPROVALS/STATUS/DESIGN1–4/MODEL_ROUTING→③ 안전/범위→④ lap1286 독립확인·middle 판정→⑤ 이력보존→⑥ 문서-only 검사. PROMPT의 과거 G2 10000/G4 활성 문구는 DESIGN/최신지시의 G2종료/G4종결을 덮어쓰지 않는다.
- 이전 인계: `docs/history/laps/20261013_lap1287_preserved_lap1286_escalate_sol.md`, SHA256 `d3c6368d25b1fc2fdc9a2c0927357ba3c83e243576b3063fe95da19631eba2a9`, byte-exact 확인. 기존 미커밋 코드·tests·raw·배포파일 보존.
- 원본SHA(sha256sum 재계산 PASS):2614 `ac61a28f84f71d602c581a17c835ec4dbb99aad0341c6755e395549005cf88bf`; 공식2613 `818721a5e8539f9ed97090a6d64cfdba429d46ec9caaa5671528005b22f5b724`. 후보SHA/지도/활성인원/군대/fixture 없음(게임 미실행).
- lap1286 G1 key4 SHA 재계산 모두일치: `tools/g1_hd_convert.py` cab166cb4710ef3ea9072abc29c1b65c22c6577ce07fe2e84f853bc211a1830b·`tools/inmm_stub/g1_hd_asset.c` 5e074325e411411d88f1dc22ebb3af87c8c05bf9cb3519106483bf99e06d91db·`tests/test_g1_hd_convert.py` 06a1012b23f6192f96e2b14248772838cf85999bd58cba33132134ba8e198c8e·`tests/test_g1_hd_native_reader.py` 3facee6fc60a6b9767691ac7db81d155075fd66dd5c3893014ec288b8bd6e576.
- 과거 게이트: `logs/gates/lap1283-root-make-check.log` raw2203 passed/9 skipped·960.16s·lint/typecheck/context성공·`.exit`0·로그SHA256 `499dcc216d8bd4f30e48f5bfba092f9f4140b5bd5e5f793d5eb6693f3aa6d1fc`. 이는 당시 G1 전달준비만의 증거이며 현재source/2614/G5 PASS가 아니다. lap569 source mismatch 결과 미사용.
- fingerprint before: validation `3b4533e89aa83bd788c84452428e1a378b13bd9c`; implementation `688b6c39fe0bb8e20cd13d7907e33bc2a1a1558a`(loop.sh 실제함수). 로컬 baseline `logs/gates/lap1287-middle-boundary-before.json`. 
- 직접 코드 확인: `tools/g5_candidate_drag_probe.py` legacy v3 import·TARGET_SHA `e5004764…`·SEED_COUNT55·count0..50·recall50·원본SHA가 고정되어 `--source`만2614로 넣어도100기시험 불가. V8 선택배열100칸 주소 기록은 V8핀에 한정하며2614 실제cap 증거가 아니다.

## work handoff — 재계획 없이 첫 실제 probe로

1. 입력은 `../[ESL]Syw2plus - ESL2614/` 전체의 새 사본/독립prefix/빈display. 원본SHA 위 값 확인, 원본DLL로 공식2614의 선택스위치만 대상으로 한다. G1/옛HD/변형/G2/G6/G8/G9를 섞지 않고 원본·핀은 불변. 디스크/소유프로세스/원복 규칙 유지.
2. 공식2613 대조는 선택경로diff 읽기전용. `.text/.sel60/.grp60` 변경은 조사 후보일 뿐 정답이 아니다.2614 실제 count/entries 주소·UID/owner·관련루프를 바이트/디스어셈블리로 확인하고 원본 드래그상한을 관측한다. 비활성 이유/단일스위치 여부 UNKNOWN. 배열100칸을 cap100으로 간주하지 않는다.
3. 기존probe의 격리·입력·명령receipt·save/load 패턴은 재사용하되 legacy SHA/주소/55fixture/50oracle을2614용으로 명시바인딩하는 최소대응만 work가 한다. 기존핀/legacy검사를 완화·갱신하지 않는다. 동일소유 실제selectable 유닛100초과(예:120기)·좌표/UID/owner·생성fixture를 기록한다. 장부값만100으로 쓰거나 화면밖 유닛을 입력성공으로 세지 않는다.
4. 원본관측과 native제어흐름이 비활성스위치를 증명하면 정확한old bytes/버전거부·사본출력·비중첩·byte-exact restore를 갖는 최소패치. 다른기능/상한/배열확장 금지. 단일스위치로 부족하거나 실질충돌이 있으면 근거·최소다음행동으로 승격하며 임의로넓히지 않는다.
5. 원본/후보 동일fixture에서 드래그 count/raw UID목록·UI/초상표시·선택100기 각UID 이동/공격/정지 receipt와 후속행동·Shift추가·Ctrl+숫자 저장/호출·save/load 뒤 재선택·명령·크래시를 비교한다. 일부명령누락·잘못된UID·메모리오염·비정상종료 FAIL·표본/입력실패는 도구오류·UNKNOWN으로 구분. 100개 표시만으로전원명령 PASS 금지. 멀티는 미검증/관련코드 위험공개만 하며 새실행조건에 추가하지 않는다.
6. 관련pytest→lint/typecheck→격리실게임 우선. 추적가능 패치/하네스/좌표결함은 수리→재실행. 원인불명필수실패3회/안전위반/실질충돌은 승격. 가능성조사 work1회/60분/실패가설2회 및 보조작업2회/60분 상한 유지. 종료는 요청싱글행동 실제결과/한계와 fresh middle 인계이며 전달/사용자승인 아님. 전체make check는 전달후보고정 뒤1회만.

## 기록·판정

- 변경: STATUS/DESIGN/INBOX/APPROVALS 및 lap기록·이전ESCALATE전문·새 `loop/ESCALATE_SOL`(무시된runtime state). 게임/제품/하네스/테스트 수정0·실행0·전달0·커밋0. 
- 문서검사: `python3 checks/context_limits.py`·`python3 checks/safety.py check --require-game`·PROMPT문서한도/Blockers1개·implementation fingerprint 불변/입력SHA불변·`git diff --check`. 최종결과는 아래에기록. pytest/lint/typecheck/전체check SKIP(코드변경없음). 100기/Windows/G1사용자판정 미검증. 
- root는 scope확인과 ESCALATE_SOL을 회수해 지정work를 연결한다. 새사용자허가·반복middle계획은 불필요. 이번회차는 마일스톤경계규칙으로 종료하며 직접구현/후속work 실행 안 함. 현재다음한가지는 STATUS만 따른다.

- 최종확인 PASS: context/원본·보호핀 safety/전체기존diff whitespace 정상; STATUS 46·INBOX 294·APPROVALS 68줄, Blockers1개. 이전ESCALATE SHA/입력2EXE SHA/lap카운터 불변. implementation before/after `688b6c39fe0bb8e20cd13d7907e33bc2a1a1558a` MATCH. history/DESIGN 추가로 validation fingerprint는 변경될 수 있으며 현재 전체검사 PASS로 승격하지 않았다. 결과·이번 문서SHA 목록은 무시된 `logs/gates/lap1287-middle-boundary-final.json`에 보존.
