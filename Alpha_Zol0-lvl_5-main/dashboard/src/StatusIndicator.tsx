import React from "react";

type StatusIndicatorProps = {
  status: boolean;
  label: string;
};

const StatusIndicator: React.FC<StatusIndicatorProps> = ({ status, label }) => (
  <span style={{ display: "inline-flex", alignItems: "center", marginRight: 12 }}>
    <span
      style={{
        display: "inline-block",
        width: 12,
        height: 12,
        borderRadius: "50%",
        background: status ? "#4caf50" : "#f44336",
        marginRight: 6,
        border: status ? "1px solid #388e3c" : "1px solid #b71c1c"
      }}
    />
    <span style={{ color: status ? "#4caf50" : "#f44336", fontWeight: 500 }}>{label}</span>
  </span>
);

export default StatusIndicator;
