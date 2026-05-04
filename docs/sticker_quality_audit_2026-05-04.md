# Sticker Quality Audit: 2026-05-04

Scope: audit the 10 automated static sticker packs created on 2026-05-04 and turn the failure modes into reusable factory improvements.

## Executive Finding

The 10 packs are technically packageable, but they are not market-grade LINE sticker products. They pass file validation because the factory mostly checks dimensions, transparency, metadata, source traceability, ZIP order, and review-risk keywords. Those checks do not prove commercial quality.

The user's critique is correct:

- Most packs look closer to low-effort legacy free sticker art than current paid creator stickers.
- Character appeal is weak or missing.
- Expression variety is too small.
- Many items communicate only after reading the text; the pose itself does not carry the message.
- The local text-composition fallback creates detached label-like text, which makes the artwork feel generic.
- The packs satisfy "one phrase" mechanically, but they do not create a compelling repeated-use character world.
- The automated QA incorrectly treated `validation PASS` as readiness.

`futon_called_me` is the closest to usable because it has a soft character premise and some visual charm. Even that pack still needs stronger expressions, more distinct silhouettes, and better integrated lettering before it should be considered sellable.

## Market Reality Check

Current LINE Store and Creators Market pages show that successful creator stickers are not merely valid PNG sets. They tend to combine:

- A recognizable character with repeatable visual identity.
- Large readable expressions and emotional poses.
- Daily-use phrases, greetings, polite language, funny replies, or relationship-specific reactions.
- Strong silhouettes and close-up faces that read at chat size.
- Clear item-to-item variation: mood, gesture, camera distance, props, and message function.
- Integrated text that looks designed with the artwork, not pasted below it.
- A coherent product promise buyers can understand in seconds.

Relevant sources checked:

- LINE Creators sticker guidelines: https://creator.line.me/en/guideline/sticker/
- LINE Creators Japanese sticker guidelines: https://creator.line.me/ja/guideline/sticker/
- LINE Creators review guidelines: https://creator.line.me/ja/review_guideline/
- LINE Store top creators showcase: https://store.line.me/stickershop/showcase/top_creators/en
- LINE Store cute top creators showcase: https://store.line.me/stickershop/showcase/top_creators/en?taste=1

LINE's own guideline language is especially relevant: recommended stickers are easy to use in daily conversation and have understandable expressions, messages, and illustrations. Non-recommended examples include hard-to-use objects/scenery, poor visibility, and sets that lack variety.

## What Failed

### 1. Market Research Was Too Shallow

The previous process reduced market research to "daily replies and short text are popular." That is not enough.

Missing research dimensions:

- How popular packs create a mascot or character hook.
- How much of the meaning is readable without text.
- Common camera patterns: close-up face, bust shot, exaggerated full body, reaction pose.
- Text treatment: handwritten, shaped, integrated, expressive, not generic labels.
- Competitive density: cute animals, cats, rabbits, bears, office humor, polite messages, weird micro-characters.
- Buyer motivation: "I want this character in my chat," not just "this sentence is useful."

### 2. The Prompt Strategy Produced Generic Sheet Art

Generating one 4x2 sheet per pack was efficient but quality-damaging.

Observed problems:

- Items inherit the same scale and pose rhythm.
- The model optimizes for "eight small variations" instead of eight polished stickers.
- Character design is underdeveloped because the prompt asks for object poses, not a mascot sheet first.
- The output has no iteration loop for the strongest single character.
- Cropping cells from a sheet loses composition control per sticker.

Future rule: production-quality stickers need character development first, then one image per final sticker or a high-quality controlled batch only after style lock.

### 3. Character Design Was Not Treated as a Gate

Most packs use "object with face" as a default. That is not enough.

Missing character criteria:

- Distinct head/body shape.
- Memorable face proportions.
- Signature accessory or visual gimmick.
- Repeatable emotional range.
- A reason buyers would like the character, not just understand the object.
- Differentiation from generic clip-art mascots.

`stapler_apology`, `drop_it_there`, `meeting_too_long`, and `rice_first` are especially weak here. They read as utility icons with captions, not characters.

### 4. Expression and Use-Case Variety Were Underspecified

The item plans described physical object actions, not communication intents.

