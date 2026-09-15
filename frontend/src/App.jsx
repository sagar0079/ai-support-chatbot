import { useEffect, useRef, useState } from "react";

const INITIAL_MESSAGE = {
  role: "assistant",
  content: "Hi, I'm the AI support bot. Ask me about billing, trials, or your account.",
};

export default function App() {
  const [messages, setMessages] = useState([INITIAL_MESSAGE]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const scrollRef = useRef(null);

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: "smooth" });
  }, [messages, loading]);

  async function sendMessage(e) {
    e.preventDefault();
    const text = input.trim();
    if (!text || loading) return;

    const nextMessages = [...messages, { role: "user", content: text }];
    setMessages(nextMessages);
    setInput("");
    setLoading(true);

    try {
      const res = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: text }),
      });
      if (!res.ok) throw new Error(`Request failed: ${res.status}`);
      const data = await res.json();
      setMessages((prev) => [...prev, { role: "assistant", content: data.reply }]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: "Something went wrong reaching the assistant. Please try again." },
      ]);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="page">
      <div className="chat-card">
        <header className="chat-header">
          <span className="chat-header-dot" />
          <div>
            <h1>AI Support</h1>
            <p>AI assistant &middot; demo knowledge base</p>
          </div>
        </header>

        <div className="chat-log" ref={scrollRef}>
          {messages.map((m, i) => (
            <div key={i} className={`bubble-row ${m.role}`}>
              <div className={`bubble ${m.role}`}>{m.content}</div>
            </div>
          ))}
          {loading && (
            <div className="bubble-row assistant">
              <div className="bubble assistant typing">
                <span />
                <span />
                <span />
              </div>
            </div>
          )}
        </div>

        <form className="chat-input-row" onSubmit={sendMessage}>
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask about billing, trials, your account..."
            disabled={loading}
          />
          <button type="submit" disabled={loading || !input.trim()}>
            Send
          </button>
        </form>
      </div>
    </div>
  );
}
