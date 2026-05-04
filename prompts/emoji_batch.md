# Emoji Batch Prompt

Generate original source images for regular LINE emoji after HAG-4 approval.

Each item must remain readable at small inline-chat size, use clear expressions, and be transparent-background PNG-ready at 180 x 180 px.

Use the Codex built-in `image_gen` tool through the `imagegen` skill. Do not create production images with Pillow, simple shapes, or placeholders.

For emoji, prefer no text unless HAG-4 approves it. If exact text is required, generate it as part of the artwork first, keep it very short, and regenerate malformed text before considering a local text-compositing fallback.
