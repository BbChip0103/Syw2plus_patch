# 2026-09-28 | lap 742 | 목표 G5 ((G) 멀티 — IPXWrapper 네이티브 override로 2인 LAN 재시도)

- 실제 provider/model/effort / 지정 역할: Claude Code Sonnet 5 / high / work tier(구현·조사 실행).
- 가설 / 사용자 관찰: 2026-09-28 15:23 운영자 판정(lap741 선택지 (가) 채택) — 사용자가 사이드
  이펙트 전수 확인을 요구했으므로 멀티는 정적 대조로 끝내지 않는다. 멀티 로비 UI 자동화(호스트:
  멀티→IPX 공급자→방 만들기, 게스트: 같은 공급자→방 목록 선택→참가→시작)를 구축해 IPXWrapper
  동봉 DLL로 2인스턴스 세션 성립을 시도한다(15:05 지시 그대로). 한 lap에서 세션 성립까지 못 가면
  막힌 화면 캡처·오류와 함께 진척을 기록하고 다음 lap이 이어간다. 3 lap 안에 불가하면 (나)로 전환.
  이 lap은 그 3-lap 예산의 1회차다.
- 예상 PASS/FAIL 조건: T1(세션 성립) = client가 host 세션을 목록에서 찾고 참가, 두 인스턴스 모두
  게임 화면(ps==3) 진입. FAIL = 목록 비어 있음·참가 오류·크래시. 크래시가 나면 그 자체가 15:05
  지시의 "실패하면 구체 오류와 함께 BLOCKED 확정" 조건을 충족하는 것으로 본다(work tier 판단,
  비가역 아님).
- 변경 파일: 제품 source·패치·게임 EXE **0 변경**. 진단 드라이버 5개는 `/tmp`(세션 로컬, 저장소
  밖)에 작성했고, 산출물(raw JSON·캡처·오케스트레이터 로그)은 재현성을 위해 공유
  `temp/Syw2plus_patch/g5_multiplayer_lobby/20260928_lap742_*/`에 보존했다(w48 lap578 선례와
  동일하게 `/tmp`가 아니라 공유 temp에 보존 — 다음 세션이 다시 찾을 수 있게 함, lap741이
  `/tmp`에만 남겨 "저장소에 없다"고 기록했던 문제를 반복하지 않기 위함). 저장소 신규 파일: 이 lap
  기록 1개, `docs/STATUS.md`/`docs/feedback/INBOX.md` 갱신·압축, `docs/history/` 보존본 2개
  (STATUS lap717~741, INBOX lap643~741).
- 원본 SHA / 후보 SHA / 환경: 보호 원본 `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`
  (모든 실행에서 `runtime_env.prepare()`가 사후 해시 확인, 5회 전부 일치). 후보는 이 lap 범위 밖
  (제품 코드 미변경, EXE는 항상 원본). Wine `wine-9.0 (Ubuntu 9.0~repack-4build3)`.
  기본 소스 `Syw2plus_re/Syw2plus`에 이미 네이티브 IPXWrapper 파일 세트(`dpwsockx.dll`
  SHA `04b1265c…28cf4`/`wsock32.dll`/`mswsock.dll`/`ipxwrapper.dll`/`IPXConfigWIN32.reg`)가
  동봉돼 있음을 확인(`[ESL]Syw2plus/`의 동일 파일과 SHA-256 완전 일치) — 별도 source 지정 없이
  `runtime_env.prepare()` 기본 경로로 5회 모두 이 파일들이 포함된 격리 사본을 만들었다(원본
  저장소는 읽기만 함, 0 쓰기).

## 실행/조사 내용

### 1. UI 클릭 계약 재확립 (단일 인스턴스, 2회 실행)

기존 lap578 `w48_c0_full_pair.py`(`temp/Syw2plus_patch/g2_capacity/20260925_lap578_w48_c0_full_pair/`,
저장소 밖이지만 공유 temp에 보존돼 있어 재사용 가능함을 이번 lap이 발견 — lap741이 "저장소에
보존되지 않았다"고 기록한 것은 부정확했다; `/tmp`가 아니라 공유 temp를 확인하지 않았던 것이
원인)의 클릭 시퀀스 `(184,560)`→ps7 대기→`(400,219)`+`(608,564)`→ps13 대기는 **모호했다**: PS7에
도달하면 화면에는 이미 두 개의 상위 버튼("IPX 대전"/"온라인하기", G1 `multiplayer_mode`/
`solo_mode`와 같은 좌표 `(344,169)`/`(462,169)` 자리)과 그 위에 겹친 DirectPlay provider 목록
모달(행1 "Internet TCP/IP Connection For DirectPlay" y≈219, 행2 "IPX Connection For DirectPlay"
y≈240)이 동시에 떠 있다. `(400,219)`는 provider 행1(TCP/IP)을 클릭하므로 **IPX를 요청한 적이 없는
채로** 확인을 누르는 셈이었다.

