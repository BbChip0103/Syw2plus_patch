# 2026-09-28 | lap 741 | 목표 G5 ((G) 멀티 — 2인 LAN 명령 동기화)

- 실제 provider/model/effort / 지정 역할: Claude Code Sonnet 5 / high / work tier(구현·조사 실행).
- 가설 / 사용자 관찰: 2026-09-28 14:45 운영자 판정(lap740 v7 수용) — 다음 work는 (G) 멀티: 2인 LAN
  격리 실행(두 인스턴스·가상 네트워크)에서 50기 이동/정지/공격 명령이 양쪽에 동기화되는지(유닛
  위치·명령 상태 비교, desync 없음). "격리 환경에서 LAN이 불가하면 사유와 대안(원본 20 대비 명령
  패킷 수·형식 정적 대조)을 기록"이 (G) 항목 자체의 완료 조건으로 명시돼 있다(2026-09-28 01:31
  사용자 지시 체크리스트 원문). 가설: G2 S4 전송 트랙(lap577~580)이 이미 이 저장소와 같은 환경에서
  DirectPlay LAN 세션 생성/탐색 자체가 동작하지 않음을 정적 근거(N211, dpwsockx.dll 콜백 stub)로
  확정했다면, 같은 EXE·같은 Wine 설치를 쓰는 G5도 동일하게 BLOCKED이고, 실제 2-인스턴스 실행을
  다시 시도하는 것은 새 정보 없이 실패를 재현할 뿐이다(PROMPT.md③ "같은 추측 반복 금지").
- 예상 PASS / FAIL 조건: (a) 현재 환경의 DirectPlay Winsock SP(`dpwsockx.dll`) 해시가 G2 N211이
  분석한 파일과 일치하면 환경 동일성 확정 → 실행 재시도 없이 BLOCKED 판정, (b) 불일치하면 환경이
  달라졌으므로 실제 2-인스턴스 실행을 시도해야 한다.
- 변경 파일: 없음(조사·문서만, 제품 코드/EXE/패치 0 변경). 신규 저장소 파일: 이 lap 기록 1개,
  `docs/STATUS.md`/`docs/feedback/INBOX.md`/`docs/feedback/APPROVALS.md` 갱신·압축.
- 원본 SHA / 후보 SHA / 환경: 보호 원본 `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`
  (변경 없음, 이번 lap은 게임 실행 자체를 하지 않았으므로 재확인 불필요). 기준 후보 v7
  `30efafa067b6cb524bd68594dedee4d0d4c68e1efef348e2f16c211dc8229bef`(lap740). Wine
  `wine-9.0 (Ubuntu 9.0~repack-4build3)`(`wine --version`, 이번 lap 실측).

## 실행/조사 내용과 raw 근거

1. **환경 동일성 확인(실측):** `sha256sum`으로 세 경로를 직접 재해시했다.
   - 시스템 패키지 원본: `/usr/lib/i386-linux-gnu/wine/i386-windows/dpwsockx.dll` =
     `3b4f6a9d355114fb78f1e2a3961f48324b654c7e246a1bcd0925f3cdbe7986c9` — G2 lap580
     `G2_STRATEGY_W48_DISPOSITION_LAP580.md` §2가 기록한 값과 **완전 일치**.
   - 이 게임이 실제로 로드하는 32비트 syswow64 사본(여러 wine prefix: `~/.wine`, `~/.wine_test`,
     `~/.wine_syw2_359` 등) = 동일하게 `3b4f6a9d…986c9` — 세 개 서로 다른 prefix 전부 일치, 즉
     32비트 게임 EXE가 실제로 로드하는 DLL이 G2가 분석한 바로 그 stub 빌드다.
   - x86_64-windows 사본(64비트, 이 게임과 무관)만 다른 해시(`5ae8cfa5…`)였다 — 아키텍처가
     다른 별개 빌드일 뿐 모순이 아니다.
   - **결론: 환경 동일성 확정(가설 a).** G2 lap580 N211(`DPWSCB_*` 콜백 15개 중 GetCaps만 구현,
     나머지 14개 — EnumSessions/Open/Send/SendEx/CreatePlayer/DeletePlayer/GetAddress/CloseEx/
     ShutdownEx/GetAddressChoices/SendToGroupEx/Cancel/GetMessageQueue/Reply — 는 `... stub`
     문자열이 있는 FIXME 스텁)는 지금 이 저장소 환경에도 바이트 단위로 그대로 적용된다.
