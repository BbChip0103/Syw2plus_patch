# lap350 middle — lap349 S1 로드 진입 근거 봉투 판정

2026-09-12 / Codex 현재 세션 / 정확한 모델 ID는 주장하지 않음 / high / middle
(진단·계획·확인). 게임 코드·하네스·제품 테스트 hands-on 수정과 게임 실행은 0이다.
이 판정은 M1/G1 내부 연구 봉투만 다루며 Stage B·제품·마일스톤 승인이 아니다.

## 0. 판정

**BLOCKED.** 원본 PS35 슬롯 hit-test와 `slot-1 → 0x440FF0` 연결은 현행 원본에서
정적으로 닫혔다. 그러나 fixture 내용을 해석한 lap284-work/lap286-middle의 ACCEPT와,
같은 정사각·짝수 한계 때문에 그 파일 오프셋 환산이 불가능하다는 lap322 §14.1 REJECT가
서로 충돌한다. 또한 `0x440FF0`은 파일 열기 실패 시 조기 반환하지만 상위 handler는 그대로
PS3를 반환하므로 PS3 단독은 실제 로드 완료 증거가 아니다. 사용자 중단 규칙에 따라 이
세션에서 한쪽을 임의 채택하거나 하네스 구현/게임 실행을 발효하지 않는다.

## 1. 입력과 이전 바퀴 독립 검수

- `loop/.lap_counter`는 `350`; runtime 주석 `lap=349`보다 counter를 우선했고 쓰지 않았다.
- lap349 입력 probe `20260912_lap348_middle_lap345_candidate_r1_artifact_probe.py`
  (`fdca6f6c…c093`)를 수정 없이 정확히 1회 재실행했다. rc0, `failures=[]`, stdout SHA
  `46902e207a07e81ff806b5516899a31e6b162f43627b494238efa755fda3a52a`로 lap349 기록과 같다.
- 원본 EXE SHA `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`,
  `tools/runtime_env.py` SHA `965e3709…b547b`, R1 test SHA `891b60eb…b4265`를 재계산했다.
- 새 게임/Wine/Xvfb/클릭/PNG/후보 artifact는 0이다. 기존 R1은 PS35와 origin
  `(240,145,8)`까지만 확인하며 슬롯 선택·파일 open·복원 완료를 확인하지 않는다.

## 2. lap349 §2 여섯 제출 항목

| 제출 항목 | 판정 | 현행 근거와 남은 결측 |
|---|---|---|
| 미결 목록 | **ACCEPT** | origin 전역 관측으로 다이얼로그 구성과 A `(240,145)`만 해소. 슬롯 실제 입력, 선택 파일, open 성공, 복원 scene, 두 run 결정성은 분리해 UNKNOWN 유지. |
| 슬롯 근거 | **ACCEPT (정적 범위)** | 아래 §3에서 원본 SHA·주소·폭·old bytes로 7 rect hit-test, 선택 WORD, 1-based→0-based, `0x440FF0` 호출을 연결. Plan C 사용 0. 실제 클릭 허가는 아님. |
| fixture | **BLOCKED** | save000/006 SHA와 prepare 복사 출처는 일치하지만 lap284-work/lap286-middle과 lap322 §14.1의 파일 오프셋·내용 판정이 충돌. 이 세션은 save000/006 중 하나를 확정하지 않음. |
| 로드 완료 관측 | **BLOCKED** | PS3은 open 실패와 성공을 구별하지 못함(§4). 선택 fixture의 정적 원시 필드와 post-PS3 scene를 잇는 비순환 reader/sentinel이 아직 승인되지 않음. |
| 실무 변경 | **NOT ACTIVATED** | 구현 근거 충돌 중이므로 `tools/runtime_env.py`/tests 변경 범위를 발효하지 않음. 판정 후 조건부 범위는 §5. |
| 제품 경계 | **ACCEPT** | 연구 PS35→load 관측은 기존 PS5→PS3 제품 PASS와 파일 수준으로 분리하고 lap277 §3 (A)+(B), F2-R2 강등, WM_CLOSE, Stage B 금지를 유지. |

## 3. 새로 닫힌 슬롯 정적 연결

원본 객체는 `0x01086278`; rect 배열은 `this+0x408`, stride `0x10`, 개수는
`WORD[this+0xF9C]=7`, 선택값은 `WORD[this+0xF9E]`다.

