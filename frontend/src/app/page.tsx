import ChatWindow from "../components/chat/ChatWindow";
import FileUploader from "../components/upload/FileUploader";

export default function HomePage() {
  return (
    <main style={{ minHeight: "100vh", background: "#f8fafc", padding: 24, color: "#0f172a" }}>
      <div style={{ maxWidth: 1100, margin: "0 auto" }}>
        <section
          style={{
            background: "white",
            borderRadius: 20,
            padding: 28,
            boxShadow: "0 10px 30px rgba(15, 23, 42, 0.08)",
            border: "1px solid #e2e8f0",
          }}
        >
          <h1 style={{ fontSize: 32, margin: 0, fontWeight: 700 }}>Assistant RAG multimodal</h1>
          <p style={{ marginTop: 10, marginBottom: 24, fontSize: 16, color: "#475569", maxWidth: 720 }}>
            Uploadez un document, puis posez une question en langage naturel. Cette première version
            vous permet de tester rapidement la conversation et la recherche dans vos documents.
          </p>

          <div style={{ display: "grid", gap: 20, gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))" }}>
            <div>
              <FileUploader />
            </div>
            <div>
              <ChatWindow />
            </div>
          </div>
        </section>
      </div>
    </main>
  );
}
