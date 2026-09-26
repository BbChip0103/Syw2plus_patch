# 2026-09-11 | lap 149 | 목표 G1

- 실제 provider/model/effort / 지정 역할: Claude Code, 세션 표면 모델명 `claude-opus-5`, 지정 역할은
  중간 tier(진단·계획·확인). 실제 effort attestation은 현재 표면에서 확인할 수 없어 추정하지 않는다.
  게임 코드 hands-on 수정은 하지 않았고 문서만 작성했다.
- 가설 / 사용자 관찰: lap148 `loop/ESCALATE_SOL`이 요청한 독립 검수. 검수 가설은 "config-only 2×
  후보의 presentation 층은 정상이고, PS9 정체의 원인은 wrapper가 아니라 하네스가 클릭 좌표를
  논리좌표에서 물리좌표로 ×2 선(先)변환한 입력 좌표 계약에 있다"이다.
- 예상 PASS / FAIL 조건: (a) lap148이 기록한 4개 증거 해시가 재계산으로 일치, (b) 적용된
  `dxwrapper.ini`가 후보 SHA와 byte 일치하고 3개 변경이 기록된 offset/old/new와 일치,
  (c) raw trace가 게임 논리 surface를 800×600으로 유지했음을 보이면 escalation 1번의 앞부분은
  PASS, (d) 입력 결선 지점은 trace에 입력 관측이 하나라도 있어야 사실로 판정 가능하고, 없으면
  UNKNOWN으로 남기고 추론과 분리한다. 하나라도 어긋나면 승격하지 않는다.

## 재계산한 사실 (facts)

- 증거 해시 4개 전부 일치:
  `evidence.json df460618508488879b5acc54779ac8393833493c701a4f49fc130394a0456a94`,
  `verdict.json e2855f1721dcc6fb6674ed7018325d3216ab067500760535454c5a4ead803e03`,
  `provenance.json df2599d6f72487a3b9a78e7cb7ae6d350b1b9fbd20d180643b6266c82a80acae`,
  `trace_raw.jsonl 4b8bb4a02acb90994daa0d26305bcb084cb2798f1c6382ca1cff3f39791b75a3`.
  추가로 `trace_install.jsonl 2ffdd4a689d29fbd0f024de213cda6541811c6f0f54853787d50e6745f390e07`은
  evidence 내부 `trace_gate.install_trace_sha256` / `owned_win32_process.trace_sha256`과 일치한다.
- 적용 config 일치: `dxwrapper.ini.applied` 실측 SHA는 후보
  `f0ce9e649a48a79d427cb218f7952de50095091b8bba4e68ea7dfe8922566785`와 byte 일치한다. 기록된 변경 3개는
  offset 211 `LoadCustomDllPath = syw2x.dll` → 공백, offset 1590 `DdrawIntegerScalingClamp 0`→`1`,
  offset 1622 `DdrawMaintainAspectRatio 0`→`1`뿐이고, 파일 본문도 `Dd7to9=1`,
  `DdrawUseNativeResolution=1`, `FullScreen=0`, `DdrawOverrideWidth/Height=0`로 확인된다.
- 원복/pin 재확인: private copy의 `dxwrapper.ini`는 old `918e704346c20a0393a32501844b64536d7a233163c26305a332f8e56aeea5a2`로
  byte-exact 복구되어 있고, `ddraw.dll 3bc7230d...bd19`, `dxwrapper.dll 96c44319...be8fe`,
  `syw2plus_original.exe b56986e0...a8ac`가 pin/원본과 일치한다.
- **게임 논리 구성은 바뀌지 않았다**: `trace_raw.jsonl` 354 events 중 `set_display_mode` 11건은
  800×600×8bpp와 640×480×16bpp를 번갈아 요청하고 마지막은 800×600×8bpp다. primary surface는
  `flags=33/caps=568/backbuffer_count=1`로 800×600 논리면이며, 오프스크린도 800×600·832×600·
  800×203 등 원본 치수 그대로다. wrapper는 게임 내부 구성을 확대하지 않았다.
