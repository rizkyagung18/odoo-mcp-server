import React from "react";
import { Easing, Interactive, interpolate, useCurrentFrame } from "remotion";
import { Background, SceneCaption, useAppear } from "../ui";
import { colors, mono } from "../theme";

const TOOLS = [
  "list_leads",
  "search_partners",
  "get_sales_orders",
  "get_unpaid_invoices",
  "pipeline_summary",
  "create_lead",
];
const FLIP = 34; // frame where the switch turns on

const ToolPill: React.FC<{ index: number; name: string }> = ({ index, name }) => {
  const frame = useCurrentFrame();
  const style = useAppear(6 + index * 4);
  const isWrite = name === "create_lead";
  return (
    <div
      style={{
        ...style,
        opacity: isWrite
          ? interpolate(frame, [FLIP + 10, FLIP + 30], [1, 0.25], {
              extrapolateLeft: "clamp",
              extrapolateRight: "clamp",
            }) * style.opacity
          : style.opacity,
        fontFamily: mono,
        fontSize: 26,
        padding: "12px 20px",
        borderRadius: 14,
        backgroundColor: colors.card,
        border: `2px solid ${isWrite ? colors.amber : colors.cardBorder}`,
        color: isWrite ? colors.amber : colors.text,
        textDecoration: isWrite && frame > FLIP + 10 ? "line-through" : "none",
      }}
    >
      {name}
    </div>
  );
};

export const ReadOnlyScene = () => {
  const frame = useCurrentFrame();
  const on = frame >= FLIP;
  const knob = interpolate(frame, [FLIP - 6, FLIP + 4], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.bezier(0.16, 1, 0.3, 1),
  });

  return (
    <Background>
      <SceneCaption step="04">One switch for read-only</SceneCaption>

      {/* The env-var "switch" */}
      <div
        style={{
          position: "absolute",
          top: 170,
          left: 0,
          right: 0,
          display: "flex",
          justifyContent: "center",
          alignItems: "center",
          gap: 24,
          fontFamily: mono,
          fontSize: 40,
        }}
      >
        <span>ODOO_READ_ONLY=</span>
        <span style={{ color: on ? colors.green : colors.muted, width: 110 }}>{on ? "true" : "false"}</span>
        <div
          style={{
            width: 110,
            height: 56,
            borderRadius: 999,
            backgroundColor: on ? "#1f4d33" : "#2a2d3c",
            border: `3px solid ${on ? colors.green : colors.cardBorder}`,
            position: "relative",
          }}
        >
          <div
            style={{
              position: "absolute",
              top: 5,
              left: 6 + knob * 52,
              width: 40,
              height: 40,
              borderRadius: 999,
              backgroundColor: on ? colors.green : colors.muted,
            }}
          />
        </div>
      </div>

      <div
        style={{
          position: "absolute",
          top: 290,
          left: 140,
          right: 140,
          display: "flex",
          flexWrap: "wrap",
          justifyContent: "center",
          gap: 18,
        }}
      >
        {TOOLS.map((t, i) => (
          <ToolPill key={t} index={i} name={t} />
        ))}
      </div>

      <Interactive.Div
        name="Takeaway"
        style={{
          position: "absolute",
          bottom: 110,
          left: 80,
          right: 80,
          textAlign: "center",
          fontSize: 36,
          fontWeight: 600,
          opacity: interpolate(frame, [FLIP + 22, FLIP + 36], [0, 1], {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
          }),
        }}
      >
        Write tools aren't registered, so the LLM never sees them.
      </Interactive.Div>
    </Background>
  );
};