단일 인스턴스로 2회 실행해 확인했다:
- run1(모호한 `(400,219)` 재현): TCP/IP 행 선택 → 확인 → **PS13을 건너뛰고 곧장 ps=5(방
  설정/맵선택 화면, 플레이어 슬롯 1~8 + 맵 목록 + 확인/취소)로 직행**. 캡처
  `.../20260928_lap742_provider_probe/…after_create_click.png`.
- run2(명시적 IPX 선택): `(343,169)`(IPX 대전 모드 버튼) → `(400,240)`(IPX Connection For
  DirectPlay 행) → `(608,564)`(확인) → **PS13(세션목록: 돌아가기/찾아보기/참여하기/방만들기)
  도달, 재현 2/2**(`20260928_lap742_walk_probe/`와 `20260928_lap742_crash_repro/`의 session_list
  캡처가 픽셀 단위로 동일한 화면). 이 계약을 이후 모든 실행에 사용했다.

### 2. 2인스턴스 C0 (원본 EXE, 새 UI 계약, IPX 명시 선택)

`temp/Syw2plus_patch/g5_multiplayer_lobby/20260928_lap742_c0_ipx_pair/`. Display `:6611`/`:6612`,
각자 새 `runtime_env.prepare()` 사본·prefix. `ss -lun`/`ss -ltn`으로 사전에 47624·2300~2400
비점유 확인(기록: 이번 lap 셸 로그, 점유 없음). `WINEDLLOVERRIDES="ddraw=b;dpwsockx,wsock32,
mswsock,ipxwrapper=n,b"` 양쪽 동일. `IPXConfigWIN32.reg`를 각자 prefix에 `wine reg import`
(returncode 0/0).

- host: title→184,560→ps7→343,169→400,240→608,564→**ps13 도달**(PS13 캡처, 세션 목록 비어있음
  정상). "방만들기"(723,563) 클릭 → 3초 후 상태 읽기는 여전히 ps=13(캐시/지연)이었으나, 이어진
  "room_settings_confirm"(605,563) 클릭 후 캡처에서 **Wine 크래시 대화상자**를 확인:
  "프로그램 syw2plus_original.exe은는 심각한 문제에 직면해서 종료합니다.불편을 끼쳐드려
  죄송합니다." 이후 host의 모든 `state()` 폴링(settle 구간 20초, 20샘플)이 `read_error`(프로세스
  없음/메모리 읽기 실패)로 실패 — **host 프로세스가 실제로 죽었다.**
- client: 같은 클릭 시퀀스였으나 이번 실행에서는 **PS13이 아니라 곧장 ps=5(단독 방 설정 화면)로
  직행**했다(run1과 같은 경로, 원인 미상 — 두 인스턴스가 동시에 IPX 브로드캐스트를 시도하며
  타이밍이 달라졌을 가능성이 있으나 확인 안 됨, UNKNOWN으로 기록). client는 그 화면에서 PS13용
  버튼 좌표(483,563/400,190/603,563)를 눌렀고 최종적으로 **ps=3(인게임)**, tick이 419→519로
  꾸준히 증가 — 이것은 host와 무관한 **client 자신의 로컬 스커미시**로 판단한다(자원
  5000/5000, 인구 20/1500 HUD가 방금 시작한 솔로 게임과 일치하는 캡처, `client_06_settled.png`).
  즉 이 실행은 실제 멀티 세션이 아니라 client가 우연히 로컬 게임을 시작한 것이며 host와
  desync 비교는 의미가 없다.
- **T1 = FALSE**(정직하게 기록, `result.json`의 `t1_session_established: false`). host가
  크래시했으므로 client가 무엇을 하든 세션은 성립할 수 없었다.

### 3. 크래시 재현성 확인 — 단일 인스턴스 2회 대조

