PYTHON ?= .venv/bin/python
.PHONY: test lint typecheck check check-all doctor doctor-runtime

# 2026-10-09 user decision: the loop Fast gate excludes the separate 2611 G2 session's
# untracked work-in-progress files. `make check-all` (FOREIGN_IGNORE=) still checks them.
FOREIGN_PATHS ?= patches/esl2610 tools/g2_esl2610_spike_probe.py tools/g2_esl2611_replication.py tools/g2_esl2611_saveload_replication.py tests/test_g2_esl2610_spike_probe.py tests/test_g2_esl2611_replication.py tests/test_g2_esl2611_saveload_replication.py
FOREIGN_IGNORE ?= $(FOREIGN_PATHS)
comma := ,
empty :=
space := $(empty) $(empty)

test:
	$(PYTHON) -m pytest -ra $(addprefix --ignore=,$(FOREIGN_IGNORE))
lint:
	$(PYTHON) -m ruff check patches tools tests checks $(if $(FOREIGN_IGNORE),--extend-exclude $(subst $(space),$(comma),$(strip $(FOREIGN_IGNORE))))
	$(PYTHON) -m compileall -q patches tools tests checks
typecheck:
	$(PYTHON) -m mypy patches/population/fixed_supply_5000.py patches/population/runtime_driver.py patches/population/build_runtime_bridge.py tools/check_setup.py tools/runtime_env.py tools/check_runtime_evidence.py tools/check_g1_presentation_trace.py tools/compare_g1_stage_b.py tools/g1_hd_extract.py tools/g1_hd_convert.py checks/context_limits.py checks/safety.py --follow-imports=skip
check: test lint typecheck
	$(PYTHON) checks/context_limits.py
	@for f in loop/*.sh checks/*.sh tests/test_build.sh; do bash -n "$$f" || exit; done
check-all:
	$(MAKE) check FOREIGN_IGNORE=
doctor:
	$(PYTHON) tools/check_setup.py
doctor-runtime:
	@test -n "$(MANIFEST)" || { echo 'MANIFEST=path/to/runtime/manifest.json is required' >&2; exit 2; }
	$(PYTHON) tools/check_setup.py --require-runtime --runtime-manifest "$(MANIFEST)"
