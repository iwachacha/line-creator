# Sticker Batch Prompt

Generate original source images for ordinary static LINE stickers after HAG-4 approval.

Each item must be readable in daily conversation, visually varied, and transparent-background PNG-ready. Keep final sticker artwork within 370 x 320 px after finishing.

Use the Codex built-in `image_gen` tool through the `imagegen` skill. Do not create production images with Pillow, simple shapes, or placeholders.

If exact text is required, generate it as part of the artwork first. Use `Text must read exactly: "<phrase>"`, keep one short phrase, make it large and high contrast, and describe how it visually belongs to the sticker world. Regenerate malformed text before considering a local text-compositing fallback.
