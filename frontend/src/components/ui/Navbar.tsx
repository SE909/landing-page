import { Link } from "react-router-dom";

const logoUrl = "https://store.aicrafters.com/assets/brand/logo-aic-black.png";

export default function Navbar() {
  return (
    <header className="app-header sticky top-0 z-50 border-b backdrop-blur-md">
      <div className="mx-auto flex max-w-6xl items-center justify-between px-4 py-3.5">
        <Link to="/" className="flex items-center gap-3" aria-label="AI Crafters - accueil">
          <img src={logoUrl} alt="AI Crafters" className="brand-logo" />
          <span className="hidden border-l pl-3 text-sm font-semibold sm:inline" style={{ borderColor: "var(--aic-line)", color: "var(--aic-muted)" }}>
            Landing Builder
          </span>
        </Link>
        <div className="flex items-center gap-3 text-sm font-semibold" style={{ color: "var(--aic-muted)" }}>
          <Link to="/history" className="transition hover:text-[#e8734a]">
            Mes pages
          </Link>
          <Link to="/" className="rounded-full px-4 py-2 text-xs font-semibold text-white transition hover:-translate-y-0.5" style={{ background: "var(--aic-gradient)" }}>
            Créer une page
          </Link>
        </div>
      </div>
    </header>
  );
}
