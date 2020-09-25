#!/bin/sh

# Build wheel and source distribution files and upload them to the associated
# ref on sourcehut. SRHT_TOKEN environment variable must be set with a
# sourcehut personal access token.

set -eu

if ! command -v poetry >/dev/null; then
	# Install poetry
	echo "poetry not found, installing..."
	curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python3
	. $HOME/.poetry/env
fi

last_tag=$(git describe --abbrev=0 HEAD)
version=$(echo "$last_tag" | tr -d 'v')

curdir=$(pwd)
tmpdir=$(mktemp -d)

git worktree add "$tmpdir" "$last_tag"

cd "$tmpdir"

poetry build
curl -H Authorization:"token $SRHT_TOKEN" -F file=@dist/acciobook-"$version"-py3-none-any.whl https://git.sr.ht/api/repos/acciobook/artifacts/"$last_tag"
curl -H Authorization:"token $SRHT_TOKEN" -F file=@dist/acciobook-"$version".tar.gz https://git.sr.ht/api/repos/acciobook/artifacts/"$last_tag"

cd "$curdir"
git worktree remove --force "$tmpdir"
rm -rf "$tmpdir"
