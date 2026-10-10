# 2026-10-09 | lap 1204 | G1 H-HDU2(업스케일러 입력 묶음) — 사전등록 부재, 승격

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-sonnet-5-5` / 실무(work)
- 가설 / 사용자 관찰: 2026-10-09 13:52 사용자 선택 "입력 묶음 만들어줘"(lap1203 선택지 (1)). 디스크는 root 정리로 여유 239 GB.
- 예상 PASS / FAIL 조건: 해당 없음(구현 착수 전 경계 판정).
- 변경 파일 / source fingerprint / 커밋: 문서만(이 기록, STATUS, INBOX, `loop/ESCALATE_SOL`). 제품 코드·테스트·게임 run 0. uncommitted.
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 해당 없음(게임 실행 0).
- 실행 명령 / 로그 / 캡처 경로 및 해시: `ls docs/work/active | grep -i HDU`, `grep -l HDU2 -r docs/work docs/history/laps` → H-HDU2 카드·사전등록 없음(INBOX 13:52 root 메모가 "다음 middle이 사전등록"이라고 명시). `loop/STOP`·기존 `loop/ESCALATE_SOL` 없음.
- 측정값 / 판정: UNKNOWN(구현 안 함). 사유 = 사전등록(묶음 범위·구성·성공/실패 측정식·위치) 없이 work가 마일스톤 경계 작업을 추측 구현하지 않는다(PROMPT 역할 규칙, 사용자 결정 원문 "다음 middle이 이 작업을 사전등록한다").
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: 없음. 참고 사실 — `tools/g1_hd_extract.py`(H-HDX1)는 프레임당 1x 인덱스 PNG(`imjin2.pal`, 투명 254)·실루엣 마스크·Scale2x 초안을 만든다. 이번 세션 셸의 `python3 -I`에는 numpy가 없어(`ModuleNotFoundError`) 도구 실행 환경(venv 경로)을 middle 카드가 명시해야 한다.
- 다음 한 가지: middle이 H-HDU2를 사전등록 → 그다음 work가 구현.

## middle이 정할 것(승격 인계)

1. 묶음 범위·구성: char·tile·fnt 약 43,622프레임(약 0.6 GB), 투명 254, 팔레트, 출력 규칙(`hd/<원본 상대경로>/<프레임4자리>.png` 사양 대조), 마스크·Scale2x 초안 포함 여부.
2. 위치: 공유 `temp/Syw2plus_patch/` 아래 새 폴더. 안내문 txt 금지(AGENTS) — 안내는 APPROVALS 항목에만.
3. 성공/실패 측정식: 프레임 수 전수 일치(manifest), 투명 254 보존, 팔레트 해시, 원본 read-only SHA, 재추출 결정론.
4. 추출 도구 실행 환경(numpy 포함 python)과 디스크 여유 확인(239 GB).
