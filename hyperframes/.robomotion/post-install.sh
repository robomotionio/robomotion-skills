#!/bin/sh
# hyperframes group install hook - runs once at image build (CWD = group root).
#
# The skills drive the hyperframes CLI: it lays a video out in HTML, plays it
# in a pinned headless Chrome and encodes the frames with FFmpeg. A narrated
# video also needs a voice and that voice's word timings (captions follow
# them); with no HeyGen sign-in both are local: Kokoro speaks, whisper times.
# None of it is in the base image, and everything the CLI would otherwise
# fetch on first use (Chrome, two models, a whisper.cpp build from an
# unpinned master) is fetched here, pinned, so a run downloads nothing.
#
# The CLI keeps all of that under $HOME/.cache/hyperframes. The agent's
# terminal runs as the host user, whose home differs per machine and may not
# exist, so the CLI gets one home of its own, /opt/hyperframes/home, from the
# `hyperframes` wrapper this puts on PATH.
set -eu

# The CLI version at the upstream commit the skills are synced from
# (upstreams.yaml). Bump the two together.
HF_VERSION=0.8.39
WHISPER_TAG=v1.9.4
WHISPER_COMMIT=927cfce34f31707e17f2bff35c349632fb9e2c3a
KOKORO_ONNX_VERSION=0.6.1
SOUNDFILE_VERSION=0.14.0

HF_HOME_DIR=/opt/hyperframes/home
CACHE=$HF_HOME_DIR/.cache/hyperframes

# fetch <url> <sha256> <dest>
fetch() {
  mkdir -p "$(dirname "$3")"
  curl -fsSL --retry 3 -o "$3" "$1"
  echo "$2  $3" | sha256sum -c -
}

# The CLI reinstalls itself in the background whenever npm has a newer
# version, fetches skills of its own from GitHub and reports to its
# analytics. All three stay off: the version is the pin above and the skills
# are this reviewed group.
export HYPERFRAMES_NO_UPDATE_CHECK=1 HYPERFRAMES_NO_AUTO_INSTALL=1 \
  HYPERFRAMES_SKIP_SKILLS=1 HYPERFRAMES_NO_TELEMETRY=1 DO_NOT_TRACK=1

# FFmpeg encodes. The libraries are what the headless Chrome links against on
# Ubuntu 24.04 (the list `hyperframes doctor` asks for); the fonts are what
# text renders in when a composition names none it can load. certutil
# (libnss3-tools) is for the wrapper below, which teaches Chrome the
# sandbox's proxy CA. The compiler is for whisper.cpp and leaves again below.
apt-get update -qq
apt-get install -y -qq --no-install-recommends \
  ffmpeg libnss3-tools \
  libnss3 libnspr4 libatk1.0-0t64 libatk-bridge2.0-0t64 libcups2t64 libdrm2 \
  libxkbcommon0 libatspi2.0-0t64 libxcomposite1 libxdamage1 libxfixes3 \
  libxrandr2 libgbm1 libpango-1.0-0 libcairo2 libasound2t64 \
  fonts-liberation fonts-dejavu-core fonts-noto-color-emoji \
  cmake g++ make

# whisper-cli on PATH is the first place the CLI looks. The image is built on
# the machine that runs it, so the default native CPU tuning is right.
git clone -q --depth 1 --branch "$WHISPER_TAG" https://github.com/ggml-org/whisper.cpp.git /tmp/whisper.cpp
[ "$(git -C /tmp/whisper.cpp rev-parse HEAD)" = "$WHISPER_COMMIT" ]
cmake -S /tmp/whisper.cpp -B /tmp/whisper.cpp/build -DCMAKE_BUILD_TYPE=Release \
  -DBUILD_SHARED_LIBS=OFF -DWHISPER_BUILD_TESTS=OFF -DWHISPER_BUILD_SERVER=OFF >/dev/null
