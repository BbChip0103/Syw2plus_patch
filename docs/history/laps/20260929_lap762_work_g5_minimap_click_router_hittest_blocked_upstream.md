# 2026-09-29 | lap 762 | 목표 G5 (사용자 항목(2), 미니맵 "마지막 1 lap" — 클릭 입력 핸들러)

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-sonnet-5`, high effort; 지정 역할
  work(실무) — 승인된 범위의 실측/코드/실행만 수행, milestone 판정이나 G5 종료 선언은 하지 않음.
- 가설 / 사용자 관찰: 2026-09-29 12:37 운영자 지시("미니맵 마지막 1 lap") — 미니맵 화면 영역 클릭
  시 호출되는 함수(마우스 좌표→미니맵 영역 판정→월드 좌표 변환→이동/카메라)를 브레이크포인트로
  찾고, 원본에서 입력이 도달하는지 확인하라. 도달하면 명령 발행이 선택 전원(원본20/v10 50)에
  가는지 paired, 도달하지 않으면(격리 환경에서 미니맵 입력 비활성) 근거를 남기고 UNKNOWN 확정.
- 예상 PASS / FAIL 조건: 후보 히트테스트 함수가 라이브 클릭 중 1회 이상 호출되고 그 명령이 선택
  유닛에 도달하면 PASS(멀티/렌더와 무관하게 입력 경로 자체는 살아있음 증명); 함수가 전혀 호출되지
  않으면 UNKNOWN 확정(다만 어느 지점에서 막히는지까지 코드 위치로 좁히는 것을 이 lap의 최소 성공
  기준으로 삼음 — 단순 재현이 아니라 새 정보).
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted): 신규
  `tools/g5_minimap_hittest_entry_trace.py`(SHA256
  `6a57e920027f0fcd2accaf117145b49b43479eea7b06216fb1ab3d06766c04fc`, gdb 배치 스크립트, 5개
  non-invasive breakpoint), `tools/g5_minimap_click_hittest_probe.py`(SHA256
  `c2f8577d1a143ef1dffbcc5d035063df076b3a3b72417c702cef60096543b1c0`, 구동 하네스),
  `analysis/memory_maps/g5_minimap_click_router_lap762.md`(정적+실측 주소 근거) — 전부 조사용
  read-only 도구/문서, 제품 코드(EXE 패치) 0 변경. uncommitted(`LOOP_ALLOW_COMMITS=0`).
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 원본
  `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`(2회 실행 전후
  `source_unchanged=true`). 후보 없음(원본만 — 이 조사는 G5 선택 상한 relocate와 무관한 순정
  UI/입력 경로). 격리 Wine prefix/Xvfb 1600x1200, 솔로 로비 새 게임 각 1회, 별도 fixture 스폰 없음.
- 실행 명령 / 로그 / 캡처 경로 및 해시: 정적 확인은 `objdump -d -M intel --start-address=0x400000
  --stop-address=0x800000 "[ESL]Syw2plus/[HQ]Syw2plus 2002.exe"`(전수, `/tmp/full_disasm_lap762.txt`,
  311563줄) + xref grep. 실행 1(초기 3-breakpoint 버전):
  `PYTHONPATH=. .venv/bin/python -m tools.g5_minimap_click_hittest_probe --runtime-root
  local/runtime/g5-lap762-minimap-hittest --artifact-root
  /home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/20260929_lap762_minimap_hittest`
  (COMPLETE, `probe-result.json` SHA256 `311a8a942394f6b808272bd99c6e91eb40cce9228a2da8776e494a570134ccfa`).
  실행 2(엔큐/디큐 breakpoint 2개 추가, 같은 하네스 재실행): `--runtime-root
  local/runtime/g5-lap762-minimap-hittest-r2 --artifact-root
  .../20260929_lap762_minimap_hittest_r2` (COMPLETE, `probe-result.json` SHA256
  `9f12cc1217ec0007e97f23a088115bbaf714ce9223451a440283b7c982ac56f1`). 두 실행 모두 게임 사본(각
  ~1.4GB→cleanup 후 581MB)은 실행 직후 `game/` 서브폴더만 삭제(output/manifest/prefix/log는 보존).
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN):
  - **정적: 클릭 라우팅 체인 신규 특정.** WM_LBUTTONDOWN/UP·WM_RBUTTONDOWN/UP 핸들러(WndProc 내부,
    switch 케이스 확인) → `FUN_004216B0`(마우스 이벤트 링버퍼 enqueue) → 매 틱 클릭 라우터
    (`0x41e269`~`0x41e60c`, `FUN_004217B0`로 dequeue, 호출부 `0x0041E299`) → 여러 필터 분기 통과 시
    → **`FUN_004516A0`(this=미니맵 위젯 `0x00639350`, 히트테스트+좌표변환)** → 실패 시에만
    `FUN_00417DB0`(메인 뷰포트 히트테스트) 폴백. 상세는 memory map 문서 참고.
  - **정적+실측: `FUN_004516A0`의 판정 범위는 화면 x∈[0,180], y∈(509,599]** — lap710이 이미
    클릭-테스트한 "다이아몬드" 영역(x∈[0,176], y∈[511,598])과 거의 완전히 겹친다.
  - **신규 반증(중요): 위젯 생성자 `FUN_00451130`는 LUT을 0xFF(sentinel)로 먼저 전부 채우지만,
    같은 함수 안의 후속 루프가 실제 맵 타일 데이터로 그중 일부를 굽는다 — 그리고 이번 lap의 실측
    (원본 실행 중 LUT-A 32400바이트 직접 읽기)으로 정확히 16200/32400(50%)이 0xFF가 아님을
    확인했다.** 즉 "미니맵 렌더/좌표 서브시스템이 완전히 죽어있다"는 이전 세션들의 반복 negative
    결론(lap677/710/758/760)은 적어도 이 좌표-LUT 지점에서는 틀렸다 — 실제 지형 데이터가 살아서
    구워져 있다.
  - **실측(gdb 5-breakpoint 진입 카운트, 실행 2, lap710 다이아몬드 5지점+`MINIMAP_CLICK`+
    `MINIMAP_CENTER`+LUT에서 찾은 실제 비-FF 픽셀 좌표(89,510)까지 총 8지점 우클릭):**
    `FUN_004216B0`(enqueue) **24회**, 라우터 dequeue 호출 `0x0041E299` **19086회**(매 틱), 그러나
    **`FUN_004516A0`(미니맵 히트테스트) 0회, 성공/실패 리턴 둘 다 0회.**
  - **결론: 입력은 저수준 WM 핸들러(enqueue 확인)와 매 틱 라우터 폴링까지는 확실히 도달하지만,
    미니맵 위젯 히트테스트 자체는 이 세션에서 한 번도 호출되지 않는다.** 병목은 "렌더/좌표계산
    죽음"이 아니라 **라우터 내부의 enqueue↔dequeue 사이 또는 dequeue 성공 후 히트테스트 분기
    직전의 필터 체인(버튼타입 검사 `0x41e332`, 좌표 sentinel 검사 `0x41e365`, 게이트 호출
    `0x41e43d call 0x41c450`)** 중 하나로 코드 위치가 좁혀졌다 — 어느 분기가 실제 원인인지는
    이 lap 예산 밖(추가 브레이크포인트 3개 필요).
  - **12:37 지시의 최종 판정: `UNKNOWN` 확정** (입력이 후보 히트테스트 함수에 도달하지 않음 —
    지시의 "도달하지 않으면 근거를 남기고 UNKNOWN 확정" 조항 충족). 다만 이 UNKNOWN은 이전
    세션들의 "렌더 진입점 자체를 못 찾음"보다 훨씬 구체적이다: 정확한 함수 주소·바운딩박스·LUT
    베이킹 상태·클릭 라우터의 정확한 필터 체인 위치까지 실측으로 확정했다.
  - 크래시 0, `alive_at_end=true` 2/2, `source_unchanged=true` 2/2, `cleanup.ok=true` 2/2.
    `ruff check`/`python -m compileall` 신규 파일 2개 PASS, `checks/safety.sh check` →
    `SAFETY_PASS`, `checks/context_limits.py` → `CONTEXT_PASS`. 제품 코드/EXE 0 변경이므로
    lap758~760과 동일 판단으로 전체 `make check`(pytest 스위트)는 이번 lap에서 생략(신규 진단
    도구는 기존 pytest 대상 경로에 대응 테스트가 없는 read-only 조사 스크립트 계열, 선행
    lap759/760도 동일).
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: 회귀 없음(제품 코드 0 변경, 순정 EXE만 실행,
  `source_unchanged=true` 2/2). 남은 위험: (1) 정확히 어느 필터 분기가 클릭을 떨어뜨리는지는
  미확정(다음 후보 3곳을 memory map 문서에 명시). (2) LUT-A가 절반 베이킹돼 있다는 사실이 LUT-B/
  LUT-C(다른 두 sentinel 채움 블록, `0x1bd7a`/`0x4061`)에도 그대로 적용되는지는 이번 lap에서
  확인하지 않음(비차단 갭). (3) 이 발견은 "미니맵 렌더가 죽어있다"던 이전 세션들의 결론 일부를
  반증하므로, 사용자 항목(2) 미니맵 판정에 영향을 줄 수 있어 middle/운영자 확인이 필요하다 — 이
  work tier는 milestone 판정을 내리지 않는다. 독립 검수 요청 없음(work tier, 정보 제공용).
- 다음 한 가지: 다음 work가 (a) `0x41e332`/`0x41e365`(`0x41e3a5`가 참조)/`0x41e43d`의
  `call 0x41c450` 반환값에 개별 브레이크포인트+레지스터 캡처를 걸어 세 갈래 중 실제로 클릭을
  걸러내는 지점을 특정하거나, (b) 3-lap 예산(12:37 지시는 "미니맵 마지막 1 lap"이었으므로) 소진을
  이유로 이 결과를 middle이 (1)+(2) 전체 v10 재검수에 반영(미니맵은 "라우터 필터 체인에서 막힘,
  렌더/LUT은 절반 살아있음"으로 UNKNOWN 근거를 갱신)하는 쪽으로 진행할지 middle/운영자가 정한다.
