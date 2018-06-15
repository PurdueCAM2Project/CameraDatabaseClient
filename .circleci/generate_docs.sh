#!/bin/bash
# Adopted from https://github.com/eldarlabs/ghpages-deploy-script
# ideas used from https://gist.github.com/motemen/8595451

# abort the script if there is a non-zero error
set -e

# show where we are on the machine
pwd

remote=$(git config remote.origin.url)

# make a directory to put the gp-pages branch
mkdir gh-pages-branch
cd gh-pages-branch
# now lets setup a new repo so we can update the gh-pages branch
git config --global user.email "$GH_EMAIL" > /dev/null 2>&1
git config --global user.name "$GH_NAME" > /dev/null 2>&1
git init
git remote add --fetch origin "$remote"

# switch into the gh-pages branch
if git rev-parse --verify origin/gh-pages > /dev/null 2>&1
then
    git checkout gh-pages
else
    git checkout --orphan gh-pages
fi

# create new site
mkdir pythonAPIClient
cp -a ../pythonAPIClient/* ./pythonAPIClient/
make html
rm -rf pythonAPIClient/*


# stage any changes and new files
git add -A
# now commit, ignoring branch gh-pages doesn't seem to work, so trying skip
git commit --allow-empty -m "Deploy to GitHub pages [ci skip]"
# and push, but send any output to /dev/null to hide anything sensitive
git push --force --quiet origin gh-pages > /dev/null 2>&1

# go back to where we started and remove the gh-pages git repo we made and used
# for deployment
cd ..
rm -rf gh-pages-branch

echo "Finished Deployment!"
