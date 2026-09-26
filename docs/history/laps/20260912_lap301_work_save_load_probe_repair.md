# 2026-09-12 | lap 301 | G1/S1 save-load 정적 layout probe T1~T4 수리

- 실제 provider/model/effort / 지정 역할: Codex work tier / hands-on 구현 작업자 / high.
- 목표: lap300 middle의 §11 handoff에 따라 lap299 probe의 앵커 구멍·fixture pin·단일 화면 가정과
  provenance를 수리한다. 제품 G1 합격·실행 허가·Stage B·runtime 예산 요청은 범위 밖이다.
- 가설: 원본 `FUN_004D60B0`의 슬롯0 `sub ecx,0x1a`와 슬롯 높이 `+0x18`을 직접 anchor하면 드리프트를
  잡을 수 있고, 원본 입력 sprite SHA를 고정한 뒤 화면 전역 writer를 전수 열거하면 800×600과
  640×480의 진입 경로 후보를 실행 없이 분리해 보고할 수 있다.
- 예상 PASS / FAIL 조건: T1 두 anchor 존재, T2 원본 sprite 경로와 SHA 일치, T3 writer 4개와 후보 A/B
  각각의 전제·geometry 결과 출력, T4 기존 `logs/lap299/` 보존 및 새 lap301 report 생성. 하나라도
  실패하면 정적 후보를 승격하지 않고 기록한다.
- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted):
  - `docs/history/laps/probes/20260912_lap299_work_save_load_layout_probe.py`
    SHA `a6f682ebc3303bc1b040fca8d432f37b7872c165409891ca09840ea3a428c7a0`.
  - `logs/lap301/save_load_layout_probe.json`
    SHA `c312b42e3593c2af5bb47e9df9e1b624f8a55ea618a1cc70b7e6dc709caaf10a`.
  - `docs/STATUS.md`와 본 history 추가. 원본/참고 EXE·DLL/assets, `tools/`, `patches/`, runtime
    harness, comparator/PASS 규칙 변경 0. 커밋 없음(`LOOP_ALLOW_COMMITS=0`).
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture:
  - 원본 EXE `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`, 후보 없음.
  - 원본 입력 fixture `../Syw2plus/yfnt/saveloadtitle.spr`, SHA
    `7d154cdbf37dbea78c162ada870e656a039a224c5aa63ee52d86d8123c08a5c5`, header `[9,320,310,1]`.
  - offline Linux `.venv` + `/usr/bin/objdump`; 활성 플레이어/지도/군대 없음; 게임/Wine/Xvfb/
    Stage B/runtime/PNG 실행 0.
- 실행 명령 / 로그 / 캡처 경로 및 해시:
  - 사전 독립 확인: lap300 middle probe exit0, report SHA `bcac0a41…764c67b2`; 구 lap299 probe
    exit0, stdout SHA `8e735a9a…76d2bb0b`.
  - `.venv/bin/python docs/history/laps/probes/20260912_lap299_work_save_load_layout_probe.py`
    → exit0, stdout/report SHA `c312b42e…caaf10a`; 같은 명령으로 `logs/lap301/`에 저장.
  - report의 screen-global writer 4개: `0x431B79/0x431B7F`, `0x4324B8/0x4324C2`.
  - 후보 A `(800,600)` title `(240,145)`, 후보 B `(640,480)` title `(160,85)`; 두 후보 모두
    slot non-overlap/inside-screen/buttons-inside/outside-slot 네 검사 true.
  - `make check` → **292 passed**, Ruff/compileall/mypy/CONTEXT_PASS.
  - `bash checks/safety.sh check` → **SAFETY_PASS**.
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN):
  - T1 **PASS**: `sub ecx,0x1a`, `add eax,0x18`, `add ecx,0x18` anchor가 원본 disassembly에 존재.
  - T2 **PASS**: 참조 저장소가 아닌 원본 입력 경로와 pinned sprite SHA/header 사용.
  - T3 **PASS (정적 report)**: 하드코딩 단일 `SCREEN` 제거, `.text` writer 전수 4개와 후보 A/B의
    precondition을 출력. 클릭 시점 전역값·버튼 hitbox·slot selection·load transition은 **UNKNOWN**.
  - T4 **PASS**: 기존 `logs/lap299/save_load_layout_probe.json` 삭제/수정 없이 lap301 report 생성.
  - 첫 수리 실행은 fixture 경로를 `REPO/Syw2plus`로 잘못 잡아 exit1했으나, 원본 입력의 실제 형제
    경로 `REPO.parent/Syw2plus/yfnt`로 즉시 수정 후 필수 probe와 Fast gate가 PASS했다.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: 원본 SHA·보호 기준·안전 기준은 변경하지 않았다.
  제품 G1~G4 증거 0, 실제 입력/scene pair 0, Stage B 0, 사용자 마일스톤 승인 없음. 다음 새
  middle(Sol/Opus5/high)이 source/report SHA, writer enumeration, 후보 전제와 geometry를 독립
  검수해야 하며 그 전까지 실행·좌표 승격 금지. W3 stale self-pin은 이번 바퀴에서 건드리지 않았다.
- 다음 한 가지: 다음 새 middle이 lap301 산출물을 독립 검수하고, 실행 없이 확인 가능한 수리만
  ACCEPT/REVISE로 판정한다.
