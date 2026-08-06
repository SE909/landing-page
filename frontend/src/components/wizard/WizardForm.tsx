import { useState } from "react";
import { useNavigate } from "react-router-dom";
import type { CampaignFormData } from "../../types/campaign";
import { defaultFormData, sampleFormData } from "../../types/campaign";
import { createCampaign, generateLandingPage } from "../../api/client";
import StepUserInfo from "./StepUserInfo";
import StepFormation from "./StepFormation";
import StepBranding from "./StepBranding";
import StepSocialProof from "./StepSocialProof";
import StepReview from "./StepReview";

const STEPS = [
  "Informations formateur",
  "Formation",
  "Branding",
  "Preuve sociale",
  "Récapitulatif",
];

export default function WizardForm() {
  const navigate = useNavigate();
  const [step, setStep] = useState(0);
  const [formData, setFormData] = useState<CampaignFormData>(defaultFormData);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const updateForm = (partial: Partial<CampaignFormData>) => {
    setFormData((prev) => ({ ...prev, ...partial }));
  };

  const fillSampleData = () => {
    setFormData(sampleFormData);
  };

  const next = () => setStep((s) => Math.min(s + 1, STEPS.length - 1));
  const prev = () => setStep((s) => Math.max(s - 1, 0));

  const handleGenerate = async () => {
    setLoading(true);
    setError("");
    try {
      const campaign = await createCampaign(formData);
      await generateLandingPage(campaign.id);
      navigate(`/preview/${campaign.id}`);
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Erreur lors de la génération. Vérifiez que MongoDB et Ollama sont démarrés."
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="mx-auto max-w-3xl">
      <div className="mb-6 flex justify-end">
        <button
          type="button"
          onClick={fillSampleData}
          className="coral-soft inline-flex items-center gap-1.5 rounded-full border border-[#f0c5b0] px-3.5 py-1.5 text-xs font-semibold transition hover:bg-[#fbe8de]"
        >
          💡 Remplir avec un exemple
        </button>
      </div>

      <div className="mb-8">
        <div className="mb-4 flex justify-between">
          {STEPS.map((label, i) => (
            <div key={label} className="flex flex-1 flex-col items-center">
              <div
                className={`flex h-8 w-8 items-center justify-center rounded-full text-sm font-bold transition-all ${
                  i <= step
                    ? "text-white shadow-md shadow-[#e8734a]/30"
                    : "bg-[#e7ddd0] text-[#6b6357]"
                }`}
                style={i <= step ? { background: "var(--aic-gradient)" } : undefined}
              >
                {i + 1}
              </div>
              <span className={`mt-1 hidden text-xs font-medium sm:block ${i === step ? "coral-text font-semibold" : "text-[#6b6357]"}`}>
                {label}
              </span>
            </div>
          ))}
        </div>
        <div className="h-2 rounded-full bg-[#e7ddd0] overflow-hidden">
          <div
            className="h-2 rounded-full transition-all duration-300"
            style={{ width: `${((step + 1) / STEPS.length) * 100}%`, background: "var(--aic-gradient)" }}
          />
        </div>
      </div>

      <div className="card">
        {step === 0 && (
          <StepUserInfo
            data={formData.user_info}
            onChange={(user_info) => updateForm({ user_info })}
          />
        )}
        {step === 1 && (
          <StepFormation
            data={formData.formation}
            onChange={(formation) => updateForm({ formation })}
          />
        )}
        {step === 2 && (
          <StepBranding
            data={formData.branding}
            onChange={(branding) => updateForm({ branding })}
          />
        )}
        {step === 3 && (
          <StepSocialProof
            data={formData.social_proof}
            onChange={(social_proof) => updateForm({ social_proof })}
          />
        )}
        {step === 4 && <StepReview data={formData} />}

        {error && (
          <div className="mt-4 rounded-lg bg-red-50 p-3.5 text-sm text-red-600 border border-red-200">
            {error}
          </div>
        )}

        <div className="mt-6 flex justify-between pt-4 border-t border-gray-100">
          <button
            type="button"
            onClick={prev}
            disabled={step === 0}
            className="btn-secondary disabled:opacity-40"
          >
            Précédent
          </button>
          {step < STEPS.length - 1 ? (
            <button type="button" onClick={next} className="btn-primary">
              Suivant →
            </button>
          ) : (
            <button
              type="button"
              onClick={handleGenerate}
              disabled={loading}
              className="btn-primary shadow-md shadow-[#e8734a]/20"
            >
              {loading ? (
                <span className="flex items-center gap-2">
                  <svg className="h-4 w-4 animate-spin" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"></path>
                  </svg>
                  Génération Ollama...
                </span>
              ) : (
                "✨ Générer ma landing page"
              )}
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
