# Generation Quality Rules

These rules capture reusable production lessons for LINE sticker and emoji artwork.

## Production Image Generation

- Use Codex built-in `image_gen` through the `imagegen` skill for production artwork.
- Do not use Pillow, simple geometry, placeholder SVGs, or dummy fixtures as production art unless the user explicitly approves fallback quality.
- If image generation is unavailable, stop and ask for direction instead of silently downgrading.
- Keep every character and motif original. Avoid existing characters, famous work styles, specific living artist styles, logos, trademarks, public figures, advertising copy, and unclear-rights references.

## LINE Artwork Fit

- Generate for LINE sticker or emoji usage, not for a physical sticker mockup.
- Avoid die-cut white borders, paper backing, drop shadows, sticker sheet presentation, floor shadows, mockup lighting, and decorative frames unless the style lock explicitly requires them.
- Keep the final silhouette clear, centered, and readable at chat size.
- Use varied poses, silhouettes, props, and expression beats across the set.

## Integrated Text

- When text is part of the sticker concept, generate the text inside the artwork.
- Do not default to generic post-processing labels or detached rectangular speech bubbles.
- Prompt exact text as `Text must read exactly: "<phrase>"`.
- Keep the phrase short, shown once, large, high-contrast, and visually tied to the scene.
- Describe text as part of the world: hand-painted lettering, steam, motion marks, cheering marks, heart accents, or other style-locked elements.
- If Japanese text is malformed, regenerate that item with stricter text constraints before considering local text compositing.

## Generation QA

- Before `finish`, create or inspect a raw generation contact sheet when practical.
- Check exact text, typos, mojibake, duplicated tiny text, style drift, physical sticker mockup artifacts, rights risk, expression variety, and transparent-background readiness.
- Only accepted generated assets should be copied into `assets/source/`.