- **X11 표시 층은 의도대로 2×였다**: root 1600×1200, content window `0x800103` = (0,0) 1600×1200,
  border 0, `window.scale=[2.0,2.0]`, 스크린샷 dimensions 1600×1200 /
  `logical_content_size=[800,600]` / `physical_content_size=[1600,1200]` / `scaled_2x=true`.
  letterbox 오프셋은 없다. 즉 800×600 논리면이 1600×1200 client에 정수 2배로 표시됐다.
- **게임은 살아 있었다**: program_state는 40→60→180을 거쳐 9로 안정됐고, PS9에서 마지막까지
  `blt_fast` 256건이 연속 기록됐다. 정지/크래시/포인터 손상 증거는 없다.
- **입력은 정확히 1회, ×2 선변환으로 전송됐다**: `inputs[0] = {tag: menu,
  logical_content:[184,560], physical_root:[368,1120], scale:[2.0,2.0], result:"SENT"}`.
  `result`는 lap146의 `"PASS"`와 달리 `"SENT"`이며 효과 확인이 아니다.
- **wrapper는 커서 훅을 걸었다**: 같은 run의 `game/dxwrapper-syw2plus_original.log`(19:23:19~22)에
  `m_IDirectDrawX::InitDdraw Hooking mouse cursor!`가 있고, 같은 로그에
  `Hook::HotPatch Error: 'GetDeviceCaps' is not patch aware at addr=7A6464A0`라는 훅 설치 실패도 1건 있다.
  또한 `IID_IAMMediaStream` 질의가 5회 있어 기동 초기 동영상 재생 구간이 존재한다.
- **대조군(lap146 PASS)의 기하**: `local/runtime/20260911_184524_3746509_0`의 content child
  `0x800142` = (0,0) **800×600**, `content_crop=(0,0,800,600)`, 클릭 root (184,560) → PS9→PS7 PASS.
  두 run 모두 게임 창이 root 원점·border 0이므로 **root 좌표 = client 좌표**가 항등이다.
  따라서 lap146 대비 입력 경로에서 바뀐 단 하나의 변수는 좌표 ×2 선변환이다.

## 판정 (inference, 사실과 분리)

- escalation 1번 앞부분 → **PASS(사실)**: pinned wrapper + config-only 프로필은 800×600 논리
  surface를 1600×1200 client에 2배로 표시했다. 이것은 표시층 관측이며 제품 G1 승인이 아니다.
- escalation 1번 뒷부분(물리→게임 입력 결선 단절 지점) → **UNKNOWN(사실로는 판정 불가)**:
  진단 bridge는 DirectDraw만 계측하고(`direct_draw_create_ex`/`set_display_mode`/`create_surface`/
  `blt`/`blt_fast`/`get_surface_desc`/`surface_release`/`install`) 커서·메시지·버튼 이벤트를 전혀
  기록하지 않는다. 게임이 실제로 받은 좌표를 보여주는 증거가 0건이므로 단절 지점을 사실로 지목할 수 없다.
- 다만 좌표 계약 결함은 **사실로 좁혀진다(추론)**: 게임의 히트테스트 공간은 800×600이고
  목표점은 (184,560)이다. wrapper가 들어오는 좌표를 논리공간으로 역변환하지 않으면 게임은
  y=1120(유효범위 0~599 밖)을 보고 어떤 메뉴도 맞지 않는다. 역변환한다면 (368,1120)은 이중 변환되어
  (92,280)이 되고 역시 목표 메뉴가 아니다. **두 해석 모두 같은 결론** — ×2 선변환은 어느 쪽이든 틀렸다.
- 경쟁 가설 H2(좌표와 무관하게 입력이 게임 창에 도달하지 못함)는 배제되지 않았다.
  찬성 증거: `result:"SENT"`뿐이고 수신 확인이 없다, 같은 프로필에서 `GetDeviceCaps` 훅 설치가 1건 실패했다.
  반대 증거: 같은 Wine/Xvfb/XTest 하네스가 lap146에서 동일 게임에 입력을 성공시켰다.
- 경쟁 가설 H3(메뉴 핫스팟 이동)은 약하다. 게임 논리면과 `source_composition`이 800×600으로 불변이다.
- 경쟁 가설 H4(동영상 등 비대화 구간에 클릭 투입)도 배제되지 않았다. 찬성: `IAMMediaStream` 질의와
  11회 모드 전환, 마지막 질의(19:23:22.148)와 스크린샷(19:23:22.796) 간격이 0.65초다.
  반대: lap146도 동일한 PS9 게이트를 썼고 trace 말미는 PS9 정상 프레임 루프다.

