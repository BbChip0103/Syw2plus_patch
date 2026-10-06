# lap893 — P4b-S 구현 보존·실행 전 안전 수리 handoff

- 시각: 2026-10-03 16:47 KST. 기존 lap892 승인 카드의 P4b-S 구현을 계속한다. 새로운 제품 분기/사용자 승인 요청이 아니다.
- 실제 worker: Codex `gpt-6-luna`/high/Fast, PID381850. 독립 native read-only evidence slice `snapshot_abi_probe`: Codex `gpt-6.1-sol`/high. 설치된 역할 selector 없는 native 표면의 bounded 자료 검수이며 Architect/Ralplan 권한·최종 수용을 주장하지 않는다.
- 해당 native 검수는 소스/문서 수정·빌드·실행 없이 frozen C/h와 원본 old bytes만 읽었다. sole implementation writer를 유지했다.
- frozen C SHA `f184dc35986475e7397c5561d0e3db76b74515ce6a40615d255f3df9bfd1eff2`, 공유 temp `20261003_1641_snapshot_abi_probe/`. 종료 직전 live C SHA `6770807b15f4a9658ff13987928194916dbb28e4f6ec8682eb4b69eba95710f7`; 아래 결함은 live에서도 재확인했다.
- 두 callsite의 old bytes 및 원본 SHA MATCH. six ranges/header 수치 일치: payload 2,378,704 bytes, header128, total2,378,832. 이것은 구현 전체 승인/실행 증거가 아니다.

## 다음 work의 필수 수리·검증 (기존 P4b-S 범위)

1. `patch_call`의 보호 복원 실패 rollback에도 cache flush와 보호 복원 처리를 명시한다. `CALL_B` 설치 실패 후 `CALL_A` rollback, detach 모두 `VirtualProtect` 성공을 확인하기 전 `.text`를 쓰지 않는다. 실패 시 부정확한 원복/성공 주장을 하지 않는다.
2. detach/rollback은 `E8`만 보지 말고 자신이 설치한 5바이트 rel32 전체와 일치하는 소유 hook만 복원한다. 다른 hook을 덮지 않는다. 설치 단계·부분 실패·cache flush·보호 실패·소유권 충돌 회귀 증거를 남긴다.
3. 컴파일된 두 naked wrapper 및 `call_update` thunk를 disassemble해 원본 호출의 stack/register/flags 반환 의미를 보존하는지 확인한다. native 검수는 stack balance만 확인했으며 thunk ABI는 미증명이다. 불필요한 compiler thunk가 있으면 실무 writer가 최소 수정한다.
4. 승인 카드는 preallocated buffer를 요구한다. 현재 per-target HeapAlloc을 설치 시 선할당으로 맞춘다. runtime divergence를 발견했다는 뜻은 아니다.
5. 남은 DLL install/detach integration, host parser/full-field preservation, honest acquisition regressions를 완료한다. 기존 source 변경을 지우거나 새 설계로 되돌리지 않는다. 필수 targeted/lint/typecheck와 ABI/안전 증거 뒤 기존 E1~E4 격리 runtime으로 바로 진행한다. 안전한 snapshot2회 pair 연속 증거 및 새 middle 검수 후 C로 이어간다.

## 세션 회수와 판정

- 안전상 불완전 구현을 runtime 전에 수리하도록 exact argv/PID를 확인한 Codex worker381850에만 SIGINT. 다른 세션/process/global kill 없음. child game/probe/build/check는 당시 없었다.
- lap893 agent exit1, outer runner max-laps(1) exit0. 둘을 PASS로 쓰지 않는다. 변경파일은 그대로 uncommitted 보존했다. 게임 runtime·E1~E4·Fast·B'/G1 PASS 없음. 원본/golden/validator/pins/기존 raw 변경0, commit0.
- 다음 fresh Luna work를 즉시 연결한다. 사용자 G1 달성까지 자율 지속 및 약10분 보고 지시는 유지한다. 내부 회수/수리 handoff이며 G1 중단/재허가 대기가 아니다.
