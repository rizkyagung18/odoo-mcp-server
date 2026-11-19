# Demo video

Source of the README demo (`docs/demo.gif`, `docs/demo.mp4`), built with [Remotion](https://www.remotion.dev).

This is an animated walkthrough, not a screen recording. Every number in it is real output from the MCP tools against the local demo database (`pipeline_summary`, `get_unpaid_invoices`, and the Phase 4 `create_lead` preview and result).

```bash
npm i
npm run dev        # Remotion Studio preview
# re-render the README assets
npx remotion render OdooMcpDemo ../docs/demo.mp4 --codec=h264 --crf=20
npx remotion render OdooMcpDemo ../docs/demo.gif --codec=gif --every-nth-frame=2 --scale=0.6
```

- **Scenes:** `src/scenes/` (one file per scene). They're put in order in `src/Demo.tsx`.
- **Shared parts:** `src/ui.tsx` holds the chat bubbles, tool chips and cards; `src/theme.ts` holds the colors and fonts.
- **Rendering uses Chrome for Testing.** `remotion.config.ts` sets this because the default headless Chrome crashed on macOS here.
- **License:** Remotion is free for individuals and small teams. See the [Remotion license](https://www.remotion.dev/docs/license).
