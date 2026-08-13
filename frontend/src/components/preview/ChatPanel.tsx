import { useState, useEffect, useRef } from "react";
import { applyChatCampaign, chatCampaign } from "../../api/client";

interface ChatPanelProps {
  campaignId: string;
  onUpdateHtml: (html: string) => void;
}

type HistoryItem = {
  role: "user" | "assistant";
  text: string;
};

type ChatResponse = {
  message: string;
  proposal?: {
    id: string;
    html_preview: string;
  };
  html?: string;
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
  const historyRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    if (historyRef.current) {
      try {
        historyRef.current.scrollTo({ top: historyRef.current.scrollHeight, behavior: "smooth" });
      } catch (e) {
        historyRef.current.scrollTop = historyRef.current.scrollHeight;
      }
    }
  }, [history]);

  return (
    <div className="flex h-full flex-col rounded-3xl border border-[#e7ddd0] bg-white p-5 shadow-sm">
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

      <div className="mt-6 flex flex-1 flex-col">
          {history.length > 0 && (
            <div ref={historyRef} className="rounded-3xl border border-[#e7ddd0] bg-[#f9f7f2] p-4 mb-4 flex-1 overflow-auto max-h-[55vh]">
            <h3 className="mb-3 text-sm font-semibold text-slate-700">Historique des instructions</h3>
            <div className="space-y-3">
              {/* Transform history so assistant responses appear before the user's message when they are consecutive */}
              {(() => {
                const display: HistoryItem[] = [];
                for (let i = 0; i < history.length; i++) {
                  const entry = history[i];
                  const next = history[i + 1];
                  if (entry.role === "user" && next && next.role === "assistant") {
                    // show user request above assistant response
                    display.push(entry);
                    display.push(next);
                    i++; // skip next since we've already pushed it
                  } else {
                    display.push(entry);
                  }
                }
                return display.map((entry, index) => (
                  <div key={index} className={entry.role === "user" ? "rounded-2xl bg-white p-3 shadow-sm" : "rounded-2xl bg-[#fff8ed] p-3 shadow-sm"}>
                    <div className="mb-1 text-[11px] uppercase tracking-[0.12em] text-slate-500">
                      {entry.role === "user" ? "Vous" : "Assistant"}
                    </div>
                    <pre className="whitespace-pre-wrap text-sm leading-6 text-slate-700">{entry.text}</pre>
                  </div>
                ));
              })()}
            </div>
          </div>
        )}

        {/* Input area stays fixed at bottom of the panel */}
        <div className="mt-4 w-full">
          {error ? (
            <div className="mb-2 rounded-2xl bg-red-50 px-4 py-3 text-sm text-red-700 border border-red-100">
              {error}
            </div>
          ) : null}

          <div className="mb-4">
            <textarea
              rows={3}
              value={instruction}
              onChange={(e) => setInstruction(e.target.value)}
              placeholder="Par exemple : Augmente la pression avec un appel à l'action plus urgent."
              className="input-field min-h-[110px] w-full rounded-2xl border border-[#e7ddd0] bg-[#f9f7f2] p-4 text-sm outline-none transition focus:border-[#e8734a] focus:ring-2 focus:ring-[#e8734a]/10"
            />
          </div>

          <div className="flex flex-wrap items-center gap-3">
            <button
              type="button"
              onClick={handleSubmit}
              disabled={loading || !instruction.trim()}
              className="btn-primary inline-flex items-center gap-2 disabled:opacity-50"
            >
              {loading ? "Envoi en cours..." : "Envoyer"}
            </button>
            <button
              type="button"
              onClick={() => setInstruction("")}
              className="btn-secondary inline-flex items-center gap-2"
            >
              Effacer
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default function ChatPanel({ campaignId, onUpdateHtml }: ChatPanelProps) {
  const [instruction, setInstruction] = useState("");
  const [history, setHistory] = useState<HistoryItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [pendingProposal, setPendingProposal] = useState<any>(null);
  const [mobileOpen, setMobileOpen] = useState(false);

  const handleSubmit = async () => {
    if (!instruction.trim()) return;
    const submittedInstruction = instruction.trim();
    setLoading(true);
    setError("");
    setHistory((prev) => [...prev, { role: "user", text: submittedInstruction }]);
    setInstruction("");

    try {
      const data = (await chatCampaign(campaignId, submittedInstruction)) as ChatResponse;
      const message = data.message;

      if (data.proposal?.html_preview) {
        setPendingProposal({ proposal_id: data.proposal.id });
        onUpdateHtml(data.proposal.html_preview);
      }

      setHistory((prev) => [
        ...prev,
        { role: "assistant", text: message },
      ]);

      if (data.proposal?.html_preview) {
        return;
      }

      if (data.html) {
        onUpdateHtml(data.html);
      }
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

  const handleConfirm = async () => {
    if (!pendingProposal) return;
    setLoading(true);
    setError("");

    try {
      const data = (await applyChatCampaign(campaignId, pendingProposal.proposal_id)) as ChatResponse;
      if (data.html) {
        onUpdateHtml(data.html);
      }
      setHistory((prev) => [
        ...prev,
        { role: "assistant", text: data.message },
      ]);
      setPendingProposal(null);
    } catch (err: any) {
      setError(err?.response?.data?.detail || "Échec de l'application des changements.");
    } finally {
      setLoading(false);
    }
  };

  const handleCancelProposal = () => {
    setPendingProposal(null);
    setHistory((prev) => [
      ...prev,
      { role: "assistant", text: "La proposition a été annulée." },
    ]);
  };

  const proposalActions = pendingProposal ? (
    <div className="mt-3 flex flex-wrap gap-2">
      <button
        type="button"
        onClick={handleConfirm}
        disabled={loading}
        className="btn-primary inline-flex items-center gap-2"
      >
        {loading ? "Application..." : "Confirmer et appliquer"}
      </button>
      <button
        type="button"
        onClick={handleCancelProposal}
        disabled={loading}
        className="btn-secondary inline-flex items-center gap-2"
      >
        Annuler
      </button>
    </div>
  ) : null;

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
        {proposalActions}
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

              {proposalActions}
            </div>
          </div>
        )}
      </div>
    </>
  );
}
