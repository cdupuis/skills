---
tags: [skill-creator]
max_turns: 20
timeout_seconds: 600
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Bash]
---

write a slack msg for #eng-builds: nightly image build went from 38 min to 11 after I took the commit SHA out of the base layer cache key (the layer only depends on the lockfile). two tests are still flaky, test_volume_mount and test_proxy_reconnect, about 1 in 20 runs, cause unknown. want to roll this out to all pipelines monday unless someone objects. save it to slack-message.txt
