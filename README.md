# skills

Agent skills I use, and a Docker Sandboxes kit that installs them.

| Skill | What it does |
|---|---|
| [humanizer](humanizer/SKILL.md) | Makes text read as written by a person. Carries the list of tells from Wikipedia's "Signs of AI writing" and a script that flags them in a draft. |

## Layout

Each skill is one top-level directory with a `SKILL.md`. One v3 mixin kit at the root of the repo installs all of them.

```
skills.yaml            kit descriptor
skills.dockerfile      kit recipe
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

Nothing is published to a registry yet.

## What the kit does

- It ships each skill at `/usr/share/cdupuis-skills/<name>` and declares it as `agent-skill@1`. The runtime shows it in the agent's own skill directory, for example `~/.claude/skills/humanizer`.
- It adds a short note to the agent's context (`agent-context`): use the humanizer skill before writing prose for the user. The note also gives the path, for agents that have no skill discovery.
- All of its capabilities are optional. A sandbox whose skill store already holds a skill of the same name still starts; it keeps the one it has.
- It asks for no network access and no credentials.

The humanizer checker needs `python3` in the sandbox. The kit doesn't install it. The `claude` agent kit has it. Without it, the skill still works from its list of tells.

`evals/` directories are left out of the kit.

## Use a skill without a sandbox

Link the directory into the agent's skill directory:

```console
$ ln -s "$PWD/humanizer" ~/.claude/skills/humanizer
```

## Build and check the kit

```console
# descriptor only; fails in a second on a bad field
$ docker buildx build . -f skills.yaml --output type=cacheonly

# build, then check conformance with kit-tck from docker/sandbox-kit-spec
$ docker buildx build . -f skills.yaml -t skills:1.0.0 \
    --output type=oci,dest=/tmp/skills-layout,tar=false
$ kit-tck validate --layout /tmp/skills-layout 1.0.0
```
