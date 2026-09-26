# lap150 `loop/ESCALATE_SOL` 원문 보존 (lap151 middle이 해소 후 archive)

lap151 middle tier가 아래 escalation의 ①(source-root 계약 판정)을 해소하고
`loop/ESCALATE_SOL`을 비웠다. 판정 근거는
`docs/history/laps/20260911_lap151_middle_g1_source_root_contract_confirmation.md`.
②③(runtime 1회 실행, milestone 금지)은 해소되지 않았고 work tier로 이월했다.
원문은 삭제하지 않고 아래에 그대로 보존한다.

---

# ESCALATE_SOL — lap 150 G1 input-coordinate contract runtime blocked

## 상태

승인된 G1 단일 변경과 Fast 검증은 완료했지만 fresh runtime의 필수 `prepare`가
예상 밖으로 실패했다. 다른 source 경로, 기존 copy/prefix/display, 좌표, profile 또는
runtime을 재시도하지 않는다. 현재 코드 변경과 fresh build 산출물은 보존한다.

## 근거

- 보호 원본에 기대한 SHA: `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`
- 이번 변경 source SHA:
  - `tools/runtime_env.py` `69d0c54da7da06849ef8a6929ad7e6fec43bf12b87fefb6ba3e605cee240a296`
  - `tools/check_g1_presentation_trace.py` `22003230b08c12749b592e609831149fe3451751322d714bc5d22cffe519b188`
  - `tests/test_runtime_env.py` `4206eee7003163bb823b1a5b9de95e379c7baddcc339e9dd97ce9e31187e128b`
  - `tests/test_g1_presentation_trace.py` `86f32f6305f65162279c4cb9f192b11de0e7ba62fac2d191ecb0f8bcdb527bf9`
- fresh parent: `/tmp/syw2plus_lap150.uf0IeV`
- fresh helper SHA: `9de316b5dce92c8ddbb142dc7d04d7a46a144711286ce06ab5b6391d7de6be59`
- fresh close target SHA: `36220451ed3af2ef0d1cc363d34f03ac7534c0e654e91a209003229d69ac330b`
- fresh diagnostic bridge SHA: `5971ef5c02d5d816ad5f9ea98cf858b1a3c9cd5e152a347203b144b506ee09bd`
- 빌드: helper/bridge 모두 RC0; bridge compiler warning은 기존 경고이며 빌드 산출물은 생성됐다.
- prepare 명령:
  `.venv/bin/python tools/runtime_env.py prepare --source /home/dev_00/sharedfolder/260320_Syw2plus/Syw2plus_re --bridge /tmp/syw2plus_lap150.uf0IeV/bridge/_inmm.dll --timeout 60`
- prepare 결과: RC2, `missing or linked original executable: /home/dev_00/sharedfolder/260320_Syw2plus/Syw2plus_re/syw2plus_original.exe`
- 읽기 전용 확인: 실제 파일은 `/home/dev_00/sharedfolder/260320_Syw2plus/Syw2plus_re/Syw2plus/syw2plus_original.exe`에 중첩되어 있다. source 경로 의미를 바꾸거나 nested path를 자동 선택하는 것은 이번 work 승인 범위를 넘는다.
- 실행 fixture/prefix/display/game copy: 생성되지 않음. EXE/DLL/assets/config/baseline/golden은 변경하지 않았다.

## 이번 lap 검증

- G1 runtime 코드: client `(800,600)` 또는 `(1600,1200)` 허용, logical surface 800×600 및
  마지막 `set_display_mode`/primary descriptor 증거 검사, 논리좌표 `(184,560)` 무선변환 입력 기록.
- targeted tests: `80 passed`.
- `make check`: `179 passed`, Ruff PASS, compileall PASS, mypy PASS, CONTEXT_PASS.
- `bash checks/safety.sh check`: `SAFETY_PASS`.

## 승격 작업자가 이어서 검증할 것

1. 중간 tier가 `runtime_env.prepare`의 source root 계약과 중첩된 실제 원본 위치를 독립 판정하고,
   올바른 source 입력을 명시적으로 승인한다. 임의로 `/Syw2plus_re/Syw2plus`를 대체 입력으로
   재실행하지 않는다.
2. source 계약이 확정된 뒤에만 새 helper/bridge와 새 private copy/prefix/display를 다시 만들고,
   `g1-presentation-trace`를 정확히 1회 실행한다. 이번 lap에는 게임 입력이 전혀 실행되지 않았다.
3. runtime PASS/FAIL 전에는 G1이나 milestone을 마감하지 말고, 이 lap의 Fast PASS와 prepare BLOCKED를
   제품 완료로 승격하지 않는다.
