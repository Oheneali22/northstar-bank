# Continuous integration

Northstar Bank uses GitHub Actions to validate every change before it can be considered for
merge. The workflow is defined in `.github/workflows/ci.yaml` and separates web, API, container,
and Compose checks so failures are isolated. On `main`, the container job also publishes the
validated web and API images to private Amazon ECR repositories.

## Trigger and permission model

The workflow runs for:

- pull requests targeting `main`, which provides pre-merge feedback;
- pushes to `main`, which verifies the final merged commit; and
- manual dispatches, which support troubleshooting and controlled re-runs.

The workflow-level `GITHUB_TOKEN` permission is limited to `contents: read`. The container job
adds `id-token: write` so GitHub can issue an OIDC identity token; this permission does not itself
grant AWS access. AWS validates the token against the IAM role trust policy and returns temporary
credentials only for the protected `main` branch. Concurrent runs for the same pull request or
branch are grouped. Older pull-request runs are cancelled when a new commit arrives, while a
`main` publishing run is allowed to finish so a newer merge cannot interrupt an image push.

## Quality gates

| Check | What it proves | Commands |
| --- | --- | --- |
| Web quality gates | The frontend installs reproducibly, passes tests and lint, and produces a production build. | `pnpm install --frozen-lockfile`, `pnpm test`, `pnpm lint`, `pnpm build` |
| API quality gates | The Python service installs, passes static analysis, and passes its automated tests. | `python -m pip install -e '.[dev]'`, `ruff check .`, `pytest` |
| Container builds | Both production Dockerfiles can produce images from a clean runner; successful `main` builds are published to ECR. | `docker build` on pull requests; BuildKit build and push on `main` |
| Compose validation | The Compose file resolves to a valid application model. | `docker compose config --quiet` |

The Docker job uses a matrix. A matrix applies the same job definition to multiple parameter
sets, reducing duplication while GitHub runs each image build as a separate job. It waits for the
web, API, and Compose jobs. Pull requests build without AWS access; pushes to `main` assume a
restricted IAM role, authenticate to ECR, and publish each image as `sha-<full-commit>`. `fail-fast`
is disabled so one failed image does not hide the result of the other image.

## Private image publishing

The repository must define the GitHub Actions variables `AWS_ROLE_ARN` and `AWS_REGION`. The IAM
role trusts GitHub's OIDC provider only for `Oheneali22/northstar-bank` on `main` and currently uses
the AWS-managed `AmazonEC2ContainerRegistryPowerUser` policy. No long-lived AWS access key is
stored in GitHub. Before production use, replace the broad managed policy with a customer-managed
policy scoped to the `northstar-web` and `northstar-core-api` repositories and required push actions.

ECR repositories use immutable tags. The workflow therefore publishes only traceable tags such as
`sha-012345...`; it does not publish `latest`. A later deployment workflow must receive or resolve
an exact image tag and deploy that same artifact without rebuilding it.

## Reproducibility and supply-chain controls

- Node.js, Python, and pnpm use explicit major or exact versions matching project requirements.
- pnpm uses the committed lockfile with `--frozen-lockfile`; dependency drift fails the job.
- GitHub Actions are pinned to full commit SHAs. The adjacent version comments make intentional
  upgrades discoverable without relying on mutable tags at runtime.
- Dependency caches improve speed, but `node_modules` and the Python environment are rebuilt on
  every clean runner. A cache is an optimization, not a source artifact.
- Every job has a timeout to bound stuck processes and runner consumption.

## Local equivalents

Run the same gates before pushing:

```bash
pnpm install --frozen-lockfile
pnpm test
pnpm lint
pnpm build

cd services/core-api
python -m pip install -e '.[dev]'
ruff check .
pytest
cd ../..

docker build --file Dockerfile --tag northstar-web:ci .
docker build \
  --file services/core-api/Dockerfile \
  --tag northstar-core-api:ci \
  services/core-api
docker compose config --quiet
```

## Investigating a failed run

1. Identify the first failed step in the affected job; later failures may be consequences.
2. Reproduce that exact command locally with the project version of the runtime.
3. Fix the cause rather than weakening or skipping the quality gate.
4. Re-run all checks affected by the change and push the fix to the same pull request.
5. If a runner or dependency service failed transiently, document the evidence before re-running.

Do not automatically assume a red build is an infrastructure problem. A useful CI system makes
failures deterministic enough to distinguish a code defect from a transient platform failure.

## Recommended branch protection

After the workflow has completed successfully on the default branch, configure a ruleset for
`main` that:

- requires a pull request before merging;
- requires the web, API, both container-build, and Compose checks;
- requires branches to be current with `main` before merging;
- blocks force pushes and branch deletion; and
- requires conversation resolution.

Repository rules are an external GitHub setting and are not silently changed by this workflow.
Required check names should be selected only after GitHub has observed the workflow once.

## Interview discussion

Be prepared to explain:

- why pull-request CI and post-merge CI are both valuable;
- why jobs are independent instead of one long shell script;
- the difference between dependency caching and build artifacts;
- why full action SHAs are safer than mutable version tags;
- why pull-request builds receive no AWS credentials while `main` uses OIDC and a restricted IAM
  role to publish; and
- why a successful image build is useful but does not replace integration or runtime tests.