Bad pattern:

- "holding ladle"
- "checking timer"
- "placing box"
- "looking at clock"

Better pattern:

- "Please wait, I am actively preventing disaster."
- "I saw this, but cannot respond yet."
- "I am sorry in a small work-safe way."
- "I am rushing but still not out the door."

Each sticker should have a primary chat function and an emotional state. The generated packs mostly have props but not emotions.

### 5. Text Handling Degraded Product Quality

The local text fallback solved text accuracy but harmed sticker quality.

Problems:

- The white rounded label is detached from the artwork.
- Text takes too much vertical space while the character remains small.
- The label makes every pack feel like a template.
- Chat-size readability is technically okay, but it is not aesthetically integrated.
- The visual meaning often depends entirely on the label.

Future rule: if text is required, the style lock must define a text system: hand lettering, expressive motion type, speech shape, object-integrated lettering, or a deliberate caption format. A generic fallback label should be treated as emergency-only and should fail market-grade QA.

### 6. Validation Confused Compliance With Readiness

The CLI did what it was built to do: ensure files are valid and packageable. The failure is that the production workflow treated that as sellable quality.

Missing gates:

- Market-grade score.
- Character appeal score.
- Expression readability without text.
- Pack variety score.
- Text integration score.
- Currentness score.
- Human visual audit requirement when automated mode produces weak art.

Automated mode must not mean "mark READY after compliance validation." It means "do not stop for HAG, but run stricter automated QA and record a readiness decision."

## Pack-Level Audit

### pot_watch_delay

- Strength: premise is specific and usable.
- Failure: pot face is generic; most poses read the same.
- Failure: "I am watching the pot" depends on text, not action.
- Needed: larger face, more steam disasters, boil-over panic, calm guarding pose, taste-check comedy, distinct emotional arc.

### futon_called_me

- Strength: soft, cute, closest to marketable.
- Failure: too low contrast and too similar in silhouette.
- Needed: stronger sleepy expressions, more face close-ups, integrated handwritten sleep text, one lovable futon mascot design.

### stapler_apology

- Strength: work-safe apology niche is usable.
- Failure: stapler is an office icon, not a charming apologetic character.
- Needed: face-forward guilt, bowing exaggeration, paper cuts avoided, "tiny sincere coworker" persona, more expressive body language.

### drop_it_there

- Strength: practical household/work use.
- Failure: pack is visually the weakest as a character product; it reads like delivery icons.
- Needed: a porter mascot, hands/gesture language, clearer "left it here" spatial comedy, arrows or location cues designed into the art.

### presence_only

- Strength: concept is weird and useful for low-energy replies.
- Failure: quietness became low-impact and unclear.
- Needed: stronger "barely here" face, peeking comedy, higher contrast, specific visible emotional states like shy, exhausted, monitoring, lurking politely.

### almost_leaving

- Strength: common use case.
- Failure: generated character is inconsistent and visually busy; some cells look like unrelated small scenes.
- Needed: one frantic entryway mascot, big sweat/eyes, key/door/shoe symbols, clear "not yet out" gag.

### rice_first

- Strength: lifestyle specificity is memorable.
- Failure: rice cooker is too static; rice grains are not lovable enough.
- Needed: rice-grain cast with faces, cooking-status drama, steam reveal, "almost done" tension.

### pre_read_ack

- Strength: phrase is funny and current for work/friend chats.
- Failure: document fairy is too tiny and the joke does not read from the image.
- Needed: huge premature OK gesture, unread document stack, reckless stamp action, expressive eyes, stronger comedic timing.

### melting_time

- Strength: surreal concept has potential.
- Failure: too many small abstract blobs; no recognizable recurring character.
- Needed: a melting-clock mascot with face, visible panic/exhaustion, bold puddle shapes, fewer tiny details.

### meeting_too_long

- Strength: office use case is real.
- Failure: chairs and desks feel like icons; emotional readability is weak.
- Needed: one exhausted chair character, deadpan office humor, stronger poses, visible meeting-duration gag.

## Root Causes

