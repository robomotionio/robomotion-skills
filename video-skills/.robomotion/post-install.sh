#!/bin/sh
# video-skills install hook - runs once at image build (CWD = group root).
#
# spine.py finds the beat grid with librosa; the other scripts need only
# numpy (sync_check, envelope), ffmpeg and Node, which the hyperframes group
# installs. Pinned so a run downloads nothing.
set -eu
pip install --no-cache-dir --break-system-packages \
  librosa==0.11.0 soundfile==0.14.0
python3 -c "import librosa, numpy; print('librosa', librosa.__version__, 'numpy', numpy.__version__)"
