import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { listCampaigns, deleteCampaign, getExportUrl } from "../api/client";
import Navbar from "../components/ui/Navbar";

interface CampaignItem {
  id: string;
  formation: {
    name: string;
    category: string;
    price: number;
    currency: string;
  };
  user_info: {
    full_name: string;
  };
  status: string;
  created_at: string;
}

export default function HistoryPage() {
  const [campaigns, setCampaigns] = useState<CampaignItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const loadCampaigns = async () => {
    try {
      const data = await listCampaigns();
      setCampaigns(data);
    } catch {
      setError("Impossible de charger l'historique des campagnes.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadCampaigns();
  }, []);

  const handleDelete = async (id: string) => {
    if (!confirm("Voulez-vous vraiment supprimer cette landing page ?")) return;
    try {
      await deleteCampaign(id);
      setCampaigns((prev) => prev.filter((c) => c.id !== id));
    } catch {
      alert("Erreur lors de la suppression.");
    }
  };

  return (
    <div className="app-shell min-h-screen flex flex-col">
      <Navbar />
      <main className="flex-1 py-10 px-4">
        <div className="mx-auto max-w-5xl">
          <div className="mb-8 flex items-center justify-between">
            <div>
              <p className="mb-1 text-xs font-bold uppercase tracking-[0.2em] coral-text">AI Crafters</p>
              <h1 className="app-title text-2xl font-bold">Mes Landing Pages</h1>
              <p className="app-copy text-sm mt-1">
                Gérez et téléchargez vos landing pages générées.
              </p>
            </div>
            <Link
              to="/"
              className="btn-primary inline-flex items-center gap-1.5"
            >
              + Nouvelle Landing Page
            </Link>
          </div>

          {error && (
            <div className="mb-4 rounded-lg bg-red-50 p-3.5 text-sm text-red-600 border border-red-200">
              {error}
            </div>
          )}

          {loading ? (
            <div className="flex justify-center py-12">
              <svg className="coral-text h-8 w-8 animate-spin" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"></path>
              </svg>
            </div>
          ) : campaigns.length === 0 ? (
            <div className="card p-12 text-center">
              <div className="coral-soft mx-auto flex h-12 w-12 items-center justify-center rounded-full text-2xl">
                📄
              </div>
              <h3 className="mt-4 text-base font-semibold text-gray-900">Aucune landing page trouvée</h3>
              <p className="mt-1 text-sm text-gray-500">
                Créez votre première landing page dès maintenant avec notre wizard.
              </p>
              <div className="mt-6">
                <Link to="/" className="btn-primary">
                  Créer une landing page
                </Link>
              </div>
            </div>
          ) : (
            <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
              {campaigns.map((c) => (
                <div
                  key={c.id}
                  className="card flex flex-col justify-between p-5 transition hover:-translate-y-0.5"
                >
                  <div>
                    <div className="flex items-center justify-between">
                      <span className="coral-soft rounded-full px-2.5 py-0.5 text-xs font-semibold">
                        {c.formation?.category || "Formation"}
                      </span>
                      <span
                        className={`text-xs font-medium ${
                          c.status === "generated" ? "text-green-600" : "text-amber-600"
                        }`}
                      >
                        {c.status === "generated" ? "✓ Générée" : "Brouillon"}
                      </span>
                    </div>

                    <h3 className="mt-3 text-base font-bold text-gray-900 line-clamp-1">
                      {c.formation?.name || "Sans titre"}
                    </h3>
                    <p className="mt-1 text-xs text-gray-500">
                      Par {c.user_info?.full_name || "Formateur"} • {c.formation?.price} {c.formation?.currency || "EUR"}
                    </p>
                  </div>

                  <div className="mt-5 flex items-center justify-between border-t border-gray-100 pt-3 text-xs">
                    <Link
                      to={`/preview/${c.id}`}
                      className="coral-text font-semibold hover:underline"
                    >
                      👁️ Aperçu
                    </Link>
                    <a
                      href={getExportUrl(c.id)}
                      download
                      className="font-semibold text-gray-600 hover:text-gray-900"
                    >
                      📥 HTML
                    </a>
                    <button
                      type="button"
                      onClick={() => handleDelete(c.id)}
                      className="font-medium text-red-500 hover:text-red-700"
                    >
                      Supprimer
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
