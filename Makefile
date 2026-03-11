.PHONY: help env run run-all summarize figures clean

PYTHON ?= python

help:
	@echo "SubVIO-Stress-Bench - available targets:"
	@echo ""
	@echo "  env        Create the conda environment"
	@echo "  run        Run a single benchmark evaluation (see Makefile for config)"
	@echo "  run-all    Run all perturbation experiments"
	@echo "  summarize  Aggregate results into summaries"
	@echo "  figures    Generate evaluation figures and tables"
	@echo "  tree       Print the repository directory tree"
	@echo "  clean      Remove generated outputs (logs, figures, tables)"
	@echo ""

env:
	conda env create -f environment.yml

run:
	@echo "TODO: add benchmark run command"
	# $(PYTHON) scripts/run_benchmark.py --config configs/default.yaml

run-all:
	@echo "TODO: add run-all command"
	# $(PYTHON) scripts/run_all.py --config configs/all_perturbations.yaml

summarize:
	@echo "TODO: add summarize command"
	# $(PYTHON) tools/summarize_results.py --results-dir results/

figures:
	@echo "TODO: add figure generation command"
	# $(PYTHON) tools/generate_figures.py --results-dir results/ --output-dir results/figures/

tree:
	$(PYTHON) tools/tree_summary.py

clean:
	@echo "Removing generated outputs..."
	@find results/logs -name "*.log" -delete 2>/dev/null || true
	@find results/outputs -type f -delete 2>/dev/null || true
	@find results/figures -type f -delete 2>/dev/null || true
	@find results/summaries -type f -delete 2>/dev/null || true
	@find results/tables -type f -delete 2>/dev/null || true
	@echo "Done."
