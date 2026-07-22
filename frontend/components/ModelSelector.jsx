import React, { useState, useEffect } from "react";

export default function ModelSelector({ onModelSelect, currentModel }) {
  const [models, setModels] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch("/models")
      .then(res => res.json())
      .then(data => {
        setModels(data.models || []);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, []);

  if (loading) return <span className="model-selector">Loading models...</span>;
  if (models.length === 0) return <span className="model-selector">No models found</span>;

  return (
    <select
      className="model-selector"
      value={currentModel || ""}
      onChange={(e) => onModelSelect(e.target.value)}
    >
      <option value="" disabled>Select a model</option>
      {models.map(m => (
        <option key={m.filename} value={m.filename}>
          {m.filename}
        </option>
      ))}
    </select>
  );
}
