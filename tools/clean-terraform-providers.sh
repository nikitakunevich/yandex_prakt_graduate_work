#!/bin/bash

set set -eux -o pipefail

find .. -name .terraform -type d -exec rm -rf {} \;
find .. -name terraform.tfstate -type f -exec rm -f {} \;
