#!/bin/bash

function clean {
    rm -rf dist build dymoapi.egg-info
}

function build {
    python setup.py sdist bdist_wheel
}

function publish {
    twine upload dist/*
}

function deploy {
    clean
    build
    publish
}

"$@"