#!/usr/bin/env bash
# One command to re-check the whole design: parts, hand layout, physics, firmware.
#   pip install manifold3d trimesh numpy matplotlib mujoco networkx lxml   (once)
#   ./validate.sh
set -euo pipefail
cd "$(dirname "$0")"
echo "=== 1/4 printable finger parts + joint range ==="; (cd cad && python3 generate_parts.py)
echo; echo "=== 2/4 full hand: collisions, routing, stability, assembly details ==="; (cd cad && python3 hand.py --checks-only)
echo; echo "=== 2b/4 how the parts fit together + palm camera ==="; (cd cad && python3 audit.py)
echo; echo "=== 3/4 physics (MuJoCo) ==="; (cd sim && python3 finger_sim.py | tee results/report.txt)
echo; echo "=== 4/4 firmware: compile + behaviour test on the PC ==="
g++ -std=c++17 -Wall -Wextra -Werror -Wno-unused-parameter -Ifirmware/test/mock -x c++ firmware/test/test_firmware.cpp -o /tmp/robohand_fwtest
/tmp/robohand_fwtest | tail -n 1
