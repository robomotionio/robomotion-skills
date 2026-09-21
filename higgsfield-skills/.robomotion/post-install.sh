#!/bin/sh
# Higgsfield group install hook - runs once at image build.
#
# Every skill here says "if `higgsfield` is not on PATH, pipe the installer
# from the CLI repo's main branch into a shell". That would run unpinned,
# unreviewed code at run time. Put the CLI on PATH here, at a pinned version,
# so that line never fires. Bump the version in a reviewed change.
set -eu
npm install -g @higgsfield/cli@1.1.26
