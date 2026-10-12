---
name: session-close
description: Close a WhoLLsoMe work session — write the day's session log in logs/, update STATUS.md, tick finished items in docs/Plan.md, commit, and start any long unattended job. Use when Shailesh says he is wrapping up or ending the session, or when the session's planned work is done.
---

# Session close

Run these steps in order. Don't skip one because the session was short.

1. **Find the plan day.** Read `STATUS.md` and `docs/Plan.md` → section 5. The log file is `logs/DNN.md` (two digits, e.g. `logs/D04.md`). If it already exists, append a new entry for this session rather than overwriting.
2. **Write the log** using `log-template.md` in this folder. Evidence means numbers, samples, file paths and eval scores, not narration. A claim without evidence goes under Flags as a gap.
3. **Phase stops.** On Day 14, 21 or 32, check that the phase report from `CLAUDE.md` section 4.2 exists. If not, say so and write it before closing.
4. **Update `STATUS.md`:** last-update date, plan day, done, next session's task, open decisions, latest eval results, parking list, and section 6 (token calibration) if a heavy run happened.
5. **Tick finished items** in `docs/Plan.md` section 5 (`- [ ]` → `- [x]`). Change nothing else in the plan; deviations go in the log under Flags.
6. **Restricted-text check (blocking).** Run `python3 pipeline/restricted.py split`, then `git add` the session's work, then `python3 pipeline/restricted.py check`. If the check reports any staged file holding text from a restricted source (`restricted = true` in `pipeline/sources.toml`), **stop**: do not commit. Unstage that file or move its restricted share to `corpus/restricted/`, run the check again, and note it under Flags. Then run `python3 evals/sets.py check`: if any staged file holds text of a private crisis test statement (`evals/private/crisis.jsonl`), **stop** the same way and remove that text. Both checks run as a git pre-commit hook; never bypass it with `--no-verify`.
7. **Commit** with a message starting with the plan day, e.g. `D04: normalise sources, pilot extraction`. Never commit `.env` or other secrets.
8. **Long jobs:** if the next task can run unattended (extraction, tagging, eval runs), first follow `CLAUDE.md` section 4.3 (usage reading, estimate, agreed budget), then start it and note in the log what is running, its budget and how to check on it.
9. **Report to Shailesh** in at most 5 lines: what got done, any flags, decisions needed from him, next session's task.
