# 2026-09-12 | lap 284 | G1 S1 저장 파일 레이아웃 정적 모델

- 실제 provider/model/effort / 지정 역할: Codex work session / work tier high contract / hands-on 조사·probe 구현
- 목표: `docs/work/active/G1_RUNTIME_CONTRACT_MIDDLE_LAP284.md` §7의 offline 카드. 게임 실행·하네스 수정 없이 원본 save serializer의 정적 순서/폭을 유도하고 네 fixture 크기로 반증한다.
- 가설 / 예상 PASS·FAIL: save entry의 직접 `fwrite`만으로는 부족하므로 중간 helper `0x403950`, `0x4441E0`, `0x4464B0`의 고정 블록까지 포함하면 static prefix 뒤 remainder가 `0x758` roster record의 정수배가 된다. 네 파일 중 하나라도 정수배가 아니면 모델을 폐기한다.

## 변경 / 근거

- 신규 probe: `docs/history/laps/probes/20260912_lap284_work_save_layout_probe.py`
- 신규 출력: `logs/lap284/work_save_layout_probe.json`
- 게임 코드·하네스·comparator·producer·회귀 테스트·PASS 규칙 변경 0. 원본/fixture 쓰기 0.
- 원본 EXE SHA: `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`.
- fixture SHA는 probe가 재확인: save000 `1c703551…629e719da`, save006 `616b799…9289a0d064`, save011 `23dd24d…be14dfa4`, save012 `5a6863c…819c28f1`.

## 실행 / 수치

- 실행 명령: `.venv/bin/python docs/history/laps/probes/20260912_lap284_work_save_layout_probe.py`
- static call graph: save entry `0x440C20`, layer call 28개, helper fixed fwrite 3개, roster `0x40F4B0`; map dimensions는 파일 offset 210/212에서 읽었다.
- 예측/대조: save000 `180×180`, static prefix `2,388,902`, roster `375×0x758`; save006 `180×180`, 같은 prefix, `558×0x758`; save011/012 `100×100`, static prefix `1,705,702`, 각각 `147/149×0x758`. 네 reconstructed size가 실제 `3,093,902 / 3,437,942 / 1,982,062 / 1,985,822`와 정확히 일치, `failures=[]`, exit 0.
- save000/006 bulk의 PlayerStruct와 roster 대조: save000 절대 unit record 375, owner별 `0:124, 1:1, 2:123, 3:124, 5:3`; save006 558, `0:95, 2:92, 3:95, 5:104, 6:97, 7:75`. nation/is_cpu/alliance와 configured vs record-bearing active를 probe JSON에 보존했다.
- fixture 선택 결론은 제품/실행 승인이 아니다. save000은 더 작은 동일-map roster지만, 실제 로드 경로·결정성·G1 증거는 여전히 미검증이다.

## 판정 / 검증 / 남은 위험

- 판정: **PASS (이 offline 카드 범위)**. static model은 네 fixture에 반증되지 않았다. 최종 `make check`는 292 passed in 48.17s, Ruff/compileall/mypy 및 CONTEXT_PASS, safety `SAFETY_PASS`; probe/Ruff/py_compile도 0이다.
- 해석 경계: 레이어 serializer의 static 폭/순서와 파일 크기는 확인했지만, 실제 runtime layer pointer의 의미·save/load 값 동일성·로드 메뉴/PS35 경로는 확인하지 않았다.
- 실제 게임/Wine/Xvfb/Stage B/PNG 0. 제품 G1~G4 미완료. G3 9~16 저장공간 초과와 runtime contract blocker는 유지한다.

## 다음 한 가지

새 middle(Sol/Opus5)이 이 probe와 원본/fixture SHA, 28 layer 및 세 helper의 독립 재실행을 검수하고 ACCEPT/REJECT를 판정한다. 그 전까지 runtime 예산·게임 실행·하네스 로드 경로 구현은 열지 않는다.
