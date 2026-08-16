from pathlib import Path
import tempfile
import unittest

import numpy as np

from subvio_bench.evaluation import evaluate
from subvio_bench.discovery import discover
from subvio_bench.trajectory import associate, load_tum


class TrajectoryTest(unittest.TestCase):
    def test_loads_extra_columns_and_normalizes_nanoseconds(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "trajectory.txt"
            path.write_text("# header\n1000000000000000000 0 0 0 0 0 0 1 99\n2000000000000000000 1 0 0 0 0 0 1 99\n", encoding="utf-8")
            data = load_tum(path)
            self.assertEqual(data.shape, (2, 8))
            self.assertAlmostEqual(data[1, 0], 2_000_000_000.0)

    def test_association_and_rigid_alignment(self):
        with tempfile.TemporaryDirectory() as directory:
            reference = Path(directory) / "reference.txt"
            estimate = Path(directory) / "estimate.txt"
            t = np.arange(5.0)
            xyz = np.column_stack((t, t * 0.5, np.zeros_like(t)))
            q = np.tile([0, 0, 0, 1], (5, 1))
            np.savetxt(reference, np.column_stack((t, xyz, q)))
            np.savetxt(estimate, np.column_stack((t + 0.001, xyz + [4, -2, 1], q)))
            metrics = evaluate(reference, estimate, max_diff=0.01)
            self.assertEqual(metrics["matched_poses"], 5)
            self.assertLess(metrics["ape_rmse_m"], 1e-10)
            self.assertAlmostEqual(metrics["coverage"], 1.0)

    def test_discovery_ignores_dangling_links(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            result = root / "AirSLAM/Results_airslam/CERBERUS/test"
            result.mkdir(parents=True)
            (result / "trajectory.txt").symlink_to(result / "missing.txt")
            catalog = discover(root)
            self.assertEqual(catalog["trajectory_count"], 0)

    def test_coverage_uses_path_distance_and_penalizes_truncation(self):
        with tempfile.TemporaryDirectory() as directory:
            reference = Path(directory) / "reference.txt"
            estimate = Path(directory) / "estimate.txt"
            t = np.arange(5.0)
            # Unequal step lengths distinguish distance coverage from duration.
            xyz = np.column_stack(([0, 1, 2, 6, 10], np.zeros(5), np.zeros(5)))
            q = np.tile([0, 0, 0, 1], (5, 1))
            np.savetxt(reference, np.column_stack((t, xyz, q)))
            np.savetxt(estimate, np.column_stack((t[:3], xyz[:3] + [3, 0, 0], q[:3])))
            metrics = evaluate(reference, estimate, max_diff=0.01)
            self.assertAlmostEqual(metrics["coverage"], 0.2)
            self.assertEqual(metrics["penalized_reference_poses"], 2)
            self.assertGreater(metrics["penalized_ape_rmse_m"], metrics["ape_rmse_m"])


if __name__ == "__main__":
    unittest.main()
