# G2 ESL 2606 검은 월드 회귀 — 2026-09-25 직접 조사

- 목표: 사용자에게 전달한 `개인유닛1200_공유풀10000_실험.exe` 두 종의 인게임 검은 화면을 재현·격리·수리한다. 이 기록은 G2 전체 합격이 아니다.
- 최초 누락: 전달 전에는 메뉴/정적 검사만 했고 실제 PS3 게임 화면은 확인하지 않았다. 사용자 신고 후 두 파일을 `temp/Syw2plus_patch/g2_esl2606_pool10000/20260925_185704/QUARANTINED_PS3_BLACK/`로 옮겨 `.BROKEN_DO_NOT_USE`를 붙였다. 원본 두 EXE는 변경하지 않았다.
- 입력 SHA256: 일반 `4a03895d8e6690080714fab7e851c3a0e9d44b7cac47fed78fc21a2f5210c6f8`, 시작자리고정 `daf0b6a07f01d04397018924f9dd0c6ff414148c0547adc2d5c9e0b403a58523`, 핀 원본 `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`.
- 실패 후보 SHA256: 일반 `73977e34160caebdbaa7aedff6b50ed4d6a860c582ce74c3eb421829d3672387`, 시작자리고정 `c29d34173dbc428a9dce88ba8c733ba03a18859121d684aebfcd14277efcb3e1`.

## 재현/분리

전부 `tools.runtime_env.prepare()`가 만든 별도 전체 게임 사본·새 Wine prefix·빈 Xvfb에서, 로비 UI 클릭 PS9→PS7→PS5→PS3로 시작했다. `temp/Syw2plus_patch/g2_esl2606_pool10000/20260925_185704/ingame_probe.py`와 각 `local/runtime/g2_esl2606_ingame_*/.../output/g2_ingame_probe.json`에 원시 이벤트·SHA·cleanup 기록을 보존했다. 종료된 재현 실행의 `game/`·`prefix/` 복제본 일부는 디스크 부족으로 제거했지만 raw JSON·로그·캡처는 남겼다.

| 후보 | PS3 화면 | 캡처 |
|---|---|---|
| 미패치 일반 ESL 2606 | 지형·건물·HUD 보임 | `captures/20260925_191948_g2_esl2606_original_control_ps3_scene.png` |
| 최초 배포 일반 10,000 풀 | 월드 검음, UI 일부만 | `captures/20260925_192042_g2_esl2606_pool10000_candidate_ps3_scene.png` |
| stock N=10,001 풀 | 월드 검음 | `captures/20260925_192403_g2_stockN10001_ready_ps3_scene.png` |
| stock N=4,001 풀 | 월드 검음 | `captures/20260925_192702_g2_stockN4001_arrays_ps3_scene.png` |
| stock N=4,001 PE 헤더만 변경 | 월드 보임 | `captures/20260925_193051_g2_stockN4001_B1_header_ps3_scene.png` |
| stock N=4,001 pool/existence/age 3개만 재배치 | 월드 보임 | `captures/20260925_193203_g2_stockN4001_pool3_only_ps3_scene.png` |
| stock N=4,001 여섯 배열 전부 재배치 | 월드 검음 | `captures/20260925_193322_g2_stockN4001_full6_only_ps3_scene.png` |
| 위 후보에서 active 목록 fixup만 생략 | 월드 보임 | `captures/20260925_193521_g2_stockN4001_minus_active_ps3_scene.png` |
| 위 후보에 빠진 상대주소 3곳만 수정 | 월드·HUD 보임 | `captures/20260925_194058_g2_stockN4001_active_rel3_ps3_scene.png` |

검은 후보에서도 존재 배열에는 slot 3997~4000의 4기가 있고, relocated active 목록 count=4·entries `[4000,3999,3998,3997]`였다. 따라서 단순한 유닛 미생성이 아니다. 원본 `.text`의 `0x004A39DA`, `0x004A39E6`, `0x004A3A1B`은 `0x0041CE8E: mov ecx,0x892410` → `0x0041CE93: call 0x4A3800` 경로의 EBX-relative active count/base 접근이다. 기존 절대주소 스캐너가 이 세 displacements `0xE34F8/0xE2B98/0xE34F8`을 놓쳤다. N=4,001의 새 displacements는 `0xF33D1A/0xF31DD8/0xF33D1A`; 직접 3곳만 보정한 일회성 후보 SHA `282c5253982bd3bd3e0fc1d7a24dd2c4dab81597afbdfcbb83466bb6908439b3`이 새 PS3에서 월드 표시를 회복했다.

## 수리 후보/한계

- 첫 수리 구현이 기존 `g2_full_unit_capacity_v1` 바이트를 바꿔 역사적 SHA 핀 두 개를 깨뜨렸다(해당 targeted 검사 18 passed/2 failed). 이를 되돌리고 새 `g2_esl2606_pool10000_owner1200` composer에만 opt-in 3-site fixup을 적용했다. 역사적 SHA 핀은 바꾸지 않았다. 새 빌드가 인게임 확인을 마친 두 파일과 byte-exact 일치한다.
- 그 상태에서 빌드한 새 ESL 후보 SHA: 일반 `d4b14335f695f7478acaafe8d46c52a22892d41c07588ccfd7ef450ce08d8c87`, 시작자리고정 `a1e0b197519e4b76be0eb7779f1be82f99f9abef3baf247d3b519c14e7c8de3e`.
- 두 새 후보 모두 신규 격리 실행에서 PS3 tick 107/109와 건물·지형 표시를 확인했다. 캡처: `captures/20260925_194326_g2_esl2606_repaired_normal_ps3_scene.png`, `captures/20260925_194728_g2_esl2606_repaired_fixedstart_ps3_scene.png`.
- 시작자리고정의 상단 자원 숫자가 안 보인 현상은 미패치 시작자리고정 파일의 별도 신규 격리 실행에서도 동일했다(`captures/20260925_195339_g2_esl2606_fixedstart_control_retry_ps3_scene.png`); 이 비교는 패치 고유 회귀가 아니라는 좁은 판정이다.
- 미검증: 이 두 파일의 8인×전비5000, 10,000 동시 풀 점유, 전투·저장/로드·멀티·장기 안정성. 초기 PS3 화면 PASS를 G2 전체 합격으로 쓰지 않는다.
- 최종 기계 검사: targeted 20 passed/135.63s, `make doctor` 설치/원본 해시 확인, `make check` 877 passed/569.00s + Ruff/compileall/mypy/context PASS, `bash checks/safety.sh check`=`SAFETY_PASS`. 원본·두 ESL 입력 SHA는 종료 전 재확인해 불변이었다.
- 최종 배치: `260921_temp/`에 기존 원본을 보존하면서 `_검은화면수정.exe` 두 이름으로 새 사본을 추가했다. 일반 SHA `d4b14335…08d8c87`, 시작자리고정 SHA `a1e0b197…c8de3e`; 원본/옛 실패 후보를 덮어쓰지 않았다. 전체 경로와 캡처/raw는 `temp/Syw2plus_patch/g2_esl2606_pool10000/20260925_1942_active_rel3_repair/MANIFEST.json`에.
