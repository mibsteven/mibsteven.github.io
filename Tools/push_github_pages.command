#!/bin/bash
set -u

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
repo_dir="$(cd "$script_dir/.." && pwd)"

cd "$repo_dir" || exit 1

printf '\nGitHub Pages push\n'
printf 'Repository: mibsteven/mibsteven.github.io\n'
printf 'Branch: main\n\n'
printf 'When prompted for Password, paste your GitHub Personal Access Token.\n'
printf 'The token will not appear while you type, and it will not be saved.\n\n'

git -c credential.helper= push \
  https://mibsteven@github.com/mibsteven/mibsteven.github.io.git \
  HEAD:main
push_status=$?

if [ "$push_status" -eq 0 ]; then
  printf '\nPush completed. GitHub Pages will update shortly.\n'
else
  printf '\nPush did not complete. Check that the token is current and has repository write access.\n'
fi

printf '\nPress Return to close this window.'
read -r
exit "$push_status"