2. **게임 UI 재확인(신규 실행 없이 G2 캡처 재사용, PROMPT③ 근거):** G2 lap580 §1이 이미 실제 실행
   캡처로 확인한 대로 이 게임의 멀티 로비는 "돌아가기/찾아보기/참여하기/방만들기" 뒤 공급자 선택
   화면(`Internet TCP/IP Connection For DirectPlay`, `IPX Connection For DirectPlay`)만 제공하고
   IP 입력란이 없다 — 두 공급자 모두 Wine의 DirectPlay Winsock SP(`dpwsockx.dll`)를 거치므로
   §1의 stub 콜백이 그대로 적용된다. 게임 자체 지원 DLL(`_inmm/ddraw/dxwrapper/syw2x`)에는
   DirectPlay 대체 구현이 없다(G2 lap580 §1, 원본 게임 폴더 구조는 G5도 동일 EXE).
   **이번 lap은 이 화면을 다시 캡처하지 않았다** — 동일 EXE·동일 로비 코드 경로이므로 새 실행이
   새 정보를 주지 않는다(가설 a 확정에 따른 결론, PROMPT③ "같은 추측 반복 금지"에 따라 실행
   생략을 명시).
3. **판정: `BLOCKED(env: wine9.0 dpwsockx stub)`.** 2-인스턴스 LAN 격리 실행으로 50기 명령 동기화를
   직접 관측하는 것은 이 환경에서 불가능하다 — session 열거/생성/송신 콜백이 stub이므로 host가
   `방만들기` 뒤 진행하지 못하고 client가 세션 목록을 얻지 못한다(G2 lap580 §1 raw로 이미 관측된
   증상, 환경 동일성 확정으로 G5에도 적용). `NOT_FEASIBLE`(제품에 멀티 기능 자체가 없다는 뜻)이
   아니라 `BLOCKED(env)`다 — 이 Wine 빌드가 아닌 환경(다른 Wine 버전, 네이티브 DirectPlay 런타임,
   실제 Windows 호스트/VM)이면 다를 수 있으나 그런 환경 변경은 새 의존성이라 사용자 승인이 필요하고
   이번 lap의 범위 밖이다(G2 lap580 §3의 대안 (i)~(iii)과 동일 성격).

## 대안 — 원본 20 대비 명령 패킷 수·형식 정적 대조 (요청된 (G) 완료 경로)

1. **실제 주문 발행 호출부는 단일 지점이다.** `analysis/memory_maps/g5_selection_consumers_inventory_20260928.md`
   §"실제 주문 발행"(lap725 작성, lap719 재확정)이 이미 정적으로 확정한 사실을 재확인만 했다(신규
   조사 아님, 인용): 이동·공격·정지·홀드·순찰을 포함한 모든 실제 유닛 명령은 `0x41F0A4`
   (opcode = 런타임 전역 `word [0x892ffe]`) 단 하나의 호출부를 거친다. `FUN_004AE550`의 나머지
   21개 직접 호출부는 명령 발행이 아니라 UI 알림/아이콘 갱신용이며 선택 인원과 무관한 고정 opcode다
   (lap676 정적 반증, lap719 재확인).
