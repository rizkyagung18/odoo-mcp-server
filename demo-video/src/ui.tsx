// Small building blocks shared by the chat-style scenes.
import React from "react";
import { AbsoluteFill, Easing, interpolate, useCurrentFrame } from "remotion";
import { colors, mono, sans } from "./theme";

const ease = Easing.bezier(0.16, 1, 0.3, 1);
const clamp = { extrapolateLeft: "clamp", extrapolateRight: "clamp" } as const;

/** Fade + rise in, starting at frame `at`. */
export const useAppear = (at: number) => {
  const frame = useCurrentFrame();
  return {
    opacity: interpolate(frame, [at, at + 12], [0, 1], { ...clamp, easing: ease }),
    translate: interpolate(frame, [at, at + 18], ["0px 28px", "0px 0px"], {
      ...clamp,
      easing: ease,
    }),
  };
};

export const Background: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <AbsoluteFill
    style={{
      backgroundColor: colors.bg,
      backgroundImage:
        "radial-gradient(circle at 15% 0%, rgba(167,139,250,0.16), transparent 45%)," +
        "radial-gradient(circle at 100% 100%, rgba(74,222,128,0.07), transparent 40%)",
      fontFamily: sans,
      color: colors.text,
    }}
  >
    {children}
  </AbsoluteFill>
);

/** Step label shown at the top-left of each chat scene. */
export const SceneCaption: React.FC<{ step: string; children: React.ReactNode }> = ({
  step,
  children,
}) => {
  const style = useAppear(0);
  return (
    <div
      style={{
        ...style,
        position: "absolute",
        top: 48,
        left: 80,
        display: "flex",
        alignItems: "center",
        gap: 18,
        fontSize: 36,
        fontWeight: 800,
      }}
    >
      <span
        style={{
          fontFamily: mono,
          fontSize: 26,
          color: colors.accent,
          border: `2px solid ${colors.accentDim}`,
          borderRadius: 10,
          padding: "4px 12px",
        }}
      >
        {step}
      </span>
      {children}
    </div>
  );
};

/** The user's message, typed out character by character. */
export const UserBubble: React.FC<{ at: number; text: string; fontSize?: number }> = ({
  at,
  text,
  fontSize = 34,
}) => {
  const frame = useCurrentFrame();
  const style = useAppear(at);
  const shown = Math.round(
    interpolate(frame, [at + 4, at + 4 + text.length * 0.9], [0, text.length], clamp),
  );
  return (
    <div style={{ ...style, display: "flex", flexDirection: "column", gap: 8 }}>
      <div style={{ fontSize: 22, color: colors.muted, fontWeight: 600 }}>You</div>
      <div
        style={{
          backgroundColor: colors.accentDim,
          border: `2px solid ${colors.accent}`,
          borderRadius: 22,
          padding: "16px 24px",
          fontSize,
          lineHeight: 1.25,
          fontWeight: 600,
        }}
      >
        {text.slice(0, shown)}
        {/* zero-width cursor so it never causes an extra wrapped line */}
        <span
          style={{
            display: "inline-block",
            width: 0,
            opacity: shown < text.length ? 1 : 0,
            color: colors.accent,
          }}
        >
          ▍
        </span>
      </div>
    </div>
  );
};

/** Claude calling one of our MCP tools. */
export const ToolChip: React.FC<{ at: number; call: string; badge?: string; badgeColor?: string }> = ({
  at,
  call,
  badge = "read-only",
  badgeColor = colors.green,
}) => {
  const frame = useCurrentFrame();
  const style = useAppear(at);
  const done = frame >= at + 16;
  return (
    <div style={{ ...style, display: "flex", flexDirection: "column", gap: 8 }}>
      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
        <span style={{ fontSize: 22, color: colors.muted, fontWeight: 600 }}>Claude calls a tool</span>
        <span
          style={{
            fontFamily: mono,
            fontSize: 17,
            color: badgeColor,
            border: `2px solid ${badgeColor}`,
            borderRadius: 999,
            padding: "1px 10px",
            whiteSpace: "nowrap",
          }}
        >
          {badge}
        </span>
      </div>
      <div
        style={{
          display: "flex",
          alignItems: "center",
          gap: 14,
          backgroundColor: colors.card,
          border: `2px solid ${colors.cardBorder}`,
          borderRadius: 16,
          padding: "10px 18px",
          fontFamily: mono,
          fontSize: 25,
        }}
      >
        <span style={{ color: done ? colors.green : colors.amber }}>{done ? "✓" : "…"}</span>
        <span style={{ color: colors.text }}>{call}</span>
      </div>
    </div>
  );
};

export const Card: React.FC<{
  at: number;
  title: string;
  borderColor?: string;
  children: React.ReactNode;
}> = ({ at, title, borderColor = colors.cardBorder, children }) => {
  const style = useAppear(at);
  return (
    <div
      style={{
        ...style,
        backgroundColor: colors.card,
        border: `2px solid ${borderColor}`,
        borderRadius: 24,
        padding: "24px 30px",
        display: "flex",
        flexDirection: "column",
        gap: 16,
      }}
    >
      <div style={{ fontSize: 22, color: colors.muted, fontWeight: 600, letterSpacing: 1 }}>
        {title}
      </div>
      {children}
    </div>
  );
};

/** Two-column chat layout: conversation on the left, result on the right. */
export const ChatLayout: React.FC<{
  left: React.ReactNode;
  right: React.ReactNode;
  leftGap?: number;
}> = ({ left, right, leftGap = 26 }) => (
  <div
    style={{
      position: "absolute",
      top: 130,
      left: 80,
      right: 80,
      bottom: 56,
      display: "flex",
      gap: 40,
    }}
  >
    <div style={{ width: 430, display: "flex", flexDirection: "column", gap: leftGap }}>{left}</div>
    <div style={{ flex: 1, display: "flex", flexDirection: "column", gap: 22 }}>{right}</div>
  </div>
);
