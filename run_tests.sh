#!/usr/bin/env bash
# Runs the integration tests against the from-source Kuma test image
# (docker/kuma-test, pinned in versions.env), the same one CI uses.
# The tests delete all monitors and notifications: only the throwaway
# container started here is ever used.
set -euo pipefail
cd "$(dirname "$0")"

set -a
. docker/kuma-test/versions.env
set +a

version="${1:-$KUMA_VERSION}"
if [ "$version" != "$KUMA_VERSION" ]; then
  echo "Only $KUMA_VERSION is defined in docker/kuma-test/versions.env, got $version" >&2
  exit 1
fi

# Content-keyed tag, as in .github/workflows/kuma-image.yml.
tag="kuma-test:${KUMA_VERSION}-$(git rev-parse --short=12 HEAD:docker/kuma-test)"
if [ -n "$(git status --porcelain docker/kuma-test)" ]; then
  # The tag only sees committed files, so do not trust a cached image.
  echo "docker/kuma-test has uncommitted changes: rebuilding $tag"
  docker build -t "$tag" --build-arg KUMA_REF="$KUMA_REF" docker/kuma-test
elif ! docker image inspect "$tag" > /dev/null 2>&1; then
  echo "Building $tag from Uptime Kuma $KUMA_REF..."
  docker build -t "$tag" --build-arg KUMA_REF="$KUMA_REF" docker/kuma-test
fi

echo "Starting uptime kuma $version..."
docker run -d --rm -p 3001:3001 --name kuma-test "$tag" > /dev/null
trap 'echo "Stopping uptime kuma..."; docker stop kuma-test > /dev/null' EXIT

ready=
for _ in $(seq 240); do
  if [ "$(curl -s -L -o /dev/null -w '%{http_code}' 127.0.0.1:3001)" = "200" ]; then
    ready=1
    break
  fi
  sleep 0.5
done
if [ -z "$ready" ]; then
  echo "Uptime Kuma did not answer HTTP 200 within 120 s" >&2
  exit 1
fi

echo "Running tests..."
python -m unittest discover -s tests
