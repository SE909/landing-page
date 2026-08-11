import type { BrandingInfo } from "../../types/campaign";

interface Props {
  data: BrandingInfo;
  onChange: (data: BrandingInfo) => void;
}

const TONES = ["Professionnel", "Amical", "Urgent", "Inspirant"];
const MODELS = [
  { value: "ollama", label: "Ollama (Local)" },
  { value: "gpt-5", label: "GPT-5" },
];
const STYLES = ["Moderne", "Classique", "Minimaliste"];

export default function StepBranding({ data, onChange }: Props) {
  return (
    <div>
      <h2 className="mb-6 text-xl font-bold">Branding & ton</h2>
      <div className="grid gap-4 sm:grid-cols-2">
        <div>
          <label className="label-field">Ton de voix</label>
          <select
            className="input-field"
            value={data.tone}
            onChange={(e) => onChange({ ...data, tone: e.target.value })}
          >
            {TONES.map((t) => (
              <option key={t}>{t}</option>
            ))}
          </select>
        </div>
        <div>
          <label className="label-field">Modèle IA</label>
          <select
            className="input-field"
            value={data.ai_model}
            onChange={(e) => onChange({ ...data, ai_model: e.target.value as BrandingInfo["ai_model"] })}
          >
            {MODELS.map((model) => (
              <option key={model.value} value={model.value}>
                {model.label}
              </option>
            ))}
          </select>
        </div>
        <div>
          <label className="label-field">Style</label>
          <select
            className="input-field"
            value={data.style}
            onChange={(e) => onChange({ ...data, style: e.target.value })}
          >
            {STYLES.map((s) => (
              <option key={s}>{s}</option>
            ))}
          </select>
        </div>
        <div>
          <label className="label-field">Couleur principale</label>
          <div className="flex items-center gap-3">
            <input
              type="color"
              value={data.primary_color}
              onChange={(e) =>
                onChange({ ...data, primary_color: e.target.value })
              }
              className="h-10 w-14 cursor-pointer rounded border"
            />
            <input
              className="input-field"
              value={data.primary_color}
              onChange={(e) =>
                onChange({ ...data, primary_color: e.target.value })
              }
            />
          </div>
        </div>
        <div>
          <label className="label-field">Couleur secondaire</label>
          <div className="flex items-center gap-3">
            <input
              type="color"
              value={data.secondary_color}
              onChange={(e) =>
                onChange({ ...data, secondary_color: e.target.value })
              }
              className="h-10 w-14 cursor-pointer rounded border"
            />
            <input
              className="input-field"
              value={data.secondary_color}
              onChange={(e) =>
                onChange({ ...data, secondary_color: e.target.value })
              }
            />
          </div>
        </div>
      </div>

      <div className="mt-6 rounded-lg p-6" style={{ background: data.primary_color }}>
        <p className="text-center text-sm font-medium text-white opacity-80">
          Aperçu des couleurs
        </p>
        <div
          className="mx-auto mt-3 max-w-xs rounded-lg p-4 text-center text-white"
          style={{ background: data.secondary_color }}
        >
          Bouton d'action
        </div>
      </div>
    </div>
  );
}