cmake --build /tmp/whisper.cpp/build -j"$(nproc)" --target whisper-cli >/dev/null
install -m 755 /tmp/whisper.cpp/build/bin/whisper-cli /usr/local/bin/whisper-cli
rm -rf /tmp/whisper.cpp
apt-get purge -y -qq cmake g++ make
apt-get autoremove -y -qq
rm -rf /var/lib/apt/lists/*

# Kokoro runs in Python; `hyperframes tts` imports these two.
pip install --no-cache-dir --break-system-packages \
  "kokoro-onnx==${KOKORO_ONNX_VERSION}" "soundfile==${SOUNDFILE_VERSION}"

npm install -g --no-fund --no-audit "hyperframes@${HF_VERSION}"

# onnxruntime-node ships every platform's runtime plus the CUDA and TensorRT
# providers, about 500 MB this container never loads: keep this platform's
# CPU runtime only.
ort="$(npm root -g)/hyperframes/node_modules/onnxruntime-node/bin/napi-v3"
arch=$(node -p process.arch)
find "$ort" -mindepth 1 -maxdepth 1 ! -name linux -exec rm -rf {} +
find "$ort/linux" -mindepth 1 -maxdepth 1 ! -name "$arch" -exec rm -rf {} +
rm -f "$ort/linux/$arch/libonnxruntime_providers_cuda.so" \
  "$ort/linux/$arch/libonnxruntime_providers_tensorrt.so"

# The CLI's own pinned Chrome (pixels drift between Chrome versions).
HOME="$HF_HOME_DIR" hyperframes browser ensure
chrome=$(find "$CACHE/chrome" -type f -name chrome-headless-shell | head -n 1)
[ -n "$chrome" ] || { echo "hyperframes: no chrome-headless-shell after browser ensure" >&2; exit 1; }

# The models, where the CLI looks before downloading them. small.en is the
# one the narration script transcribes with.
fetch https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.onnx \
  7d5df8ecf7d4b1878015a32686053fd0eebe2bc377234608764cc0ef3636a6c5 \
  "$CACHE/tts/models/kokoro-v1.0.onnx"
fetch https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin \
  bca610b8308e8d99f32e6fe4197e7ec01679264efed0cac9140fe9c29f1fbf7d \
  "$CACHE/tts/voices/voices-v1.0.bin"
fetch https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-small.en.bin \
  c6138d6d58ecc8322097e0f987c32f1be8bb0a18532a3f88f734d1bbf9c41e5d \
  "$CACHE/whisper/models/ggml-small.en.bin"

# Any uid writes its own files into the CLI's home; nobody removes another's.
# (The CLI makes its folders 0700, parents included, so /opt/hyperframes too.)
chmod -R a+rX /opt/hyperframes
find "$HF_HOME_DIR" -type d -exec chmod 1777 {} +

# /usr/local/bin comes before npm's /usr/bin on PATH, so both `hyperframes`
# and `npx hyperframes` (npx runs an installed package's command by name)
# land here.
real=$(command -v hyperframes)
cat > /usr/local/bin/hyperframes <<EOF
#!/bin/sh
export HOME="$HF_HOME_DIR"
export HYPERFRAMES_BROWSER_PATH="$chrome"
export HYPERFRAMES_NO_UPDATE_CHECK=1 HYPERFRAMES_NO_AUTO_INSTALL=1 \\
  HYPERFRAMES_SKIP_SKILLS=1 HYPERFRAMES_NO_TELEMETRY=1 DO_NOT_TRACK=1

# The agent's sandbox sends every https request through a credential proxy
# that re-signs the traffic, and names the proxy's CA in SSL_CERT_FILE. curl,
# Python and Node read that variable; Chrome does not. It trusts its own
# roots plus \$HOME/.pki/nssdb, so without the CA there, every page a
# composition loads fails with ERR_CERT_AUTHORITY_INVALID. The db is made
# here, per run, because the CA is the machine's, not the image's.
if [ -n "\${SSL_CERT_FILE:-}" ] && [ -r "\$SSL_CERT_FILE" ]; then
  db="\$HOME/.pki/nssdb"
  [ -f "\$db/cert9.db" ] || { mkdir -p "\$db" && certutil -d "sql:\$db" -N --empty-password; }
  certutil -d "sql:\$db" -L -n robomotion-proxy-ca >/dev/null 2>&1 \\
    || certutil -d "sql:\$db" -A -t "C,," -n robomotion-proxy-ca -i "\$SSL_CERT_FILE"
fi

exec "$real" "\$@"
EOF
chmod 755 /usr/local/bin/hyperframes

hyperframes --version
