# 2026-09-25 | lap 578 | G2 S4-0 (work)

- 날짜/lap/목표/가설: 2026-09-25 KST / 578 / G2 S4 지원 전송 가능성. 원본 두 인스턴스가
  127.0.0.1 DirectPlay 세션을 만들 수 있으면 결합 후보로 이동할 수 있다는 가설.
- 지정 역할: hands-on work. 카드 `docs/work/active/G2_STRATEGY_S4_TRANSPORT_W48_LAP577.md` §4.
- 변경파일: 제품 source·브리지·게임 EXE 0. 새 읽기 전용 근거
  `analysis/memory_maps/g2_s4_directplay_transport_20260925.md`; 실행 하네스와 raw는
  공유 temp에만 보존. 커밋 0 (`LOOP_ALLOW_COMMITS=0`).
- 원본/후보 SHA: 원본 `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`.
  C0가 T1에서 막혀 결합 후보 `dfdc91ad…3883` C1은 실행하지 않았다.
- 정적 실행: `objdump -p`/`strings`로 `DPLAYX.dll`, `WSOCK32.dll`, `Host`,
  `gamestate/maxplayers/hostport/hostip`, `SETMULTI004/005` 확인. 기존 pinned map의
  `00439FA0→00439E80→0046B300→IDirectPlay4A::SendEx`를 근거로 삼고 오프셋 추측은 하지 않았다.
- C0 시도1: 두 새 prefix/display `:6557/:6558`, PS9→PS7→PS13까지 양쪽 도달; 동일 입력
  가설로 host/join 분리 없이 종료. raw `20260925_lap578_w48_c0_pair/c0_result.json`.
- C0 시도2: 두 새 prefix/display `:6559/:6560`. host `방만들기`, client
  `찾아보기→첫 행→참여하기`; host PS7 provider 복귀, client PS13 잔류. PS3 진입 0/2,
  tick 0/0, T1 FAIL·T2 FAIL·T3 UNKNOWN. raw `c0_attempt2_result.json` SHA
  `e0a1f7cba736af5fe7331130908dd0bb1b26ed8d72f7225b47ae8d0dacea800a`.
- 캡처/fixture: 원본 2인 멀티 UI, seed/resource/bridge/memory write 없음. 대표 화면은
  `/home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/captures/W48_*.png`에
  timestamp와 SHA로 보존했다. attempt2 하네스가 attempt1 helper의 capture global output을
  재사용해 raw JSON의 원래 경로가 attempt1 디렉터리를 가리키는 provenance defect가 있다.
  실제 파일·복사본·SHA는 보존했고, middle은 이 caveat를 포함해 독립 검수한다. 포트 pre/post
  `ss`에서 47624·2300~2400 listener 없음.
- 판정: **`BLOCKED(env)`**. static 경로는 존재하지만 Wine builtin DirectPlay 환경에서
  원본 C0가 두 번의 허용된 입력 가설 안에 T1을 성립시키지 못했다. 제품 불가능 판정이나
  후보 회귀 판정으로 승격하지 않는다.
- Fast/안전: 두 실행 모두 foreground 회수, 소유한 prefix/display만 종료, 기존 Wine/Xvfb
  미접촉, 원본 SHA 전후 동일. 문서 반영 후 `make check` **835 passed in 494.72s**,
  Ruff/compileall/mypy/`CONTEXT_PASS`, `checks/safety.sh check`=`SAFETY_PASS`.
  실제 24k/144k·후보 C1·멀티 동기화는 미검증.
- 다음행동: middle이 summary를 배제하고 raw JSON·화면 SHA·포트/프로세스 종료를 독립
  검수한다. 그 뒤 W49 화면 증거는 카드 사전 허가대로 별도 1회 진행하고, strategy가
  S5′에 `BLOCKED(env)`와 대안을 올린다.
