# 2026-09-23 | lap 523 | 목표 G2

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5-5` / high / **middle**(중간 계획·컨펌). 게임 코드 hands-on 수정 없음.
- 가설 / 사용자 관찰: 사용자 Q8=(ㄱ)(2026-09-23 18:43). lap522 strategy가 교전을 원본 `FUN_00415480` 스크립트 입력으로 만들기로 했다.
  이번 회차는 그 S0 카드(W35) 1장을 발행한다. strategy J5가 허가한 **유일한 문서 회차**다.
- 예상 PASS / FAIL 조건: 카드에 호출 규약이 원본 바이트에서 유도돼 있고, 적대 판정 항목·60분 상자·`FEASIBLE`/`NOT_FEASIBLE`/`BLOCKED` 식이 실행 전에 고정돼 있으면 PASS.
- 변경 파일(전부 문서, uncommitted, HEAD unborn):
  - 신규 `docs/work/active/G2_S0_ORIGINAL_ORDER_ENGAGEMENT_FEASIBILITY_LAP523.md`(W35 카드)
  - 신규 `analysis/memory_maps/g2_original_order_admission_contract_lap523.md`(주소 근거)
  - 신규 이 파일. 갱신 `docs/STATUS.md`, `docs/feedback/INBOX.md`(Q8 항목 추기 1줄), `loop/ESCALATE_SOL` §81 추가.
  - 제품 source·바이너리·브리지·테스트 변경 0.
- 원본 SHA `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`(확인). 후보 `a10024de5e1c1cbedcddde0c3b52f5b3a9cf0721ee066542669f4883a1bb2d68`
  (현재 source `build_candidate(orig, 4001)` 메모리 안 재빌드로 일치 확인, 파일 기록 없음). 환경·fixture: 실행 없음.
- 실행 명령:
  - `objdump -Mintel -D -b pei-i386 --start-address=… syw2plus_original.exe`: `0x415480..0x415640`, `0x415880..0x415940`, `0x416FD0..`, `0x4177A0..0x417890`, `0x417890..`
  - 파이썬 한 번: 후보를 메모리에서 빌드하고 13개 명령 즉치를 원본과 비교했다.
- 측정값 / 판정:
  - **호출 규약:** thiscall, `ECX`=소스 Unit, 스택 DWORD 3개(`ret 0x0C`) = (x, y, target_id). 반환 1=수락, 0=거부. 기존 G4 typedef와 일치.
  - **N177:** 적대 판정은 `0x417890 → 0x4177A0`의 `PlayerStruct+0x05` byte 비교다. 같으면 명령을 거부한다.
    N87 무교전의 가설 ②(비적대)는 이 byte 8개를 읽으면 명령 수락 기준으로는 판별된다(자동 교전 경로 공유 여부는 미확인).
  - **N178:** 목표 id는 하위 16비트를 슬롯으로 쓴다. N=4001 후보의 slot≥1200에서도 성립하는지 미실측이다. 카드에 fail-closed 검사를 넣었다.
  - **N179:** G4 op(`control_executor.c`)는 stock 풀 하드코딩이라 재배치 후보에서 쓸 수 없다. op8은 `runtime_bridge.c`에 둔다.
  - **N180(정정):** strategy 문서 §2의 "G4 호출은 worker thread였고 동시성 안전 미입증"은 일부만 맞다.
    같은 기록 하단에 `chb_call_handler` main-thread 재현(`MAINTHREAD_ORIGINAL_ORDER_MOVEMENT_PASS`)이 있다. 다만 stock 풀·owner0 한정이라 G2 재배치 후보 증거는 아니다.
  - 재배치 확인: 수락 경로 풀 참조 10건 전부 `0x0108C000` 풀·`0x017B8658` 존재배열로 fixup됨. PlayerStruct 참조 3건 불변.
  - 판정: **카드 발행 PASS**(계획 산출물). 제품 증거 아님.
- 검증: `checks/safety.sh check`·`checks/context_limits.py`만 실행(이번 회차 source 변경 0이므로 전체 `make check` 생략, 2026-09-20 21:58 지시·N22).
  결과는 STATUS 검증 상태 절에 적는다.
- 회귀 / 남은 위험:
  - 하위 경로 `0x4AEE10…0x40C640`과 이동·공격 루틴의 N=4001 적합성은 미대조다. lap414 `0x414133` 계열 fault 재발 가능성은 S0 실행이 드러낸다.
  - `0x415640`(P4)·`0x415940` 내부는 미해독이다.
  - streak: 무증가 3회째(lap521·522·523)지만 strategy §80 J5가 이 한 회차를 미리 허가했다. 다음은 반드시 실제 실행이다.
  - 독립 검수: 다음 work 실행 결과를 그다음 middle이 원시로 검수한다. 사용자 승인 없음.
- 다음 한 가지: **work(Sonnet5): W35 실행** — op8 구현 → 후보 재빌드 → 게임 1회 foreground → F1~F4 → `make check` 전체.
