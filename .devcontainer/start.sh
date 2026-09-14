#!/bin/bash
# Run each time the codespace starts. Starts JupyterLab in the background,
# detached so it outlives this script, with the checkout as its root so the
# workshops, collection.json and the welcome file resolve as they do on
# Binder. Output goes to /tmp/jupyterlab.log.
#
# Token authentication is off so opening the forwarded port, from VS
# Code's notification or its Ports panel, goes straight into JupyterLab
# with no token to copy. That relies on the forwarded port staying
# private, the default, which only the codespace's owner, signed in to
# GitHub, can reach. The welcome file tells the learner not to make it
# public. Remote access is allowed because requests arrive
# with the forwarded github.dev host name rather than localhost.
#
# JupyterLab is run through python -m so nothing depends on where pip put
# the jupyter scripts or whether that directory is on this command's PATH.
set -euo pipefail

cd "$(dirname "$0")/.."

log=/tmp/jupyterlab.log
status_url=http://127.0.0.1:8888/api/status

ready() {
  python -c 'import sys, urllib.request; urllib.request.urlopen(sys.argv[1], timeout=2)' \
    "$status_url" 2>/dev/null
}

if ready; then
  echo "JupyterLab is already running on port 8888"
  exit 0
fi

setsid nohup python -m jupyterlab \
  --no-browser \
  --ServerApp.ip=0.0.0.0 \
  --ServerApp.port=8888 \
  --ServerApp.root_dir="$PWD" \
  --IdentityProvider.token= \
  --ServerApp.allow_remote_access=True \
  --ServerApp.trust_xheaders=True \
  > "$log" 2>&1 < /dev/null &

# Wait until JupyterLab answers before returning. A process still starting
# when the start command ends can be cleaned up along with it, which left
# no JupyterLab and no log at all; once it answers it runs in its own
# session. Waiting also puts a failure in the creation log, where
# returning at once reported success whatever happened.
for _ in $(seq 120); do
  if ready; then
    echo "JupyterLab is running on port 8888; output is in $log"
    exit 0
  fi

  sleep 1
done

echo "JupyterLab did not answer within two minutes; the end of $log follows" >&2
tail -n 40 "$log" >&2 || true
exit 1
