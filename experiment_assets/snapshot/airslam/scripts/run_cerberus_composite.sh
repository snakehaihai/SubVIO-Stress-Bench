#!/usr/bin/env bash
#  Docker CERBERUS composite  230s
#   - K 8  | occ 9  | occ30_Kn 8  | minetunnel 24  | minetunnel40 occ10+20+40+60+80
#
# :
#   bash src/airslam/scripts/run_cerberus_composite.sh              #  17 K+occ
#   bash src/airslam/scripts/run_cerberus_composite.sh --occ       # occ 9
#   bash src/airslam/scripts/run_cerberus_composite.sh --k          # K 8
#   bash src/airslam/scripts/run_cerberus_composite.sh --occ30-k   # occ30_Kn 8
#   COMPOSITE_ROOT=/dataset/CERBERUS_minetunnel bash ... --minetunnel     # 24 occ50+70+90
#   COMPOSITE_ROOT=/dataset/CERBERUS_minetunnel bash ... --minetunnel40   #  40 occ10+20+40+60+80
#
# :
#   COMPOSITE_ROOT  -  minetunnel  /media/zyy/Doremi1/Datasets_minetunnel/CERBERUS_composite  /dataset/CERBERUS_minetunnel
#   RESULT_ROOT     -  /ws/results
#   SKIP_EXISTING   - 1  trajectory.txt
#   SEQ_TIMEOUT     -  230

set -e

COMPOSITE_ROOT="${COMPOSITE_ROOT:-/dataset/CERBERUS_composite}"
RESULT_ROOT="${RESULT_ROOT:-/ws/results}"
SKIP_EXISTING="${SKIP_EXISTING:-0}"
SEQ_TIMEOUT="${SEQ_TIMEOUT:-230}"

#
MODE="all"
for arg in "$@"; do
  case "$arg" in
    --occ|--occ-only)   MODE="occ"; break ;;
    --k|--k-only)       MODE="k"; break ;;
    --occ30-k|occ30_kn) MODE="occ30-k"; break ;;
    --minetunnel)       MODE="minetunnel"; break ;;
    --minetunnel40)     MODE="minetunnel40"; break ;;
  esac
done

