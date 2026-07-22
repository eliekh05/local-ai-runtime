import React, { useState, useRef, useEffect } from "react";

export default function InputBar({ onSend, disabled = false }) {
  const [value, setValue] = useState("");
  const textareaRef = useRef(null);

  const handleSubmit = () => {
    const trimmed = value.trim();
    if (!trimmed || disabled) return;
    onSend(trimmed);
    setValue("");
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  // Auto-resize textarea
  useEffect(() => {
    const el = textareaRef.current;
    if (el) {
      el.style.height = "auto";
      el.style.height = Math.min(el.scrollHeight, 150) + "px";
    }
  }, [value]);

  return (
    <div className="input-bar">
      <textarea
        ref={textareaRef}
        className="input-bar__field"
        value={value}
        onChange={(e) => setValue(e.target.value)}
        onKeyDown={handleKeyDown}
        disabled={disabled}
        placeholder={disabled ? "Waiting for response..." : "Type a message..."}
        rows={1}
      />
      <button
        className="input-bar__send"
        onClick={handleSubmit}
        disabled={disabled || !value.trim()}
      >
        Send
      </button>
    </div>
  );
}