2. **v4 패치 자체가 패킷 형식을 명시적으로 문서화해 두었다.** `patches/selection/g5_selection_cap50_v4.py:215`:
   `"record_format": "unchanged; 60-byte record, 20-word unit-list, issued up to 3 times per order"`
   — 원본 단일 호출(≤20기, 60바이트 레코드 1회)과 동일한 레코드 포맷을 그대로 재사용하고, 50기
   선택 시 `entries[0:20]`/`[20:40]`/`[40:50]` 세 조각으로 최대 3회 반복 호출한다(v3
   `CHUNK_UNITS` 상수 재사용, `patches/selection/g5_selection_cap50_v4.py:91`).
3. **이 청크 메커니즘이 v5→v6→v7까지 무변경으로 이어졌음을 이번 lap이 직접 확인했다(신규 확인):**
   `grep -n "^from\|CHUNK_UNITS"`로 v6/v7의 import 그래프를 실측 —
   `g5_selection_cap50_v6.py`는 `g5_selection_cap50_v5`를 import하고(자체 청크 로직 재정의 없음),
   `g5_selection_cap50_v7.py`는 `g5_selection_cap50_v6`를 import한다(마찬가지). v6는 사망-후-호출
   그룹 정리 훅(H4) 하나만, v7은 저장/로드 shadow-mirror 훅 두 개만 추가하며 둘 다 STATUS/lap733·
   lap740 기록대로 `0x41F0A4`나 그 청크 래퍼와 무관한 별도 call-site다. 즉 **기준 후보 v7의 실제
   명령 발행 경로는 v4 문서화 그대로다**: 원본과 바이트 단위로 동일한 60바이트/20-word 레코드
   포맷을 유지한 채, 50기 주문 1건당 최대 3회(⌈50/20⌉)만 반복 발행 — 새 opcode·새 레코드
   레이아웃·가변 길이 필드 없음.
4. **남는 미확인(정직하게 UNKNOWN으로 표시):** 이 `0x41F0A4` 호출이 실제로 DirectPlay
   Send/SendEx로 직렬화되는 정확한 지점(로컬 싱글플레이와 네트워크 동기화가 같은 큐를 쓰는지,
   아니면 별도 lockstep 입력 레코더가 있는지)은 이번 lap에서 disasm으로 확인하지 않았다 — §3의
   BLOCKED 판정 때문에 실제 실행으로도 확인할 수 없다(전송 계층 자체가 죽어 있어 패킷을 관측할
   방법이 없다). 따라서 "50기 명령이 실제로 최대 3배 패킷으로 나간다"는 문장은 **정적 구조 근거로
   PLAUSIBLE**이지, 와이어 캡처로 CONFIRMED는 아니다. 이 한계는 STATUS/next-thing에 명시한다.

## 판정 요약

- **(G) = 완료로 판단** — 체크리스트 원문의 "불가 시 사유 명시" 경로. 라이브 동기화 관측은
  `BLOCKED(env: wine9.0 dpwsockx stub)`(환경 동일성 실측 확정, G2 lap580 근거 재사용 — 신규
  게임 실행 0회). 대안 정적 대조는 기존 v4 문서화 + 신규 import-그래프 확인으로 "원본과 동일
  레코드 포맷, 주문당 최대 3배 발행 상한"을 확정(PLAUSIBLE, 와이어 미관측).
- 크래시: 해당 없음(게임 미실행). `source_unchanged`: 해당 없음(제품 파일 0 변경, 조사만).
- `make check`: 이 lap은 코드를 변경하지 않았지만 STATUS/INBOX/APPROVALS 문서 갱신 후 안전을 위해
  동일 fingerprint로 1회 실행했다 — 결과는 이 파일 하단 §부록 또는 STATUS 다음 갱신에 기록
  (백그라운드 PID 폴링으로 이 세션 안에서 완주까지 대기).

## 추가 지시(같은 lap 안, 2026-09-28 15:05 운영자) — 네이티브 IPXWrapper 재시도

