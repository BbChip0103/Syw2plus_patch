# G2 strategy lap580 — W48 계약 결함 처분: (B) `UNKNOWN(harness_contract)` + 정적 N211, W49 진행

- 작성: lap580 strategy. 실제 모델 Claude Code `claude-opus-5-5`(effort 세션 비노출). 라우팅 계약의 strategy 모델(`claude-fable-5`/Astra)과 다르며 lap567·572·577과 같은 대체다. 게임 실행 0, 제품 source·하네스·후보·raw 변경 0, 커밋 0.
- 입력: `loop/ESCALATE_SOL` §130(lap579 middle `REJECT / BLOCKED(harness_contract)`), 카드 `G2_STRATEGY_S4_TRANSPORT_W48_LAP577.md`, INBOX 2026-09-24 23:05 상시 지시(절차·예산은 묻지 말고 결정).
- **이 문서는 G2 PASS·마일스톤 마감·다음 목표 전환이 아니다.** 번복 가능한 strategy 결정이다.

## 1. §130 확인 (이전 바퀴 검수)

- raw SHA 재계산 일치: attempt1 `abe81730…dc2d`, attempt2 `e0a1f7cb…800a`.
- attempt2 runner `w48_c0_full_pair.py`에는 좌표 클릭(`click`)만 있고 `127.0.0.1`·키 입력이 없다(N209 확인). raw 최상위 키는 `attempt/captures/displays/finished/fixture/instances/schema/source/source_sha_expected/status`뿐이며 `ss` 출력이 없다(N210 확인).
- 캡처 확인: PS13 세션 목록 화면에는 IP 입력란이 없다(버튼 `돌아가기/찾아보기/참여하기/방만들기`만). host의 `방만들기` 뒤 화면은 PS7 공급자 선택(`Internet TCP/IP Connection For DirectPlay`, `IPX Connection For DirectPlay`)이다.
- 게임 폴더 support DLL은 `_inmm/_inmm_orig/ddraw/dxwrapper/syw2x`뿐이다. DirectPlay는 Wine builtin을 쓴다.
- **§130 REJECT에 동의한다.** lap578 `BLOCKED(env)` 귀속은 쓰지 않는다.

## 2. 신규 정적 근거 N211 — 설치된 Wine 9.0 dpwsockx 콜백 stub

- 대상: `wine-9.0 (Ubuntu 9.0~repack-4build3)`, `/usr/lib/i386-linux-gnu/wine/i386-windows/dpwsockx.dll` SHA-256 `3b4f6a9d355114fb78f1e2a3961f48324b654c7e246a1bcd0925f3cdbe7986c9`(dplayx.dll `16d85061…4c57`). 읽기 전용.
- 명령: `strings -n 5 dpwsockx.dll | grep -E 'DPWS|stub'`, `strings -n 3 dpwsockx.dll | grep '%'`.
- 관측: `DPWSCB_*` 콜백 이름 15개(EnumSessions, Reply, Send, CreatePlayer, DeletePlayer, GetAddress, GetCaps, Open, CloseEx, ShutdownEx, GetAddressChoices, SendEx, SendToGroupEx, Cancel, GetMessageQueue)와 인자 형식 문자열 14개가 같은 순서로 있다. 그중 13개가 `... stub`(CloseEx/ShutdownEx의 `(%p) stub`은 한 문자열로 합쳐짐)이고, stub이 없는 것은 7번째 `(%ld,%p,0x%08lx,%p)` 하나로 GetCaps 인자(`idPlayer, lpCaps, dwFlags, lpISP`)와 맞는다. 첫 형식 `(%p,%ld,%p,%u) stub`은 EnumSessions(`lpMessage, dwMessageSize, lpISP, bReturnStatus`), `(%u,%p,%p,%u,0x%08lx,0x%08lx) stub`은 Open(`bCreate, lpSPMessageHeader, lpISP, bReturnStatus, dwOpenFlags, dwSessionFlags`)과 맞는다. 즉 GetCaps 외 14개 콜백이 stub이다.
- 해석(정적, 실행 미증명): 이 환경의 TCP/IP 서비스 공급자는 세션 탐색·세션 생성·송신을 구현하지 않는다. 그러면 host `Open` 실패(PS7 복귀)와 client 빈 목록이 설명된다. 127.0.0.1 입력이 있어도 SP가 주소를 쓰지 않으므로 결과가 바뀔 근거가 없다. 문자열 순서만으로 함수와 형식을 짝지었고 역어셈블로 확인하지 않았다 — 다음 middle이 독립 확인한다.

