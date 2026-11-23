---
tags: [skill-creator]
max_turns: 20
timeout_seconds: 600
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Bash]
---

write the commit message and the PR description for this change, as commit.txt and pr.md. the change: retry wrapper around the registry client's token refresh. before, a 401 in the middle of a long push killed the upload. now we refresh the token once and retry the failed chunk. added a test with a fake registry that expires the token after 2 chunks. no behaviour change for pulls. fixes #482. I didn't touch the backoff logic in the client, that's a separate PR.
