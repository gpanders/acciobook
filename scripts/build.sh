#!/bin/sh

# Build wheel and source distribution files and upload them to the associated
# ref on sourcehut and to PyPI.

set -eu

if [ $# -eq 0 ]; then
	echo "Usage: $0 TAG"
	exit 1
fi

if ! command -v poetry >/dev/null; then
	# Install poetry
	echo "poetry not found, installing..."
	curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python3
	. $HOME/.poetry/env
fi

tag=$1
version=$(echo "$tag" | tr -d 'v')

curdir=$(pwd)
tmpdir=$(mktemp -d)

git worktree add "$tmpdir" "$tag"

cd "$tmpdir"

poetry build

# Upload to PyPI
poetry publish -u "$PYPI_USERNAME" -p "$PYPI_PASSWORD"

# Upload to sourcehut
curl -H Authorization:"token $SRHT_TOKEN" -F file=@dist/acciobook-"$version"-py3-none-any.whl https://git.sr.ht/api/repos/acciobook/artifacts/"$tag"
curl -H Authorization:"token $SRHT_TOKEN" -F file=@dist/acciobook-"$version".tar.gz https://git.sr.ht/api/repos/acciobook/artifacts/"$tag"

cd "$curdir"
git worktree remove --force "$tmpdir"
rm -rf "$tmpdir"
