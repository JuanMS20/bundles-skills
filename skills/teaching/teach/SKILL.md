---
name: teach
description: "Teach the user a new skill or concept within a teaching workspace. Stateful, multi-session learning framework with MISSION.md, GLOSSARY.md, RESOURCES.md, and learning-records/. Use when user wants to learn a topic systematically."
---

# Teach Skill

Teach the user a new skill or concept. The current directory is treated as a **teaching workspace**.

## Teaching Workspace Components

| File | Purpose |
|------|---------|
| `MISSION.md` | Why the user wants to learn this topic |
| `GLOSSARY.md` | Terminology for the topic |
| `RESOURCES.md` | High-quality, trusted resources |
| `./learning-records/*.md` | What the user has learned (numbered 0001-*.md) |

## Teaching Philosophy

Three pillars:
1. **Knowledge**: From high-quality, trusted resources
2. **Skills**: Through hands-on exercises
3. **Wisdom**: From real-world interaction

## Key Rules

1. **Mission First**: Every session must tie back to MISSION.md. If unclear, question the user.
2. **Zone of Proximal Development**: Challenge "just enough". Scope tight, tied to mission.
3. **Never Trust Parametric Knowledge**: All knowledge from verified resources, not model memory.
4. **Feedback Loops**: Every exercise needs immediate performance feedback.
5. **Glossary Compliance**: All workspace files must use glossary terms.

## Process

1. Read or create MISSION.md (why do you want to learn this?)
2. Populate RESOURCES.md with trusted sources
3. Build GLOSSARY.md as terms are encountered
4. Teach via HTML explainers or interactive exercises
5. Create learning-records for each topic mastered
6. Find communities for wisdom-building

## Format Files

See linked files for MISSION.md, GLOSSARY.md, RESOURCES.md, and learning-records formats.
