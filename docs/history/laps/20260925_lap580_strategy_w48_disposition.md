# 2026-09-25 | lap 580 | G2 S4-0 W48 처분 (strategy)

- 실제 provider/model/effort / 지정 역할: Claude Code `claude-opus-5-5`, effort 세션 비노출 / strategy(상위 방향). 계약 모델 `claude-fable-5`/Astra가 아닌 대체(lap567·572·577과 같음).
- 가설 / 사용자 관찰: §130의 두 선택지 중, corrected C0(127.0.0.1 입력+포트 raw) 1회가 새 정보를 줄 수 있는가. 설치된 Wine DirectPlay SP가 기능하지 않으면 재실행은 같은 추측의 반복이다.
- 예상 PASS / FAIL 조건: Wine 9.0 builtin `dpwsockx.dll`의 세션 탐색/생성/송신 콜백이 구현돼 있으면 (A) corrected C0 1회 허용, stub이면 (B).
- 변경 파일 / source fingerprint / 커밋: 새 `docs/work/active/G2_STRATEGY_W48_DISPOSITION_LAP580.md`, 이 기록, `docs/STATUS.md`, `docs/feedback/INBOX.md`, `loop/ESCALATE_SOL` §131. 제품 source·하네스·후보·raw 변경 0. 시작 fingerprint `9b4bbe4ba416ea71345bebee85e654b47f90539b`; 최종 Fast fingerprint는 STATUS. 커밋 0(uncommitted).
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 원본 `b56986e0…a8ac`, 결합 후보 `dfdc91ad…3883` 둘 다 실행 0. 환경 `wine-9.0 (Ubuntu 9.0~repack-4build3)`, `dpwsockx.dll` `3b4f6a9d355114fb78f1e2a3961f48324b654c7e246a1bcd0925f3cdbe7986c9`, `dplayx.dll` `16d850611adfe95a6ecf5f06b10654847ce2f109fd9b84bfa47725b6a5484c57`. 게임 실행 0.
- 실행 명령 / 로그 / 캡처: `sha256sum` 두 raw(attempt1 `abe81730…dc2d`, attempt2 `e0a1f7cb…800a` 일치), `grep`으로 attempt2 runner 입력 확인(좌표 click만, `127.0.0.1`·키 입력 없음), `jq keys`로 raw에 `ss` 필드 없음 확인, 캡처 `W48_…_instance0_session_list.png`(IP 입력란 없음)·`W48_…_host_after_create.png`(PS7 공급자 화면) 육안 확인, `strings` 두 명령으로 dpwsockx 형식 문자열 확인.
- 측정값 / 판정: N209·N210 재확인, §130 REJECT 동의. **N211(정적):** `DPWSCB_*` 15개 중 GetCaps만 TRACE, EnumSessions·Open·Send·SendEx 등 14개는 FIXME stub(문자열 순서·인자형 대조, 역어셈블 미확인). 판정 **(B)**: corrected C0 불허, W48 = `UNKNOWN(harness_contract)` + 환경 원인 후보 `BLOCKED(env: wine9.0 dpwsockx stub)`(middle 확인 조건). `NOT_FEASIBLE` 아님.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: N211은 문자열 짝짓기 기반이라 middle 독립 확인 필요. 대안 (i) 새 Wine (ii) 네이티브 DirectPlay DLL (iii) Windows 호스트/VM (iv) 환경 미검증 명시는 새 의존성/범위 문제라 모델이 고르지 않고 S5′에 올린다. lap579·580 연속 실행 증거 0(한도 2) → 다음은 실행 회차. G2 PASS·사용자 3단 승인 아님.
- 다음 한 가지: work가 W49 화면 증거를 카드 `G2_STRATEGY_S4_TRANSPORT_W48_LAP577.md` §5 그대로 1회 실행. 이어 middle이 W49 raw + N211 독립 확인, 그 뒤 strategy S5′.
