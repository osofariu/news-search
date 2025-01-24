#!/usr/bin/env bash

cd "$(dirname $0)/.."

if [[ ! -d .venv ]]; then
    python -m venv .venv
fi

source ./.venv/bin/activate
pipenv install
