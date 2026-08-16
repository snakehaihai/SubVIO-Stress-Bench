#!/bin/bash
# occ30_Kn 30%  + Kn 8
# Bag: /datasets/CERBERUS_composite/seq1_occ30_K*.bag
# : ~/Datasets/DARPA-CERBERUS/anymal_3/gt_tum/seq1.txt
# : /ws/results/CERBERUS/occ30_Kn/<SEQ>/trajectory.txt
#
# : ./run_cerberus_occ30_Kn.sh <SEQ> [doviz]
# :   ./run_cerberus_occ30_Kn.sh seq1_occ30_K2 false

SEQ=${1:? ": $0 <SEQ> [doviz]  : $0 seq1_occ30_K2 false"}
DOVIZ=${2:-"false"}

BAG_PATH="/datasets/CERBERUS_composite/${SEQ}.bag"
RESULT_DIR="/ws/results/CERBERUS/occ30_Kn/${SEQ}"
PATH_EST="${RESULT_DIR}/trajectory.txt"
PATH_TIME="${RESULT_DIR}/timing.txt"

mkdir -p "${RESULT_DIR}"

echo "=========================================="
echo " CERBERUS occ30_Kn"
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
