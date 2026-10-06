# 2026-10-02 | lap 858 | G1 W70 — P3 2단 통합 수용, P4 지형 blitter 카드 발행

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-fable-5-1`, 러너 지정 strategy(큰 방향/master-plan) 역할,
  effort는 세션에 비노출. 자동 폴백 아님. `loop/.lap_counter`는 858을 읽기만 했다(러너 evidence 블록은 lap=857 표기,
  PROMPT 규칙대로 파일 값 사용). 게임 코드/하네스/validator/바이너리 수정0, 게임 실행0, subagent0, 커밋0.
- 가설 / 사용자 관찰: (1) lap855와 lap857 일반 middle 검수의 합이 P3c 카드 §3의 2단 조건을 채우며, 두 회차의 재승격은
  P단계 전환을 마일스톤 경계로 읽은 절차 해석 때문이다. (2) 지형 타일은 기존 hook과 같은 렌더러 객체의 프리미티브가
  직접 그리므로 W70 P4를 별도 구조 판정 회차 없이 hook 확장 구현으로 시작할 수 있다.
- 예상 PASS / FAIL 조건(이 판정의): (1) 기록의 SHA·수치가 raw 재계산과 일치하고 §3 항목마다 독립 확인 회차가 있으면 통합
  수용, 하나라도 비거나 어긋나면 HOLD 유지. (2) 원본 disassembly에서 지형 callee가 `renderer+0x1514` 버퍼·`+0x10` stride를
  쓰는 thiscall 프리미티브면 `FEASIBLE`, 다른 버퍼/복사 구조면 구조 판정 회차 유지.
- 변경 파일 / source fingerprint / 커밋: 신규 `docs/work/active/G1_STRATEGY_W70_P4_TERRAIN_BLITTER_HD_LAP858.md`,
  신규 `analysis/memory_maps/g1_w70_p4_terrain_blitter_family_lap858.md`, 이 기록, 신규 보존본
  `docs/history/20261002_lap858_prior_lap857_escalate_sol_archive.md`(lap857 `loop/ESCALATE_SOL` 16줄 그대로, SHA256
  `40453f03c82b9d4a71196b3532fcd2c1feddbd8febedb51c5509db69cb1f5c1f`)와 `docs/history/20261002_status_lap858_precompaction.md`
  (압축 전 STATUS 126줄 그대로, SHA256 `08a5644d3dd713d5a07a054369550ea7c111feb5e1073825b2463563f12f8886`), P3c 카드 머리에
  종결 포인터 2줄, `docs/STATUS.md`, `docs/feedback/INBOX.md`, `docs/feedback/APPROVALS.md`. `loop/ESCALATE_SOL`은 보존본 SHA
  일치 확인 뒤 제거했다(판정으로 해소, 다음 회차를 work로 보내기 위함 — lap853 선례). uncommitted(`LOOP_ALLOW_COMMITS=0`).
  G1 source 불변(열람만): `g1_mirror2x.c` `e3aa30a6…8f967233`, `g1_hd_asset.c` `72453123…c563bfef`, `g1_census.c`
  `0d8c9143…a8291f1f`, `g1_perf_sections.c` `7d7ee27e…4a161f5e`, `direct_draw_trace.c` `4e946685…19a38ddc`,
  `tools/g1_saved_scene_probe.py` `742260b1…bd0e9927`, `tools/g1_hd_scale2x_probe.py` `67b88c9a…0e3149af`,
  `tests/test_g1_hd_scale2x_probe.py` `b83b0478…f452de81`.
- 원본 SHA / 후보 SHA / 환경 / fixture: 보호 원본 EXE `[ESL]Syw2plus/[HQ]Syw2plus 2002.exe` 직접 재해시
  `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`. save006 `616b7997…89a0d064`는 pair-result에서 읽음
  (이번 lap 재해시 없음). 후보 DLL SHA는 lap854/855 기록 참조. 새 runtime 없음. 상세 558 unit records는 활성 8인 부하 증명이 아니다.
- 실행 명령 / 로그: 읽기·재계산만. `sha256sum`(validator/test/ESCALATE_SOL/lap857 기록/review.json/pair 4개/C 5파일/probe/원본 EXE),
  `PYTHONPATH=. .venv/bin/python -m pytest -q tests/test_g1_hd_scale2x_probe.py`, 같은 인터프리터로
  `tools/g1_hd_scale2x_probe.py --trace <파일>` 6회(반례 2 + raw 4), python json 독립 집계(pair 4개·raw 4개),
  `i686-w64-mingw32-objdump -d -Mintel`(보호 원본, 출력은 저장소 밖 임시 파일에 두고 종료 전 삭제), gate1 baseline/candidate
  `loaded.png` 열람. 검증 명령은 아래.
- 측정값 / 판정:
  - SHA: validator/test/ESCALATE_SOL/lap857 기록(`efc7d4f0…7c61b660`)/review.json(`5085b322…fca6509f`)/pair 4개가 기록과 일치.
  - validator: 반례 `inside=1`·`17385`(deficit 17384) 둘 다 `BLOCKED`, latch/gate1/gate2/gate3 raw `PASS`
    (present 1013/1350/1324/1362). targeted pytest 4 passed.
  - 독립 재계산: 5049 present에서 `deficit≥0`·`4×inside≥deficit`·`inside≤deficit`·outside diff·palette·full-frame·clip replay·
    viewport mutation/restore·lookup miss·invalid 위반 0. tick ratio `0.9999997655 / 0.9999920427 / 0.9999969883 /
    1.0000019160`(400/400 tick, 20.000초 창), p95 baseline 1ms·candidate 6ms(+5), present 400·drop 0. selection/empty/
    drag_exact true, scene equal·source unchanged·cleanup true. minimap/production은 `UNKNOWN(original parity)` 그대로.
  - coverage(gate1~3 PS3 present 2678개): 유효 HD(`covered−stale`) min 5.39% / p50 6.23% / p95 7.20% / max 7.26%.
  - 정적: `0x435400`이 `0x465190`(viewport 완전 포함 검사)과 shade 테이블 유무로 `0x468C30`(ret 0x10)·`0x468CC0`(0x18)·
    `0x468F00`(0x14)·`0x4690A0`(0x18)을 고르고, `0x468E10`(0x14)은 `0x4351BD`에서 호출된다. 다섯 모두 `ecx=0xE5BF18`,
    `+0x1514` 버퍼·`+0x10` stride. `0x468C30`/`0x468CC0`/`0x468E10`은 본문 전체에서 viewport·목적지 읽기 없음,
    클립 2종은 주요 참조만 확인. 상세는 memory map.
  - **판정: P3 2단 통합 수용 `PASS(partial)` / P단계 전환은 마일스톤 경계 아님(middle이 직접 판정) / P4 `FEASIBLE`(정적,
    실행 미검증) — 구조 판정 회차 없이 다음 work가 hook 확장 구현 / G1 W70 계속 / 기준 §3.5·validator 불변 / G1 HOLD.**
- 회귀 / 남은 위험 / 독립 검수·사용자 승인: 이 판정은 기존 검수의 합과 raw 산술·정적 판독이며 새 실행 증거가 아니다. QPC
  compose 수치(6.06ns/픽셀)는 lap855 값을 인용했고 다시 계산하지 않았다. P4 귀속은 coverage p50 <30%면 반증된다(카드 §5-1).
  coverage 55% 기준은 캡처 기반 추정이다. 지형은 픽셀 수가 약 10배라 성능 gate가 최대 위험이다. 스크롤 중 성능·두 번째
  장면은 측정된 적이 없다. 2단 middle의 P4 검수·3단 사용자 승인 없음. G1 마일스톤 판정 아님.
- 다음 한 가지: work가 P4 카드 §4(A hook 확장 → B 배관 pair → C fresh 3 pair, 수리 ≤3회)를 수행한다.

## 검증 (문서만 변경)

- 기록 후 G1 source SHA 불변 확인, `make lint`/`make typecheck`, `checks/context_limits.py`, `checks/safety.sh check`,
  scoped `git diff --check`, 최종 `make check` 1회 — 결과 수치는 STATUS에만 보강한다(PROMPT ⑥ fingerprint 규칙).
