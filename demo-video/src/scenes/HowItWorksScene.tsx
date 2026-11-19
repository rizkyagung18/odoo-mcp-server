import React from "react";
import { Easing, Interactive, interpolate, useCurrentFrame } from "remotion";
import { Background, useAppear } from "../ui";
import { colors, mono } from "../theme";

const NODES = [
  { title: "You", sub: "ask a question" },
  { title: "Claude", sub: "picks a tool" },
  { title: "odoo-mcp", sub: "runs it safely" },
  { title: "Odoo 18", sub: "your ERP data" },
];
const LINKS = ["question", "tools/call", "XML-RPC"];

const NODE_W = 196;
const GAP = 120;
const ROW_LEFT = (1280 - (NODES.length * NODE_W + (NODES.length - 1) * GAP)) / 2;
const ROW_TOP = 260;

const Node: React.FC<{ index: number; title: string; sub: string }> = ({ index, title, sub }) => {
  const style = useAppear(8 + index * 10);
  const highlight = index === 2; // our server
  return (
    <div
      style={{
        ...style,
        position: "absolute",
        left: ROW_LEFT + index * (NODE_W + GAP),
        top: ROW_TOP,
        width: NODE_W,
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        gap: 14,
      }}
    >
      <div
        style={{
          width: NODE_W,
          height: 130,
          borderRadius: 24,
          backgroundColor: highlight ? colors.accentDim : colors.card,
          border: `3px solid ${highlight ? colors.accent : colors.cardBorder}`,
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          fontSize: 34,
          fontWeight: 800,
          fontFamily: highlight ? mono : undefined,
        }}
      >
        {title}
      </div>
      <div style={{ fontSize: 24, color: colors.muted }}>{sub}</div>
    </div>
  );
};

const Link: React.FC<{ index: number; label: string }> = ({ index, label }) => {
  const style = useAppear(14 + index * 10);
  const left = ROW_LEFT + (index + 1) * NODE_W + index * GAP;
  return (
    <div
      style={{
        ...style,
        position: "absolute",
        left,
        top: ROW_TOP + 20,
        width: GAP,
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        gap: 6,
      }}
    >
      <div style={{ fontFamily: mono, fontSize: 18, color: colors.accent, whiteSpace: "nowrap" }}>
        {label}
      </div>
      <div style={{ fontSize: 40, color: colors.muted, lineHeight: 1 }}>⟷</div>
    </div>
  );
};

export const HowItWorksScene = () => {
  const frame = useCurrentFrame();
  const rowWidth = NODES.length * NODE_W + (NODES.length - 1) * GAP;

  return (
    <Background>
      <Interactive.Div
        name="Heading"
        style={{
          position: "absolute",
          top: 90,
          left: 0,
          right: 0,
          textAlign: "center",
          fontSize: 64,
          fontWeight: 800,
          opacity: interpolate(frame, [0, 12], [0, 1], {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
          }),
        }}
      >
        How it works
      </Interactive.Div>

      {NODES.map((n, i) => (
        <Node key={n.title} index={i} title={n.title} sub={n.sub} />
      ))}
      {LINKS.map((l, i) => (
        <Link key={l} index={i} label={l} />
      ))}

      {/* A request travelling from "You" to Odoo and back, along a faint track. */}
      <div
        style={{
          position: "absolute",
          top: ROW_TOP + 214,
          left: ROW_LEFT + NODE_W / 2,
          width: rowWidth - NODE_W,
          height: 2,
          backgroundColor: colors.cardBorder,
          opacity: interpolate(frame, [44, 52], [0, 1], {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
          }),
        }}
      />
      <div
        style={{
          position: "absolute",
          top: ROW_TOP + 206,
          left: interpolate(
            frame,
            [52, 82, 96, 120],
            [ROW_LEFT + NODE_W / 2, ROW_LEFT + rowWidth - NODE_W / 2, ROW_LEFT + rowWidth - NODE_W / 2, ROW_LEFT + NODE_W / 2],
            {
              extrapolateLeft: "clamp",
              extrapolateRight: "clamp",
              easing: Easing.inOut(Easing.cubic),
            },
          ),
          width: 18,
          height: 18,
          marginLeft: -9,
          borderRadius: 999,
          backgroundColor: frame < 89 ? colors.accent : colors.green,
          boxShadow: `0 0 24px ${frame < 89 ? colors.accent : colors.green}`,
          opacity: interpolate(frame, [48, 54, 118, 124], [0, 1, 1, 0], {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
          }),
        }}
      />

      <Interactive.Div
        name="Takeaway"
        style={{
          position: "absolute",
          bottom: 100,
          left: 80,
          right: 80,
          textAlign: "center",
          fontSize: 36,
          fontWeight: 600,
          color: "#eceef5",
          opacity: interpolate(frame, [62, 76], [0, 1], {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
          }),
        }}
      >
        Claude never touches the database, only 6 safe tools.
      </Interactive.Div>
    </Background>
  );
};
