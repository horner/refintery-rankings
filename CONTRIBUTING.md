# Contributing

## Preview required before merge

Contributors and coding agents must include a working GitHub Pages preview hosted in their own fork for any pull request that changes the published site, data, generated output, or publishing behavior. Reviewers must be able to open and review the proposed result before merging it into `horner/refintery-rankings`.

Include a **Preview** section in the PR description with:

- The contributor-owned Pages URL.
- The full PR commit SHA deployed to that URL.
- A link to the successful Pages workflow run.
- What you checked in the browser, including a narrow/mobile viewport and the pages or interactions affected.

Verify that the URL opens without contributor-only access, loads its assets and data, and shows the proposed changes. A repository link, a localhost address, screenshots alone, or the upstream publication is not a hosted preview.

Redeploy after changes and update the deployed SHA and workflow link. Keep the preview available until review and merge are complete. A fork normally has one Pages site, so deploying another branch can replace the preview; keep the URL pointed at the commit being reviewed.

For a documentation-only PR that changes no published files or deployment behavior, write **Documentation only — hosted preview not required** in the Preview section and explain why. All PRs must include this section.

## Publish a preview from your fork

The existing [Pages workflow](.github/workflows/pages.yml), named **Publish interactive rankings**, rebuilds and verifies the project and publishes `broadcast/dist`.

1. Push your proposed changes to a branch in your own fork.
2. Open your fork's **Actions** tab and enable workflows if GitHub prompts.
3. In your fork's **Settings → Pages → Build and deployment → Source**, choose **GitHub Actions**. Reuse the existing workflow; it uploads the built site rather than the repository root.
4. Open **Actions → Publish interactive rankings → Run workflow**, select your PR branch, then run it. The workflow must also exist on the fork's default branch for the manual-run option to be available.
5. If deployment is blocked by a branch rule, configure your fork's **Settings → Environments → github-pages** to allow the preview branch.
6. After the deployment succeeds, open the URL reported by the deployment. Normally it is `https://<your-github-username>.github.io/refintery-rankings/`. Check that it shows your changes, then add the URL, deployed commit SHA, and workflow-run link to the PR.

Pushes to `main` trigger this workflow automatically. Other branches require a manual run after each update. Generated files must be committed and match their sources: the workflow checks this with `git diff --exit-code`.

Make these settings changes in your fork only. Do not change the upstream Pages source or run an upstream production deployment to obtain a preview. The upstream `main` branch publishes the live site.

GitHub documentation: [Pages publishing sources](https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site) and [running a workflow manually](https://docs.github.com/en/actions/how-tos/manage-workflow-runs/manually-run-a-workflow).

## Prepare and validate changes

Follow the [README build and verification commands](README.md#rebuild-and-verify) and the [correction guidelines](README.md#contributing-corrections). Preserve source evidence, provenance, and generated-file consistency. Include the relevant verification results in the PR.

For a local check before publishing your fork preview, serve the committed site from the repository root:

```sh
python3 -m http.server 8765 --bind 127.0.0.1 --directory broadcast/dist
```

Open `http://127.0.0.1:8765/`. This local check supplements the hosted preview required for review.
