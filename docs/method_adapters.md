# Method adapters

An adapter is one experiment entry in YAML. It identifies a method, sequence,
perturbation, argument-vector command, expected trajectory, optional ground
truth, working directory, environment, and timeout.

```yaml
- id: orb3-seq1-occ30
  enabled: true
  method: ORB-SLAM3
  sequence: seq1_occ_p30
  perturbation: {type: occlusion, severity: 30}
  cwd: ${HOME}/Algs/orb3
  command: [bash, scripts/run_cerberus_composite_occ.sh, seq1_occ_p30]
  trajectory: ${HOME}/Algs/orb3/Results_orb3/CERBERUS/composite/seq1_occ_p30/trajectory.txt
  ground_truth: ${HOME}/Datasets/DARPA-CERBERUS/anymal_3/gt_tum/seq1.txt
  timeout_s: 300
```

Commands are executed without a shell. Put environment variables under `env`
instead of embedding `export`, redirection, or pipelines. The method script may
run directly or call a pre-existing container; the benchmark does not assume a
single ROS distribution or Docker image.

Verified local entry points are documented in `materials/`:

- AirSLAM: `src/airslam/scripts/run_cerberus_composite.sh`
- ORB-SLAM3: `scripts/run_cerberus_composite_kn.sh` and
  `scripts/run_cerberus_composite_occ.sh`
- OpenVINS: `ov_msckf/scripts/run_cerberus_composite.sh` and
  `run_cerberus_occ.sh`
- SchurVINS: `run_sensitivity.py`

All real entries in `configs/default.yaml` are disabled by default so cloning
the repository never launches long ROS jobs accidentally.
