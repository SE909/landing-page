import type { CampaignFormData } from "../../types/campaign";

interface Props {
  data: CampaignFormData;
}

export default function StepReview({ data }: Props) {
  return (
    <div>
      <h2 className="mb-6 text-xl font-bold">Récapitulatif</h2>
      <div className="space-y-4 text-sm">
        <div className="rounded-xl border border-[#e7ddd0] bg-[#fffaf6] p-4">
          <h3 className="mb-2 font-semibold text-gray-700">Formateur</h3>
          <p>{data.user_info.full_name}</p>
          <p className="text-gray-500">{data.user_info.email}</p>
        </div>
        <div className="rounded-xl border border-[#e7ddd0] bg-[#fffaf6] p-4">
          <h3 className="mb-2 font-semibold text-gray-700">Formation</h3>
          <p className="font-medium">{data.formation.name}</p>
          <p className="text-gray-500">
            {data.formation.category} — {data.formation.level} —{" "}
            {data.formation.duration_hours}h — {data.formation.price}{" "}
            {data.formation.currency}
          </p>
          <p className="mt-1 text-gray-500">
            {data.formation.modules.length} module(s)
          </p>
        </div>
        <div className="rounded-xl border border-[#e7ddd0] bg-[#fffaf6] p-4">
          <h3 className="mb-2 font-semibold text-gray-700">Branding</h3>
          <div className="flex flex-wrap items-center gap-3 text-sm">
            <span>Ton : {data.branding.tone}</span>
            <span>Modèle IA : {data.branding.ai_model === "ollama" ? "Ollama (Local)" : "GPT-5"}</span>
            <span
              className="inline-block h-5 w-5 rounded-full"
              style={{ background: data.branding.primary_color }}
            />
            <span
              className="inline-block h-5 w-5 rounded-full"
              style={{ background: data.branding.secondary_color }}
            />
          </div>
        </div>
        {data.social_proof.testimonials.length > 0 && (
          <div className="rounded-xl border border-[#e7ddd0] bg-[#fffaf6] p-4">
            <h3 className="mb-2 font-semibold text-gray-700">Preuve sociale</h3>
            <p>{data.social_proof.testimonials.length} témoignage(s)</p>
          </div>
        )}
      </div>
      <p className="mt-4 text-sm text-gray-500">
        Cliquez sur "Générer ma landing page" pour créer votre page avec l'IA.
      </p>
    </div>
  );
}
