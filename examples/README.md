# Examples

`mock_method.py` and `data/ground_truth.txt` form a deterministic end-to-end
fixture used by `configs/self_test.yaml`. Run `make self-test`; no ROS, Docker,
GPU, or external dataset is required.

The mock output deliberately includes a global translation, demonstrating that
the evaluator aligns trajectories before computing APE. The degraded fixture
adds a non-rigid deviation so its error is measurably higher than baseline.
