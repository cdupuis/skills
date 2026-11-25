# skills

Agent skills I use, and a Docker Sandboxes kit that installs them.

| Skill | What it does |
|---|---|
| [humanizer](humanizer/SKILL.md) | Makes text read as written by a person. Carries the list of tells from Wikipedia's "Signs of AI writing" and a script that flags them in a draft. |

The kit also installs skills from other repos. They are not copied into this repo; the build fetches each at a pinned commit, listed in [`external.txt`](external.txt).

| Source | Version | Skills | License |
|---|---|---|---|
| [obra/superpowers](https://github.com/obra/superpowers) | v7.0.2 | 15 | MIT |
| [emilkowalski/skills](https://github.com/emilkowalski/skills) | `main` at 64eb3de (2026-11-15) | 20 | MIT |
| [pbakaus/impeccable](https://github.com/pbakaus/impeccable) | skill-v4.9.1 | 1 | Apache-2.0 |
| [Leonxlnx/taste-skill](https://github.com/Leonxlnx/taste-skill) | v2.5.1 | 1 | MIT |

## Layout

Each skill is one top-level directory with a `SKILL.md`. One v3 mixin kit at the root of the repo installs all of them.

```
skills.yaml            kit descriptor
skills.dockerfile      kit recipe
external.txt           skills from other repos, pinned
humanizer/
  SKILL.md             the skill
  scripts/check.py     the checker
  references/          the list of tells, and a voice profile
  evals/               test cases for the skill
```

## Add a skill

1. Add a directory with a `SKILL.md`. The recipe picks up every top-level directory that has one.
2. Add an `agent-skill@1` entry for it to `skills.yaml`. The path has to be written out there, so the build fails when a skill has no entry.
3. Bump `version:` in `skills.yaml`.

## Add or update an external skill

1. Add a line to `external.txt`: the repo, a full commit id, the SHA-256 of that commit's tarball, and where the skills are in the repo. The file explains the format. To update a source, change the commit and the checksum.

   ```console
   $ curl -fsSL https://codeload.github.com/OWNER/REPO/tar.gz/COMMIT | sha256sum
   ```

2. Add an `agent-skill@1` entry to `skills.yaml` for each skill the source brings, and remove entries for skills it dropped. The build names the ones that are missing or left over.
3. Bump `version:` in `skills.yaml`.

Two skills can't have the same directory name; the build stops when they do.

## Use the skills in a sandbox

The kit is a mixin, so it goes on top of an agent:

```console
$ git clone git@github.com:cdupuis/skills.git
$ sbx run claude --kit ./skills .
```

Or add it to a sandbox that already exists:

```console
$ sbx kit add my-sandbox ./skills
```

`sbx` can also read the kit from git. This repo is private, so the host needs git credentials for it, and the publisher has to be allowed once:

```console
$ sbx settings set kit.allowedSources '["docker.io/","github.com/cdupuis/"]'
$ sbx run claude --kit 'git+https://github.com/cdupuis/skills.git' .
```

That `settings set` replaces the list, so include what is already in it.

## Publish and use the registry kit

The [publish kit workflow](.github/workflows/publish-kit.yaml) runs on
every branch push and can also be started from the Actions page. It calls
[Docker's shared builder](https://github.com/docker/github-builder) to
build `skills.yaml` for `linux/amd64` and `linux/arm64`. The builder reads
the committed Git source, including the companion recipe and external
skill pins.

Each platform builds on its own native runner with `distribute: true`.
The workflow requests an SPDX SBOM, and the shared builder generates and
signs attestations with SLSA v1 provenance. Provenance uses `mode=min`
for this private repository and `mode=max` for public repositories.
The combined index retains these attestations. Kit annotations remain
on the platform manifests, so TCK warns about their absence on the index.

The workflow pins the official kit frontend from commit `49950e9` by
digest through `BUILDKIT_SYNTAX`. This frontend supports the builder's
Git context. The current `:3` frontend does not yet include that support.

Each run publishes `ghcr.io/cdupuis/skills:sha-<full-commit-sha>` using
the repository's `GITHUB_TOKEN`. No registry secret is needed. The
workflow does not publish release tags or `latest`, and the kit version
still comes from `skills.yaml`.

A separate job checks both platform manifests and reads each platform's
SBOM and provenance from the registry. It checks that the provenance
names the current workflow run as its builder, then runs checksum-pinned
`kit-tck` v3.0.0-m.13, installed by the spec repository's `setup-tck`
action, against the published digest. The workflow passes
only after validation passes. Its summary gives the immutable image
reference to use in a sandbox.

The GHCR package is private. To pull it, log in with a personal access
token with `read:packages` access to the package:

```console
$ printf '%s' "$GHCR_TOKEN" | docker login ghcr.io --username cdupuis --password-stdin
$ sbx run claude --kit 'ghcr.io/cdupuis/skills@sha256:<digest>' .
```

Replace `<digest>` with the value from the successful run's summary.
Allow `ghcr.io/cdupuis/` in `kit.allowedSources` alongside your existing
entries before the first use.

## What the kit does

- It ships each skill at `/usr/share/cdupuis-skills/<name>` and declares it as `agent-skill@1`. The runtime shows it in the agent's own skill directory, for example `~/.claude/skills/humanizer`.
- It adds a short note to the agent's context (`agent-context`): use the humanizer skill before writing prose for the user. The note also gives the path, for agents that have no skill discovery.
- All of its capabilities are optional. A sandbox whose skill store already holds a skill of the same name still starts; it keeps the one it has.
- It asks for no network access and no credentials.

The upstream licenses are in `/usr/share/doc/cdupuis-skills/`.

Some skills need things the kit doesn't install or set up:

- The humanizer checker needs `python3`. The `claude` agent kit has it. Without it, the skill still works from its list of tells.
- superpowers is installed as plain skills. Its plugin also has a session-start hook that loads `using-superpowers` into every session; the kit doesn't set that up, so the agent picks these skills by their descriptions.
- impeccable is upstream's Claude Code build. Upstream builds the skill once per agent, and a kit can ship one build under a name. Its launcher downloads an engine binary from the project's GitHub releases on first run, so the sandbox needs network access to github.com for that.
- taste-skill needs Node 22 or later and Chrome, Edge or Chromium for its checker. It is about 36 MB, most of it reference images.

`evals/` directories are left out of the kit.

## Use a skill without a sandbox

Link the directory into the agent's skill directory:

```console
$ ln -s "$PWD/humanizer" ~/.claude/skills/humanizer
```

## Build and check the kit

```console
# descriptor only; fails fast on a bad field
$ docker buildx build . -f skills.yaml --output type=cacheonly

# build, then check conformance with kit-tck from docker/sandbox-kit-spec
$ docker buildx build . -f skills.yaml -t skills:1.1.0 \
    --output type=oci,dest=/tmp/skills-layout,tar=false
$ kit-tck validate --layout /tmp/skills-layout 1.1.0
```

The build downloads the external skills from codeload.github.com.
