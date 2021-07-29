#!/bin/bash

set -eux -o pipefail

# login to AWS Elastic Container Registry
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin ${AWS_ACCOUNT_ID}.dkr.ecr.us-east-1.amazonaws.com

function retry {
  local n=1
  local max=5
  local delay=2
  while true; do
    "$@" && break || {
      if [[ $n -lt $max ]]; then
        ((n++))
        echo "Command failed. Attempt $n/$max:"
        sleep $delay;
      else
        fail "The command has failed after $n attempts."
      fi
    }
  done
}

function build_and_push() {
  cd images

  for image in $(ls); do
    cd $image

    if [[ ! -f Dockerfile ]]
    then
      echo "No dockerfile for ${image} image found!"
      cd ..
      continue
    fi

    docker build -t "${image}:latest" .
    docker tag "${image}:latest" "${AWS_ACCOUNT_ID}.dkr.ecr.us-east-1.amazonaws.com/${image}:latest"
    docker push "${AWS_ACCOUNT_ID}.dkr.ecr.us-east-1.amazonaws.com/${image}:latest"
    cd ..

  done
}

retry build_and_push
