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
