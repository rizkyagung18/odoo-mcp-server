import { Interactive, interpolate, useCurrentFrame } from "remotion";
import { Background } from "../ui";
import { colors, mono } from "../theme";

export const OutroScene = () => {
  const frame = useCurrentFrame();
  return (
    <Background>
      <div
        style={{
          position: "absolute",
          inset: 0,
          display: "flex",
          flexDirection: "column",
          justifyContent: "center",
          alignItems: "center",
          gap: 34,
        }}
      >
        <Interactive.Div
          name="Title"
          style={{
            opacity: interpolate(frame, [0, 14], [0, 1], {
              extrapolateLeft: "clamp",
              extrapolateRight: "clamp",
            }),
            fontSize: 88,
            fontWeight: 800,
            letterSpacing: -2,
          }}
        >
          Odoo MCP Server
        </Interactive.Div>
        <Interactive.Div
          name="Checklist"
          style={{
            opacity: interpolate(frame, [10, 24], [0, 1], {
              extrapolateLeft: "clamp",
              extrapolateRight: "clamp",
            }),
            display: "flex",
            gap: 40,
            fontSize: 34,
            fontWeight: 600,
            color: "#4ade80",
          }}
        >
          <span>✓ 6 tools</span>
          <span>✓ preview → confirm</span>
          <span>✓ 50 tests</span>
        </Interactive.Div>
        <Interactive.Div
          name="Setup"
          style={{
            opacity: interpolate(frame, [20, 34], [0, 1], {
              extrapolateLeft: "clamp",
              extrapolateRight: "clamp",
            }),
            fontFamily: mono,
            fontSize: 26,
            color: colors.muted,
          }}
        >
          docker compose up -d · uv run odoo-mcp
        </Interactive.Div>
      </div>
    </Background>
  );
};
