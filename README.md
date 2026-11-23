# skills

Agent skills I use, each with a Docker Sandboxes kit that installs it.

| Skill | What it does |
|---|---|
| [humanizer](humanizer/SKILL.md) | Makes text read as written by a person. Carries the list of tells from Wikipedia's "Signs of AI writing" and a script that flags them in a draft. |

## Layout

Each skill is one directory. It is a skill directory (a `SKILL.md` with its `scripts/` and `references/`) and a v3 kit directory (`<name>.yaml` and `<name>.dockerfile`) at once, so the kit builds from the files beside it and there is no second copy to keep in step.

```
humanizer/
  SKILL.md               the skill
  scripts/check.py       the checker
  references/            the list of tells, and a voice profile
  evals/                 test cases for the skill
  humanizer.yaml         kit descriptor
  humanizer.dockerfile   kit recipe
```

## Use a skill in a sandbox

The kit is a mixin, so it goes on top of an agent:

```console
$ git clone git@github.com:cdupuis/skills.git
$ sbx run claude --kit ./skills/humanizer .
```

Or add it to a sandbox that already exists:

```console
$ sbx kit add my-sandbox ./skills/humanizer
```

`sbx` can also read the kit from git. This repo is private, so the host needs git credentials for it, and the publisher has to be allowed once:

```console
$ sbx settings set kit.allowedSources '["docker.io/","github.com/cdupuis/"]'
$ sbx run claude --kit 'git+https://github.com/cdupuis/skills.git#dir=humanizer' .
```

That `settings set` replaces the list, so include what is already in it.

Nothing is published to a registry yet.

## What the kit does

- It ships the skill at `/usr/share/cdupuis-skills/humanizer` and declares it as `agent-skill@1`. The runtime shows it in the agent's own skill directory, for example `~/.claude/skills/humanizer`.
- It adds a short note to the agent's context (`agent-context`): use the skill before writing prose for the user. The note also gives the path, for agents that have no skill discovery.
- All of its capabilities are optional. A sandbox whose skill store already holds a `humanizer` skill still starts; it keeps the one it has.
- It asks for no network access and no credentials.

The checker needs `python3` in the sandbox. The kit doesn't install it. The `claude` agent kit has it. Without it, the skill still works from its list of tells.

`evals/` is left out of the kit.

## Use a skill without a sandbox

Link the directory into the agent's skill directory:

```console
$ ln -s "$PWD/humanizer" ~/.claude/skills/humanizer
```

## Build and check a kit

```console
$ cd humanizer

# descriptor only; fails in a second on a bad field
$ docker buildx build . -f humanizer.yaml --output type=cacheonly

# build, then check conformance with kit-tck from docker/sandbox-kit-spec
$ docker buildx build . -f humanizer.yaml -t humanizer:1.0.0 \
    --output type=oci,dest=/tmp/humanizer-layout,tar=false
$ kit-tck validate --layout /tmp/humanizer-layout 1.0.0
```

Bump `version:` in the descriptor when the skill changes.
