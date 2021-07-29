#!/bin/bash

set -eux

./init-infra.sh
./set-dns-records.sh
./build-all-images.sh
./deploy-all-to-k8s.sh