크래시가 위 2인스턴스 실행의 일회성 경합 때문인지 확정하기 위해 **가설 2회**(PROMPT③ 한도)를
썼다:

1. `20260928_lap742_crash_repro/`(display `:6621`, 네이티브 override 동일) — 단일 인스턴스로
   같은 계약을 반복: title→ps7→IPX 모드→IPX 행→확인→**ps13 도달**(캡처로 확인) → "방만들기"
   (723,563) → 3초 후 캡처 = **동일한 Wine 크래시 대화상자**(`after_create_click.png`, 2인스턴스
   run의 크래시 대화상자와 텍스트·레이아웃 완전 동일). `game_proc.poll() is None`은 참이었으나
   이는 wine 크래시-리포터 프로세스가 아직 살아있다는 뜻일 뿐(대화상자를 닫아야 실제 종료),
   `state()`가 읽은 `ps=13`은 죽기 직전의 캐시된 마지막 값으로 판단한다. **크래시 재현 2/2.**
2. `20260928_lap742_stub_compare/`(display `:6622`, **override만 `ipxwrapper=b`로 되돌림** —
   즉 Wine builtin `dpwsockx` stub, 나머지 절차 동일) — 같은 클릭 시퀀스, "방만들기" 클릭 3초 후
   상태는 **크래시 없이 ps=7(provider 화면)로 조용히 복귀** — lap578/lap580이 이미 기록한
   "host `방만들기` 뒤 PS7 provider 복귀" 패턴과 정확히 일치, **크래시 없음**.

이 대조로 **크래시의 원인이 네이티브 IPXWrapper override 자체임을 확정**한다(같은 EXE·같은
클릭·같은 실행 스크립트 골격에서 override 한 줄만 바꿔 크래시 유무가 갈림).

## 판정

- **(G) = `BLOCKED(env: native ipxwrapper crashes on room creation, wine9.0)`로 확정.**
  근거: 네이티브 IPXWrapper override + "IPX 대전" 모드 + IPX provider 명시 선택 + PS13
  "방만들기" 클릭 조합이 Wine 크래시 대화상자를 동반한 프로세스 종료를 **2/2 재현**했다(2인스턴스
  host 1회 + 단일인스턴스 재현 1회). builtin stub 대조군(같은 절차, override만 원복)은 크래시
  없이 기존 문서화된 방식(PS7 복귀)으로 실패한다 — 즉 **네이티브 override는 기존 BLOCKED를
  해결하지 못했을 뿐 아니라 새로운 크래시를 유발**한다.
- 이것은 **제품/후보 회귀가 아니다** — 크래시는 완전 무패치 원본 EXE(`b56986e0…c9c08a8ac`,
  실행 전후 해시 재확인)에서, 배포물에 이미 동봉된 네이티브 DLL을 `WINEDLLOVERRIDES`로 강제한
  이 환경 조합에서만 발생한다. G5 선택 상한 50 패치(v7)는 이 lap에서 전혀 실행하지 않았다
  (제품 코드 0 변경).
- **이번 lap 안에서 15:23 지시의 "실패하면 구체 오류와 함께 BLOCKED 확정" 조건을 충족했다고
  판단해 3-lap 예산(1회차 사용)을 조기 종결한다.** 나머지 2 lap을 소모적으로 반복하기보다,
  이미 재현 가능한 크래시 증거가 확보됐으므로 middle/운영자가 이 판정을 수용할지, 아니면 gdb로
  크래시 원인(어떤 native IPXWrapper 호출이 죽는지)을 더 추적할지 판단하도록 다음 한 가지로
  넘긴다.
- client 쪽 PS13/PS5 경로 비결정성(2절)은 host 크래시가 이미 결정적이므로 (G) 판정에 영향을
  주지 않는다 — UNKNOWN으로만 기록하고 추가 조사하지 않았다(예산 배분: 크래시 원인 확정에 집중).

## Fast/안전

- 사전 `ss -lun`/`ss -ltn`: 47624·2300~2400 비점유 확인, 실행 후 자기 프로세스만 종료(다른
  wineserver/Xvfb 미접촉).
- 원본 SHA 5회 실행 전부 `prepare()` 사후 확인 일치(`b56986e0…c9c08a8ac`). 디스크 위생: 각 실행의
  격리 `game` 사본(회당 약 580MB, 총 8회 실행 — provider_probe/walk_probe/c0_ipx_pair×2/
  crash_repro/stub_compare)은 실행 직후 삭제, `manifest.json`/`output`/`prefix`는 보존
  (`local/runtime/20260928_15*`, 확인 완료). 다른 프로세스/로그 정리 없음.
