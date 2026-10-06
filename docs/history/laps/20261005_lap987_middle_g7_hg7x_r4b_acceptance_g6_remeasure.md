# 2026-10-05 | lap 987 | 목표 G7 (H-G7x/R4b 독립 검수 + 다음 가설 정의)

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5-5` / high, 중간(middle) 1 lap. 게임 실행·source 변경·commit 0.
- 가설 / 사용자 관찰: lap986 H-G7x(R4 X-3 FAIL → R4b: 솔로 게이트 안 `mov dword [0xB63FC4],0` 뒤 `0x43AF40`)의 probe-result 10개와 R4b 후보 바이트가 제품 helper 없이 재계산해도 기록과 같으면 수용한다.
- 예상 PASS / FAIL 조건: 재계산 불일치 0·후보 SHA 4개 재조립 일치·cave 역어셈블 일치면 수용. 불일치나 근거 충돌이면 ESCALATE.
- 변경 파일 / source fingerprint / 커밋: 문서만(uncommitted) — 카드 `docs/work/active/G7_MIDDLE_LAP987_HG7X_R4B_ACCEPTANCE_G6_REMEASURE_HANDOFF.md`(신규), `analysis/memory_maps/g6_g7_local_player_slot_bugs_20261004.md`(lap987 절 추가), 이 기록, `docs/STATUS.md`. `loop/ESCALATE_SOL` 처리·삭제. 제품 patch/하네스/bridge/EXE 불변.
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 이식판 normal `0e28ef57…d257`·fixed_start `703deaf4…6ea0`(직접 sha256 MATCH). R4b 재조립 G7 normal `a75aa129…e08b`·fixed `7edcc078…6dfbb`·G6+G7 normal `fb7c2131…c56a`·fixed `58b9b22a…f078` 모두 기록과 일치. fixture = lap986 그대로(혼자하기 기본 지도, lobby-snapshot seat 2·기본 seat 0, S2 `1c5acd27…`·S0 `51c7e3e7…` SHA 재확인).
- 실행 명령 / 로그 / 캡처 경로 및 해시: `.venv/bin/python ../temp/Syw2plus_patch/20261005_lap987_middle_review/recalc_lap987.py …/recalc_lap987.json`(스크립트 SHA256 `10c1b0bd…a2ba`, 출력 `6b1a99a3…a9f3`). 캡처 대조: lap986 `c67_x3/shots/20261005_065505_x0_watch_end.png`("패배했습니다.") vs `r4b_x3/shots/20261005_070224_x0_watch_end.png`(인게임), `r4b_x12/shots/20261005_070423_x0_title_return.png`(타이틀).
- 측정값 / 판정:
  - 재계산: R4 X-3 local 2 잔존·ps `[3,27,29]`(port 동일, 표 불변) / R4b X-3 local 2→0·ids `[1]*8`·ps `[3]`·owner 0, X-4 local 0→2·owner 2(R4·R4b, port는 패배), X-1/X-2 타이틀 복귀 직후 local 0 → S2 2·S0 0, R-1 local 2, R-3 local 0. 기록 대비 **불일치 0**. R4b 로드 직후 표 앞 0x170 = 세이브 스냅샷.
  - 바이트: cave 66 B·jne rel8 0x29·diff 59 B(범위 밖 0)·capstone 일치, 제품 cave/hook 바이트 = 독립 조립.
  - **판정: H-G7x PASS(partial, 기술) 수용, R4b를 G7 현행 후보로 채택.** DESIGN G7 사용자 합격 아님.
  - 관찰: R4 c67_x3·port_x4 "loaded" 표본 표가 로드 전/스냅샷 어느 쪽도 아님(패배로 가는 run, 게임이 표를 고쳐 쓴 것으로 봄, writer UNKNOWN·비차단). 타이틀 도움말에 "▲▼ : 방장만, 자리 변경" 표시(사용자 답과 일치).
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: G6 on cand67(R4b) 미측정, fixed_start 런타임 0회, 자리 2 한 곳·own 0만, 멀티 UNKNOWN(게이트 밖 무접촉), 사용자 ↑/↓ 런타임 동일성 UNKNOWN(비차단, 사용자 합격 요청에서 확인).
- 다음 한 가지: Sonnet work 1 lap — H-G6r(G6 재측정 on cand67 `fb7c2131…` seat 2·seat 0 + fixed_start cand67 `58b9b22a…` observe 1회), 카드 §4 그대로. 그 뒤 middle이 사용자 합격 요청 범위 확정(마일스톤 경계).
