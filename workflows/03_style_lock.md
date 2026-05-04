# 03 Style Lock

Input: concept and base candidate images or descriptions.

Output: one locked style direction with palette, line weight, expression rules, text placement rules, character identity anchors, and forbidden deviations.

Approval gate: in manual mode, HAG-3 requires the user to select the final style. In automated mode, choose the strongest style candidate, record the selection rationale, and continue.

Before final production, create `reports/character_design_lock.md`. It must describe the recurring character's silhouette, face, expression range, signature visual hook, text system, and why the character is appealing enough to repeat across a paid sticker pack. A generic object with a small face is not sufficient unless the lock explains a strong mascot identity.

For repeated-character packs, also create `reports/character_consistency_qa.md`. It must define:

- The approved model sheet or reference image path.
- Immutable identity anchors: body proportions, silhouette, face spacing, signature marks/accessories, palette, line weight, and text style.
- Allowed variables: pose, expression, camera distance, item prop, and item text.
- Forbidden drift: changed face layout, changed accessory position, changed outline weight, changed body species/shape, changed palette, or a pose that makes the character read as a different mascot.
- Per-item QA notes after generation, including whether each accepted source matches the identity anchors.

Image generation note: use the Codex built-in `image_gen` tool through the `imagegen` skill for original base candidates. Do not use Pillow/simple-shape fallback candidates for HAG-3 unless the user explicitly asks for a rough placeholder. If image generation is unavailable, stop and ask for direction.

Style lock must also record negative constraints. For LINE sticker and emoji work, explicitly decide whether to avoid physical sticker artifacts such as die-cut white borders, paper backing, drop shadows, sticker-sheet mockups, floor shadows, and decorative frames.

Also record the background and edge-treatment policy:

- Native transparent PNG, or approved chroma-key removal workflow.
- Expected edge alpha behavior, including no visible pixels touching canvas edges unless intentionally cropped.
- Forbidden chroma-key residue colors, commonly flat green or magenta.