위 §3 BLOCKED 판정을 기록한 직후, 운영자가 `docs/STATUS.md`를 직접 편집해 새 지시를 남겼다: 새 원본
폴더 `[ESL]Syw2plus/`에는 Wine 내장 stub가 아니라 **게임 자체가 배포한 네이티브 IPXWrapper
DLL 세트**(`dpwsockx.dll` 29184B/`wsock32.dll`/`mswsock.dll`/`ipxwrapper.dll`/`ipxconfig.exe`,
2015-12-02 컴파일, IPXWrapper 0.6.0)가 동봉돼 있으므로, `WINEDLLOVERRIDES`로 이 DLL들을 native로
강제해 "IPX Connection For DirectPlay" 공급자로 재시도하라는 지시다. 같은 lap 안에서 이어서
수행했다.

1. **실측 확인:** `ls -la "[ESL]Syw2plus/"`로 지시된 파일 6개(`dpwsockx.dll`/`wsock32.dll`/
   `mswsock.dll`/`ipxwrapper.dll`/`ipxconfig.exe`/`IPXConfigWIN32.reg`+`IPXConfigWIN64.reg`) 전부
   실재함을 확인. `ipxwrapper.log`(36,928B, 이미 존재)는 원본 배포자의 실제 Windows PC에서 만들어진
   과거 로그(Realtek NIC·Radmin VPN 어댑터·`192.168.45.219` 등 이 샌드박스와 무관한 네트워크 구성)
   임을 raw로 확인 — 즉 이 로그는 이번 조사 이전부터 있던 배포물의 일부다.
2. **아카이브 열람(읽기 전용, `/tmp`에서만):** `Syw2plus/IPXWrapper+v0.6.0.7z`를 `/tmp`에 압축
   해제해 `ipxwrapper.dll` 문자열을 스캔 — 레지스트리 베이스 `Software\IPXWrapper`, 인터페이스별
   `enabled`/`primary`/`port` 값, "Hamachi" 특수 처리 문자열을 확인. **peer 정적 목록 문자열은 이
   버전(0.6.0)에 없음** — 이 버전은 브로드캐스트(같은 서브넷) 또는 Radmin VPN/Hamachi 같은 가상
   어댑터의 브로드캐스트에 의존하는 설계로 보인다(원본 로그의 VPN 어댑터 사용과 일치).
3. **호스트 네트워크 확인:** `ip addr`로 이 샌드박스에 실제 브로드캐스트 가능 인터페이스
   `enp6s0`(172.30.1.54/24, brd 172.30.1.255)가 있음을 확인 — loopback 외에 진짜 NIC가 있어
   Wine이 이를 그대로 게스트에 노출하면 IPXWrapper가 그 서브넷으로 브로드캐스트를 시도할 수 있다.
4. **신규 단일 인스턴스 부팅 스모크 probe(`/tmp/lap741_ipx_native_smoke_driver.py`, 저장소 밖,
   기존 `runtime_env.prepare()`+`_xvfb()` 재사용, 제품 코드 0 변경):**
   - `runtime_env.prepare()`로 격리 사본 1개 생성(원본 SHA 사전확인 통과).
   - `IPXConfigWIN32.reg`를 그 prefix에 `wine reg import`(returncode 0, 성공) — "IPX Connection
     For DirectPlay" 공급자 등록.
   - **1차 시도** `WINEDLLOVERRIDES="ddraw=b,dpwsockx,wsock32,mswsock,ipxwrapper=n,b"`(콤마로만
     연결) → 부팅은 성공했지만 `ipxwrapper.log` mtime 무변화 — Wine의 `WINEDLLOVERRIDES` 문법은
     세미콜론으로 override 그룹을 구분해야 하는데 콤마만 쓴 첫 시도는 두 번째 `=` 때문에 파싱이
     깨져 override 자체가 적용되지 않았을 가능성이 높다고 판단해 **재시도(가설 실패 1/2, PROMPT③
     한도 내)**.
   - **2차 시도(문법 수정)** `WINEDLLOVERRIDES="ddraw=b;dpwsockx,wsock32,mswsock,ipxwrapper=n,b"`
     (세미콜론으로 override 그룹 분리) → 레지스트리 임포트 성공(returncode 0), 게임 12초간
     크래시 없이 생존(`process_alive_after_12s=true`) — **override 자체가 부팅을 깨지 않음은
     확인됐다.** 그러나 `ipxwrapper.log`는 **여전히 mtime 무변화**(원본 배포자의 과거 로그 그대로).
