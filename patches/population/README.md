# 원본 전비 5000 실험 패치 — 2026-09-10

**가능성은 원본 게임 실행으로 확인했다. 배포용 완성 패치는 아니다.**
전비는 유닛 수가 아니다. 원래 개인 개수 상한 250과 공유 슬롯 제한은 변경하지 않는다.

## 안전한 복사본 생성 / 원복

```sh
python3 patches/population/fixed_supply_5000.py create-copy \
  Syw2plus/syw2plus_original.exe /path/to/private/game/supply5000.exe
python3 patches/population/fixed_supply_5000.py restore /path/to/private/game/supply5000.exe
python3 -m pytest -q patches/population/test_fixed_supply_5000.py patches/resolution/test_qhd_probe.py
```

정확한 원본 SHA256만 허용하며 입력 EXE를 변경하지 않는다. 출력은 새 경로여야 한다.
`.original` 백업과 패치 결과를 검증한 뒤에만 원복한다. 다른 버전이나 QHD 패치 완료본을
이 CLI의 입력으로 주면 거부한다. 게임 데이터/저장 파일도 별도 복사본에서 실험한다.

초기값과 재계산 함수 두 명령 범위에서 **실제로 달라지는 바이트는 5개**다.
영웅 보너스를 더한 값이 아니라 최종 상한을 **고정 5000**으로 만든다.
패치 자체에는 진단 DLL이 필요 없다. 재현 실험은 기존 Wine/DirectDraw 환경과
별도로 계측한 `_inmm.dll`을 사용했다.

## 실제 확인한 동작

- 원본 게임의 전비 재계산 후에도 상한 5000 유지.
- 원본 생성/배치 함수를 통해 실제 전비 합계 4990인 144개체를 준비.
  마지막 일꾼을 원래 생산 절차로 완성하여 **145개체, 합계 5000**에 도달.
- 5000에서 추가 생산 거부와 실제 “전비가 부족합니다” 표시.
- 완성 군대 저장/로드, 생산 중 저장/로드 후 정확히 한 번 생산 완료.
- [QHD 실험 패치](../resolution/README.md)와 합친 동일 원본 게임에서도 위 동작 확인.
  실제 렌더러 2560×1440, pitch 2560, 원래 화면 범위 밖 x=1280에서 HQ 선택.
- 마지막 로드 뒤 연속 **24,836틱**, 743개 관측 모두 게임 진행 및 상한5000 유지.
  AI 전투로 현재 전비/개체 수는 감소한다. 최대 군대를 전 구간 유지한 시험은 아니다.

142개 전비35 유닛은 원본 엔진을 호출해 **시험용으로 생성**했고 자원은 제공했다.
전체 군대를 자연 생산했다고 주장하지 않는다. 단순히 표시 숫자나 전비 장부만
부풀린 실험(run2)과 실제 개체/비용 합계를 확인한 실험(run3/4)은 증거에서 분리했다.

## 도구 / 증거

- `runtime_driver.py`: 별도 게임 복사본, Wine prefix, Xvfb와 자식 프로세스만 제어하는 계측기.
- `runtime_bridge.c`, `build_runtime_bridge.py`: 기존 inmm 소스를 임시 경로로 복사하여
  원본 메인 루프의 안전한 지점에서 생산/저장/로드/시험 군대 생성을 호출하는 진단 DLL.
  Plan C 구현을 대신 실행하거나 원본 폴더 DLL을 덮어쓰지 않는다.
- `verification_0910/`: 실행 파일 해시, 실제 메모리 스냅샷, 요청 결과, 검증 증거.
- [분석 및 검증 보고서](../../analysis/memory_maps/population_5000_runtime_0910.md).

미검증: 네이티브 Windows, LAN 동기화, 모든 지도/국가/영웅 조합, 144k 출시 검증.
QHD HUD/입력 배치는 미완성이다. 12인 확장은 이 패치의 기능이 아니다.

## 최신 제품 목표와 이 실험의 관계

현재 프로젝트는 활성8인 전비5000의 개체 풀/메모리 안정성, 최대16인, AI도 목표로 한다.
이 파일의 기존 패치는 단일플레이어 기술 근거이며 그 목표들을 이미 충족한 것이 아니다.
상세 목표는 `docs/DESIGN.md`(저장소 루트 기준)를 따른다.

## 2026-09-20 확장 풀 현황

단순 전비 숫자 패치에서 더 진행해, 8인용 공학 후보는 전역 UnitStruct 풀과 existence/age/
category-A/category-B/active-list를 **4001 슬롯**으로 함께 재배치한다. 개인 로스터 상한은
1200개로 유지한다. 이 후보로 8명이 각각 `used + reserved == 5000`, 총 4000 라이브
유닛에 도달했고, 전투·사망·재할당을 포함한 144,228틱 동안 existence/active/category-B
목록이 일치했다. 중복·누락·예상 밖 슬롯은 0이었다.

저장 실험 후보 `g2_full_capacity_persistence_v1.py`는 원본 bulk 저장 뒤에 다섯 확장 배열을
추가 직렬화한다. 약 1300개와 3993개 상태에서 실제 저장→다른 상태로 변경→로드를 수행했고,
로드 직후 메모리의 전체 56,020바이트 배열이 저장 파일 바이트와 정확히 일치했다. 외부 증거는
다음 명령으로 재검증할 수 있다.

```sh
python3 -m patches.population.verify_g2_persistence_artifacts \
  /home/dev_00/sharedfolder/260320_Syw2plus/temp/Syw2plus_patch/g2_capacity/\
20260920_n4001_persistence_sidecar/runtime_20260920_174739
```

이는 **배포 완료 선언이 아니다**. 현재 저장 ABI에는 구버전 세이브를 식별하는 magic/version이
없으므로 동일 후보가 새로 만든 저장만 검증됐다. LAN 동기화, 네이티브 Windows, 일반 생산만으로
구성한 장기 재현은 남아 있다. 144k 실험에서 라이브 `used`는 5000을 넘지 않았지만, 생산 완료와
다음 예약의 같은 틱 순서 때문에 `used=5000,reserved=10`이 일시적으로 나타난 적이 있다. 단순
필드 clamp나 최종 spawn gate 변경은 회계를 깨뜨릴 수 있어 적용하지 않았다.

세부 원인·후보 SHA·실행 증거 해시는
`docs/history/laps/20260920_lap412_g2_full_capacity_lists_runtime.md`에 기록한다.
