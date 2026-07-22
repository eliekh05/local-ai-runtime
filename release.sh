#!/bin/bash
set -e

# Bump patch version in pyproject.toml
CURRENT=$(python3 -c "import re; print(re.search(r'version = \"(.+?)\"', open('pyproject.toml').read()).group(1))")
IFS='.' read -r MAJOR MINOR PATCH <<< "$CURRENT"
NEW="$MAJOR.$MINOR.$((PATCH + 1))"

sed -i '' "s/version = \"$CURRENT\"/version = \"$NEW\"/" pyproject.toml

echo "Version: $CURRENT -> $NEW"

rm -rf dist
uv build

# Publish — enter __token__ + your PyPI token when prompted
echo ""
echo "Enter PyPI credentials when prompted:"
echo "  Username: __token__"
echo "  Password: (your pypi token)"
echo ""
uv publish --interactive

git add pyproject.toml
git commit -m "v$NEW"
git tag "v$NEW"
git push && git push --tags

echo "Published v$NEW — test: uvx local-ai-runtime==$NEW"
