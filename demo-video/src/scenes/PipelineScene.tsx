import React from "react";
import { Easing, interpolate, useCurrentFrame } from "remotion";
import { Background, Card, ChatLayout, SceneCaption, ToolChip, UserBubble, useAppear } from "../ui";
import { colors, mono } from "../theme";

// Real output of pipeline_summary() from the local demo database.
const STAGES = [
  { stage: "New", count: 4, revenue: 116500 },
  { stage: "Qualified", count: 5, revenue: 87300 },
  { stage: "Proposition", count: 6, revenue: 105100 },
  { stage: "Won", count: 3, revenue: 23800 },
];
const MAX = Math.max(...STAGES.map((s) => s.revenue));

const Bar: React.FC<{ index: number; stage: string; count: number; revenue: number }> = ({
  index,
  stage,
  count,
  revenue,
}) => {
  const frame = useCurrentFrame();
  const start = 66 + index * 8;
  const grow = interpolate(frame, [start, start + 22], [0, revenue / MAX], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.bezier(0.16, 1, 0.3, 1),
  });
  return (
    <div style={{ display: "flex", alignItems: "center", gap: 16 }}>
      <div style={{ width: 150, fontSize: 26, fontWeight: 600 }}>{stage}</div>
      <div style={{ flex: 1, height: 38, backgroundColor: "#1f2230", borderRadius: 10 }}>
        <div
          style={{
            width: `${grow * 100}%`,
            height: "100%",
            borderRadius: 10,
            backgroundColor: stage === "Won" ? colors.green : colors.accent,
          }}
        />
      </div>
      <div style={{ width: 170, textAlign: "right", fontFamily: mono, fontSize: 22 }}>
        ${(revenue / 1000).toFixed(1)}k · {count}
      </div>
    </div>
  );
};

export const PipelineScene = () => {
  const totals = useAppear(108);
  return (
    <Background>
      <SceneCaption step="01">Ask in plain language</SceneCaption>
      <ChatLayout
        left={
          <>
            <UserBubble at={6} text="Summarize my sales pipeline by stage" />
            <ToolChip at={44} call="pipeline_summary()" />
          </>
        }
        right={
          <Card at={58} title="EXPECTED REVENUE BY STAGE">
            <div style={{ display: "flex", flexDirection: "column", gap: 18, marginTop: 6 }}>
              {STAGES.map((s, i) => (
                <Bar key={s.stage} index={i} {...s} />
              ))}
            </div>
            <div
              style={{
                ...totals,
                marginTop: 10,
                paddingTop: 18,
                borderTop: `2px solid ${colors.cardBorder}`,
                fontSize: 30,
                fontWeight: 800,
              }}
            >
              18 opportunities · $332,700 expected
              <div style={{ fontSize: 22, fontWeight: 400, color: colors.muted, marginTop: 6 }}>
                $136,183 weighted by win probability
              </div>
            </div>
          </Card>
        }
      />
    </Background>
  );
};
