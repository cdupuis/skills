# syntax=docker/dockerfile:1
# The skill is text and one Python script, so it is staged on the
# builder's CPU and the overlay is the same on every platform.
FROM --platform=$BUILDPLATFORM debian:trixie-slim@sha256:a72b4433de1cf7d6bae0c4cee74d0547f58601a643b3375f070c51600d63b6b2 AS build
# The source sits outside any agent's skill directory; the runtime
# exposes it there. evals/ stays out: it tests the skill and is no use to
# an agent that only runs it.
COPY SKILL.md /out/usr/share/cdupuis-skills/humanizer/SKILL.md
COPY references /out/usr/share/cdupuis-skills/humanizer/references
COPY scripts /out/usr/share/cdupuis-skills/humanizer/scripts
# Modes are set here and not taken from the checkout, whose umask may
# have left files unreadable for the agent user. `COPY --chmod` is no
# substitute: it puts the file mode on the directories as well.
RUN <<'SH'
set -eu
cd /out/usr/share/cdupuis-skills/humanizer
test -s SKILL.md
test -s references/tells.md
test -s references/voice.md
test -s scripts/check.py
find /out -name __pycache__ -prune -exec rm -r {} +
find /out -type d -exec chmod 0755 {} +
find /out -type f -exec chmod 0644 {} +
chmod 0755 scripts/check.py
chown -R 0:0 /out
SH

FROM scratch
COPY --from=build /out /
