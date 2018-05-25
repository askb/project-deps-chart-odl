#!/bin/bash
# SPDX-License-Identifier: EPL-1.0
##############################################################################
# Copyright (c) 2017 The Linux Foundation and others.
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Eclipse Public License v1.0
# which accompanies this distribution, and is available at
# http://www.eclipse.org/legal/epl-v10.html
##############################################################################
#!/bin/bash

# This script determines the dependency graph for the ODL autorelease projects
# and outputs the organogram format files.
#
#   Usage: ./merge-order.sh <URL/path/to/dependencies.log>
#
# For example:
# ./merge-order.sh https://logs.opendaylight.org/releng/vex-yul-odl-jenkins-1/autorelease-release-fluorine/91/dependencies.log.gz


set +u  # Allow unbound variables for virtualenv
virtualenv --quiet "/tmp/v/merge-order"
# shellcheck source=/tmp/v/git-review/bin/activate disable=SC1091
source "/tmp/v/merge-order/bin/activate"
pip install --quiet --upgrade "pip==9.0.3" setuptools
pip install --quiet --upgrade networkx==1.11
pip install --quiet --upgrade matplotlib pydotplus
set -u

#TODO:
# 1. write to log file instead of printing output
# 2. Migrate the python code to py3.x and networkx latest release 2.1
# 3. Integrate this script with auto-merge change patch

[[ -f "/tmp/dependencies.log.gz" ]] && rm /tmp/dependencies.log.gz
[[ -f "/tmp/dependencies.log" ]] && rm "/tmp/dependencies.log"
[[ -f "/tmp/output-merge-order.log" ]] && rm "/tmp/output-merge-order.log"
[[ -f "/tmp/merge-order.png" ]] && rm "/tmp/merge-order.png"
[[ -f "/tmp/merge-order.dot" ]] && rm "/tmp/merge-order.dot"

wget -nv -O /tmp/dependencies.log.gz "$1"
zcat /tmp/dependencies.log.gz > /tmp/dependencies.log

if [[ ! -f "/tmp/dependencies.log" ]]; then
    exit 1
fi

python determine-merge-order.py "/tmp/dependencies.log" "/tmp/output-merge-order.log" "/tmp/merge-order.png" "/tmp/merge-order.dot" > "./output_log_python-$(date +%F)" 2>&1

if [[ -f "/tmp/merge-order.png" ]] && [[ -f "/tmp/merge-order.dot" ]] && [[ -f "/tmp/output-merge-order.log" ]]; then
    echo "Merge order determined successfully!"
else
    exit 1
fi

#  // Use dot to generate the output
#  dot /tmp/tree_level-dot.dot -Tpng > /tmp/tree_level-dot.png
#  eog /tmp/tree_level-dot.png
dot "/tmp/merge-order.dot" -Tpng > "/tmp/tree_level-dot-$(date +%F).png"

if [ -f "/tmp/tree_level-dot-$(date +%F).png" ]; then
    echo ".png file created successfully /tmp/tree_level-dot-$(date +%F).png"
fi

#  // For a more typical organogram format, you can force orthogonal edge routing by
#  dot /tmp/tree_level-dot.dot -Tpng -Gsplines=ortho > /tmp/tree_level-dot-ortho.png
dot "/tmp/merge-order.dot" -Tpng -Gsplines=ortho > "/tmp/tree_level-dot-ortho-$(date +%F).png"

if [ -f "/tmp/tree_level-dot-ortho-$(date +%F).png" ]; then
    echo ".dot file created successfully /tmp/tree_level-dot-ortho-$(date +%F).png"
    echo "run the command 'eog /tmp/tree_level-dot-ortho-$(date +%F).png' to view the graph"
fi
