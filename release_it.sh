# check parameters
if [ "$#" -ne 1 ]; then
    >&2 echo "Illegal number of parameters"
    >&2 echo "usage: ./release_it.sh [major|minor|patch]"
    exit 1
fi


# get variables
RELEASE_PART=$1
CURRENT_BRANCH=$(git branch --show-current)
INFO=$(bump2version --list --dry-run "$RELEASE_PART")
if [ "$?" -ne 0 ]; then
    >&2 echo "Error while running bump2version, exiting"
    exit 1
fi

CURRENT_VERSION=$(echo "$INFO" | grep "current_version" | sed -r s,"^.*=",,)
NEW_VERSION=$(echo "$INFO" | grep "new_version" | sed -r s,"^.*=",,)

# ask
while true; do
    read -p "Do you wish to upgrade from $CURRENT_VERSION to $NEW_VERSION? [y/n] " yn
    case $yn in
        [Yy]* ) break;;
        [Nn]* ) exit 0;;
        * ) echo "Please answer yes or no.";;
    esac
done


# go to dev and ensure latest version
if [[ $CURRENT_BRANCH != "dev" ]]; then
  git checkout dev
fi

git pull

# bump version
bump2version "$RELEASE_PART" --verbose
git push --follow-tags origin dev

# switch back to current branch
if [[ $CURRENT_BRANCH != "dev" ]]; then
  git checkout "$CURRENT_BRANCH"
fi