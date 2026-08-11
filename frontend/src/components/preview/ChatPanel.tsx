import { useState } from "react";
import { chatCampaign } from "../../api/client";

interface ChatPanelProps {
  campaignId: string;
  onUpdateHtml: (html: string) => void;
}

type HistoryItem = {
  role: "user" | "assistant";
  text: string;
};

type PanelContentProps = {
  instruction: string;
  setInstruction: (value: string) => void;
  handleSubmit: () => Promise<void>;
  loading: boolean;
  error: string;
  history: HistoryItem[];
};

function PanelContent({ instruction, setInstruction, handleSubmit, loading, error, history }: PanelContentProps) {
  return (
    <div className="rounded-3xl border border-[#e7ddd0] bg-white p-5 shadow-sm">
      <div className="mb-4 flex items-center justify-between gap-4">
        <div>
          <h2 className="text-lg font-semibold">Assistant de modification IA</h2>
          <p className="mt-1 text-sm text-slate-500">
            Donnez une instruction pour ajuster le contenu de la page et voir l'aperçu se mettre à jour.
          </p>
        </div>
        <span className="rounded-full bg-[#f6f2ed] px-3 py-1 text-xs font-medium text-[#7b6a53]">
          En direct après génération
        </span>
      </div>

      <div className="mb-4">
        <textarea
          rows={3}
          value={instruction}
          onChange={(e) => setInstruction(e.target.value)}
          placeholder="Par exemple : Augmente la pression avec un appel à l'action plus urgent."
          className="input-field min-h-[110px] w-full rounded-2xl border border-[#e7ddd0] bg-[#f9f7f2] p-4 text-sm outline-none transition focus:border-[#e8734a] focus:ring-2 focus:ring-[#e8734a]/10"
        />
      </div>

      {error ? (
        <div className="mb-4 rounded-2xl bg-red-50 px-4 py-3 text-sm text-red-700 border border-red-100">
          {error}
        </div>
      ) : null}

      <div className="flex flex-wrap items-center gap-3">
        <button
          type="button"
          onClick={handleSubmit}
          disabled={loading || !instruction.trim()}
          className="btn-primary inline-flex items-center gap-2 disabled:opacity-50"
        >
          {loading ? "Application en cours..." : "Appliquer à la page"}
        </button>
        <button
          type="button"
          onClick={() => setInstruction("")}
          className="btn-secondary inline-flex items-center gap-2"
        >
          Effacer
        </button>
      </div>

      <div className="mt-6 space-y-4">
        {history.length > 0 && (
          <div className="rounded-3xl border border-[#e7ddd0] bg-[#f9f7f2] p-4">
            <h3 className="mb-3 text-sm font-semibold text-slate-700">Historique des instructions</h3>
            <div className="space-y-3">
              {history.map((entry, index) => (
                <div key={index} className={entry.role === "user" ? "rounded-2xl bg-white p-3 shadow-sm" : "rounded-2xl bg-[#fff8ed] p-3 shadow-sm"}>
                  <div className="mb-1 text-[11px] uppercase tracking-[0.12em] text-slate-500">
                    {entry.role === "user" ? "Vous" : "Assistant"}
                  </div>
                  <pre className="whitespace-pre-wrap text-sm leading-6 text-slate-700">{entry.text}</pre>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default function ChatPanel({ campaignId, onUpdateHtml }: ChatPanelProps) {
  const [instruction, setInstruction] = useState("");
  const [history, setHistory] = useState<HistoryItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [mobileOpen, setMobileOpen] = useState(false);

  const handleSubmit = async () => {
    if (!instruction.trim()) return;
    setLoading(true);
    setError("");

    setHistory((prev) => [...prev, { role: "user", text: instruction.trim() }]);

    try {
      const data = await chatCampaign(campaignId, instruction.trim());
      onUpdateHtml(data.html);
      setHistory((prev) => [
        ...prev,
        {
          role: "assistant",
          text: `Compétence appliquée : ${data.skill}. Changements : ${JSON.stringify(
            data.changes,
            null,
            2
          )}`,
        },
      ]);
      setInstruction("");
    } catch (err: any) {
      const backendMessage = err?.response?.data?.detail || err?.response?.data?.message;
      setError(
        backendMessage ?? (err instanceof Error ? err.message : "Erreur réseau lors de l'édition IA.")
      );
      setHistory((prev) => [
        ...prev,
        {
          role: "assistant",
          text: "La demande n'a pas pu être traitée. Vérifiez que le backend est démarré et que le modèle IA est disponible.",
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const closeMobile = () => setMobileOpen(false);

  return (
    <>
      {/* Desktop / large screens: inline panel */}
      <div className="hidden sm:block">
        <PanelContent
          instruction={instruction}
          setInstruction={setInstruction}
          handleSubmit={handleSubmit}
          loading={loading}
          error={error}
          history={history}
        />
      </div>

      {/* Mobile: floating button + drawer */}
      <div className="sm:hidden">
        <button
          aria-label="Ouvrir l'éditeur IA"
          onClick={() => setMobileOpen(true)}
          className="fixed right-4 bottom-6 z-40 inline-flex items-center gap-2 rounded-full bg-gradient-to-r from-[#f08b5a] to-[#e56f3b] px-4 py-3 text-white shadow-lg"
        >
          💬 Éditeur IA
        </button>

        {mobileOpen && (
          <div className="fixed inset-0 z-50 flex items-end sm:hidden">
            <div className="absolute inset-0 bg-black/40" onClick={closeMobile} />
            <div className="relative w-full rounded-t-2xl bg-white p-4 shadow-xl">
              <div className="mb-3 flex items-center justify-between">
                <h3 className="text-sm font-semibold">Assistant IA</h3>
                <button onClick={closeMobile} className="text-sm text-slate-600">Fermer</button>
              </div>
              <PanelContent
                instruction={instruction}
                setInstruction={setInstruction}
                handleSubmit={handleSubmit}
                loading={loading}
                error={error}
                history={history}
              />
            </div>
          </div>
        )}
      </div>
    </>
  );
}
