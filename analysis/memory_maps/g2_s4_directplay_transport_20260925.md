# G2 S4 DirectPlay transport — lap578 static/runtime evidence

- 조사: lap578 work, 2026-09-25 KST. 읽기 전용 정적 확인과 원본 C0 대조군만 수행했다.
- 고정 원본: `Syw2plus/syw2plus_original.exe`, SHA-256
  `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`, 1,032,192B.
- 정적 명령: `objdump -p Syw2plus/syw2plus_original.exe`; `strings -el`/`strings`로
  `Host`, `gamestate`, `maxplayers`, `numplayers`, `hostport`, `hostip`, `SETMULTI004`,
  `SETMULTI005`, DirectPlay 오류 문자열을 확인했다. imports에는 `DPLAYX.dll`, `WSOCK32.dll`,
  `ole32.dll`, `DDRAW.dll`이 있다.
- 기존 동일-SHA 주소 지도 `analysis/memory_maps/hqcdd_external_display_map_20260921.md`의
  독립 대조 근거에 따라 DirectPlay 송신 경로는 `00439FA0 → 00439E80 → 0046B300 →
  IDirectPlay4A::SendEx`로 기록한다. 이 lap에서는 새 오프셋을 추측 적용하지 않았다.

## C0 runtime

- 입력: 두 새 전체 게임 복사본, 서로 다른 fresh Wine prefix와 Xvfb display, 원본 EXE만.
  제품 source·브리지·게임 데이터·원본 파일은 변경하지 않았다. 127.0.0.1/허용 포트만을
  사용했고 네이티브 DirectPlay DLL·LAN broadcast·netns를 사용하지 않았다.
- 시도 1: `20260925_lap578_w48_c0_pair/w48_c0_pair.py`, displays `:6557/:6558`.
  양쪽 PS9→PS7→provider confirm→PS13 세션 목록은 관측됐으나 두 인스턴스에 동일 입력을
  넣어 host/join을 분리하지 못한 메뉴 가설 실패. 마지막 PS13, tick 0.
- 시도 2: `20260925_lap578_w48_c0_full_pair/w48_c0_full_pair.py`, displays `:6559/:6560`.
  host `방만들기`, client `찾아보기→첫 행→참여하기`를 분리 입력했다. host는 PS13에서
  PS7 provider 화면으로 복귀했고 client는 PS13에 남았다. host/client 모두 PS3 진입 없음,
  tick 0, 세션 동기화·T1/T2 FAIL. raw JSON SHA-256:
  `c0_attempt2_result.json` `e0a1f7cba736af5fe7331130908dd0bb1b26ed8d72f7225b47ae8d0dacea800a`.
- T4 화면 원본은 `temp/Syw2plus_patch/captures/`에 보존했다. 대표 SHA: session list
  `631e1ed3b18d04c4d1903d8707953a93c3f7480a04fc95c7d833d0c3e81285ee`, host return
  `a43167aed6eb30db9990c6f80039ffc867c859059b65072afcad876daf398497`, client join
  `8318aecf89471cd77d65696fd33dcf69cc0a3f0be946d1f286485ae940db707a`.
- pre/post `ss -lun`/`ss -ltn`에서 47624 및 2300~2400 listener 없음. 종료 후 해당 prefix의
  Wine/Xvfb만 정리했고 잔류 없음. `BLOCKED(env)`는 원본 DirectPlay 경로 부재가 아니라
  현재 Wine builtin DirectPlay 실행 환경에서 T1을 성립시키지 못한 판정이다.
