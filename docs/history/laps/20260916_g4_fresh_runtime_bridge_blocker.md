# G4 fresh AI runtime 재진단 (2026-09-16)

## 정정된 결론

처음 관측한 `PS=40/tick=0`, Wine serious-error, `EIP=0x00464F20`
(`FUN_00464EC0`의 DirectDraw surface `Lock`)은 **diagnostic bridge 자체의 재현 가능한
startup blocker가 아니었다**. 당시 파일시스템 여유 공간이 4 MB까지 고갈됐고, 이미 실패한
prefix를 재사용한 대조군도 섞여 있었다.

생성한 private runtime만 삭제해 4.5 GB를 확보한 뒤, 서로 독립적인 새 runtime 두 개를
공식 `runtime_env.py g1-baseline` 경로로 실행했다.

| fresh runtime | `_inmm.dll` SHA | 결과 |
|---|---|---|
| stock | `03192987e9c877cf344874412d2c0e1a80b5d5f8b91f325771e9615feadbf160` | PS9→PS3, scene tick 5, 최종 tick 379 |
| current diagnostic | `592d03ecf4deee17edcbc8de8bb7a42880e5512b34bf19a6245343f0850b3030` | PS9→PS3, scene tick 8, 최종 tick 382 |

두 실행 모두 DirectDraw surface는 PS9 `800×600×8bpp`, PS3 pitch 832로 읽혔고,
cleanup도 PASS했다. 둘 다 마지막 고정 미니맵 클릭만 `FAIL_NO_EFFECT`였으며 이는 startup,
PS3 진입, tick 진행 실패가 아니다. 따라서 **bridge startup blocker 가설은 반증**됐다.

## 남은 실제 blocker

보존 combat capture 도구는 과거 고정 prefix/게임 경로를 import하고 결과를 보호된 메인 repo에
쓰도록 결합되어 있다. 이 도구를 그대로 재실행한 과거 recipe에서만 `0x00464F20` crash가
나왔으므로, 장기 AI capture 전에 다음을 분리해야 한다.

1. patch repo private manifest의 game/prefix를 받는 adapter.
2. 산출물을 `temp/Syw2plus_patch/`에만 쓰는 output override.
3. 공식 PS9→PS3 진입 경로 재사용; legacy desktop/chain bootstrap 중복 제거.
4. 1분 smoke에서 unit samples가 비어 있지 않으면 그때만 장기 반복 비교 허용.

이 문서 뒤 `20260916_g4_ai_smoke_capture.md`에서 공식 baseline 경로에 sampling을 직접 붙여
20초/10 sample/tick 16→616을 수집했다. 따라서 fresh sample blocker는 해소됐고,
장기 반복성·고정 scenario/seed·후보 intervention만 BLOCKED다.

## 보존 evidence

- stock JSON SHA: `bddbf1dcc8784e54fecebb2d9fdee1cdf22702e1603d671046a0322624d1d45c`
- diagnostic JSON SHA: `a5665536d8ae37b341beccffb225ce825f9d9ce0c51f2f9430f77bf59f38bf46`
- temp:
  - `g4_ai/20260916_130928_stock_clean/`
  - `g4_ai/20260916_131049_bridge_clean/`

원본 repo와 원본 게임 데이터는 수정하지 않았고 두 private runtime은 evidence 복사 후 삭제했다.
