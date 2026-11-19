import { Easing, Interactive, interpolate, useCurrentFrame } from "remotion";
import { Background } from "../ui";
import { colors, mono } from "../theme";

export const TitleScene = () => {
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
          gap: 26,
        }}
      >
        <Interactive.Div
          name="Kicker"
          style={{
            opacity: interpolate(frame, [0, 12], [0, 1], {
              extrapolateLeft: "clamp",
              extrapolateRight: "clamp",
            }),
            fontFamily: mono,
            fontSize: 26,
            color: colors.accent,
            border: "2px solid #3b2f63",
            borderRadius: 999,
            padding: "6px 20px",
          }}
        >
          Model Context Protocol · Odoo 18
        </Interactive.Div>
        <Interactive.Div
          name="Title"
          style={{
            opacity: interpolate(frame, [4, 20], [0, 1], {
              extrapolateLeft: "clamp",
              extrapolateRight: "clamp",
            }),
            translate: interpolate(frame, [4, 24], ["0px 40px", "0px 0px"], {
              extrapolateLeft: "clamp",
              extrapolateRight: "clamp",
              easing: Easing.bezier(0.16, 1, 0.3, 1),
            }),
            fontSize: 104,
            fontWeight: 800,
            letterSpacing: -2,
          }}
        >
          Odoo MCP Server
        </Interactive.Div>
        <Interactive.Div
          name="Subtitle"
          style={{
            opacity: interpolate(frame, [16, 32], [0, 1], {
              extrapolateLeft: "clamp",
              extrapolateRight: "clamp",
            }),
            fontSize: 44,
            color: "#9399ab",
            textAlign: "center",
          }}
        >
          Ask Claude about your CRM, sales and invoices
        </Interactive.Div>
        <Interactive.Div
          name="Tags"
          style={{
            opacity: interpolate(frame, [28, 42], [0, 1], {
              extrapolateLeft: "clamp",
              extrapolateRight: "clamp",
            }),
            marginTop: 18,
            fontFamily: mono,
            fontSize: 24,
            color: "#9399ab",
          }}
        >
          Python · MCP SDK v2 · XML-RPC · Docker
        </Interactive.Div>
      </div>
    </Background>
  );
};
