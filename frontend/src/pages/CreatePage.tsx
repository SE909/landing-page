import WizardForm from "../components/wizard/WizardForm";
import Navbar from "../components/ui/Navbar";

export default function CreatePage() {
  return (
    <div className="app-shell min-h-screen flex flex-col">
      <Navbar />
      <main className="flex-1 py-10 px-4">
        <div className="mb-8 text-center">
          <p className="mb-2 text-xs font-bold uppercase tracking-[0.2em] coral-text">AI Crafters</p>
          <h1 className="app-title text-3xl font-extrabold sm:text-4xl tracking-tight">
            Générateur de Landing Page
          </h1>
          <p className="app-copy mt-2 text-base max-w-xl mx-auto">
            Créez une page de vente à fort taux de conversion pour votre formation grâce à notre wizard guidé et notre IA Ollama.
          </p>
        </div>
        <WizardForm />
      </main>
    </div>
  );
}
