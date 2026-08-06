import type { FormationInfo, ModuleItem } from "../../types/campaign";

interface Props {
  data: FormationInfo;
  onChange: (data: FormationInfo) => void;
}

const CATEGORIES = [
  "Développement",
  "Marketing",
  "Design",
  "Business",
  "Data",
  "Autre",
];

const LEVELS = ["Débutant", "Intermédiaire", "Avancé"];
const FORMATS = ["En ligne", "Présentiel", "Hybride"];

export default function StepFormation({ data, onChange }: Props) {
  const updateModule = (index: number, field: keyof ModuleItem, value: string) => {
    const modules = [...data.modules];
    modules[index] = { ...modules[index], [field]: value };
    onChange({ ...data, modules });
  };

  const addModule = () => {
    onChange({
      ...data,
      modules: [...data.modules, { title: "", description: "", duration: "8h" }],
    });
  };

  const removeModule = (index: number) => {
    if (data.modules.length <= 1) return;
    onChange({ ...data, modules: data.modules.filter((_, i) => i !== index) });
  };

  return (
    <div>
      <h2 className="mb-6 text-xl font-bold">Informations formation</h2>
      <div className="grid gap-4 sm:grid-cols-2">
        <div className="sm:col-span-2">
          <label className="label-field">Nom de la formation *</label>
          <input
            className="input-field"
            value={data.name}
            onChange={(e) => onChange({ ...data, name: e.target.value })}
            placeholder="Python pour débutants"
          />
        </div>
        <div>
          <label className="label-field">Catégorie</label>
          <select
            className="input-field"
            value={data.category}
            onChange={(e) => onChange({ ...data, category: e.target.value })}
          >
            {CATEGORIES.map((c) => (
              <option key={c}>{c}</option>
            ))}
          </select>
        </div>
        <div>
          <label className="label-field">Niveau</label>
          <select
            className="input-field"
            value={data.level}
            onChange={(e) => onChange({ ...data, level: e.target.value })}
          >
            {LEVELS.map((l) => (
              <option key={l}>{l}</option>
            ))}
          </select>
        </div>
        <div>
          <label className="label-field">Public cible *</label>
          <input
            className="input-field"
            value={data.target_audience}
            onChange={(e) =>
              onChange({ ...data, target_audience: e.target.value })
            }
            placeholder="Débutants sans expérience"
          />
        </div>
        <div>
          <label className="label-field">Durée (heures)</label>
          <input
            type="number"
            className="input-field"
            value={data.duration_hours}
            onChange={(e) =>
              onChange({ ...data, duration_hours: Number(e.target.value) })
            }
          />
        </div>
        <div>
          <label className="label-field">Format</label>
          <select
            className="input-field"
            value={data.format}
            onChange={(e) => onChange({ ...data, format: e.target.value })}
          >
            {FORMATS.map((f) => (
              <option key={f}>{f}</option>
            ))}
          </select>
        </div>
        <div>
          <label className="label-field">Prix (EUR)</label>
          <input
            type="number"
            className="input-field"
            value={data.price}
            onChange={(e) =>
              onChange({ ...data, price: Number(e.target.value) })
            }
          />
        </div>
        <div className="sm:col-span-2">
          <label className="label-field">Description courte *</label>
          <textarea
            className="input-field"
            rows={2}
            value={data.short_description}
            onChange={(e) =>
              onChange({ ...data, short_description: e.target.value })
            }
          />
        </div>
        <div className="sm:col-span-2">
          <label className="label-field">Objectifs pédagogiques *</label>
          <textarea
            className="input-field"
            rows={3}
            value={data.objectives}
            onChange={(e) => onChange({ ...data, objectives: e.target.value })}
          />
        </div>
        <div className="sm:col-span-2">
          <label className="label-field">Bonus inclus</label>
          <input
            className="input-field"
            value={data.bonuses || ""}
            onChange={(e) => onChange({ ...data, bonuses: e.target.value })}
            placeholder="Accès à vie, certificat, support..."
          />
        </div>
      </div>

      <div className="mt-6">
        <div className="mb-3 flex items-center justify-between">
          <h3 className="font-semibold">Modules du programme</h3>
          <button type="button" onClick={addModule} className="btn-secondary text-xs">
            + Ajouter un module
          </button>
        </div>
        {data.modules.map((mod, i) => (
          <div key={i} className="mb-4 rounded-xl border border-[#e7ddd0] bg-[#fffaf6] p-4">
            <div className="mb-2 flex justify-between">
              <span className="text-sm font-medium text-gray-500">
                Module {i + 1}
              </span>
              {data.modules.length > 1 && (
                <button
                  type="button"
                  onClick={() => removeModule(i)}
                  className="text-xs text-red-500"
                >
                  Supprimer
                </button>
              )}
            </div>
            <div className="grid gap-3 sm:grid-cols-3">
              <input
                className="input-field sm:col-span-2"
                placeholder="Titre du module"
                value={mod.title}
                onChange={(e) => updateModule(i, "title", e.target.value)}
              />
              <input
                className="input-field"
                placeholder="Durée (ex: 8h)"
                value={mod.duration}
                onChange={(e) => updateModule(i, "duration", e.target.value)}
              />
              <textarea
                className="input-field sm:col-span-3"
                rows={2}
                placeholder="Description"
                value={mod.description}
                onChange={(e) => updateModule(i, "description", e.target.value)}
              />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
