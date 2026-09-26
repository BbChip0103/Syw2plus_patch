# G2 활성 목록 상대주소 누락과 검은 화면 (2026-09-25)

원본 PE32 SHA256: `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`. 이 주소는 이 버전에만 적용한다. 원본 파일은 읽기 전용이다.

`0x0041CE8E: mov ecx,0x00892410` → `0x0041CE93: call 0x004A3800`. `0x004A3800`은 ECX를 스택에 보관하고 `0x004A39D3`에서 EBX로 다시 읽는다. 따라서 아래 세 displacement는 stock bulk-state base `0x00892410`을 기준으로 한 **활성 유닛 슬롯 목록**의 상대주소다. 기존 절대주소 스캐너는 이를 보지 못했다.

| 명령 VA | 원본 명령 bytes | 의미 | 원본 disp | 새 disp 식 |
|---|---|---|---|---|
| `0x004A39DA` | `66 39 BB F8 34 0E 00` | active count 비교 | `0x000E34F8` | `(active.new_start + 2N) − 0x00892410` |
| `0x004A39E6` | `66 8B B4 53 98 2B 0E 00` | active slot 읽기 | `0x000E2B98` | `active.new_start − 0x00892410` |
| `0x004A3A1B` | `66 3B BB F8 34 0E 00` | active count 비교 | `0x000E34F8` | `(active.new_start + 2N) − 0x00892410` |

원본 active base `0x00974FA8`, WORD count `0x00975908`. N=4001에서 새 base `0x017C41E8`, count `0x017C612A` → displacement count/base/count `0x00F33D1A/0x00F31DD8/0x00F33D1A`. N=10001에서 새 base `0x022979A8`, count `0x0229C7CA` → `0x01A0A3BA/0x01A05598/0x01A0A3BA`. 값은 `full_tail_relocation_storage_layout_v1.layout(N)`로 산출한다.

N=4001 여섯 배열 재배치 후보는 PS3에서 검은 월드였고, active 목록 재배치 fixup만 생략하면 월드가 보였다. 세 상대주소만 추가 수정한 후보 SHA256 `282c5253982bd3bd3e0fc1d7a24dd2c4dab81597afbdfcbb83466bb6908439b3`는 fresh PS3에서 월드·HUD가 보였다. 2606 N=10001 두 후보도 같은 3곳을 새 레이아웃으로 보정한 SHA로 fresh PS3 월드 표시를 확인했다. 캡처/raw는 `docs/history/laps/20260925_direct_g2_esl2606_black_world_incident.md`에 있다.

이 수리는 사용자 요청의 정확한 ESL 2606 두 버전에만 opt-in이다. 오래된 `g2_full_unit_capacity_v1` 후보 해시/안전 pin을 자동 갱신하지 않는다. 초기 화면의 회복은 장기 G2 안정성 증거가 아니다.
