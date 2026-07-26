#!/usr/bin/env bash
set -euo pipefail

project_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
build_dir="$project_dir/dist"

rm -rf "$build_dir"
mkdir -p "$build_dir/server" "$build_dir/client"

cp "$project_dir/worker/static-worker.js" "$build_dir/server/index.js"
cp "$project_dir/index.html" "$project_dir/updates.html" "$project_dir/privacy.html" "$project_dir/terms.html" "$project_dir/support.html" "$project_dir/app-ads.txt" "$build_dir/client/"
cp -R "$project_dir/apps" "$project_dir/assets" "$build_dir/client/"

printf 'Static Sites build prepared at %s\n' "$build_dir"
