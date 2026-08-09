import { useState } from "react";
import { chatEditPage } from "../../api/client";

interface Props {
  campaignId: string;
  onHtmlUpdate: (html: string) => void;
}

interface Message {
  role: "user" | "assistant";
  content: string;
}

const SUGGESTIONS = [
  "Rends le titre principal plus percutant",
  "Change le texte du bouton en « Réserver ma place »",
  "Réécris la section prix sur un ton plus rassurant",
];

export default function ChatPanel({ campaignId, onHtmlUpdate }: Props) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const send = async (text: string) => {
    const message = text.trim();
    if (!message || loading) return;

    const history = messages;
    setMessages([...history, { role: "user", content: message }]);
    setInput("");
    setError("");
    setLoading(true);
    try {
      const res = await chatEditPage(campaignId, message, history);
      if (res.html) onHtmlUpdate(res.html);
      const changed = res.changed?.length
        ? `\n\nSections mises à jour : ${res.changed.join(", ")}`
        : "";
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: (res.reply || "C'est fait.") + changed },
      ]);
    } catch (err: unknown) {
      const detail =
        (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail ??
        "Erreur lors de la modification.";
      setError(detail);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex h-full flex-col rounded-2xl border border-[#e7ddd0] bg-white shadow-sm">
      <div className="border-b border-[#e7ddd0] px-4 py-3">
        <h2 className="app-title text-sm font-bold">💬 Assistant d'édition</h2>
        <p className="text-xs text-gray-500">Demandez une modification, la page se met à jour.</p>
      </div>

      <div className="flex-1 space-y-3 overflow-y-auto p-4 text-sm">
        {messages.length === 0 && (
          <div className="space-y-2">
            {SUGGESTIONS.map((suggestion) => (
              <button
                key={suggestion}
                type="button"
                onClick={() => send(suggestion)}
                className="coral-soft block w-full rounded-lg border border-[#f0c5b0] px-3 py-2 text-left text-xs font-medium hover:bg-[#fbe8de]"
              >
                {suggestion}
              </button>
            ))}
          </div>
        )}
        {messages.map((message, index) => (
          <div
            key={index}
            className={`whitespace-pre-wrap rounded-lg px-3 py-2 ${
              message.role === "user"
                ? "coral-soft ml-6 border border-[#f0c5b0]"
                : "mr-6 bg-gray-50 text-gray-800"
            }`}
          >
            {message.content}
          </div>
        ))}
        {loading && <p className="text-xs text-gray-500">L'assistant modifie la page...</p>}
        {error && (
          <p className="rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-xs text-red-600">
            {error}
          </p>
        )}
      </div>

      <form
        className="flex gap-2 border-t border-[#e7ddd0] p-3"
        onSubmit={(event) => {
          event.preventDefault();
          send(input);
        }}
      >
        <input
          value={input}
          onChange={(event) => setInput(event.target.value)}
          placeholder="Ex : raccourcis le sous-titre"
          className="flex-1 rounded-lg border border-[#e7ddd0] px-3 py-2 text-sm focus:outline-none"
        />
        <button
          type="submit"
          disabled={loading || !input.trim()}
          className="coral-soft rounded-lg border border-[#f0c5b0] px-3 py-2 text-xs font-semibold disabled:opacity-50"
        >
          Envoyer
        </button>
      </form>
    </div>
  );
}