K_SEQ=(seq1_K0.05 seq1_K0.1 seq1_K0.2 seq1_K0.5 seq1_K1 seq1_K2 seq1_K5 seq1_K10)
OCC_SEQ=(seq1_occ_p10 seq1_occ_p20 seq1_occ_p30 seq1_occ_p40 seq1_occ_p50 seq1_occ_p60 seq1_occ_p70 seq1_occ_p80 seq1_occ_p90)
OCC30_K_SEQ=(seq1_occ30_K0.05 seq1_occ30_K0.1 seq1_occ30_K0.2 seq1_occ30_K0.5 seq1_occ30_K2 seq1_occ30_K5 seq1_occ30_K10 seq1_occ30_K20)
# /media/zyy/Doremi1/Datasets_minetunnel/CERBERUS_composite   COMPOSITE_ROOT=/dataset/CERBERUS_minetunnel
MINETUNNEL_SEQ=(
  seq1_occ50_K0.05 seq1_occ50_K0.1 seq1_occ50_K0.2 seq1_occ50_K0.5 seq1_occ50_K2 seq1_occ50_K5 seq1_occ50_K10 seq1_occ50_K20
  seq1_occ70_K0.05 seq1_occ70_K0.1 seq1_occ70_K0.2 seq1_occ70_K0.5 seq1_occ70_K2 seq1_occ70_K5 seq1_occ70_K10 seq1_occ70_K20
  seq1_occ90_K0.05 seq1_occ90_K0.1 seq1_occ90_K0.2 seq1_occ90_K0.5 seq1_occ90_K2 seq1_occ90_K5 seq1_occ90_K10 seq1_occ90_K20
)
#  40 occ10 + occ20 + occ40 + occ60 + occ80 8 Kn
MINETUNNEL40_SEQ=(
  seq1_occ10_K0.05 seq1_occ10_K0.1 seq1_occ10_K0.2 seq1_occ10_K0.5 seq1_occ10_K2 seq1_occ10_K5 seq1_occ10_K10 seq1_occ10_K20
  seq1_occ20_K0.05 seq1_occ20_K0.1 seq1_occ20_K0.2 seq1_occ20_K0.5 seq1_occ20_K2 seq1_occ20_K5 seq1_occ20_K10 seq1_occ20_K20
  seq1_occ40_K0.05 seq1_occ40_K0.1 seq1_occ40_K0.2 seq1_occ40_K0.5 seq1_occ40_K2 seq1_occ40_K5 seq1_occ40_K10 seq1_occ40_K20
  seq1_occ60_K0.05 seq1_occ60_K0.1 seq1_occ60_K0.2 seq1_occ60_K0.5 seq1_occ60_K2 seq1_occ60_K5 seq1_occ60_K10 seq1_occ60_K20
  seq1_occ80_K0.05 seq1_occ80_K0.1 seq1_occ80_K0.2 seq1_occ80_K0.5 seq1_occ80_K2 seq1_occ80_K5 seq1_occ80_K10 seq1_occ80_K20
)
case "$MODE" in
  k)             SEQUENCES=("${K_SEQ[@]}") ;;
  occ)           SEQUENCES=("${OCC_SEQ[@]}") ;;
  occ30-k)       SEQUENCES=("${OCC30_K_SEQ[@]}") ;;
  minetunnel)    SEQUENCES=("${MINETUNNEL_SEQ[@]}") ;;
  minetunnel40)  SEQUENCES=("${MINETUNNEL40_SEQ[@]}") ;;
  *)             SEQUENCES=("${K_SEQ[@]}" "${OCC_SEQ[@]}") ;;
esac

if [[ ! -d "$COMPOSITE_ROOT" ]]; then
  echo ": composite : $COMPOSITE_ROOT"
  exit 1
fi

echo ": $MODE ${#SEQUENCES[@]} : ${SEQ_TIMEOUT}s"
echo ""

for SEQ in "${SEQUENCES[@]}"; do
  DATAROOT="${COMPOSITE_ROOT}/${SEQ}"
  SAVING_DIR="${RESULT_ROOT}/CERBERUS/composite/${SEQ}"
  TRAJ_V0="${SAVING_DIR}/trajectory_v0.txt"
  TRAJ_TXT="${SAVING_DIR}/trajectory.txt"

  if [[ ! -d "$DATAROOT" ]]; then
    echo "[] $SEQ: "
    continue
  fi

  if [[ "$SKIP_EXISTING" == "1" && -f "$TRAJ_TXT" && -s "$TRAJ_TXT" ]]; then
    echo "[] $SEQ:  trajectory.txt"
    continue
  fi

  mkdir -p "$SAVING_DIR"
  echo "========== $SEQ ( ${SEQ_TIMEOUT}s) =========="

  # timeout  124
  ret=0
  timeout "$SEQ_TIMEOUT" roslaunch air_slam vo_cerberus.launch \
    dataroot:="$DATAROOT" \
    saving_dir:="$SAVING_DIR" \
    visualization:=false || ret=$?

  if [[ $ret -eq 124 ]]; then
    echo "  [] ${SEQ_TIMEOUT}s "
  elif [[ $ret -ne 0 ]]; then
    echo "  [] =$ret"
  fi

  if [[ -f "$TRAJ_V0" && -s "$TRAJ_V0" ]]; then
    cp -f "$TRAJ_V0" "$TRAJ_TXT"
    echo "   trajectory.txt"
  else
    echo "   trajectory_v0.txt"
  fi
  echo ""
done

echo "==========  =========="
echo ": python3 src/airslam/scripts/eval_evo_rmse_coverage.py --result-dir Results_airslam --gt ~/Datasets/DARPA-CERBERUS/anymal_3/gt_tum/seq1.txt"
