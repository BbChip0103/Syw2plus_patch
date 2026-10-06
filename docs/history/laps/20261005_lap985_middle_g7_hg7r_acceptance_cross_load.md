# 2026-10-05 | lap 985 | 목표 G7 (H-G7r 독립 검수 + 다음 가설 정의)

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5-5` / high, 중간(middle) 1 lap. 게임 실행·source 변경·commit 0.
- 가설 / 사용자 관찰: lap984 H-G7r(R4: `0x441310` hook + cave `0x18A7D00`, 솔로에서 저장 스냅샷 `0x632F7C`→live `0x632C9C` 복사 뒤 `0x43AF40`)의 probe-result 4개와 후보 바이트가 제품 helper 없이 재계산해도 기록과 같으면 수용한다.
- 예상 PASS / FAIL 조건: 재계산 불일치 0·후보 SHA 재조립 일치·hook 꼬리로 들어오는 분기 0이면 수용. 불일치나 근거 충돌이면 ESCALATE.
- 변경 파일 / source fingerprint / 커밋: 문서만(uncommitted) — 카드 `docs/work/active/G7_MIDDLE_LAP985_HG7R_ACCEPTANCE_CROSS_LOAD_HANDOFF.md`(신규), `analysis/memory_maps/g6_g7_local_player_slot_bugs_20261004.md`(lap985 절 추가), 이 기록, `docs/STATUS.md`. `loop/ESCALATE_SOL` 처리·삭제. 제품 patch/하네스/bridge/EXE 불변.
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 이식판 normal `0e28ef57…d257`·fixed_start `703deaf4…6ea0`(이번 lap 직접 sha256 MATCH). 후보 재조립 normal `1a209807…5c91`·fixed `5c79833d…c09b`·G6+G7 normal `2de1944e…810c`·fixed `8b390817…8e72` 모두 기록과 일치. fixture = lap984 그대로(혼자하기 기본 지도, lobby-snapshot seat 2·기본 seat 0, lap982 P save001 `7e92e474…`).
- 실행 명령 / 로그 / 캡처 경로 및 해시: `temp/Syw2plus_patch/20261005_lap985_middle_review/`에서 `.venv/bin/python recalc_lap985.py recalc_lap985.json`(스크립트 SHA256 `69a9381e…8bac`, 출력 `efc7959a…4141`), `callers.py 0x41CA80`. 캡처 대조: lap984 `cand_s2/shots/20261005_061744_d_watch_end.png` vs lap982 `port/shots/20261005_054645_d_watch_end.png`.
- 측정값 / 판정:
  - 재계산: R-1 cand_s2 D local 0→2·ids `[1,1,0,…]`·ps `[3]`·owner 2, R-2 C 동일, R-3 cand_s0 local 0·ps `[3]`·owner 0, R-4 cand_oldsave local 2·ps `[3]`·owner 2, cand67 C·D local 2. 기록 대비 **불일치 0**. D live 표 앞 0x170 = A 표 = save 스냅샷(offset 1,827,770). solo 1·own 0 전 stage.
  - 바이트: 카드 레이아웃 독립 조립 SHA 4개 일치, diff 54 B, capstone 일치, `0x441311..0x441315` 진입 분기 0, 레지스터·플래그·esp 보존. 캡처: 후보 D 인게임, 기준 D "패배했습니다.".
  - **판정: H-G7r PASS(partial, 기술) 수용.** DESIGN G7 사용자 합격 아님.
  - 새 위험: `0x43AF40`이 일치 없으면 local 불변 → 1P 세이브(ids `[1]*8`)를 local≠0 상태에서 로드하면 이전 자리 잔존 가능(인게임 교차 로드, 같은 프로세스 타이틀 로드는 `0x41CA80` 초기화 경유 여부에 달림). R-3 PASS는 부팅값 0 덕분.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: 같은 프로세스·교차 로드 UNKNOWN, 멀티 `[0x4ED848]` UNKNOWN(게이트 밖 무접촉), G6 기능 on cand67 미측정, fixed_start 런타임 미실행, 사용자 ↑/↓ 경로 런타임 동일성 UNKNOWN(정적으로는 메커니즘 비차단, 카드 §5) — 사용자 합격 요청에서 최종 확인. 0x170 뒤 로비 영역 73 B 차이는 관찰 기록.
- 다음 한 가지: Sonnet work 1 lap — H-G7x(cand67·port 같은 프로세스/교차 로드 매트릭스 X-1~X-4, X-2/X-3 잔존 시 같은 lap R4b 보강), 카드 §4 그대로.
