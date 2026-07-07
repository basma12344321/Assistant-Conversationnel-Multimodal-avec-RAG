"use client";

import { useState } from "react";
import api from "../services/api";

export function useChat() {
  const [messages, setMessages] = useState<{ role: string; content: string }[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");

  const sendMessage = async (text: string) => {
    if (!text.trim()) return;

    setError("");
    setMessages((prev) => [...prev, { role: "user", content: text }]);
    setIsLoading(true);

    try {
      const response = await api.post("/api/chat/", { message: text });
      setMessages((prev) => [...prev, { role: "assistant", content: response.data.answer }]);
    } catch (err) {
      setError("La réponse n’a pas pu être chargée. Vérifiez que le backend est bien lancé.");
    } finally {
      setIsLoading(false);
    }
  };

  return { messages, isLoading, error, sendMessage };
}