## 이번 검수가 찾아낸 lap148 증거의 결함

1. **실패한 하네스가 보존되지 않았다.** provenance의 command는 "inline config-only 2x runtime"이고
   `harness_sha256`은 `tools/runtime_env.py`(`2609e7c2...c896a2`, 현재 파일과 일치) 하나뿐이다. 그런데
   커밋된 `g1-presentation-trace`는 `tools/runtime_env.py:2372-2373`에서 content가 정확히 800×600이
   아니면 `RuntimeSafetyError`를 던지므로 lap148을 실행한 코드일 수 없다. 실제 입력 시퀀스(버튼
   press/release 간격, 사전 포커스/활성화 여부, 클릭 후 대기 시간)는 복원 불가다. 재현 불가 증거다.
2. **입력 관측이 0건이다.** 위 UNKNOWN의 직접 원인이며, 다음 run에서도 고치지 않으면 같은 질문에
   또 답하지 못한다.
3. 클릭 이후 스크린샷이 없고 before/after 이미지 대조가 불가능하다.
4. run이 timeout 예산 경계에서 끝났다(`elapsed_seconds=90.218`, timeout 90). 클릭 후 실제 대기
   시간이 얼마였는지 증거가 없다.
5. 유일한 PNG는 `/home/dev_00/sharedfolder/260320_Syw2plus/temp/`에 있고 이번 세션의 샌드박스가
   해당 경로 읽기·해시를 거부해 **이번 검수에서 확인하지 못했다**(SKIP). lap148 기록의 PNG 해시
   `aac4073b...2717`은 재계산되지 않았다.

- 변경 파일 / source fingerprint / 커밋(없으면 uncommitted): 이 history 파일,
  `docs/STATUS.md`, `docs/work/active/G1_INPUT_COORDINATE_CONTRACT_HANDOFF.md` 신규,
  `loop/ESCALATE_SOL` 제거(원문은 아래에 보존). 모두 uncommitted, 커밋 없음.
  게임/원본/참고 저장소, 제품 EXE·DLL·config, baseline/golden은 전혀 건드리지 않았다.
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 검수 대상은 lap148 산출물이며
  새 run을 열지 않았다. 원본 `b56986e0...a8ac`, 후보 config `f0ce9e64...6785`,
  run `local/runtime/20260911_191958_4086515_0`, fixture는 default two-player random,
  synthetic/memory_writes/control_bridge/resource_grant=false, diagnostic_bridge=true. G2~G4는 N/A.
- 실행 명령 / 로그 / 캡처 경로 및 해시: 읽기 전용 재계산만 수행했다 —
  `sha256sum evidence.json verdict.json provenance.json trace_raw.jsonl trace_install.jsonl dxwrapper.ini.applied`,
  `sha256sum game/{dxwrapper.ini,ddraw.dll,dxwrapper.dll,syw2plus_original.exe}`,
  `sha256sum tools/runtime_env.py`, `grep`/`jq`로 trace 이벤트 집계와 evidence 스칼라 덤프,
  `local/runtime/20260911_184524_3746509_0`의 lap146 evidence 대조.
  새 PNG/새 run/새 프로세스는 없다.
- 측정값 / 판정 (PASS, FAIL, SKIP, UNKNOWN):
  증거 해시 5/5 **PASS**, config byte 대조 **PASS**, 원복/pin 4/4 **PASS**,
  논리 surface 800×600 불변 **PASS**, 표시 2× **PASS**, PS9 프레임 루프 생존 **PASS**,
  입력 결선 단절 지점 **UNKNOWN**(관측 부재), 좌표 계약 결함 **CONFIRMED-BY-ELIMINATION**,
  PNG 재계산 **SKIP**(샌드박스 거부), `make check`/`checks/safety.sh` **SKIP**(이번 세션에
  `make`·`python` 실행 권한이 없고 비대화 세션이라 승인 불가. 과거 lap148의 177 passed를 현재
  성공으로 승격하지 않는다).
  종합 판정: **MIDDLE CONFIRM PASS (증거 검수) / FAST SKIP / DIRECTION = 입력 좌표 계약 수리**.
  프로필 폐기나 Astra 상위 분기는 불필요하다고 판정한다. 표시층이 목표대로 동작한 이상 프로필은 유지한다.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: 제품 EXE/DLL 패치 없음, G1 승인 없음,
  사용자 마일스톤 승인 없음. lap148의 PS9 정체와 final summary/owned-close 미도달은 현재 프로필의
  실패 증거로 그대로 보존했고, 800×600 진단 성공이나 root 크기를 G1 PASS로 승격하지 않았다.
  남은 위험: H2(입력 전달 경로)와 H4(비대화 구간 클릭)가 배제되지 않았고, 다음 run이 좌표만 바꾸고도
  실패하면 이 둘이 주 용의자가 된다. 이번 lap의 Fast 미실행은 다음 lap이 반드시 메워야 한다.
