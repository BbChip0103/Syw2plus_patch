# 2026-09-11 | lap 87 | G1-A exact record consumer review

- 실제 provider/model/effort / 지정 역할: 실제 모델 ID는 현재 표면에 노출되지 않아 주장하지 않음 / high 지정 / middle 진단·계획·확인. 게임 코드 hands-on 수정 없음.
- 가설 / 사용자 관찰: lap86의 고정 원본 SHA·old bytes·전체 xref 수·generic callee 경계가 독립 재추출과 모두 일치해야 exact enumeration을 승인할 수 있다.
- 예상 PASS / FAIL 조건: 두 원본의 SHA/byte identity, `.text` 매핑, 유일 caller, 네 field의 모든 read/write/reset와 consumer side-effect가 일치하면 PASS; 하나라도 누락되면 REVISE/ESCALATE한다.
- 변경 파일 / source fingerprint / 커밋: 검수 입력 lap86 history SHA `62f1c463a5ad9b4d6d19b5fcc8b513c38e4c22347a927401ce7264730fe624ea`; `docs/STATUS.md`, `analysis/memory_maps/player_offsets.md`, `loop/ESCALATE_SOL`, 본 이력만 문서 변경. source/tests/binary/fixture/좌표 변경 없음; `LOOP_ALLOW_COMMITS=0`, uncommitted.
- 원본 SHA / 후보 SHA / 환경 / 활성 플레이어 / 지도 / 군대 / fixture: 두 원본 SHA `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`, `cmp` byte-identical; PE32 i386, `.text` VA/raw `0x00401000/0x1000`; 후보·game run·player·map·army·fixture N/A/SKIP.
- 실행 명령 / 로그 / 캡처 경로 및 해시: `sha256sum`, `cmp`, `file`, `objdump -h/-d -Mintel`, `xxd`로 전체 address/offset xref, caller, entry bytes와 `0x004AC3E0/0x004AA820/0x004AE550/0x004A3C10` 경계를 재추출. 신규 log/PNG 없음.
- 측정값 / 판정: 유일 caller 1개, `+0x6B9C` read 3/경계 compare 1, `+0x6BA0` read 3 및 generic queue 경계는 일치. 그러나 누락된 `0x004A31F2` (`[esi+0x6B9A]` reset/write)와 `0x0041EFA5` (`+0x6BA4` read)를 확인해 lap86 reset 2/read 6/complete는 **MIDDLE REVISE / ESCALATE**. production 의미는 UNKNOWN/BLOCKED.
- 검사 / fingerprint: 문서 반영 후 `make check` **127 passed**, Ruff/compileall/mypy/context PASS; `bash checks/safety.sh check` **SAFETY_PASS**; `make doctor` top `ok=true`, original verified. runtime manifest 부재의 하위 `runtime.ok=false`는 예상 경계이며 실행 증거가 아니다. STATUS `18f4a2009a28d527b4ec683f7bd94b8d5672c8a03d7194d8a0f30fcc6eb2410b`, map `c3f7080b64f07538edbc3f15bf53896d4a2b96ff22a3486266562558cb635ce5`, marker `5b70b3f7d39c8457035bfe9ddaca7c2608a09bc3211946fac6bbb12137de7f8a`.
- 회귀 / 남은 위험 / 독립 검수 및 사용자 승인 상태: binary patch/원복 N/A. 실제 입력/runtime, G1 2배 출력·필수5입력, G2~G4 및 사용자 승인은 미검증. 필수 독립 검수가 불일치해 구현·실행 없이 근거를 보존했다.
- 다음 한 가지: 새 Luna/Sonnet5/high work-tier가 누락 2개를 포함한 네 field read/write/reset 전체 표와 consumer branch coverage를 정정하고, 다음 새 Sol/Opus5/high가 독립 검수한다. production click·game run·source/tests/binary/fixture/좌표 변경 금지.
