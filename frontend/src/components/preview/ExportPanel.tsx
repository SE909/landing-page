import { getExportUrl, getReactExportUrl } from "../../api/client";

interface Props {
  campaignId: string;
  onRegenerate: () => void;
  loading: boolean;
}

export default function ExportPanel({ campaignId, onRegenerate, loading }: Props) {
  return (
    <div className="flex flex-wrap items-center gap-3">
      <button
        type="button"
        onClick={onRegenerate}
        disabled={loading}
        className="btn-secondary inline-flex items-center gap-2 disabled:opacity-50"
      >
        {loading ? "Régénération..." : "Régénérer avec IA"}
      </button>
      <a href={getExportUrl(campaignId)} download className="btn-primary inline-flex items-center gap-2">
        Exporter (.html)
      </a>
      <a
        href={getReactExportUrl(campaignId)}
        download
        className="btn-secondary inline-flex items-center gap-2"
        title="Télécharger une version réutilisable dans un projet React"
      >
        Exporter React (.tsx)
      </a>
    </div>
  );
}
