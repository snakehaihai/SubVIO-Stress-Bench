PYTHON ?= python
CONFIG ?= configs/default.yaml

.PHONY: help install validate validate-paper manifest verify-assets check-language test self-test dry-run run run-all summarize figures tree clean

help:
	@echo "install validate validate-paper manifest verify-assets check-language test self-test dry-run run run-all summarize figures tree clean"

install:
	$(PYTHON) -m pip install -e .

validate:
	$(PYTHON) -c "from subvio_bench.config import load_config; load_config('$(CONFIG)'); print('configuration valid')"

validate-paper:
	$(PYTHON) -c "from subvio_bench.protocol import load_protocol; load_protocol(); print('paper protocol valid')"

manifest:
	$(PYTHON) tools/generate_experiment_manifest.py

verify-assets:
	$(PYTHON) tools/verify_experiment_assets.py

check-language:
	$(PYTHON) tools/check_english_only.py

test:
	$(PYTHON) -m unittest discover -s tests -v

self-test:
	$(PYTHON) scripts/run_all.py --config configs/self_test.yaml --overwrite
	$(PYTHON) tools/summarize_results.py --results-dir results/self-test
	$(PYTHON) tools/generate_figures.py --summary results/self-test/summaries/summary.csv --output-dir results/self-test/figures

dry-run:
	$(PYTHON) scripts/run_all.py --config $(CONFIG) --include-disabled --dry-run

run:
	$(PYTHON) scripts/run_benchmark.py --config $(CONFIG)

run-all:
	$(PYTHON) scripts/run_all.py --config $(CONFIG)

summarize:
	$(PYTHON) tools/summarize_results.py --results-dir results

figures:
	$(PYTHON) tools/generate_figures.py

tree:
	$(PYTHON) tools/tree_summary.py

clean:
	rm -rf results/self-test