- 구성 old bytes `0x4D61BE..0x4D61D8`:
  `8d9e0804000057b95000000033c08bfbf3ab66c7869c0f00000700`.
- `0x4D5F9D..0x4D5FF8`은 마우스 `DWORD@0x00C0CB5C`(y),
  `DWORD@0x00C0CB58`(x)를 7 rect와 strict interior로 비교하고 hit 시
  `index+1`을 `WORD[this+0xF9E]`에 쓴다. 마지막 store old bytes는
  `6689be9e0f0000`.
- 관측 origin `(240,145)`일 때 rect는
  `[260,119,540,143]`, `[260,153,540,177]`, `[260,187,540,211]`,
  `[260,221,540,245]`, `[260,255,540,279]`, `[260,289,540,313]`,
  `[260,323,540,347]`. 각 strict 내부 점만 후보가 될 수 있다.
- `0x4D6B5A..0x4D6BA3`은 handler 결과 `di`를 `esi=di-1`로 바꾸고 load mode
  `0x3ED`에서 `push esi; call 0x440FF0`, 뒤이어 `ax=3`을 반환한다. old bytes는
  `b9786208018d77ffe829feffff…c356e853a4f6ff83c40466b80300`.
- `0x440A80` path builder는 slot을 stack에 남기고 `WORD@0x0066966C`
  (`0x669590+0xDC`)를 읽은 뒤 원본 문자열 `%ssave\\save%d%02d.dat`에 대입한다.
  따라서 group=0을 별도 읽어 확인해야 selection 1/7을 save000/save006에 연결할 수 있다.

이는 rect/slot/file-index의 **정적 연결**이다. 실제 input delivery·group 값·open 성공은 아직 관측이 아니다.

## 4. PS3가 로드 완료 reader가 될 수 없는 이유

`0x440FF0`은 path를 만든 뒤 `fopen` 결과를 `esi`에 받고, `0x44101A: test esi,esi` 뒤
null이면 `0x44101E..0x441025`에서 즉시 반환한다(old bytes
`85f675085e81c404010000c3`). 호출자 `0x4D6B97`은 반환값을 검사하지 않고 stack을 정리한 뒤
`mov ax,3`을 수행한다. 그러므로 **없는 파일을 고른 경로도 PS3가 될 수 있다.**
실제 완료 판정은 최소한 (a) 클릭 전 group WORD와 선택 index로 정확한 경로를 고정하고,
(b) 그 fixture에서 정적으로 유도한 하나 이상의 복원 필드가 post-PS3 scene에서 일치하며,
(c) reader 오류/결측/불일치를 UNKNOWN으로 보존해야 한다. 현재 (b)의 근거가 §5 충돌로 막혔다.

## 5. 중단·승격과 조건부 후속 범위

다음 새 Sol/high middle 한 바퀴가 먼저 **한 가지 논리 검수**만 수행한다: lap286이 보고한
bulk/player/roster 파일 오프셋이 width/height 교환과 두 halving 공식의 모든 허용 조합에서도
현재 네 정사각·짝수 fixture에 대해 불변인지 계산하고, lap322 §14.1의 “환산 불가”와 양립하는지
ACCEPT/BLOCKED로 판정한다. 값 맞추기·새 fixture 생성·과거 probe repin은 금지한다.

그 판정이 fixture 원시 필드를 수용할 때만 work(Luna/Sonnet5/high)에 다음을 인계할 수 있다:
`tools/runtime_env.py`의 기존 R1 함수는 보존하고 별도 S1 load evidence 함수/CLI와 별도 artifact를
추가하며, group WORD→정확한 slot 내부점→PS3→fixture sentinel/scene 원시 필드를 수집한다.
회귀는 open-failure PS3를 PASS로 금지하고 파일/slot 불일치·reader 결측·timeout을 UNKNOWN으로
보존해야 한다. 실행·클릭·PNG 예산은 여전히 0이며 완성된 work 봉투 뒤 Astra가 별도 결정한다.

필수 Fast는 근거 충돌 중단 규칙 때문에 이번 lap에서 SKIP한다. 이전 입력 probe rc0을 새 봉투
승인이나 제품 PASS로 사용하지 않는다. 현재 변경과 명령 근거를 history/ESCALATE_SOL에 보존한다.
