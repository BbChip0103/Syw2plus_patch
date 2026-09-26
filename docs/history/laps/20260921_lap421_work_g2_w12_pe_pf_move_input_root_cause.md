# 2026-09-21 | lap 421 | 목표 G2

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-sonnet-5` / high / work(실무).
  카드 `docs/work/active/G2_POOL_FAULT_MOVE_FIELD_WRITER_LAP420.md`(W12, 발행 lap420 middle) 수행.

- 가설 / 사용자 관찰: W12 §2 H5(활성화 경로 자체 결함) vs H6(외부 wild write)를 P-E(정적 판별)
  + P-F(실행 probe)로 가른다. lap420이 확정한 것: 슬롯3565는 tick11,915에 9개 필드가 동시
  기동했고 `+0x692`는 정지(0)에서 활성화되며 첫 값부터 범위 밖(19,579)이었다(N32/N33/N34).

- 예상 PASS / FAIL 조건: 카드 §3 판정식 — H5 지지는 "활성화 첫 tick부터 범위 밖 + 같은 실행의
  저슬롯(<1200) 대조군은 정상 범위"; H6 지지는 "P-E가 누산기 외 기록자를 찾고 그 site가 11,915에
  실행됨". 실행 전 고정.

## P-E: `+0x692` 목적지 store 전수 (정적, 게임 미실행)

`scan421_pe.py`(lap418 `xref418.py`의 resync sweep 방식 재사용, capstone5 operand access로
read/write 분류)로 원본·후보 `.text` 306,811 insn을 재계산. 결과는 **원본·후보 완전 동일**
(패치가 이 영역을 건드리지 않음, 예상대로):

- disp `0x692` 참조 21건 중 write 5건, read 16건.
- write 5건은 **정확히 2개 site**로 나뉜다:
  1. `0x0040bc86~0x0040bcfe`(esi 기반) — lap414 N26이 이미 지목한 누산기. 4개 write 명령
     (`0x40bc97`/`0x40bca0`/`0x40bcab`/`0x40bcfe`)이 모두 이 20-byte 구간 안에 있다.
  2. `0x0040c1c2`(ebx 기반, **신규**) — `mov word ptr [ebx+0x692], 0`. 상수 0을 쓰는 리셋이며
     `move`(관측값 19579/-26278/-6599)를 만들 수 **없다**. `scan421_callers.py`로 확인한
     문맥: 같은 함수 안에서 직전에 `push 0; push 6; mov ecx,ebx; call 0x415b20`가 있어
     "새 이동 주문 발급 시 진행도 리셋" 형태로 읽힌다(호출부 0x415b20 자체는 무관한 상태
     디스패치 함수로 확인, 이 리셋과 누산기는 서로 호출관계가 아님).
- **판정: 기록자 2곳 발견.** 카드 §3 P-E 판정식은 "1곳뿐이면 H6 기각, 2곳 이상이면 어느 것이
  11,915에 실행되는지 좁히는 최소 수단을 붙인다"이므로 문자 그대로는 "2곳"에 해당하지만,
  두 번째 site는 상수 0만 쓰므로 관측된 어떤 이상값도 만들 수 없다 — **값을 만들 수 있는
  site는 사실상 1곳(누산기)뿐**. 이 구분을 P-F로 실측 확정했다(아래).

산출물: `temp/Syw2plus_patch/g2_capacity/20260921_lap421_move_field_writer/scan421_pe.py`,
`scan421_sites.json`, `scan421_callers.py`, `scan421_callers.json`.

## P-F: 축소비용 실행 probe (실행 증거)

`movement_state_probe_pf.py`(lap419 하네스 복사, boot/click/goal/op7 시퀀스 불변). 변경 3가지
(카드 §3 P-F 요구 반영): ① 매 샘플 전량 4,000슬롯 struct read 대신 존재배열(8,002B) 1회 +
추적셋만 전체 struct read로 비용 축소, ② 존재배열 diff로 slot<1200 활성화 자동 편입(저슬롯
대조군), ③ 추적 필드에 N32 co-field 8개 + 입력후보 `+0x2b0/+0x2b2/+0x2d8/+0x688/+0x690/+0x1d8`
추가. 밴드 전수 스캔은 1초 저빈도(stride4)로 분리.

- **fixture**: op7 resource-only, 8 owner, `4331d9cd…`(고정), seed42 chain-inject, 신규
  prefix/display(`:3844`). fault **재현**: tick11,928/slot3565/move19579(3번째 독립 재현,
  lap413·416·419에 이어).
- **비용 개선 확인(N34 해소)**: dense window(11,838~11,928, 91 tick) **무표본 tick 0개**
  (lap419/420은 21개 무표본), tick당 2표본 이상 42/91(46%). 목표 달성.
- **저슬롯 대조군: 미확보.** `tracked_low_slots=[]` — 이 fixture는 실행 내내 slot<1200이
  단 하나도 alive로 전이하지 않았다(존재배열 diff 0건). N28(할당기가 위→아래로 채우고 이
  fixture의 생존 개체가 3533~4000에만 분포)를 **실측으로 재확인**한 것이며, 카드 §3.2가
  요구한 "같은 실행의 저슬롯 대조군"은 이 fixture로는 원리적으로 얻을 수 없다.
- **그럼에도 결정적 증거를 확보했다 — 폐쇄형 산술 재현:**
  - 활성화 직전(tick 10,205~11,915, 알림구간 포함): `move=0` 고정, **`+0x688`가 이미
    `19679`로 고정**(alive 이후 관측 전 구간 불변). `19679 − 100 = 19579` — 최초 이상값과
    **정확히 일치**.
  - tick11,916→11,917: `move` `19579→−26278`. `19579 + 19679 = 39258`;
    signed16(39258) = 39258 − 65536 = **−26278**(정확히 일치, wraparound).
  - tick11,917→11,918: `−26278 + 19679 = −6599`(정확히 일치).
  - tick11,919(=0)→11,920(=19579): 4-tick 주기 `{0,19579,−26278,−6599}` 반복 — lap420
    N34가 "미결"로 남긴 되풀이 패턴이 **`+0x688`(상수 19679)를 매 tick 누산기가 그대로
    더하는 것"만으로 완전히 설명됨**(디스어셈블리 `0x40bc86` 블록의 `add eax,edi` +
    `>=50`일 때 `-100` 세그먼트 전환 로직과 일치; clamp 분기(`bp`)의 정확한 임계값 비트는
    이번 회차에서 특정하지 않음 — 세 번의 non-trivial 전이 전부가 단순 mod-65536 덧셈으로
    맞아떨어진 것으로 충분하다).
  - **⇒ 외부 writer 가설(H6)은 필요조차 없다.** 알려진 누산기(위 P-E의 site 1)가 이미 나쁜
    입력(`+0x688=19679`)을 정상적으로 소비한 결과가 관측값 전부를 설명한다.
  - **⇒ H5 확정(활성화 경로 자체 결함), 단 정확한 형태는 카드가 짐작한 "경로 테이블
    범위이탈"이 아니라 "입력 필드 `+0x688` 자체가 활성화 이전에 이미 오염"이다.**
- **신규 사실(다음 카드의 진짜 표적):** `+0x688`는 항상 19679가 아니었다. slot3565가
  **tick10,231**에 처음 alive됐을 때 `+0x688=10`(정상 소값)이었고, **tick10,432 샘플에서
  19679로 바뀌어 있었다**(그 사이는 이 구간이 dense 아니라 1초 간격이라 정확한 전이 tick은
  201-tick 창으로만 좁혔다). 이 구간 내내 `move=0`(경로 미실행)이었으므로 **이 write는
  P-E가 찾은 두 `+0x692` site 중 어느 쪽도 아니다** — `+0x688`에 쓰는 site는 이번 회차에서
  **아직 정적으로 찾지 않았다**.

산출물: `temp/Syw2plus_patch/g2_capacity/20260921_lap421_move_field_writer/movement_state_probe_pf.py`,
`samples.jsonl`(929줄), `orchestrator.log`, `run_summary.json`, `resource_receipts.json`.

- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted): 제품 코드 변경 **0**(정적 스캔
  스크립트·probe 스크립트는 모두 `temp/Syw2plus_patch/g2_capacity/` 산출물 디렉터리, 저장소
  추적 파일 아님). `git status --short` 확인: 저장소 신규/추적 변경 없음. 커밋 없음
  (`LOOP_ALLOW_COMMITS` 미설정, 기본 0).

- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 원본
  `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`(실행 전후 재해시 일치),
  후보(marked compat) `4331d9cd646c03a0102394727894beaf893e5b9aa3505c4ddb41eb26a4ef9bbe`. 격리
  `tools.runtime_env.prepare()` 신규 사본 + 신규 wine prefix + 신규 display `:3844`. 8 owner,
  op7 resource-only(장부/유닛 write 0), seed42 chain-inject goal, N=4001.

- 실행 명령 / 로그 / 캡처 경로 및 해시: `python3 movement_state_probe_pf.py`(위 경로).
  targeted `pytest patches/population/test_g2_full_capacity_persistence_compat_v1.py
  patches/population/test_runtime_bridge_contract.py -q` → **6 passed**(기준선 유지).
  `checks/safety.sh check` → `SAFETY_PASS`. 원본 실행 전후 SHA256 동일 확인(위).

- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN): **P-E PASS(2 site 확인, 값 생성 가능한 site는
  1곳으로 좁힘). P-F PASS(fault 3차 재현, N34 해소, `+0x688` 상수 가산의 폐쇄형 산술로 전체
  이상값 시퀀스 재현) — H5 확정/H6 기각.** 카드 §3.2 저슬롯 대조군은 **UNKNOWN/불가**(이
  fixture 구조상 slot<1200 활성화가 아예 발생하지 않음, N28 실측 재확인). 이 결손은 산술
  재현이라는 더 강한 증거로 상쇄되므로 최종 판정에는 영향 없음 — 단, 다음 검수(middle)가
  이 대체를 승인할지는 별도 확인 필요.

- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: 이번 회차는 자기 결과이며 독립(middle)
  검수 없음. 남은 위험: `+0x688` 쓰기 site 미확정이므로 "high slot에서만 발생"인지 "특정
  조건(예: 특정 유닛타입/명령 시퀀스)에서 아무 슬롯에나 발생 가능한데 우연히 이번엔 hi
  slot이었는지"는 미결. 게임 실행/원본 손상/저장 이상 관측 **0**. 이번 회차 stray 프로세스는
  본인 실행분(`:3844`, wineserver, pid 3085148 계열) 종료 후 잔류 0; lap420이 기록한
  `winedevice.exe`(pid 2089059/2089068) 등 타 회차 잔류는 그대로 관찰만 하고 정리하지 않음.

- 다음 한 가지: **W13** — `+0x688` 목적지 store 전수(같은 P-E 방식, `scan421_pe.py`의 `DISP`를
  `0x688`로 바꿔 재사용 가능)로 그 write site를 특정하고, tick 10,231~10,432 구간을 dense
  샘플링(이번 회차 P-F 하네스의 `DENSE_LO/HI`를 그 구간으로 재설정)해 정확한 전이 tick과
  당시 게임 이벤트(명령 발급/전투/생산 등)를 대조한다. 그 site가 slot id(고 슬롯)에 의존하는
  계산을 쓰는지가 P2(원본 생산 경로) 회귀의 진짜 조건이다.