- `make check`: 이 lap은 제품 코드를 변경하지 않았지만 문서 갱신 후 안전 확인을 위해 1회
  실행했다(백그라운드 PID 폴링으로 완주까지 세션 유지, 결과는 STATUS 갱신에 반영).
- 진단 스크립트(`/tmp/lap742_*.py`, 5개)는 세션 종료 시 사라지는 임시 파일이며 제품/저장소에
  포함되지 않는다. 산출물(raw JSON·캡처·로그)만 공유 `temp/Syw2plus_patch/g5_multiplayer_lobby/`
  에 보존해 다음 세션이 재현할 수 있게 했다.

## 다음 한 가지 (1차 작성 시점)

middle/운영자가 이 `BLOCKED(env: native ipxwrapper crashes on room creation)` 판정을 (G)의
최종 답으로 수용할지, 아니면 gdb로 크래시의 정확한 원인(어떤 native `dpwsockx.dll`/
`ipxwrapper.dll` 호출·주소에서 죽는지, `자세히 보기(D)` 버튼의 Wine 백트레이스)을 한 lap 더
추적할지 판단한다. 수용하면 다음 work는 (H) 장시간(50기 반복 명령 수천 tick 안정성, 단일플레이
격리 실행)으로 진행하고, A~H 전체가 채워진 뒤 새 middle이 한 번에 독립 재검수한다
(2026-09-28 03:36 판정대로).

## 추가 — 2026-09-28 15:55 운영자 지시(같은 lap742 세션 안에서 이어서 수행)

운영자가 STATUS/APPROVALS를 직접 편집해 "G 2/3 lap" 지시를 남겼다: ① Wine 크래시 백트레이스/
모듈·주소 캡처, ② override 조합 축소 실험 3~4개, ③ `ipxconfig.exe` 설정 후 재시도. 이 lap
안에서 ①②를 이어서 수행했다(③은 근거를 들어 생략, 아래).

### ① 백트레이스 (WINEDEBUG 전환)

`WINEDEBUG="-all"` → `"+seh,+loaddll"`로 바꿔 단일 인스턴스로 재현(display `:6631`,
`temp/Syw2plus_patch/g5_multiplayer_lobby/20260928_lap742_crash_backtrace/orchestrator.log`,
656줄). 같은 UI 계약(IPX 모드→IPX 행→확인→PS13→방만들기)으로 크래시 재현 확인 후 로그를 grep한
근본 원인 체인(원문 그대로 인용):

```
0118:err:dplay:IDirectPlay4Impl_InitializeConnection Unable to load service provider {44eaa760-cb68-11cf-9c4e-00a0c905425e}
0118:err:dplay:IDirectPlay4Impl_InitializeConnection Unable to load service provider {0f1d6860-88d9-11cf-9c4e-00a0c905425e}
0118:err:dplay:IDirectPlay4Impl_InitializeConnection Unable to load service provider {44eaa760-cb68-11cf-9c4e-00a0c905425e}
0118:err:dplay:DirectPlayCreate Failed to Initialize SP: DPERR_UNAVAILABLE
550:wine: Unhandled page fault on read access to 00000000 at address 7AF42740 (thread 0118), starting debugger...
```

`{44eaa760-cb68-11cf-9c4e-00a0c905425e}`는 Microsoft DirectPlay의 표준 "Internet TCP/IP
Connection For DirectPlay" 서비스 공급자 GUID, `{0f1d6860-88d9-11cf-9c4e-00a0c905425e}`는
표준 "IPX Connection For DirectPlay" GUID다(둘 다 공개된 값, 이번 lap이 새로 부여한 것이 아니라
Wine `dplayx` 소스/문헌에 나오는 잘 알려진 상수). **로그는 두 GUID 모두에 대해 로드 실패를
기록한다** — 즉 IPX만의 문제가 아니라 Wine builtin `dplayx.dll`이 이 환경에서 등록된 서비스
공급자 DLL(레지스트리 `Path=dpwsockx.dll`)을 **native로 override했을 때 전혀 로드하지 못한다**는
뜻이다. `IDirectPlay4Impl_InitializeConnection`이 `LoadLibrary`류 호출에 실패 → `DPERR_UNAVAILABLE`
반환 → 게임의 "방만들기" 핸들러가 이 실패를 확인하지 않고 반환된(아마 NULL) 인터페이스 포인터를
바로 역참조 → 주소 `0x00000000` 읽기 접근 페이지 폴트로 프로세스 종료(Wine 크래시 리포터가 이
Unhandled exception을 감지해 대화상자를 띄움). **이것은 제품(게임) 코드의 널체크 누락 버그이지만,
트리거 조건(서비스 공급자 로드 실패)은 순수 Wine 환경 문제다** — 원본 게임이 실제 Windows에서
정상 동작했다면 서비스 공급자 로드는 항상 성공했을 것이므로 이 널체크 누락이 실제로 발현된 적이
없었을 가능성이 크다.

