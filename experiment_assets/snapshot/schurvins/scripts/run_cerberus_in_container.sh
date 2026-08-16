#!/bin/bash
#  CERBERUS seq1
# : ./run_cerberus_in_container.sh [bag_file_path] [imu]
#        imu  with_imu  stereo+IMU stereo_imu/seq1/

BAG_FILE_ARG=""
USE_IMU_ARG=""
if [ -n "$1" ]; then
    BAG_FILE_ARG="BAG_FILE_ENV=$1"
fi
if [ -n "$2" ] && { [ "$2" = "imu" ] || [ "$2" = "with_imu" ]; }; then
    USE_IMU_ARG="USE_IMU=1"
    echo "Mode: stereo+IMU (results in stereo_imu/seq1/)"
fi

echo "=========================================="
echo " CERBERUS seq1"
echo "=========================================="
echo ""

#
if ! docker ps | grep -q schurvins; then
    echo ": schurvins "
    echo ": docker-compose up -d"
    exit 1
fi

echo ": "
echo ""

#
docker cp /home/zyy/Algs/schur/debug/run_cerberus_seq1.sh schurvins:/ws/debug/run_cerberus_seq1.sh 2>/dev/null || true

#
echo "..."
echo " bag : $1"
echo ""

if [ -n "$USE_IMU_ARG" ] && [ -n "$BAG_FILE_ARG" ]; then
    docker exec schurvins bash -c "cd /ws && source /opt/ros/noetic/setup.bash && source devel/setup.bash && $USE_IMU_ARG $BAG_FILE_ARG bash /ws/debug/run_cerberus_seq1.sh"
elif [ -n "$USE_IMU_ARG" ]; then
    docker exec schurvins bash -c "cd /ws && source /opt/ros/noetic/setup.bash && source devel/setup.bash && $USE_IMU_ARG bash /ws/debug/run_cerberus_seq1.sh"
elif [ -n "$1" ]; then
    docker exec schurvins bash -c "cd /ws && source /opt/ros/noetic/setup.bash && source devel/setup.bash && BAG_FILE_ENV='$1' bash /ws/debug/run_cerberus_seq1.sh"
else
    docker exec schurvins bash -c "cd /ws && source /opt/ros/noetic/setup.bash && source devel/setup.bash && bash /ws/debug/run_cerberus_seq1.sh"
fi

echo ""
echo "=========================================="
echo ""
echo "=========================================="
if [ -n "$USE_IMU_ARG" ]; then
    echo ": /ws/results/CERBERUS/stereo_imu/seq1/"
    echo ": $(pwd)/Results_schur/CERBERUS/stereo_imu/seq1/"
else
    echo ": /ws/results/CERBERUS/stereo/seq1/"
    echo ": $(pwd)/Results_schur/CERBERUS/stereo/seq1/"
fi
