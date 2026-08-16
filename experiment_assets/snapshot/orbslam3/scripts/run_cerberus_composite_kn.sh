#!/bin/bash
# CERBERUS composite Kn seq1  K K0.05, K0.1, K0.2, K0.5, K1, K2, K5, K10
#  Docker /ws/dataset
#
# :
#   [Docker ]  cd /ws && ./scripts/run_cerberus_composite_kn.sh [SEQ]
#   []     ./scripts/run_cerberus_composite_kn.sh [SEQ]
# :   CERBERUS_VIEWER=1 ./scripts/run_cerberus_composite_kn.sh [SEQ]
#
# Docker :
#   -  /wsORB3
#   -  /dataset/CERBERUS/composite/ seq1, seq1_K0.05, seq1_K0.1, ... seq1_K10
#   -  /ws/results/CERBERUS/composite/<SEQ>/trajectory.txt
#   - : cd /ws/build && make stereo_inertial_cerberus -j4
#
# :
#   COMPOSITE_DATA_ROOT   SEQ
#   RESULTS_ROOT         RESULTS_ROOT/CERBERUS/composite/<SEQ>/

set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# Docker /ws
if [ -d "/ws" ] && [ -f "/ws/Vocabulary/ORBvoc.txt" ]; then
  ORB3_ROOT="/ws"
  COMPOSITE_DATA_ROOT="${COMPOSITE_DATA_ROOT:-/dataset/CERBERUS/composite}"
  RESULTS_ROOT="${RESULTS_ROOT:-/ws/results}"
else
  ORB3_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
  COMPOSITE_DATA_ROOT="${COMPOSITE_DATA_ROOT:-$HOME/Datasets/DARPA-CERBERUS/video_processing/data/composite}"
  RESULTS_ROOT="${RESULTS_ROOT:-$ORB3_ROOT/Results_orb3}"
fi

VOCAB="${VOCAB:-$ORB3_ROOT/Vocabulary/ORBvoc.txt}"
CONFIG="${CONFIG:-$ORB3_ROOT/Examples/Stereo-Inertial/CERBERUS.yaml}"
EXEC="${EXEC:-$ORB3_ROOT/Examples/Stereo-Inertial/stereo_inertial_cerberus}"

SEQUENCES=(seq1 seq1_K0.05 seq1_K0.1 seq1_K0.2 seq1_K0.5 seq1_K1 seq1_K2 seq1_K5 seq1_K10)

if [ -n "$1" ]; then
  SEQUENCES=("$1")
fi

# Docker  ORB3_ROOT/lib
if [ -d "$ORB3_ROOT/lib" ]; then
  export LD_LIBRARY_PATH="${ORB3_ROOT}/lib:${LD_LIBRARY_PATH:-}"
fi
if [ -d "$ORB3_ROOT/Thirdparty/DBoW2/lib" ]; then
  export LD_LIBRARY_PATH="${ORB3_ROOT}/Thirdparty/DBoW2/lib:${ORB3_ROOT}/Thirdparty/g2o/lib:${LD_LIBRARY_PATH:-}"
fi

for SEQ in "${SEQUENCES[@]}"; do
  DATA_DIR="${COMPOSITE_DATA_ROOT}/${SEQ}"
  OUT_DIR="${RESULTS_ROOT}/CERBERUS/composite/${SEQ}"
  mkdir -p "$OUT_DIR"

  if [ ! -f "${DATA_DIR}/cam0/data.csv" ] || [ ! -d "${DATA_DIR}/cam0/data" ]; then
    echo " $SEQ:  ${DATA_DIR}/cam0/data.csv  cam0/data/ COMPOSITE_DATA_ROOT "
    continue
  fi
  if [ ! -d "${DATA_DIR}/cam1/data" ]; then
    echo " $SEQ:  ${DATA_DIR}/cam1/data/"
    continue
  fi
  if [ ! -f "${DATA_DIR}/imu0/data.csv" ]; then
    echo " $SEQ:  ${DATA_DIR}/imu0/data.csv"
    continue
  fi

  if [ ! -f "$EXEC" ]; then
    echo ": : $EXEC: cd /ws/build && make stereo_inertial_cerberus -j4"
    exit 1
  fi
  if [ ! -f "$VOCAB" ]; then
    echo ": : $VOCAB"
    exit 1
  fi
  if [ ! -f "$CONFIG" ]; then
    echo ": : $CONFIG"
    exit 1
  fi

  echo "=========================================="
  echo " ORB3 CERBERUS composite: $SEQ"
  echo "  : $DATA_DIR"
  echo "  : $OUT_DIR"
  echo "=========================================="
  cd "$OUT_DIR"
  if [ -n "${CERBERUS_VIEWER}" ]; then
    echo " run.log"
    "$EXEC" \
      "$VOCAB" \
      "$CONFIG" \
      "$DATA_DIR" \
      "$DATA_DIR/cam0/data.csv" || true
  else
    "$EXEC" \
      "$VOCAB" \
      "$CONFIG" \
      "$DATA_DIR" \
      "$DATA_DIR/cam0/data.csv" \
      > run.log 2>&1 || true
  fi

  if [ -f "$OUT_DIR/CameraTrajectory.txt" ]; then
    awk 'NF>=8 { t=$1/1e9; printf "%.9f %.9f %.9f %.9f %.9f %.9f %.9f %.9f\n", t, $2, $3, $4, $5, $6, $7, $8 }' "$OUT_DIR/CameraTrajectory.txt" > "$OUT_DIR/trajectory.txt"
    echo " TUM (): $OUT_DIR/trajectory.txt"
  else
    echo ":  CameraTrajectory.txt $OUT_DIR/run.log"
  fi
done
echo ". : $RESULTS_ROOT/CERBERUS/composite/"
