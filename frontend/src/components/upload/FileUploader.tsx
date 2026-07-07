"use client";

import { useState, type ChangeEvent } from "react";
import api from "../../services/api";

export default function FileUploader() {
  const [status, setStatus] = useState("");
  const [isUploading, setIsUploading] = useState(false);

  const onUpload = async (event: ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    const formData = new FormData();
    formData.append("file", file);
    setIsUploading(true);
    setStatus("Téléversement en cours...");

    try {
      const response = await api.post("/api/documents/upload", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      setStatus(`Document ajouté : ${response.data.filename}`);
    } catch {
      setStatus("Échec du téléversement. Vérifiez le backend.");
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <div style={{ width: "100%" }}>
      <h2 style={{ marginBottom: 10, fontSize: 20 }}>Ajouter un document</h2>
      <div
        style={{
          border: "1px dashed #94a3b8",
          borderRadius: 16,
          padding: 18,
          background: "#f8fafc",
        }}
      >
        <input type="file" onChange={onUpload} />
        <p style={{ marginTop: 10, color: "#475569", minHeight: 24 }}>
          {isUploading ? "Téléversement en cours..." : status}
        </p>
      </div>
    </div>
  );
}