## 3. 결정 = (B)

- **corrected C0 재실행을 허용하지 않는다.** 이유: (1) N211 때문에 같은 Wine 9.0 builtin 환경에서 IP를 넣어도 새로 알 것이 없다. (2) 게임 UI에 IP 입력란이 없다. native DirectPlay라면 SP가 주소 대화상자를 띄울 자리인데, 그 자리가 stub이다. (3) 게임쌍 2회 예산을 다시 여는 것은 PROMPT ③ "같은 추측 반복 금지"에 걸린다.
- **W48 라벨:** 실행 증거 = `UNKNOWN(harness_contract)`(N209/N210). 환경 원인 = N211 정적 근거로 `BLOCKED(env: wine9.0 dpwsockx stub)` **후보**. middle이 N211을 독립 확인하면 S5′에 이 라벨로 올린다. 확인이 실패하면 `UNKNOWN`만 올린다. 어느 쪽도 `NOT_FEASIBLE`(제품 멀티 경로 부재)이 아니다.
- **S4 대안(모델이 고르지 않음, S5′ 사용자 판단 항목):** (i) DirectPlay SP가 구현된 더 새 Wine 설치 — 새 의존성, 사용자 승인 필요, 구현 버전은 이 회차에서 확인하지 않음. (ii) 네이티브 DirectPlay 런타임 DLL — 새 의존성·배포 조건, 사용자 승인 필요. (iii) 실제 Windows 호스트/VM. (iv) 이번 G2 제출에서 멀티를 "환경 미검증"으로 명시.
- C1(결합 후보 멀티) 실행 0 유지. LAN broadcast·netns·새 DLL 금지 유지.

## 4. 다음 한 가지 = W49 화면 증거 (work, 사전 허가 그대로)

- lap579·lap580 두 회차 연속 실행 증거 0이다(PROMPT ③ 최대 2회). 다음 회차는 반드시 실제 실행 증거를 늘린다.
- 계약은 `G2_STRATEGY_S4_TRANSPORT_W48_LAP577.md` §5 그대로다. 결합 후보 `dfdc91ad…3883`, W46 하네스 파생, 혼합 fixture T0(8/8 `used`∈[4900,5000]), 교전·저장 없음. T0·+2,000·+10,000 전체 화면 각 1장, 미니맵 보이는 장면 1장, 원본 시딩 전 동일 지도 화면 1장. 각 캡처에 `tick`·owner별 `used` raw와 SHA를 같이 저장. 게임 1회, 실패 시 재실행 없음.
- 캡처는 `temp/Syw2plus_patch/captures/`에 `YYYYMMDD_HHMMSS_` 접두사. foreground 완주까지 세션 유지(background 금지).

## 5. 그 다음

1. middle: W49 raw·캡처 SHA 독립 검수 + N211 독립 확인(읽기 전용, 역어셈블 또는 Wine 9.0 소스 대조 중 하나).
2. strategy: S5′ 3단 재제출문(W21·W26·W45R·W46·W47 + S4 `UNKNOWN`/`BLOCKED(env)` 후보·대안 (i)~(iv) + W49 캡처 + 제외 항목: 교전/사망/재생산, N141).
3. 사용자 전권 유지: Q7-B 3단 판정, “8인”이 사람인지 AI인지, (ㄴ) AI 변경 예외, Q10 `(다)` 번복, S4 대안 (i)~(iv).
