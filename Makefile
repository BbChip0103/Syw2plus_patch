PYTHON ?= .venv/bin/python
.PHONY: test lint typecheck check doctor doctor-runtime

test:
	$(PYTHON) -m pytest -ra
lint:
	$(PYTHON) -m ruff check patches tools tests checks
	$(PYTHON) -m compileall -q patches tools tests checks
typecheck:
	$(PYTHON) -m mypy patches/population/fixed_supply_5000.py patches/population/runtime_driver.py patches/population/build_runtime_bridge.py tools/check_setup.py tools/runtime_env.py tools/check_runtime_evidence.py tools/check_g1_presentation_trace.py tools/compare_g1_stage_b.py checks/context_limits.py checks/safety.py --follow-imports=skip
check: test lint typecheck
	$(PYTHON) checks/context_limits.py
	@for f in loop/*.sh checks/*.sh tests/test_build.sh; do bash -n "$$f" || exit; done
doctor:
	$(PYTHON) tools/check_setup.py
doctor-runtime:
	@test -n "$(MANIFEST)" || { echo 'MANIFEST=path/to/runtime/manifest.json is required' >&2; exit 2; }
	$(PYTHON) tools/check_setup.py --require-runtime --runtime-manifest "$(MANIFEST)"
