# G1 W70 D-1 PS3 writer census — work handoff (lap908 middle)

- 기존 권한: lap858 P4 카드 D-1·lap863 P4b 카드§6. 새 strategy/구조 변경/제품 완료 승인 없음.
- prerequisite: lap907 current-source B′2·C3 화면/성능 gate를 lap908이 독립 부분 수용. fresh 전체Fast 결과는 STATUS 확인. G1 전체 HOLD 유지.
- 다음 한 가지(work/Luna high): **PS3 한 장면의 실제 last-writer 비율 측정**. census의 기존5종 terrain blitter 표 추가 여부와 PS3-only present opt-in을 좁게 확인하고, 빠진 부분만 최소 구현한다. 이미 구현됐다면 다시 쓰지 말고 실행한다.
- opt-in은 초기화 latch; present 맵은 program_state==3만. CENSUS_PRESENT_LIMIT64·writer별 event cap32 불변. 0x466280(src=0xBA3D30 지형캐시)를 일반 block_copy와 구분해 "지형 캐시 전사"로 센다. 5 terrain blitter와 cache transfer의 관계를 정적 근거/실제 호출로 연결하되 직접화면 last-writer 표와 합쳐 중복 면적을 만들지 않는다.
- 입력: 보호 원본 b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac, 비합성 save006 616b79978917c8fd6f996a5cafca50e1e411b24a4fccca05efa3cb9289a0d064. 새 전체사본/prefix/빈display, current-source private DLL. 원본/개인세션 접촉0·기존raw/golden/기준 변경0.
- 출력/측정식: 각 PS3 present의 실제 픽셀맵과 writer별 last-writer 픽셀 수/전체 화면480000 및 월드384000 분모를 따로 기록, unknown/unattributed와 writer 누락·drop/overflow 포함. PS9 표를 대체 증거로 쓰지 않는다. 캐시전사·tinted RLE·HUD/DD·GDI/원천그림없는 fill/border/set_pixel 경로의 실제 순위를 보고한다. census 수치는 HD coverage 또는 제품 PASS가 아니다.
- 기존 V1/V2/V2s/V2q·Scale2x·source/scene/cleanup을 유지하고 새 source를 바꾸면 회귀/Fast 수행. fixture/원본·DLL·build/raw/PNG SHA·실제model/effort·PS3 범위를 남긴다. PNG/분석이미지는 공유 temp의 timestamp 폴더, 실행 뒤 자기 game 사본 삭제·나머지 근거 보존.
- 실패 시 구현/하네스/입력 원인을 추적→최소수리→재실행(PROMPT③); 불명확/충돌하는 실제 근거는 raw 보존·ESCALATE_SOL. 게임실행/긴 검증은 완주까지 대기. 다음 새 middle이 수치·맵·V3를 재검수하고 P5 순서를 정한다.
- minimap/production/스크롤 후 selection UNKNOWN은 별도 잔여 입력작업으로 보존; D-1은 입력효과 완료를 주장하지 않는다. D-2 scroll-performance 및 최종 입력은 사용자 제출 전 별도 필수. HUD/P5 구현·두 번째장면·새 의존성·기준완화·G2/G5/G3/G4 재개·commit/deploy는 이 handoff 범위 밖.
