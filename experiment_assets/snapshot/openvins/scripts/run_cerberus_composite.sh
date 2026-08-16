#!/bin/bash
# Composite
# : ~/Datasets/DARPA-CERBERUS/video_processing/data/composite/seq1_K1 (bag: seq1_K1.bag)
# :   ~/Datasets/DARPA-CERBERUS/anymal_3/gt_tum/seq1.txt
# :   /ws/results/CERBERUS/composite/<SEQ>/trajectory.txt  ->  Results_ov/CERBERUS/composite/<SEQ>/
#
# : ./run_cerberus_composite.sh <SEQ> [doviz]
# :   ./run_cerberus_composite.sh seq1_K1 false

SEQ=${1:? ": $0 <SEQ> [doviz]  : $0 seq1_K1 false"}
DOVIZ=${2:-"false"}

MODE="stereo+imu"
BAG_PATH="/datasets/CERBERUS_composite/${SEQ}.bag"
RESULT_DIR="/ws/results/CERBERUS/composite/${SEQ}"
PATH_EST="${RESULT_DIR}/trajectory.txt"
PATH_TIME="${RESULT_DIR}/timing.txt"

mkdir -p "${RESULT_DIR}"

echo "=========================================="
echo " CERBERUS Composite"
echo ": ${SEQ}"
echo "Bag:  ${BAG_PATH}"
echo ": ${PATH_EST}"
echo ": ${DOVIZ}"
echo "=========================================="

if [ ! -f "${BAG_PATH}" ]; then
    echo ": Bag : ${BAG_PATH}"
    exit 1
fi

roslaunch ov_msckf cerberus.launch \
    mode:=stereo+imu \
    seq:=${SEQ} \
    bag:=${BAG_PATH} \
    max_cameras:=2 \
    use_stereo:=true \
    dosave:=true \
    dotime:=false \
    doviz:=${DOVIZ} \
    path_est:=${PATH_EST} \
    path_time:=${PATH_TIME}

echo "=========================================="
echo ": ${PATH_EST}"
echo "=========================================="
