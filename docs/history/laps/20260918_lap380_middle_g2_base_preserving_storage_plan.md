# 2026-09-18 — lap380 middle (Opus5/high): G2 base-preserving storage layout 계획

- **날짜/lap:** 2026-09-18 / lap380 (`loop/.lap_counter` = 380; 런타임 배너의 lap=379는 진입 시점 값)
- **역할:** 중간계획/컨펌. 게임 구현 0, 게임 실행 0, 바이너리 편집 0, 커밋 0.
- **목표:** STATUS "다음 한 가지" — Astra 범위의 base-preserving 비균일 저장영역 레이아웃에 대해
  변경파일·독립검증·중단조건을 확정한 Opus 계획 산출.

## 가설

H-A: 여섯 저장영역(N=1200)의 반개구간과 간극이 기록된 그대로라면, 용량 확장은 단일 delta가 아니라
**구간별 조각 선형 사상**으로만 표현 가능하며, 그 계약은 게임 실행 없이 정의·검증할 수 있다.

## 변경파일

- 신규 `docs/work/active/G2_BASE_PRESERVING_STORAGE_OPUS_PLAN_20260918.md` (계획 산출물)
- 신규 `docs/history/laps/probes/20260918_lap380_middle_g2_tail_layout_facts_probe.py` (읽기 전용, **미실행**)
- 신규 `loop/ESCALATE_SOL`
- 갱신 `docs/STATUS.md`
- 제품 코드/바이너리/원본/공유 파일 변경 **0건**

## 원본·후보 SHA

- 원본 pin `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac` —
  기록 원문(`tools/g2_relocation_manifest_evidence.json`, `tools/check_binary_contract.py`,
  `patches/population/offline_storage_v1.py`)에서 **문자열 일치만** 확인. 이번 lap에 파일 해시
  재계산은 **하지 못했다**(실행 권한 없음).
- 후보 EXE 없음.

## 실행명령 / 결과

| 명령 | 결과 |
|---|---|
| `make check` | **실행 불가** — Bash 승인 거부(비대화형) |
| `checks/safety.sh check` | **실행 불가** — 동일 |
| `python3 docs/history/laps/probes/20260918_lap380_middle_g2_tail_layout_facts_probe.py` | **실행 불가** — 동일 |

읽기 전용 명령(`ls`/`grep`/`sed`/`cat`/`wc`)만 통과했다. 이는 코드 실패가 아니라 **세션 권한 환경**
문제다. 따라서 ④-2(이전 바퀴 실행 증거 독립 재검증)와 ④-4(Fast 게이트)는 이번 lap에서 **미수행**이다.

## 수치 — 손계산 수검 (PASS, 바이트 재유도 아님)

`tools/g2_relocation_manifest_evidence.json`의 여섯 영역 전부에서 `start + elem*1200 == end` 성립:

| 영역 | start | end | elem | 다음 간극 |
|---|---|---|---|---|
| unit_pool | `0x0066B790` | `0x00892410` | `0x758` | `0x6CB8` |
| unit_existence | `0x008990C8` | `0x00899A28` | 2 | `0` (age alias) |
| unit_age | `0x00899A28` | `0x0089A388` | 2 | `0xC80` |
| category_slot_list_a | `0x0089B008` | `0x0089C2C8` | 4 | `0x2` |
| category_slot_list_b | `0x0089C2CA` | `0x0089D58A` | 4 | `0xD7A1E` |
| active_slot_list | `0x00974FA8` | `0x00975908` | 2 | — |

`0x66B790 + 0x758*1200 = 0x892410` = unit_pool end = bulk save 시작 = live state base (3중 alias).

## 새 근거 — C1 (catA end/count ↔ catB base 2바이트 겹침)

manifest는 `0x0089C2C8`을 list-A exclusive end **이자 live dword count field**로 기술하는데
catB base는 `0x0089C2CA`(= +2)다. count가 dword면 catB 첫 원소의 하위 2바이트를 덮는다.
⇒ (1) count가 실은 WORD이고 라벨이 오기거나, (2) 두 영역이 실제로 겹친다. **판정 미확정.**
`0x0089D58A`의 list-B end/count alias도 같은 형태다. 어느 쪽이든 "확장 전에 바이트로 닫아야 하는
선행 질문"이며, 추정으로 진행하면 접근 위반 없이 **조용한 손상**이 난다.

## 새 근거 — H1 (미확정)

age end `0x0089A388` → catA base `0x0089B008` 간극 `0xC80` = 3,200 B = `8 × 200 × 2`로,
STATUS의 "고정 8×200 WORD matrix"와 크기가 정확히 일치한다. **크기 일치는 증거가 아니다.**
반대 근거: owner roster는 PlayerStruct `+0xd4a`의 4바이트 목록이고 owner 상한 시작값은 250이다.
work tier는 확인 전까지 이 간극을 **외래 불변 블록**으로만 취급한다.

## PASS / FAIL / SKIP

- PASS: 여섯 영역 반개구간 산술 자기정합성, 3중 alias `0x892410` 정합성 (손계산)
- PASS: 계획 산출물 작성 (Astra 범위 내, 변경파일/독립검증/중단조건 확정)
- FAIL: 없음 (제품 주장 없음)
- **SKIP(비자발):** `make check`, `checks/safety.sh check`, probe 실행, 원본 바이트 fresh 재유도,
  lap379 실행 증거 독립 재검증

## fixture

없음. 게임 fixture 미사용, Wine/Xvfb 미기동, residue 0 (프로세스 미생성).

## 판정

Astra 범위의 layout-only 카드는 **정의 가능하고 검증 계약도 세울 수 있다**. 다만 C1이 열려 있어
mapper 착수 전 선행 바이트 판정이 필요하다. lap379 Sol의 integration/broad patcher/runtime
**NO-GO는 유효**하며 이 카드는 그것을 뒤집지 않는다. G2는 미완료다.

## 다음 행동

1. (승격/실행 가능 세션) probe rc0 + `make check` + `checks/safety.sh check` 확보.
2. C1을 원본 바이트로 닫는다.
3. 그 다음에야 Sonnet5/high가 `patches/population/base_preserving_storage_layout_v1.py`와
   테스트를 작성한다. N=1200 항등이 최상위 회귀 앵커다.

실행 권한 부재로 `loop/ESCALATE_SOL`을 생성했다.
