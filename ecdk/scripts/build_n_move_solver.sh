#!/usr/bin/bash

# Assumes that Rust toolchain is present

assert_binary_exists () {
  if ! command -v "$1" &> /dev/null
  then
    echo "Look like $1 binary is missing. Aborting"
    exit 1
  fi
}

assert_binary_exists cargo

# TODO: Check whether this envvar exists

if [ -z ${MY_MASTER_REPO+x} ]; then
  echo "Expected MY_MASTER_REPO env variable to be defined. Aborting."
  exit 1
fi

cd $MY_MASTER_REPO/solver
cargo build --release
mv target/release/solver $MY_MASTER_REPO/bin
cd $MY_MASTER_REPO/ecdk

