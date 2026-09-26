# G2 ESL 2606 인게임 명령 회귀 — 2026-09-25 직접 조사

사용자 신고: 검은 화면 수리본으로 게임을 시작한 뒤 마우스·키보드 조작이 안 된다. 이전 배송 판단은 PS3 화면만 확인하고 클릭·키·이동·생산을 검사하지 않은 검증 누락이었다. 이 문서는 그 신고의 좁은 재현이며 G2 목표 합격이 아니다.

## 격리와 비교 범위

- 사용자 폴더 `260921_temp/`의 배포본 두 개는 SHA 확인 후 `temp/Syw2plus_patch/g2_esl2606_pool10000/20260925_1942_active_rel3_repair/QUARANTINED_INPUT_UNRESPONSIVE/`로 옮겨 `.INPUT_UNVERIFIED_DO_NOT_USE`를 붙였다. 일반 `d4b14335f695f7478acaafe8d46c52a22892d41c07588ccfd7ef450ce08d8c87`, 시작자리고정 `a1e0b197519e4b76be0eb7779f1be82f99f9abef3baf247d3b519c14e7c8de3e`. 원본 두 EXE는 수정하지 않았다. **사용자 폴더에는 안전한 10,000풀 대체본이 없다.**
- Fresh 실행 모두 `tools.runtime_env.prepare()`로 별도 전체 게임 사본·새 Wine prefix·빈 Xvfb display를 만들고 게임 메뉴 UI로 PS3에 들어갔다. `temp/Syw2plus_patch/g2_esl2606_pool10000/20260925_1942_active_rel3_repair/input_probe.py`의 XTest 클릭/키, `local/runtime/g2_esl2606_input_*/<run>/output/g2_ingame_probe.json`에 source SHA·tick·선택 슬롯·실제 UnitStruct XY·자원/예약·포커스·cleanup을 남겼다. 새 캡처는 전부 공유 `temp/Syw2plus_patch/captures/YYYYMMDD_HHMMSS_*`에 있다.
- 모든 probe의 `cleanup_ok=true`와 잔여 prefix PID 0을 확인한 뒤 **이번 probe가 소유한** `game/`·`prefix/` 복제본 12쌍만 디스크 확보를 위해 삭제했다. manifest·raw JSON·로그·캡처는 보존했다. 다른 세션 runtime에는 손대지 않았다.
- 원본 일반/패치 일반/패치 시작자리고정의 초기 입력은 모두 유닛 클릭 `selection_count 0→1`, `ESC` 뒤 PS `3→23`이었다. 따라서 **마우스/키보드 이벤트 자체가 전혀 전달되지 않는다는 좁은 가설은 Wine 재현에서는 틀렸다.** 그러나 이 검사는 플레이 가능한 명령 수락을 증명하지 않는다.

## 실제 이동·생산 반례

같은 logical 클릭 `worker=(418,320)`, 오른쪽 이동 대상 `(550,350)`, 본진 `(408,242)`, 진영3 생산 아이콘 `(668,540)`을 썼다. 5초 동안 tick 약 175가 진행됐다. 좌표는 선택된 실제 유닛 슬롯의 `UnitStruct+0x2A2/+0x2A4`를 읽었다. 예약은 PlayerStruct `+0x1C`이다.

| 실행 출력 디렉토리 `local/runtime/` 아래 | 일꾼 슬롯/XY 전→후 | 본진 슬롯/생산 결과 | 판정 |
|---|---|---|---|
| `g2_esl2606_input_fixed_control_move/` (미패치 시작자리고정) | `1198`, `(92,21)→(94,19)` | `1199`, 진영3 식량 `5000→4200`, 예약 `0→10` | 대조 양성 |
| `g2_esl2606_input_n4001_move/` (진단 후보 `ca082732…d231785`) | `3999`, `(92,21)→(94,19)` | `4000`, 진영3 동일 차감·예약 | 4095 이하 양성 |
| `g2_esl2606_input_n4097_move/` (`5d282637…e468bb`) | `4095`, `(142,42)→(144,40)` | `4096`, 진영2 클릭 무변화(아이콘 의미 미확정) | 이동 경계 양성 |
| `g2_esl2606_input_n4098_move/` (`d9115c51…4e3`) | `4096`, `(92,163)` 그대로 | `4097`, 진영3 식량·예약 무변화 | 이동·생산 음성 |
| `g2_esl2606_input_n8001_move/` (`237c7544…3c8`) | `7999`, `(21,92)` 그대로 | `8000`, 진영2 클릭 무변화(아이콘 의미 미확정) | 이동 음성 |
| `g2_esl2606_input_candidate_move2/` (배포 일반 SHA) | `9999`, `(142,142)` 그대로 | `10000`, 진영1 클릭 무변화(아이콘 의미 미확정) | 이동 음성 |
| `g2_esl2606_input_fixedstart_move/` (배포 시작자리고정 SHA) | `9999`, `(92,21)` 그대로 | `10000`, 진영1 클릭 무변화(아이콘 의미 미확정) | 이동 음성 |

진영별 생산 아이콘이 다르므로 진영1·2의 무변화를 독립 생산 실패로 단정하지 않는다. 진영3의 같은 아이콘에서는 미패치와 N=4001이 생산 예약으로 이어지고 N=4098이 이어지지 않았다. N=4098은 worker slot4096을 선택하고 목적지 깃발을 표시했지만 `unit_command=1`과 XY가 그대로였다. 포커스는 실행 내 동일, PS3 tick은 계속 증가, cleanup에서 잔여 Wine PID 0이었다. 이 범위의 관찰만으로 네이티브 Windows 전 경로·8인 전투·장기 안정성까지 증명하지 않는다.

## 원인과 조치

정확한 원본 `.text`에서 명령 유닛을 WORD에 압축할 때 `0x004AE613: shl edx,12`와 `0x004AE619: mov WORD [edi],dx`, 수신 시 `0x004AE9D2/0x004AEA35/0x004AEB53/0x004AEBC8: and ...,0x0FFF`를 확인했다. 슬롯 4096 이상은 명령 수신에서 잘린다. 이 바이트는 배포 N=10001 후보에서도 미변경이다. 근거와 다른 12비트 사용의 미확인 범위는 `analysis/memory_maps/g2_esl2606_command_slot12_boundary_20260925.md`에 기록했다. 앞서 고친 활성 목록 상대주소 3곳은 월드 표시만 회복시켰다.

`patches/population/g2_esl2606_pool10000_owner1200.py`의 `create_copy()`를 fail-closed로 바꿔 알려진 플레이 불능 10,000풀 EXE의 신규 배포를 차단했고, `test_g2_esl2606_pool10000_owner1200.py`에 거부·무출력 회귀를 추가했다. 순수 `build_candidate()`는 과거 해시 재현/분석을 위해 남기되 report에 `BLOCKED_12_BIT_COMMAND_SLOT`을 명시한다. 기존 격리 후보는 복원·재배포하지 않는다.

**남은 일 / BLOCKED(12-bit command format):** 실사용 풀 10,000을 달성하려면 12비트 명령 식별 형식과 관련 producer/consumer, 지도 셀·저장/로드·멀티 호환성을 설계·패치·회귀검증해야 한다. 단순 숫자 교체 또는 현재 파일 재배포는 금지. 목표 8인×전비5000·풀/메모리·저장/멀티는 여전히 미검증이다.
