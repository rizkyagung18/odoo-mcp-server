import React from "react";
import { Background, Card, ChatLayout, SceneCaption, ToolChip, UserBubble } from "../ui";
import { colors, mono } from "../theme";

// Real preview + result of create_lead() from Phase 4 (lead #45 in the demo database).
const PREVIEW: [string, string][] = [
  ["name", "MCP test: standing desks"],
  ["partner_name", "Wood Corner"],
  ["email_from", "buyer@woodcorner.example"],
  ["expected_revenue", "12500"],
];

const Field: React.FC<{ k: string; v: string }> = ({ k, v }) => (
  <div style={{ display: "flex", gap: 16, fontFamily: mono, fontSize: 21 }}>
    <div style={{ width: 220, color: colors.muted }}>{k}</div>
    <div style={{ color: colors.text }}>{v}</div>
  </div>
);

export const WriteScene = () => (
  <Background>
    <SceneCaption step="03">Safe writes: preview, then confirm</SceneCaption>
    <ChatLayout
      leftGap={16}
      left={
        <>
          <UserBubble at={6} fontSize={29} text="Add a lead: standing desks for Wood Corner, $12,500" />
          <ToolChip at={52} call="create_lead()" badge="confirm=false" badgeColor={colors.amber} />
          <UserBubble at={100} fontSize={29} text="Yes, create it" />
          <ToolChip at={122} call="create_lead()" badge="confirm=true" badgeColor={colors.accent} />
        </>
      }
      right={
        <>
          <Card at={66} title="PREVIEW · NOTHING WRITTEN YET" borderColor={colors.amber}>
            <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
              {PREVIEW.map(([k, v]) => (
                <Field key={k} k={k} v={v} />
              ))}
            </div>
          </Card>
          <Card at={138} title="CREATED IN ODOO" borderColor={colors.green}>
            <div style={{ fontSize: 32, fontWeight: 800, color: colors.green }}>✓ Lead #45 created</div>
            <div style={{ fontSize: 22, color: colors.muted }}>
              Opportunity · Stage: New · Salesperson: Mitchell Admin
            </div>
          </Card>
        </>
      }
    />
  </Background>
);
