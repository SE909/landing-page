import { useRef } from "react";
import type { UserInfo } from "../../types/campaign";
import { uploadImage } from "../../api/client";

interface Props {
  data: UserInfo;
  onChange: (data: UserInfo) => void;
}

export default function StepUserInfo({ data, onChange }: Props) {
  const fileRef = useRef<HTMLInputElement>(null);

  const handlePhoto = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    const url = await uploadImage(file);
    onChange({ ...data, photo_url: url });
  };

  return (
    <div>
      <h2 className="mb-6 text-xl font-bold">Informations formateur</h2>
      <div className="grid gap-4 sm:grid-cols-2">
        <div className="sm:col-span-2">
          <label className="label-field">Nom complet *</label>
          <input
            className="input-field"
            value={data.full_name}
            onChange={(e) => onChange({ ...data, full_name: e.target.value })}
            placeholder="Jean Dupont"
          />
        </div>
        <div>
          <label className="label-field">Email *</label>
          <input
            type="email"
            className="input-field"
            value={data.email}
            onChange={(e) => onChange({ ...data, email: e.target.value })}
            placeholder="jean@example.com"
          />
        </div>
        <div>
          <label className="label-field">Téléphone</label>
          <input
            className="input-field"
            value={data.phone || ""}
            onChange={(e) => onChange({ ...data, phone: e.target.value })}
            placeholder="+33 6 00 00 00 00"
          />
        </div>
        <div className="sm:col-span-2">
          <label className="label-field">Site web / LinkedIn</label>
          <input
            className="input-field"
            value={data.website || ""}
            onChange={(e) => onChange({ ...data, website: e.target.value })}
            placeholder="https://linkedin.com/in/..."
          />
        </div>
        <div className="sm:col-span-2">
          <label className="label-field">Bio courte *</label>
          <textarea
            className="input-field"
            rows={3}
            value={data.bio}
            onChange={(e) => onChange({ ...data, bio: e.target.value })}
            placeholder="Expert avec 10 ans d'expérience..."
          />
        </div>
        <div className="sm:col-span-2">
          <label className="label-field">Photo / Logo</label>
          <div className="flex items-center gap-4">
            {data.photo_url && (
              <img
                src={data.photo_url}
                alt="Preview"
                className="h-16 w-16 rounded-full object-cover"
              />
            )}
            <button
              type="button"
              onClick={() => fileRef.current?.click()}
              className="btn-secondary"
            >
              Choisir une image
            </button>
            <input
              ref={fileRef}
              type="file"
              accept="image/*"
              className="hidden"
              onChange={handlePhoto}
            />
          </div>
        </div>
      </div>
    </div>
  );
}
