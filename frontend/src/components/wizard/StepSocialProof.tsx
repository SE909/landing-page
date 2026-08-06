import type { SocialProof, Testimonial } from "../../types/campaign";

interface Props {
  data: SocialProof;
  onChange: (data: SocialProof) => void;
}

export default function StepSocialProof({ data, onChange }: Props) {
  const updateTestimonial = (
    index: number,
    field: keyof Testimonial,
    value: string | number
  ) => {
    const testimonials = [...data.testimonials];
    testimonials[index] = { ...testimonials[index], [field]: value };
    onChange({ ...data, testimonials });
  };

  const addTestimonial = () => {
    onChange({
      ...data,
      testimonials: [
        ...data.testimonials,
        { name: "", text: "", rating: 5 },
      ],
    });
  };

  const removeTestimonial = (index: number) => {
    onChange({
      ...data,
      testimonials: data.testimonials.filter((_, i) => i !== index),
    });
  };

  return (
    <div>
      <h2 className="mb-2 text-xl font-bold">Preuve sociale</h2>
      <p className="mb-6 text-sm text-gray-500">
        Optionnel — laissez vide pour que l'IA génère du contenu adapté.
      </p>

      <div className="mb-6">
        <label className="label-field">Statistique clé</label>
        <input
          className="input-field"
          value={data.stats || ""}
          onChange={(e) => onChange({ ...data, stats: e.target.value })}
          placeholder="500+ élèves formés — Note moyenne 4.8/5"
        />
      </div>

      <div className="mb-3 flex items-center justify-between">
        <h3 className="font-semibold">Témoignages</h3>
        <button type="button" onClick={addTestimonial} className="btn-secondary text-xs">
          + Ajouter un témoignage
        </button>
      </div>

      {data.testimonials.length === 0 && (
        <p className="text-sm text-gray-400">Aucun témoignage ajouté.</p>
      )}

      {data.testimonials.map((t, i) => (
        <div key={i} className="mb-4 rounded-xl border border-[#e7ddd0] bg-[#fffaf6] p-4">
          <div className="mb-2 flex justify-between">
            <span className="text-sm font-medium text-gray-500">
              Témoignage {i + 1}
            </span>
            <button
              type="button"
              onClick={() => removeTestimonial(i)}
              className="text-xs text-red-500"
            >
              Supprimer
            </button>
          </div>
          <div className="grid gap-3 sm:grid-cols-2">
            <input
              className="input-field"
              placeholder="Nom"
              value={t.name}
              onChange={(e) => updateTestimonial(i, "name", e.target.value)}
            />
            <select
              className="input-field"
              value={t.rating}
              onChange={(e) =>
                updateTestimonial(i, "rating", Number(e.target.value))
              }
            >
              {[5, 4, 3, 2, 1].map((r) => (
                <option key={r} value={r}>
                  {r} étoile{r > 1 ? "s" : ""}
                </option>
              ))}
            </select>
            <textarea
              className="input-field sm:col-span-2"
              rows={2}
              placeholder="Témoignage"
              value={t.text}
              onChange={(e) => updateTestimonial(i, "text", e.target.value)}
            />
          </div>
        </div>
      ))}
    </div>
  );
}
