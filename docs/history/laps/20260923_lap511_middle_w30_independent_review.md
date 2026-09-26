# 2026-09-23 | lap 511 | 목표 G2

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5-5` / high, middle tier(진단·계획·확인).
  `loop/.lap_counter`=511. 게임 코드 hands-on 수정 0.
- 가설 / 사용자 관찰: lap510 work(W30 소비, 안 A: `used`→`+0x2100`)를 원시 산출물과 원본에서
  독립 재계산한다. 12:55 사용자 지시 트랙① F4(B) 진행 중.
- 예상 PASS / FAIL 조건: 카드 §3 M-a~M-h 그대로(사후 변경 없음). M-a 는 "정적 미참조"를 disp 일치가
  아니라 **인덱스 배열의 정적 용량 범위**까지 포함해 판정한다(카드 §2 원문 "미참조 4바이트 구멍").
- 변경 파일 / source fingerprint / 커밋: 신규 `docs/history/laps/probes/20260923_lap511_middle_w30_independent_review.py`
  (SHA256 `56b7e2a7961894d8f3abeea7efd43df33722b885d844b5a034d75210260050a5`),
  `analysis/memory_maps/g2_supply_ledger_hole_rejection_lap511_20260923.md`, 이 파일. 수정: 카드
  `G2_F4B_SUPPLY_LEDGER_32BIT_LAP509.md` §8 추가, STATUS, INBOX 12:55 항목 추기, `loop/ESCALATE_SOL` §71.
  **제품 source(`patches/population/supply_ledger_32bit.py`) 는 수정하지 않았다**(work 몫). 커밋 0.
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 원본
  `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac` 전후 불변. 후보(lap510 안 A)
  `7cb0faf3b71ca2ccfea82b4ff27e6dc6f979d2bb86ca411ae33835557eb809e0` 재현(메모리/`/tmp` 복사본만).
  런타임 입력은 lap510 원시 재사용: attempt1 `samples.jsonl` SHA `e5c12aca…af94`, attempt2
  `samples.jsonl` SHA `d779b3ab…a56f`(8 owner AI, 140×140 seed42 d4a1, op7 자원 주입, 원본 패치 0).
- 실행 명령 / 로그 / 캡처 경로 및 해시:
  `python3 docs/history/laps/probes/20260923_lap511_middle_w30_independent_review.py` → exit 0,
  산출물 `/tmp/lap511/w30_independent_review.json` SHA256 `f3e9dcbd07eae83c069b905c19c158521e9455bdb47863ce3f195bac3a7b84ee`.
  `make check` → exit 0, **817 passed**(8m27s, 로그 `/tmp/lap511/make_check.out`), `checks/safety.sh check` → `SAFETY_PASS`, `CONTEXT_PASS`. 캡처 없음.
- 측정값 / 판정:
  - **M-a FAIL ⇒ 안 A 기각.** `+0x2014`(count, word)/`+0x2018`(dword 원소) 리스트, 추가 함수
    `0x43F4C0`/`0x43F4F0` 이 `cmp ax/dx,0x3e8` 로 **용량 1,000** ⇒ 원소 영역 `[0x2018,0x2FB8)`.
    `+0x2100` 은 **58번 칸**, lap510 시도1 `+0x201c` 는 **1번 칸**. 끝 `0x2FB8` 이 다음 인덱스 배열
    시작과 맞물림. lap510 런타임 0 위반은 리스트 최대 9칸(원시 재계산)이라 58번에 못 닿았을 뿐.
  - M-b PASS: 카드 원문 11곳 old-bytes 11/11, `EDITS` VA 집합 = 카드 집합. `+0x200c` 전수(abs+base
    별칭 처리 포함) = 9곳 + `0x444C63 lea`(count 포인터, `[ecx]` 만 읽음) ⇒ lap509 N154 독립 재확인.
  - M-c PASS: `create_copy`→`restore` 원본 SHA 재현(`/tmp/lap511/restore_check`).
  - M-d PASS: diff 62B, 사이트 밖 0. 패치 후 역디스어셈블 11곳 의도 일치.
  - M-e/M-f/M-g: lap510 단위 테스트는 안 A 기준이라 안 B 교체 후 다시 판정(현재 판정 보류).
  - 표본 수 정정: lap510 기록의 "1,440" 은 원시 181행×8=**1,448** owner-표본(첫 행 제외 추정). 판정 영향 없음.
  - 안 B 입력: `+0x2016` 덮는 명령 1곳(`0x43F57F`, esi≥1 이라 비도달), 원시 2,896 표본 전부 0.
    `+0x200e` 접근 4곳(별칭 없음).
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: 절차 편차 — 카드 §2 는 A 1회 실패 시 B 로 가라
  했으나 lap510 은 A 안에서 재시도했다. 안 B 에서는 구세이브 호환 재계산이 **필수**(used·building 둘 다).
  lap510 이 background `make check` 대기 중 세션이 끝나 STATUS 미갱신 — 이번 lap 이 대신 기록.
  사용자 승인 대상 변화 없음. Q9·Q8·Q7-B 미결 불변.
- 다음 한 가지: **work(Sonnet5)가 카드 §8 안 B 를 구현**(`supply_ledger_32bit.py` 교체 + 테스트 +
  `+0x2016` 24k 런타임 상수성, 원본 패치 0). 다음 middle 이 독립 검수.
