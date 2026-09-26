# G1 W50 DxWrapper D3D9 호출 계층 — lap598 독립 검수

## 고정 입력

- 원본 EXE SHA256: `b56986e018b43293be8d9945521d145bba8dbe4e49fe70c6b6488b8c9c08a8ac`
- DxWrapper SHA256: `96c443193bad8794ebf04738566e092f8b34ae4541cb2433fd0708d49edbe8fe`
- Wine 9.0 `d3d9.dll` SHA256: `97d381c22950ac4456fd61defed8bb36b30d8dbce2d1b3433ecd993a092eeae1`
- A1/A3 final trace SHA256: `2b853e08…1982e9` / `4c8b881d…a19b9`

## 확인한 호출 계층

| 층 | preferred VA / RVA | lap597 loaded VA | 의미 | 근거 |
|---|---:|---:|---|---|
| top source | `0x101F17F8` / `0x1F17F8` | `0x771917F8` | 설정에 따라 내부 redirector를 고르는 source | `0x100DE5A2..0x100DE5D9` |
| top cache | `0x101F23B4` / `0x1F23B4` | `0x771923B4` | `0x100C18C3`이 top source를 복사하는 lazy cache | `0x100C16B3`, `0x100C18C3..0x100C18D7` |
| redirector | `0x1000A750` / `0x0000A750` | `0x76FAA750` | DxWrapper 내부 `Direct3DCreate9` redirector; native export가 아님 | loaded base `0x76FA0000` + RVA `0xA750`; `0x100DE5A9`가 이 주소를 선택 |
| inner source | `0x101BAC60` / `0x1BAC60` | 아직 raw 미수집 | underlying D3D9 function source | `0x100DE65E..0x100DE66D`, `0x1000A969` |
| inner cache | `0x101BACC0` / `0x1BACC0` | 아직 raw 미수집 | redirector가 실제 호출하는 lazy cache | `0x1000A87D`, `0x1000A8F8..0x1000A8FE` |
| inner guard | `0x101BACC4` / `0x1BACC4` | 아직 raw 미수집 | inner source→cache 초기화 guard | `0x1000A94F..0x1000A99D` |

A1/A3 raw의 `source=cache=0x76FAA750`는 loaded DxWrapper base `0x76FA0000` 안의 RVA `0xA750`과 정확히 같다. 반면 같은 run의 `/proc/<pid>/maps`에서 Wine `d3d9.dll`은 `0x76D60000`에 매핑되며, 해당 파일 export table의 `Direct3DCreate9` RVA는 `0x3A40`이다. 따라서 그 run에서 기대되는 native export VA는 `0x76D63A40`이고 `0x76FAA750`와 다르다. A3의 `native_owner_for()` 거부는 올바른 fail-closed다.

## lap598 판정과 다음 검증

- lap597 A1/A3 raw 무결성 및 A3의 factory/device zero window 포착은 `ACCEPT`한다.
- W50의 “top source/cache가 loaded `d3d9.dll!Direct3DCreate9`다”라는 전제는 `REFUTED`한다. 판정은 `REJECT / BLOCKED(plan_contract)`이며 G1 불가능성이나 제품 결함 판정이 아니다.
- strategy가 G1을 계속하면 다음 work는 게임 재실행 전에 현행 A1 audit에 inner source/cache/guard 값, 각 pointer owner/path, `GetProcAddress(d3d9.dll, "Direct3DCreate9")`를 추가한다. fresh 1회에서 inner source/cache가 같은 native export이고 factory/device가 0인 창이 확인될 때만 별도 opt-in CAS 후보를 검토한다.
- top cache의 DxWrapper redirector를 허용하는 대안은 native-owner 성공 계약을 바꾸므로 middle이 승인하지 않는다. guard 완화, W51, overlay, 기존 run 재해석은 금지한다.