1. The factory lacked a market-grade quality definition.
2. Automated mode waived human approvals but did not add stronger taste checks.
3. The workflow skipped competitive visual reference analysis.
4. The concept generator optimized for novelty, not buyer desire.
5. The item plan required 10 ideas but did not require 10 distinct communication intents.
6. The prompt did not develop a mascot before generating final items.
7. The image generation strategy optimized throughput over art direction.
8. The final QA only checked technical packaging and obvious risk, not sellability.

## Required Factory Changes

### P0: Add a Market-Grade Readiness Gate

Before any production project is marked READY, require a separate `market_quality.md` report with scores for:

- Character appeal.
- Chat-size readability.
- Expression readability without text.
- Text integration.
- Pack variety.
- Current market fit.
- Use-case clarity.
- Style consistency.
- Rights/review safety.

Any score below the configured threshold should keep the project in `needs_revision`, even if `validate` passes.

### P0: Separate Compliance PASS From Sellable READY

Statuses should mean:

- `valid`: file package passes technical validation.
- `needs_revision`: market-grade QA fails.
- `ready_for_manual_upload`: technical validation passes and market-grade QA passes.

The current projects should be considered `valid` at most, not truly ready for sale.

### P0: Require Competitive Moodboard Notes

For every production pack, record:

- 5-10 market observations from current LINE Store or creator ranking pages.
- 3 visual traits to emulate at a high level, without copying IP or artist style.
- 3 overused patterns to avoid.
- Buyer promise in one sentence.

This is not a license to copy characters. It is a way to understand current design expectations.

### P0: Add Character Design Before Item Production

Workflow should require:

1. Character premise.
2. Silhouette thumbnails.
3. Face/expression sheet.
4. Style lock.
5. Item plan.
6. Production images.

Generating final item art before character approval should fail the workflow.

### P1: Rewrite Item Plans Around Communication Intent

Each item needs:

- Phrase.
- Chat function.
- Emotional state.
- Visual action.
- Camera distance.
- Difference from neighboring items.
- Must-read-without-text note.

Example:

```text
Phrase: もうすぐ出ます
Chat function: reassure waiting person
Emotion: panicked but optimistic
Visual: mascot with one shoe on, key in mouth, door half open
Camera: close bust/full-body hybrid
Meaning without text: clearly rushing out
Difference: larger face and key gag, not another generic doorway pose
```

### P1: Ban Generic Text Labels in Production QA

Generic detached labels should trigger a market-quality failure unless the style lock explicitly justifies them.

Allowed text systems:

- Handwritten integrated lettering.
- Speech-like shape specific to the character world.
- Text formed by steam, paper, motion lines, puddles, or props.
- Deliberate clean caption style only when it is part of a strong brand system.

### P1: One Final Image Per Item

Avoid 4x2 sheet generation for final production. Use it only for rough ideation.

Final generation should be one prompt per sticker so that each item can control:

- Face size.
- Gesture.
- Text placement.
- Camera distance.
- Composition.
- Negative space.
- Emotional readability.

### P1: Add Currentness and Taste QA

Visual QA should flag:

- Legacy clip-art look.
- Overly small character.
- Weak face.
- Same pose repeated.
- Pale low-impact palette.
- Detached text label.
- Icon-like object without character charm.
- Prompt-sheet artifacts.
- Meaning unclear if the text is hidden.

### P2: Keep a Failure Corpus

Move the current 10-pack output into a documented internal failure corpus or mark it clearly as `quality_rejected`.

Use it to test future QA reports:

- It should pass file validation.
- It should fail market-grade readiness.

## Next Implementation Plan

1. Add `rules/sticker_market_quality.yml`.
2. Add `python -m line_factory.cli market-audit --project ...`.
3. Generate `reports/market_quality.md`.
4. Block `ready_for_manual_upload` when market quality fails.
5. Update `generate-plan` to require competitive notes, character design, and communication-intent item plans.
6. Update workflows to ban final 4x2 sheet generation except rough ideation.
7. Add tests using these 10 packs as negative examples.
8. Re-run one pack, preferably `futon_called_me`, through the improved process before attempting another 10-pack batch.

## Immediate Recommendation

Do not upload the current ZIPs. Treat them as technical pipeline artifacts and QA failure examples.

The next production attempt should focus on one pack only, iterate until it reaches market-grade quality, and only then scale back to multiple packs.
