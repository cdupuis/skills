# syntax=docker/dockerfile:1
# Skills are text and scripts, so they are staged on the builder's CPU
# and the overlay is the same on every platform.
FROM --platform=$BUILDPLATFORM debian:trixie-slim@sha256:a72b4433de1cf7d6bae0c4cee74d0547f58601a643b3375f070c51600d63b6b2 AS build
# The context is the repo; .dockerignore says what stays out of it.
COPY . /src
# Every top-level directory with a SKILL.md is a skill, so adding one
# needs no edit here. The source sits outside any agent's skill
# directory; the runtime exposes it there.
#
# Modes are set here and not taken from the checkout, whose umask may
# have left files unreadable for the agent user. `COPY --chmod` is no
# substitute: it puts the file mode on the directories as well.
RUN <<'SH'
set -eu
dest=/out/usr/share/cdupuis-skills
mkdir -p "$dest"
count=0
for skill in /src/*/; do
  name=$(basename "$skill")
  test -f "$skill/SKILL.md" || continue
  test ! -L "$skill/SKILL.md"
  test -s "$skill/SKILL.md"
  # agent-skill@1 takes a literal path, so the descriptor has to list
  # each skill. Stop here when it doesn't, or the skill would ship and
  # never be shown to an agent.
  grep -qxF "      path: /usr/share/cdupuis-skills/$name" /src/skills.yaml || {
    echo "skills.yaml has no agent-skill@1 entry for $name" >&2
    exit 1
  }
  cp -R "$skill" "$dest/$name"
  # evals/ tests a skill and is no use to an agent that only runs it.
  rm -rf "$dest/$name/evals"
  count=$((count + 1))
done
test "$count" -gt 0
find /out -name __pycache__ -prune -exec rm -r {} +
find /out -type d -exec chmod 0755 {} +
find /out -type f -exec chmod 0644 {} +
find /out -type f -path '*/scripts/*' -exec chmod 0755 {} +
chown -R 0:0 /out
SH

FROM scratch
COPY --from=build /out /
