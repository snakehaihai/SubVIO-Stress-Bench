# Third-party provenance

The method-specific snapshot files were collected from the following local
checkouts and remain subject to their upstream licenses:

| Method | Upstream | License |
|---|---|---|
| AirSLAM | https://github.com/sair-lab/AirSLAM | GPL-3.0 |
| ORB-SLAM3 | https://github.com/UZ-SLAMLab/ORB_SLAM3 | GPL-3.0 |
| OpenVINS | https://github.com/rpng/open_vins | GPL-3.0 |
| SchurVINS | https://github.com/bytedance/SchurVINS | GPL-3.0 |

The repository-level [`LICENSE`](../LICENSE) contains GPL-3.0. The snapshot is
not a replacement for the upstream projects and includes only local experiment
configuration, launch, generation, and dataset-preparation files. Commit IDs
are recorded in `configs/method_versions.yaml`.

CERBERUS recordings and ground truth are not included. Their provider's terms
apply independently.
