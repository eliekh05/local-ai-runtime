import React, { useRef, useEffect } from "react";
import ReactMarkdown from "react-markdown";

export default function ChatWindow({ messages = [], isLoading = false }) {
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isLoading]);

  if (messages.length === 0 && !isLoading) {
    return (
      <div className="chat-window chat-window--empty">
        <p className="empty-state">No messages yet. Type something below to start.</p>
      </div>
    );
  }

  return (
    <div className="chat-window">
      {messages.map((msg, index) => (
        <div key={index} className={`message message--${msg.role}`}>
          <span className="message__role">{msg.role}</span>
          <div className="message__content">
            {msg.role === "assistant" ? (
              <ReactMarkdown>{msg.content}</ReactMarkdown>
            ) : (
              <p>{msg.content}</p>
            )}
          </div>
          {msg.timestamp && (
            <span className="message__timestamp">
              {new Date(msg.timestamp).toLocaleTimeString()}
            </span>
          )}
        </div>
      ))}

      {isLoading && (
        <div className="message message--assistant message--loading">
          <span className="loading-indicator">···</span>
        </div>
      )}

      <div ref={bottomRef} />
    </div>
  );
}
