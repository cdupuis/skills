# syntax=docker/dockerfile:1
# Skills are text and scripts, so they are staged on the builder's CPU
# and the overlay is the same on every platform.
FROM --platform=$BUILDPLATFORM debian:trixie-slim@sha256:a72b4433de1cf7d6bae0c4cee74d0547f58601a643b3375f070c51600d63b6b2 AS build
RUN apt-get update \
 && apt-get install -y --no-install-recommends ca-certificates curl \
 && rm -rf /var/lib/apt/lists/*

# The context is the repo; .dockerignore says what stays out of it.
COPY . /src

# Two kinds of skill end up side by side in /usr/share/cdupuis-skills:
# every top-level directory of this repo that has a SKILL.md, and the
# skills of the repos listed in external.txt. That path is outside any
# agent's skill directory; the runtime exposes the skills there.
RUN <<'SH'
set -eu
dest=/out/usr/share/cdupuis-skills
docs=/out/usr/share/doc/cdupuis-skills
mkdir -p "$dest" "$docs"

# add SOURCE-DIR: stage one skill under its directory name.
add() {
  name=$(basename "$1")
  test -f "$1/SKILL.md"
  test ! -L "$1/SKILL.md"
  test -s "$1/SKILL.md"
  if [ -e "$dest/$name" ]; then
    echo "two skills are named $name" >&2
    exit 1
  fi
  # agent-skill@1 takes a literal path, so the descriptor has to list
  # each skill. Stop here when it doesn't, or the skill would ship and
  # never be shown to an agent.
  grep -qxF "      path: /usr/share/cdupuis-skills/$name" /src/skills.yaml || {
    echo "skills.yaml has no agent-skill@1 entry for $name" >&2
    exit 1
  }
  cp -R "$1" "$dest/$name"
}

for skill in /src/*/; do
  test -f "$skill/SKILL.md" || continue
  add "${skill%/}"
  # evals/ tests a skill and is no use to an agent that only runs it.
  rm -rf "$dest/$(basename "$skill")/evals"
done

grep -v -e '^#' -e '^[[:space:]]*$' /src/external.txt | while read -r repo commit sha kind path; do
  work=/tmp/external/$repo
  mkdir -p "$work"
  curl -fsSL --retry 3 "https://codeload.github.com/$repo/tar.gz/$commit" -o "$work.tar.gz"
  echo "$sha  $work.tar.gz" | sha256sum -c -
  tar -xzf "$work.tar.gz" --strip-components=1 --no-same-owner -C "$work"
  case "$kind" in
    skill)
      add "$work/$path"
      ;;
    skills)
      found=0
      for skill in "$work/$path"/*/; do
        test -f "$skill/SKILL.md" || continue
        add "${skill%/}"
        found=1
      done
      test "$found" = 1
      ;;
    *)
      echo "external.txt: unknown kind $kind for $repo" >&2
      exit 1
      ;;
  esac
  # The licenses ask for their text to travel with the copies.
  owner=${repo%/*}
  mkdir -p "$docs/$owner-${repo#*/}"
  test -s "$work/LICENSE"
  for f in LICENSE NOTICE NOTICE.md; do
    if [ -f "$work/$f" ]; then cp "$work/$f" "$docs/$owner-${repo#*/}/"; fi
  done
done

# An entry in skills.yaml with no skill behind it is a mistake too.
sed -n 's|^      path: /usr/share/cdupuis-skills/||p' /src/skills.yaml | while read -r name; do
  test -f "$dest/$name/SKILL.md" || {
    echo "skills.yaml lists $name, which no source provides" >&2
    exit 1
  }
done

find /out -name __pycache__ -prune -exec rm -r {} +
# Readable by the agent user whatever umask the checkout had. Files that
# were executable stay executable.
chmod -R u=rwX,go=rX /out
chown -R 0:0 /out
SH

FROM scratch
COPY --from=build /out /