- 다음 한 가지: 아래 handoff 카드대로 work tier가 `tools/runtime_env.py`의 입력 좌표 계약을
  1개 변경으로 수리하고, 같은 후보 프로필에서 **선변환 없는** 논리좌표 클릭 1회로 PS9→PS7을 시험한다.

## 처리한 `loop/ESCALATE_SOL` 원문 보존 (lap148 작성, lap149에서 처리 완료)

```
# ESCALATE_SOL — lap 148 G1 config-only integer-2x candidate

## 상태

필수 G1 runtime gate가 BLOCKED되어 이번 세션을 종료한다. 같은 profile을 재실행하거나 좌표를
보정하거나 다른 설정/DLL/code를 추가하지 않는다. 현재 private run/prefix/display는 cleanup
완료 상태이며 raw evidence와 적용 후보를 보존했다.

## 근거

- 원본 EXE: `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`
- pinned `ddraw.dll`: `3bc7230d1a6023a8fc0ea52b18d7edda94fcb4c0ae3d178f6e1577d68a62bd19`
- pinned `dxwrapper.dll`: `96c443193bad8794ebf04738566e092f8b34ae4541cb2433fd0708d49edbe8fe`
- config old: `918e704346c20a0393a32501844b64536d7a233163c26305a332f8e56aeea5a2`
- config candidate: `f0ce9e649a48a79d427cb218f7952de50095091b8bba4e68ea7dfe8922566785`
- profile: `LoadCustomDllPath` blank, `Dd7to9=1`, `DdrawUseNativeResolution=1`,
  `DdrawIntegerScalingClamp=1`, `DdrawMaintainAspectRatio=1`.
- fresh run: `local/runtime/20260911_191958_4086515_0`; env `WINEDLLOVERRIDES=ddraw=n,b`.
- window evidence: private root/client both 1600×1200, scale 2.0×2.0.
- failure: scaled menu input was sent once but state stayed PS9; PS7 and PS3/input/capture
  gates were not reached. Treat root cause as UNKNOWN until raw trace/log review.
- cleanup: owned launchers stopped, Xvfb stopped, prefix processes 0, global kill false, `ok=true`.
- evidence: `local/runtime/20260911_191958_4086515_0/output/g1_config_2x/`.

## 승격 작업자가 이어서 검증할 것

1. raw trace/log와 exact config manifest를 독립 대조해 wrapper가 실제 800×600 logical surface를
   1600×1200 client에 표시했는지, 그리고 XTest physical→game input 좌표 결선이 어디서 끊겼는지
   사실과 추론을 분리해 판정한다.
2. 이번 run의 PS9-only 상태, final summary/owned-close 미도달을 현재 profile의 실패 증거로 보존하고
   기존 800×600 진단 성공이나 root 크기를 제품 G1 PASS로 승격하지 않는다.
3. 다음 방향(입력 계약 수정, profile 폐기, 또는 Astra의 상위 분기)은 독립 중간/상위 판정으로
   정한 뒤에만 새 run을 승인한다. 이 lap에서는 재실행하지 않는다.
```

세 항목 모두 이번 lap에서 처리했다(1 = PASS + UNKNOWN 분리 판정, 2 = 실패 증거 보존 확인,
3 = 방향을 "입력 좌표 계약 수리"로 결정). 따라서 `loop/ESCALATE_SOL`은 제거한다.
