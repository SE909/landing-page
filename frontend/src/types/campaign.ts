export interface ModuleItem {
  title: string;
  description: string;
  duration: string;
}

export interface Testimonial {
  name: string;
  text: string;
  rating: number;
}

export interface UserInfo {
  full_name: string;
  email: string;
  phone?: string;
  website?: string;
  bio: string;
  photo_url?: string;
}

export interface FormationInfo {
  name: string;
  category: string;
  target_audience: string;
  level: string;
  duration_hours: number;
  format: string;
  short_description: string;
  objectives: string;
  modules: ModuleItem[];
  price: number;
  currency: string;
  bonuses?: string;
  start_date?: string;
}

export interface BrandingInfo {
  tone: string;
  primary_color: string;
  secondary_color: string;
  style: string;
}

export interface SocialProof {
  testimonials: Testimonial[];
  stats?: string;
}

export interface CampaignFormData {
  user_info: UserInfo;
  formation: FormationInfo;
  branding: BrandingInfo;
  social_proof: SocialProof;
}

export const defaultFormData: CampaignFormData = {
  user_info: {
    full_name: "",
    email: "",
    phone: "",
    website: "",
    bio: "",
    photo_url: "",
  },
  formation: {
    name: "",
    category: "Développement",
    target_audience: "",
    level: "Débutant",
    duration_hours: 40,
    format: "En ligne",
    short_description: "",
    objectives: "",
    modules: [{ title: "", description: "", duration: "8h" }],
    price: 299,
    currency: "EUR",
    bonuses: "",
    start_date: "",
  },
  branding: {
    tone: "Professionnel",
    primary_color: "#2563eb",
    secondary_color: "#1e40af",
    style: "Moderne",
  },
  social_proof: {
    testimonials: [],
    stats: "",
  },
};

export const sampleFormData: CampaignFormData = {
  user_info: {
    full_name: "Sarah Martin",
    email: "sarah.martin@example.com",
    phone: "+33 6 12 34 56 78",
    website: "https://linkedin.com/in/sarah-martin-dev",
    bio: "Développeuse Senior & Formatrice certifiée avec 8 ans d'expérience dans le développement Full-Stack Python & React.",
    photo_url: "https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?w=400&auto=format&fit=crop&q=80",
  },
  formation: {
    name: "Masterclass Full-Stack FastAPI & React",
    category: "Développement",
    target_audience: "Développeurs web souhaitant créer des applications modernes et performantes.",
    level: "Intermédiaire",
    duration_hours: 35,
    format: "En ligne",
    short_description: "Apprenez à concevoir, développer et déployer des applications web complètes avec FastAPI, React Vite, Tailwind CSS et MongoDB.",
    objectives: "- Maîtriser l'architecture asynchrone FastAPI\n- Créer des interfaces dynamiques et réactives avec React\n- Intégrer MongoDB avec Motor et Pydantic\n- Connecter un modèle LLM Ollama local",
    modules: [
      {
        title: "Bases & Architecture FastAPI",
        description: "Prise en main des routes, de la validation des données avec Pydantic et des dépendances FastAPI.",
        duration: "8h",
      },
      {
        title: "Interface Frontend avec React & Vite",
        description: "Création de composants réutilisables, gestion des états, formulaires dynamiques et Tailwind CSS.",
        duration: "10h",
      },
      {
        title: "Intégration Base de Données MongoDB & AI local Ollama",
        description: "Persistance asynchrone Motor et génération automatique avec Ollama 3.2.",
        duration: "10h",
      },
      {
        title: "Déploiement & Optimisation Production",
        description: "Dockerisation, gestion des CORS, variables d'environnement et bonnes pratiques de sécurité.",
        duration: "7h",
      },
    ],
    price: 490,
    currency: "EUR",
    bonuses: "Accès à vie au code source complet + Groupe privé Discord d'entraide",
    start_date: "2026-09-01",
  },
  branding: {
    tone: "Inspirant",
    primary_color: "#2563eb",
    secondary_color: "#4f46e5",
    style: "Moderne",
  },
  social_proof: {
    stats: "4.9/5 étoiles sur +350 avis d'anciens élèves",
    testimonials: [
      {
        name: "Alexandre Dubois",
        text: "Cette formation m'a permis de décrocher mon premier poste de développeur Full-Stack en moins de 3 mois !",
        rating: 5,
      },
      {
        name: "Camille Laurent",
        text: "Pédagogie au top, projets très concrets et exemples réalistes. Je recommande à 100%.",
        rating: 5,
      },
    ],
  },
};