5. **판정(솔직하게 INCONCLUSIVE로 표시, BLOCKED도 FEASIBLE도 아님):** 로그가 갱신되지 않은 것은
   override가 실패했다는 뜻이 아니라 **`dpwsockx.dll`/`ipxwrapper.dll`이 지연 초기화**이기 때문일
   가능성이 크다 — 이 DirectPlay 서비스 공급자는 게임이 실제로 멀티플레이 메뉴에서 세션 공급자를
   나열/개설(`Open`/`EnumSessions`)할 때만 로드·실행되며, 단순 메인 메뉴 부팅만으로는 호출되지
   않는다(정적 근거: G2 lap580 §1이 이미 "PS13 세션 목록 화면"이 별도 메뉴 심도에 있음을 확인).
   즉 **이번 스모크 probe는 "override가 부팅을 깨지 않는다"만 확증했고, "native DLL이 실제로
   Wine 아래에서 정상 동작해 세션을 열 수 있는가"는 여전히 미확인이다.**
6. **막힌 지점(정직하게 기록):** 실제 확인에는 메인 메뉴 → 멀티플레이 모드 선택(`tools/runtime_env.py`의
   `G1_SETUP_POINTS["multiplayer_mode"]=(344,169)`와 `_g1_selector_flow` 헬퍼가 이 지점까지는
   재사용 가능) → DirectPlay 공급자 목록 화면(PS13, G2 lap577~580에서만 관측됨, 저장소에 영구
   보존된 클릭 경로 없음 — 그 드라이버는 `/tmp` 산출물이라 이번 세션에 없음) → "IPX Connection For
   DirectPlay" 선택 → 방만들기까지 가는 UI 자동화가 필요하다. 이 자동화 자체가 G2에서 lap577
   (정적)→578(시도)→579(middle reject)→580(strategy)에 걸쳐 만들어진 규모의 작업이며, 이번 lap
   예산(이미 (G) 가설 2회: 원본 stub 확인 + native override 부팅 스모크) 안에서 새로 만들 수
   없었다. **`FEASIBLE`도 `BLOCKED`도 아닌 `INCONCLUSIVE`로 정직하게 남긴다.**
- 크래시 0(스모크 1회), `source_unchanged`: 해당 없음(원본 EXE 무변경, 격리 사본만 사용, 사본은
  probe 종료 후 삭제 — 디스크 위생). 제품 코드 0 변경(진단 드라이버는 `/tmp`에만 존재).

## 다음 work 권장 (개정)

**(G)는 이번 lap에서 완전히 닫히지 않았다.** 다음 work 후보 두 갈래 중 운영자/middle이 선택:
(가) 위 §6의 UI 자동화(멀티플레이 선택 → 공급자 목록 화면 좌표 확보 → IPX 공급자 선택 → 방만들기/
찾아보기)를 새로 만들어 네이티브 override 재시도를 완결한다(비용: G2 lap577~580급 별도 작업). (나)
이 비용을 받아들이지 않고 §3의 `BLOCKED(env: wine9.0 dpwsockx stub)`+정적 패킷 대조를 (G)의
최종 답으로 채택하고 다음은 (H) 장시간으로 넘어간다. 이번 lap은 이 선택을 대신하지 않는다.
(H) 장시간(50기 반복 명령 수천 tick 안정성, 단일플레이 격리 실행)은 (G)의 선택과 무관하게 병행
가능하다.
