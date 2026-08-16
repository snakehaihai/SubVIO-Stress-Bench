# FAQ

## Which methods are currently integrated?

Adapter examples are provided for AirSLAM, ORB-SLAM3, OpenVINS, and SchurVINS.

## Why are real experiments disabled?

They may launch Docker, ROS, GPU workloads, or hour-long sensitivity sweeps.
Explicitly enabling an experiment prevents an ordinary clone or CI run from
starting expensive jobs.

## Why did a run report `missing-trajectory`?

The command returned zero but did not create the configured trajectory path.
Inspect that run's `run.log`, the adapter path, and the upstream method's output
convention.

## Can OpenVINS trajectories be evaluated directly?

Yes. Extra covariance columns are ignored after the first eight TUM columns.

## Can monocular scale be corrected?

Use `--correct-scale` only when the experimental protocol calls for Sim(3)
alignment. Metric VIO comparisons default to rigid alignment.

## How long do real runs take?

Runtime depends on method, GPU, sequence, and perturbation sweep. It is not
estimated by this repository. Actual duration is written to `metadata.json`.
