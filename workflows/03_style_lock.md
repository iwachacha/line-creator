# 03 Style Lock

Input: concept and base candidate images or descriptions.

Output: one approved style direction with palette, line weight, expression rules, text placement rules, and forbidden deviations.

Approval gate: HAG-3. Stop until the user selects the final style.

Image generation note: use the Codex built-in `image_gen` tool through the `imagegen` skill for original base candidates. Do not use Pillow/simple-shape fallback candidates for HAG-3 unless the user explicitly asks for a rough placeholder. If image generation is unavailable, stop and ask for direction.

Style lock must also record negative constraints. For LINE sticker and emoji work, explicitly decide whether to avoid physical sticker artifacts such as die-cut white borders, paper backing, drop shadows, sticker-sheet mockups, floor shadows, and decorative frames.

Also record the background and edge-treatment policy:

- Native transparent PNG, or approved chroma-key removal workflow.
- Expected edge alpha behavior, including no visible pixels touching canvas edges unless intentionally cropped.
- Forbidden chroma-key residue colors, commonly flat green or magenta.
