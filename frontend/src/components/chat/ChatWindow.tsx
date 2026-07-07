"use client";

import { useState } from "react";
import { useChat } from "../../hooks/useChat";

export default function ChatWindow() {
  const { messages, isLoading, error, sendMessage } = useChat();
  const [draft, setDraft] = useState("");

  return (
    <div style={{ width: "100%" }}>
      <h2 style={{ marginBottom: 10, fontSize: 20 }}>Conversation</h2>
      <div
        style={{
          border: "1px solid #e2e8f0",
          borderRadius: 16,
          padding: 16,
          minHeight: 280,
          background: "#f8fafc",
          display: "flex",
          flexDirection: "column",
          gap: 10,
        }}
      >
        {messages.length === 0 && !isLoading ? (
          <div style={{ color: "#64748b", fontSize: 14 }}>
            Commencez par poser une question sur votre document.
          </div>
        ) : null}

        {messages.map((message, index) => (
          <div
            key={index}
            style={{
              padding: "10px 12px",
              borderRadius: 12,
              background: message.role === "user" ? "#2563eb" : "white",
              color: message.role === "user" ? "white" : "#0f172a",
              alignSelf: message.role === "user" ? "flex-end" : "flex-start",
              maxWidth: "85%",
            }}
          >
            <strong>{message.role === "user" ? "Vous" : "Assistant"}</strong>
            <div style={{ marginTop: 4 }}>{message.content}</div>
          </div>
        ))}

        {isLoading ? <div style={{ color: "#64748b" }}>Chargement...</div> : null}
        {error ? <div style={{ color: "#dc2626", fontSize: 14 }}>{error}</div> : null}
      </div>

      <div style={{ display: "flex", gap: 8, marginTop: 12 }}>
        <input
          value={draft}
          onChange={(event) => setDraft(event.target.value)}
          placeholder="Posez votre question"
          style={{ flex: 1, padding: "10px 12px", borderRadius: 10, border: "1px solid #cbd5e1" }}
          onKeyDown={(event) => {
            if (event.key === "Enter") {
              event.preventDefault();
              sendMessage(draft);
              setDraft("");
            }
          }}
        />
        <button
          onClick={() => {
            sendMessage(draft);
            setDraft("");
          }}
          disabled={isLoading}
          style={{
            padding: "10px 14px",
            borderRadius: 10,
            border: "none",
            background: isLoading ? "#94a3b8" : "#2563eb",
            color: "white",
            cursor: isLoading ? "not-allowed" : "pointer",
          }}
        >
          Envoyer
        </button>
      </div>
    </div>
  );
}
