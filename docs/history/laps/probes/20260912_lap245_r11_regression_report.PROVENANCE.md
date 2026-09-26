# lap245 R11 비공허성 보고서 — lap246 독립 검수에서 무효 판정

원본 보고서 `20260912_lap245_r11_regression_report.json`
(SHA256 `045cdc44a066e865029082f9b917ad7f222ac03cbda956915b7e691c431e1611`)과
probe `20260912_lap245_r11_regression_probe.py`
(SHA256 `b67b25f147191970e1674d18d70aa47bea9ab3f3ee37908ba80f5566cc2c28a5`)는
**삭제·수정하지 않는다.** 아래는 lap246 middle 독립 검수가 붙이는 무효 사유다.

- 결함: lap245 probe는 mutated probe 복사본을 `tempfile.TemporaryDirectory(prefix=...)`가 만든
  얕은 `/tmp/lap245_r11_XXXX/` 바로 아래에 둔다. 그러나 SUT probe는
  `ROOT = Path(__file__).resolve().parents[4]`로 저장소 루트를 찾는다. 얕은 경로에서는
  `parents[4]`가 `IndexError: 4`를 던져 **변이와 무관하게** import 단계에서 죽는다.
- 결과: 8개 테스트 전부가 실패한 것은 `open("x")→open("w")` 변이 때문이 아니라 재배치 때문이다.
  lap246 C1(변이 없는 동일 얕은 복사본)도 같은 8개가 실패했고 실패 목록이 lap245 보고서의
  목록과 일치한다. 따라서 lap245의 "caught=true / verdict=PASS"는 **정보가 0인 공허한 신호**다.
- 검수 근거: `20260912_lap246_r11_reverify_report.json`
  SHA256 `5b4cf4bf5fd0d35a596247d73f8a7c158e73f96fe439f074cb8487be60faef63`.
- 주의: 이것은 제품 회귀(R11 테스트) 자체의 무효가 아니다. lap246은 깊이를 맞춘 미러에서
  변이가 R11 테스트 **하나만** 죽이는 것을 따로 실측해 R11의 비공허성을 성립시켰다.
