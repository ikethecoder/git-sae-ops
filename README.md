# git-sae-ops


## Building

```

docker build --tag git-sae-ops .

```

## Running

```
export GITHUB_TOKEN=""

export PROJECTSC_HOST=""
export PROJECTSC_TOKEN=""

export GIT_USER_EMAIL=""
export GIT_USER_USERNAME=""

bin/glclic hello

```


# Commands

## Onboard project

Create a new repository in the SAE shares group and a corresponding one in the checkpoint group, and grant access to the appropriate groups.

```
./bin/glclic \
    --project project-A \
    --importUrl https://github.com/ikethecoder/external-test-repo.git \
    project
```

OR 

```
./bin/glclic \
    --project project-A \
    --repo somerepo \
    project
```


## Export Files

### Prepare for export

Called when a Researcher is ready to export files from the SAE.

```
./bin/glclic \
    --branch master \
    --repo ikethecoder-external-test-repo \
    --importUrl https://github.com/ikethecoder/external-test-repo.git \
    request-export
```


### Approve the export merge request

Typically performed by an output checker in Gitlab.

```
./bin/glclic \
    --branch master \
    --repo ikethecoder-external-test-repo \
    approve-export-merge

```

### Perform push to external repository

```
./bin/glclic \
    --branch master \
    --repo ikethecoder-external-test-repo \
    --importUrl https://github.com/ikethecoder/external-test-repo.git \
    push-to-external
```


## Import Files

### Prepare for import

Called when a Researcher is ready to import files into the SAE.

```
./bin/glclic \
    --branch master \
    --importUrl https://github.com/ikethecoder/external-test-repo.git \
    request-import
```

### Approve the import merge request

Typically performed by an output checker in Gitlab.

```
./bin/glclic \
    --branch master \
    --repo ikethecoder-external-test-repo \
    approve-import-merge

```

### Perform push to sre repository

```
./bin/glclic \
    --branch master \
    --repo ikethecoder-external-test-repo \
    push-to-sae
```


## Other commands

### Cancel an Import

```
./bin/glclic \
    --branch master \
    --repo ikethecoder-external-test-repo \
    cancel-import
```

### Cancel an Export

```
./bin/glclic \
    --branch master \
    --repo ikethecoder-external-test-repo \
    cancel-export
```
