#!/usr/bin/env bash
git add .
git commit -m "update"
git push  remote1 master
git push  remote2 master
git push -f remote3 master