# 2026-09-26 | lap 661 | 목표 G5 — strategy 부대지정 50 재배선 계약

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5-5`(세션 표기 Opus 5.5) / strategy(05:05 운영자 위임 "strategy가 짧게 정한다") / 기본. 게임 코드·패치·테스트·바이너리 수정 없음.
- 가설 / 사용자 관찰: lap660 후보 드래그 50이지만 Ctrl+1 호출·로드 후 호출 20. 질문 ① side-table 재배선 최소 사이트, ② 세이브 21~50 처리.
- 예상 PASS / FAIL 조건: 이번 회차 PASS = 원본 디스어셈블로 부대 구조·호출자·저장 경로를 확정하고 단일 설계·사이트·측정식을 결정. 실행 증거는 다음 work가 만든다.

## 판정 (`FEASIBLE`)

1. **부대 구조는 AI 분대 저장소를 겸한다.** `G = 0x9570F4 + p*0x3ABC`(PlayerStruct+0x984), 8인 모두. AI가 `0x445B80`(20 가득이면 거부)·직접 절대주소(`0x95710A`/`0x95742A`, 폭20 하드코딩)로 쓴다.
   ⇒ 10×20 구조를 전역 확장하거나 `0x0108C100`(1인분 10×50)로 옮기면 G4 AI 행동/세이브까지 바뀐다. **side-table 재배선안은 기각.**
2. **현 후보 v1 `6c8f73ba…`에는 메모리 오염 결함이 있다:** assign `0x445CD0`이 선택 50칸을 끝까지 돌며 `G+0x16+g*0x50+i*4`에 경계 없이 저장·count 증가 → group g+1,g+2 항목을 덮고 Ctrl+9는 `G+0x336..0x3AE`(count/center/type…)까지 덮는다. lap660 `group1_count=50`이 직접 증거다.
3. **채택안 = 유닛 부대필드 권위 방식.** 유닛 레코드 `+0x344`(부대번호, 스폰 시 -1, 배지 그리기 `0x409640`이 이미 사용)가 **세이브에 유닛 레코드 0x758B 통째로 저장**된다(`FUN_0040F4B0`).
   PlayerStruct G는 stock 그대로 첫 ≤20명(count ≤20), 21~50번째는 `unit+0x344 == g`로만 표현. 호출은 stock 20 루프 뒤 로컬 소유 유닛 풀 스캔으로 채운다.
   - 세이브 형식 **불변**, 로드 후에도 50 복원(유닛 필드가 저장되므로). stock EXE가 후보 세이브를 읽어도 ≤20 정상 그룹.
   - AI·사망 제거·center·type·세이브 코드 바이트 불변. side-table `0x0108C100`은 미사용(예약 유지).
4. 사이트·cave 정확한 바이트/동작은 `analysis/memory_maps/g5_control_group_rewire_lap661.md` 표 H1/H2/H3. cave는 `.text` 0 tail `0x4E4C00..`(1307B 확인), `.text` VirtualSize 확장.

## 다음 work 지시 (middle 없이 바로 구현·실행)

1. 새 모듈 `patches/selection/g5_selection_cap50_v2.py`: v1 `build_candidate` 결과 위에 H1/H2/H3 hook + cave를 적용(v1 SHA `6c8f73ba…` 재현성 보존). old bytes 3곳·cave 0 확인·VirtualSize ≤ raw·정확 원복(byte-identity) 포함.
2. 테스트 `patches/selection/test_g5_selection_cap50_v2.py`: hook old/new bytes, cave 디코드의 분기 대상(`0x445D57 0x445DD4 0x445E01 0x445FB7 0x445ED9 0x40F750 0x40F7D0 0x416F40 0x40F790`), 불변 구간 바이트 동일(`0x445A20..0x445CCB`, `0x445FF0..0x446177`, `0x43CB00..0x43D650`, `0x4B1F20..0x4B2150`), 원복.
3. 후보 빌드 → SHA를 probe `TARGET_SHA`에 반영 → lap660과 **동일** fixture/입력으로 `--ui-roundtrip` fresh 실행 + 원본 paired.
4. 측정식(후보): 드래그 50/50 · Ctrl+1 후 `count[1]=20`·로컬 유닛 `+0x344==1` 50기 · 해제 0 → 1 호출 **50 unique = 드래그 집합** · save→load → 1 호출 **50** · Ctrl+9(같은 50) 후 `G+0x34A..G+0x3AE` 및 다른 그룹 항목 바이트가 assign 전과 동일(오염 0), `count[9]=20`. 크래시 0.
   원본 paired: 호출 20, save/load 20. FAIL-A crash → EIP/ESP; FAIL-B 호출 <50 → 필드 50 여부로 H1/H2 vs H3 귀속; FAIL-C 오염 → H2 경계 재확인.
5. PASS 뒤 `make check`(≈700s, 폴링으로 완주) → 다음 회차 middle 독립 검수 → 사용자 G5 milestone 제출. 명령 패커 `FUN_004AE550`은 이동 50이 이미 되므로 범위 밖.

- 변경 파일 / source fingerprint / 커밋: 이 파일, `analysis/memory_maps/g5_control_group_rewire_lap661.md`, `docs/STATUS.md`, `docs/feedback/INBOX.md`, `docs/history/20260926_lap661_escalate_sol_archive.md`(기존 `loop/ESCALATE_SOL` 39줄·SHA256 `3fd7a25f…6c33` 전문 보존 후 해제). 제품·패치·테스트·바이너리 0, 커밋 0(LOOP_ALLOW_COMMITS=0).
- 원본 SHA / 후보 SHA / 환경 / fixture: 원본 `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`(읽기 전용, 불변); 후보 v1 `6c8f73ba5626a978abaa09bb56adc46ee5da39bdd16d05c71285ce10d8f20b25`(메모리 재빌드만, 파일 미작성). 게임 실행 0.
- 실행 명령 / 로그: `.venv/bin/python /tmp/lap661_dis.py`(capstone 구간 디스어셈블), `/tmp/lap661_xref.py`(rel32 call·imm xref), v1 인메모리 빌드로 hook 사이트 bytes·cave 0 확인. 산출은 stdout.
- 측정값 / 판정: 정적 귀속 PASS(lap660 count 50 = 무경계 저장으로 설명), 설계 `FEASIBLE`; G5 제품 판정 UNKNOWN(실행 0); 50 호출·save/load SKIP.
- 회귀 / 남은 위험: 문서화한 edge(첫 20 전멸 시 disband 후에도 필드 멤버 호출 가능, 더블탭 중심은 첫 ≤20 기준, 전향 유닛 add 실패 시 옛 필드), G2 통합 시 풀 상수 remap 필요, 멀티 동기화 미측정. 제품 코드 없는 회차 연속 1(lap661).
- 다음 한 가지: 위 1~4를 work가 즉시 구현·실행한다.
