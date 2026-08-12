#!/bin/bash
# gh-as-git-credential: bridge git -> Windows gh auth git-credential (Git Bash)
# git calls: <helper> get|store|erase, with protocol/host on stdin
"/c/Program Files/GitHub CLI/gh.exe" auth git-credential "$1"
