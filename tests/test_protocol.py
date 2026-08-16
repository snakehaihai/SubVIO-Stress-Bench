import unittest

from subvio_bench.protocol import load_protocol
from tools.generate_experiment_manifest import rows_from_protocol


class ProtocolTest(unittest.TestCase):
    def test_complete_benchmark_matrix(self):
        protocol = load_protocol("configs/benchmark_protocol.yaml")
        rows = rows_from_protocol(protocol)
        self.assertEqual(len(rows), 1458)
        self.assertEqual(len({row["experiment_id"] for row in rows}), 1458)
        self.assertEqual(sum(row["family"] == "sensor" for row in rows), 1188)
        self.assertEqual(sum(row["family"] == "dynamic" for row in rows), 270)


if __name__ == "__main__":
    unittest.main()
