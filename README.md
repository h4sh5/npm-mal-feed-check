# NPM Mal Feed Check

A github action to check if your package.json or package-lock.json contains malicious packages. Exit with failure if it does. 

Useful for `on: push` status checks for supply chain security.

Currently pulls the past 90 days of malicious package bulletins, for efficiency and rate limiting.

## Example usage

Put the below blob in your repo under `.github/workflows/mal_npm_check.yml`

(No need to put `GITHUB_TOKEN` in your github action secrets unless you do not want to use Github Action's [automated token authentication](https://docs.github.com/en/actions/security-guides/automatic-token-authentication#permissions-for-the-github_token))

```yaml
name: Check for malicious npm dependencies

on:
  push:

  workflow_dispatch:
    inputs:
      git-ref:
        description: Git Ref (Optional)
        required: false

jobs:
  mal_check:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - uses: h4sh5/npm-mal-feed-check@main
      env:
        GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

Optionally, protect your `main` branch by setting up a branch protection rule that requires Pull Requests and require status checks to pass before merging. That will block PRs that have malicious dependencies in them.

Example repo using this workflow: https://github.com/h4sh5/malicious-dependency-examples/

