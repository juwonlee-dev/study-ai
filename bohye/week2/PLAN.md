# Week 2 HTML Implementation Plan

**Goal:** Recreate `bohye/week1/profile.png` as a standalone HTML/CSS page.

**Source:** [Issue #22](https://github.com/juwonlee-dev/study-ai/issues/22) and the approved original-faithful layout.

**Files:** `ASSIGNMENT.md` records the task criteria; `profile.html` contains semantic content and CSS; `prompt.md` records the complete user/AI conversation and Orca use.

## Steps

1. Record Issue #22 requirements and compare the PNG with the Week 0 README for exact wording.
2. Build `profile.html` with live text, CSS shapes, the same section order and visual hierarchy as the PNG. Use responsive columns for narrow screens. Do not embed the PNG or introduce external dependencies.
3. Open the page in Orca and inspect desktop and mobile renders for missing text, overlap, clipping, and horizontal overflow.
4. Record all user prompts and AI responses in `prompt.md`, including the final verification result.
5. Recheck the issue requirements, file paths, and Git status. Leave Git and GitHub changes for explicit instructions under `bohye/AGENTS.md`.

## Review focus

- Original section text is present, selectable and in the same order.
- No part of `profile.png` is used as page artwork.
- Cards remain readable on a narrow viewport and when the page is zoomed.
- Decorative layers do not obscure the content.
- Files created or changed remain under `bohye/week2/`.
