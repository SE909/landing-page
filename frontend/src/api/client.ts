import axios from "axios";
import type { CampaignFormData } from "../types/campaign";

const api = axios.create({ baseURL: "/api" });

export async function createCampaign(data: CampaignFormData) {
  const res = await api.post("/campaigns", data);
  return res.data;
}

export async function getCampaign(campaignId: string) {
  const res = await api.get(`/campaigns/${campaignId}`);
  return res.data;
}

export async function listCampaigns() {
  const res = await api.get("/campaigns");
  return res.data;
}

export async function deleteCampaign(campaignId: string) {
  const res = await api.delete(`/campaigns/${campaignId}`);
  return res.data;
}

export async function generateLandingPage(campaignId: string) {
  const res = await api.post(`/campaigns/${campaignId}/generate`);
  return res.data;
}

export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
}

export interface ChatEditResponse {
  reply: string;
  changed: string[];
  page_state: Record<string, unknown>;
  html?: string;
}

export async function chatEditPage(
  campaignId: string,
  message: string,
  history: ChatMessage[] = [],
  skillId?: string
) {
  const res = await api.post(`/campaigns/${campaignId}/chat`, {
    message,
    history,
    skill_id: skillId,
  });
  return res.data as ChatEditResponse;
}

export interface Skill {
  id: string;
  label: string;
  icon: string;
  description: string;
}

export async function listSkills() {
  const res = await api.get("/skills");
  return res.data as Skill[];
}

export async function uploadImage(file: File) {
  const form = new FormData();
  form.append("file", file);
  const res = await api.post("/upload", form);
  return res.data.url as string;
}

export function getExportUrl(campaignId: string) {
  return `/api/export/${campaignId}`;
}

export function getReactExportUrl(campaignId: string) {
  return `/api/export/${campaignId}/react`;
}