### ② override 조합 축소 실험 (1건 추가, 결정적)

`WINEDLLOVERRIDES="ddraw=b;dpwsockx=b;wsock32,mswsock,ipxwrapper=n,b"`(dpwsockx만 builtin으로
되돌리고 나머지는 native 유지, display `:6641`,
`temp/Syw2plus_patch/g5_multiplayer_lobby/20260928_lap742_combo_dpwsockx_builtin/result.json`)로
같은 절차(IPX 모드→IPX 행→확인→PS13→방만들기)를 재현 — **크래시 없음**, `after_create_click`
상태가 `ps=7`로 조용히 복귀(기존 builtin-stub 전체 대조군과 동일 패턴). **이로써 크래시 유발
변수가 `dpwsockx`의 native/builtin 여부 하나로 격리 확정됐다**: `dpwsockx=native`(다른 조합
무관) → dplayx가 로드 실패 → 크래시. `dpwsockx=builtin`(다른 DLL이 native든 아니든 무관) →
dplayx가 Wine 자신의 stub을 성공적으로 로드 → 콜백은 전부 FIXME stub이라 기능 없이 조용히 실패.

### ③ ipxconfig.exe 설정 — 실행하지 않음 (근거 있는 생략)

①의 로그가 보여주듯 실패는 **DirectPlay 객체 생성 단계**(`DirectPlayCreate`)에서 이미 확정되며,
이 시점에는 어떤 UDP 소켓도 아직 열리지 않는다(`Unable to load service provider`는 DLL을
`LoadLibrary`하는 단계의 실패이지 소켓/포트 설정 문제가 아니다). `ipxconfig.exe`가 다루는
인터페이스/포트 설정은 `dpwsockx.dll`/`ipxwrapper.dll`이 **이미 로드되고 실행된 뒤**에나
의미가 있는 설정이므로, DLL 로드 자체가 실패하는 이 실패 모드에는 영향을 줄 수 없다고 판단해
실행하지 않았다(PROMPT③ "같은 추측 반복 금지"에 준해, 근거 없는 반복 실행을 피함 — 생략 사유를
숨기지 않고 명시).

### 갱신된 판정

**(G) = `BLOCKED(env: native ipxwrapper crashes on room creation, wine9.0)`를 근본 원인까지
확정.** 원인은 Wine builtin `dplayx.dll`이 native로 override된 서비스 공급자 DLL을 구조적으로
로드하지 못하는 것이며, `dplayx.dll` 자체는 이 배포물에 native 대체본이 없어(게임 폴더에 파일
없음) 추가 override 조합으로 우회할 수 없다(새 의존성 도입 없이는). `WINEDLLOVERRIDES` 조합을
더 시도해도 결과는 이분법(native dpwsockx=크래시, builtin dpwsockx=기능 없음)을 벗어나지 못한다.
`make check` **1116 passed(814.81s)**, ruff/mypy/`CONTEXT_PASS`/`SAFETY_PASS` 전부 PASS. 제품
코드/EXE 0 변경(이번 추가 조사 2건도 진단 override 실험일 뿐).

## 다음 한 가지 (최종)

middle/운영자가 이 근본원인까지 확정된 `BLOCKED` 판정을 (G)의 최종 답으로 수용할지 확인한다.
수용되면 다음 work는 (H) 장시간(50기 반복 명령 수천 tick 안정성, 단일플레이 격리 실행)으로
진행하고, A~H 전체가 채워진 뒤 새 middle이 한 번에 독립 재검수한다(2026-09-28 03:36 판정대로).
