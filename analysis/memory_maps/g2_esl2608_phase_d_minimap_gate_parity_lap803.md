# G2 ESL2608 Phase-D 미니맵 gate parity — lap803

## 범위

이번 work는 Phase-D 첫 항목인 미니맵 입력 gate의 G2 변경 영향만 판정했다. 원본·참고
저장소와 네 입력 EXE는 읽기 전용으로 다뤘고, 제품 EXE·bridge·runtime·probe는 수정하지
않았다. 실교전, 미니맵 명령 효과, 고슬롯 초상화는 이 기록의 범위가 아니다.

## 입력 provenance

| lane | baseline SHA256 | candidate SHA256 |
|---|---|---|
| normal | `cade60b2451519ec4e305d91279b1c377cf797c813a939c5b54c2e9b30b176a3` | `83c7df80a3273d95d58e7a493866bbb40ad705d10120bc05db660400961fad60` |
| fixed_start | `f5f816eeb3d8b531ff030f4b43b2f2338ccf0d2257a5684b034e1f8dc8ee1973` | `1bdcadf9edeccc16d92696e580a60fc71f13a13b6bba22cafb8c9f50e749262f` |

네 SHA는 실행 직전 `sha256sum`으로 재확인했다. candidate 파일은 기존 날짜/수정표식
파일을 읽었으며 덮어쓰지 않았다.

## gate 계약과 대조

원본 `objdump -Mintel -D`에서 다음 경로를 확인했다.

- `0x41c450`: mode table word(`0x959af6 + mode_index*15036`) == 1, `0xb631ec == 1`,
  또는 `0x97597c != 0` 중 하나면 1을 반환한다. 모두 거짓이면 0을 반환한다.
- `0x41e43d`: `call 0x41c450` 뒤 `0x41e442: test eax,eax; je 0x41e4c1`로 0일 때
  미니맵 hit-test를 건너뛴다.
- gate 통과 시 `0x41e464: call 0x4516a0`으로 widget hit-test를 호출한다.

네 파일에서 다음 raw 범위의 바이트 digest가 모두 같았다.

| VA 범위 | 파일 바이트 수 | SHA256 | 네 파일 일치 |
|---|---:|---|---|
| `0x41c430..0x41c494` | 101 | `5982cbaa5a1e25e8e5b8abd31c199c9d0c29943cc1e6fefdfffeeab8a33ade37` | PASS |
| `0x41e420..0x41e47f` | 96 | `5b75237642db6e5bd9eff69fbc8191388c55aeef5681252c20109b2107b340a4` | PASS |

따라서 G2 pool/supply 후보는 미니맵 gate·라우터·`0x4516a0` 호출 경로를 바꾸지 않았다.
기존 G5 raw의 강제 `0x97597c=1` 결과는 이 정적 판정의 보조 근거일 뿐, G2 후보의
미니맵 runtime PASS로 승격하지 않는다.

## 판정

`MINIMAP_GATE = ORIGINAL_PARITY / STATIC_ONLY`.

이 결과는 G2 후보가 미니맵 gate를 회귀시키지 않았다는 것만 증명한다. 정상 game-type
경로의 G2 4-way 미니맵 명령 효과와 실교전은 아직 미검증이다.

## 실행 명령

```text
sha256sum <normal-baseline> <normal-candidate> <fixed-baseline> <fixed-candidate>
objdump -Mintel -D --start-address=0x41c430 --stop-address=0x41c495 <each-file>
objdump -Mintel -D --start-address=0x41e420 --stop-address=0x41e480 <each-file>
python3 <read-only byte-slice digest at 0x1c430..0x1c495 and 0x1e420..0x1e480>
python3 checks/context_limits.py
```

fixture는 정적 입력 4개와 원본 SHA뿐이며, 게임/Wine/Xvfb를 실행하지 않았다.
