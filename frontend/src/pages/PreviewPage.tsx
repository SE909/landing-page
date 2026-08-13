import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { generateLandingPage, getCampaign } from "../api/client";
import ExportPanel from "../components/preview/ExportPanel";
import LivePreview from "../components/preview/LivePreview";
import ChatPanel from "../components/preview/ChatPanel";
import Navbar from "../components/ui/Navbar";

export default function PreviewPage() {
  const { id } = useParams<{ id: string }>();
  const [campaignName, setCampaignName] = useState("Landing Page");
  const [html, setHtml] = useState("");
  const [loading, setLoading] = useState(true);
  const [regenerating, setRegenerating] = useState(false);
  const [error, setError] = useState("");
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [chatOpen, setChatOpen] = useState(false);

  useEffect(() => {
    if (!id) return;
    getCampaign(id)
      .then((campaign) => {
        if (campaign.formation?.name) {
          setCampaignName(campaign.formation.name);
        }

        if (campaign.generated_html && campaign.page_state) {
          setHtml(campaign.generated_html);
          return;
        }

        return generateLandingPage(id).then((res) => setHtml(res.html));
      })
      .catch(() => setError("Impossible de charger la landing page."))
      .finally(() => setLoading(false));
  }, [id]);

  const handleRegenerate = async () => {
    if (!id) return;
    setRegenerating(true);
    setError("");
    setChatOpen(false);
    try {
      const res = await generateLandingPage(id);
      setHtml(res.html);
    } catch {
      setError("Erreur lors de la régénération.");
    } finally {
      setRegenerating(false);
    }
  };

  const handleToggleFullscreen = () => {
    setIsFullscreen((prev) => !prev);
  };

  const handleToggleChat = () => {
    setChatOpen((prev) => !prev);
  };

  if (loading) {
    return (
      <div className="app-shell min-h-screen flex flex-col">
        <Navbar />
        <div className="flex flex-1 flex-col items-center justify-center gap-3">
          <svg className="coral-text h-8 w-8 animate-spin" viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"></path>
          </svg>
          <p className="text-sm font-medium text-gray-600">Chargement de l'aperçu...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="app-shell min-h-screen flex flex-col">
      <Navbar />
      <main className={`flex-1 py-6 px-4 ${isFullscreen ? "bg-[#f6f4ef]" : ""}`}>
        <div className={`mx-auto ${isFullscreen || !chatOpen ? "max-w-full" : "max-w-6xl"}`}>
          <div className="app-surface mb-6 flex flex-wrap items-center justify-between gap-4 rounded-2xl p-4 shadow-sm">
            <div>
              <Link to="/" className="coral-text inline-flex items-center gap-1 text-xs font-semibold hover:underline">
                ← Retour au formulaire
              </Link>
              <h1 className="app-title mt-1 text-xl font-bold">{campaignName}</h1>
            </div>
            <div className="flex flex-wrap items-center gap-3">
              <button
                type="button"
                onClick={handleToggleFullscreen}
                className="btn-secondary inline-flex items-center gap-2"
                aria-pressed={isFullscreen}
              >
                {isFullscreen ? "Quitter le plein écran" : "Plein écran"}
              </button>
              <button
                type="button"
                onClick={handleToggleChat}
                className="btn-secondary inline-flex items-center gap-2"
              >
                {chatOpen ? "Masquer l'éditeur" : "Afficher l'éditeur"}
              </button>
              {id && (
                <ExportPanel
                  campaignId={id}
                  onRegenerate={handleRegenerate}
                  loading={regenerating}
                />
              )}
            </div>
          </div>

          {error && (
            <div className="mb-4 rounded-lg bg-red-50 p-3.5 text-sm text-red-600 border border-red-200">
              {error}
            </div>
          )}

          <div className={`grid gap-6 ${!chatOpen ? "grid-cols-1" : isFullscreen ? "lg:grid-cols-[3fr_1fr]" : "xl:grid-cols-[1.5fr_0.8fr]"}`}>
            <div className={isFullscreen ? "min-h-[calc(100vh-160px)]" : ""}>
              {html ? (
                <LivePreview html={html} />
              ) : (
                <p className="text-gray-500">Aucune page générée.</p>
              )}
            </div>
            {id && chatOpen ? (
              <div className={isFullscreen ? "max-h-[calc(100vh-180px)] overflow-auto" : ""}>
                <ChatPanel
                  campaignId={id}
                  onUpdateHtml={(updatedHtml) => setHtml(updatedHtml)}
                />
              </div>
            ) : null}
          </div>
        </div>
      </main>
    </div>
  );
}
