import React from "react";
import { Background, Card, ChatLayout, SceneCaption, ToolChip, UserBubble, useAppear } from "../ui";
import { colors, mono } from "../theme";

// Real output of get_unpaid_invoices() from the local demo database.
const INVOICES = [
  { number: "INV/2026/00004", customer: "Acme Corporation", due: 31750, status: "16 days overdue", color: colors.red },
  { number: "INV/2026/00002", customer: "Acme Corporation", due: 41750, status: "1 day overdue", color: colors.amber },
  { number: "INV/2026/00003", customer: "Acme Corporation", due: 19250, status: "1 day overdue", color: colors.amber },
  { number: "INV/2026/00001", customer: "Azure Interior", due: 31750, status: "due Dec 31", color: colors.muted },
];

const Row: React.FC<{ index: number } & (typeof INVOICES)[number]> = ({
  index,
  number,
  customer,
  due,
  status,
  color,
}) => {
  const style = useAppear(64 + index * 7);
  return (
    <div
      style={{
        ...style,
        display: "flex",
        alignItems: "center",
        gap: 16,
        fontSize: 24,
        padding: "8px 0",
        borderBottom: `1px solid ${colors.cardBorder}`,
      }}
    >
      <div style={{ flex: 1, display: "flex", flexDirection: "column", gap: 2 }}>
        <div style={{ fontWeight: 600, whiteSpace: "nowrap" }}>{customer}</div>
        <div style={{ fontFamily: mono, fontSize: 16, color: colors.muted }}>{number}</div>
      </div>
      <div style={{ width: 120, textAlign: "right", fontFamily: mono }}>
        ${due.toLocaleString("en-US")}
      </div>
      <div
        style={{
          width: 180,
          textAlign: "center",
          fontSize: 18,
          fontWeight: 600,
          color,
          border: `2px solid ${color}`,
          borderRadius: 999,
          padding: "3px 0",
        }}
      >
        {status}
      </div>
    </div>
  );
};

export const InvoicesScene = () => {
  const total = useAppear(100);
  return (
    <Background>
      <SceneCaption step="02">Real answers from Odoo</SceneCaption>
      <ChatLayout
        left={
          <>
            <UserBubble at={6} text="Who owes us money?" />
            <ToolChip at={30} call="get_unpaid_invoices()" />
          </>
        }
        right={
          <Card at={46} title="UNPAID CUSTOMER INVOICES">
            <div style={{ display: "flex", flexDirection: "column" }}>
              {INVOICES.map((inv, i) => (
                <Row key={inv.number} index={i} {...inv} />
              ))}
            </div>
            <div style={{ ...total, fontSize: 30, fontWeight: 800, marginTop: 6 }}>
              $124,500 outstanding
              <span style={{ fontSize: 22, fontWeight: 400, color: colors.muted }}>
                {"  "}· 3 invoices overdue
              </span>
            </div>
          </Card>
        }
      />
    </Background>
  );
};
