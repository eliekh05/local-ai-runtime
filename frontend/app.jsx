import React, { useState, useEffect, useRef, useCallback } from "react";
import { createRoot } from "react-dom/client";
import ChatWindow from "./components/ChatWindow.jsx";
import InputBar from "./components/InputBar.jsx";
import ModelSelector from "./components/ModelSelector.jsx";
import "./styles/base.css";

const API = "";  // Vite proxy handles /status, /chat, etc.

function StatusBar() {
  const [status, setStatus] = useState({ status: "checking", model_loaded: false, version: "" });

  useEffect(() => {
    fetch(`${API}/status`)
      .then(r => r.json())
      .then(setStatus)
      .catch(() => setStatus({ status: "unreachable", model_loaded: false, version: "" }));
  }, []);

  const dotClass = status.status === "ok" ? "status-ok" : "status-unreachable";
  return (
    <span className="status-bar">
      <span className={`status-dot ${dotClass}`} />
      {" "}v{status.version || "?"}
      {status.model_loaded && status.current_model && ` · ${status.current_model}`}
    </span>
  );
}

export default function App() {
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [conversationId, setConversationId] = useState(null);
  const [currentModel, setCurrentModel] = useState("");

  // Create conversation on mount
  useEffect(() => {
    fetch(`${API}/conversations`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({}) })
      .then(r => r.json())
      .then(conv => setConversationId(conv.id))
      .catch(() => {});
  }, []);

  const sendMessage = useCallback(async (text) => {
    if (!text.trim() || isLoading) return;

    const userMsg = { role: "user", content: text, timestamp: new Date().toISOString() };
    setMessages(prev => [...prev, userMsg]);
    setIsLoading(true);
    setError(null);

    try {
      const res = await fetch(`${API}/chat/stream`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: text, conversation_id: conversationId }),
      });

      if (!res.ok) {
        const err = await res.json().catch(() => ({ detail: "Request failed" }));
        throw new Error(err.detail || `HTTP ${res.status}`);
      }

      const reader = res.body.getReader();
      const decoder = new TextDecoder();
      let fullResponse = "";

      // Add empty assistant message to update in place
      const assistantMsg = { role: "assistant", content: "", timestamp: new Date().toISOString() };
      setMessages(prev => [...prev, assistantMsg]);

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value, { stream: true });
        const lines = chunk.split("\n");

        for (const line of lines) {
          if (line.startsWith("data: ")) {
            try {
              const data = JSON.parse(line.slice(6));
              if (data.done) break;
              if (data.token) {
                fullResponse += data.token;
                setMessages(prev => {
                  const updated = [...prev];
                  updated[updated.length - 1] = { ...updated[updated.length - 1], content: fullResponse };
                  return updated;
                });
              }
              if (data.error) {
                setError(data.error);
                break;
              }
            } catch {}
          }
        }
      }
    } catch (e) {
      setError(e.message);
      // Remove the empty assistant message on error
      setMessages(prev => prev.filter((_, i) => i !== prev.length - 1 || prev[i].content));
    } finally {
      setIsLoading(false);
    }
  }, [isLoading, conversationId]);

  const retryLastMessage = useCallback(() => {
    if (messages.length > 0) {
      const lastUserMsg = [...messages].reverse().find(m => m.role === "user");
      if (lastUserMsg) {
        setMessages(prev => prev.filter(m => m !== lastUserMsg));
        sendMessage(lastUserMsg.content);
      }
    }
  }, [messages, sendMessage]);

  return (
    <div className="chat-page">
      <header className="app-header">
        <span className="app-title">local-ai-runtime</span>
        <ModelSelector currentModel={currentModel} onModelSelect={setCurrentModel} />
        <StatusBar />
      </header>

      {error && (
        <div className="error-banner">
          <span>{error}</span>
          <button className="error-retry" onClick={retryLastMessage}>Retry</button>
        </div>
      )}

      <ChatWindow messages={messages} isLoading={isLoading} />
      <InputBar onSend={sendMessage} disabled={isLoading} />
    </div>
  );
}

const root = createRoot(document.getElementById("root"));
root.render(<App />);
