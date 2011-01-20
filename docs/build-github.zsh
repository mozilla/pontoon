#!/bin/zsh

# Should be run from the docs directory: (cd docs && ./build-github.zsh)

REPO=$(git config remote.origin.url)
GH=_gh-pages


# Checkout the gh-pages branch, if necessary.
if [[ ! -d $GH ]]; then
    git clone $REPO $GH
    pushd $GH
    git checkout -b gh-pages origin/gh-pages
    popd
fi

# Update and clean out the _gh-pages target dir.
pushd $GH && git pull && rm -rf * && popd

# Make a clean build.
make clean dirhtml

# Move the fresh build over.
cp -r _build/dirhtml/* $GH
cd $GH

# Commit.
git add .
git commit -am "gh-pages build on $(date)"
git push origin gh-pages
