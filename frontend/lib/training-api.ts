/**
 * API client for training endpoints.
 */

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

// Types
export interface TrainingExample {
  id: string;
  created_at: string;
  system_prompt: string;
  user_input: string;
  assistant_output: string;
  category: string;
  language: string;
  quality_rating: number | null;
  is_approved: boolean;
}

export interface TrainingDataset {
  id: string;
  name: string;
  description: string;
  example_count: number;
  approved_count: number;
  created_at: string;
  updated_at: string;
  examples?: TrainingExample[];
}

export interface TrainingConfig {
  base_model: string;
  lora_r: number;
  lora_alpha: number;
  lora_dropout: number;
  epochs: number;
  batch_size: number;
  gradient_accumulation_steps: number;
  learning_rate: number;
  warmup_steps: number;
  max_seq_length: number;
  output_name: string;
}

export interface TrainingJob {
  id: string;
  status: "pending" | "preparing" | "training" | "completed" | "failed" | "cancelled";
  progress: number;
  current_step: number;
  total_steps: number;
  created_at: string;
  started_at: string | null;
  completed_at: string | null;
  config: TrainingConfig;
  output_path: string | null;
  error_message: string | null;
  metrics: Record<string, number>;
}

export interface BaseModel {
  id: string;
  name: string;
  description: string;
  size: string;
  vram_required: string;
}

export interface TrainedModel {
  name: string;
  path: string;
  type: "lora" | "gguf";
  size_mb?: number;
  created_at: string;
}

// ============== Dataset APIs ==============

export async function listDatasets(): Promise<TrainingDataset[]> {
  const response = await fetch(`${API_URL}/api/training/datasets`);
  if (!response.ok) throw new Error("Failed to fetch datasets");
  const data = await response.json();
  return data.datasets;
}

export async function createDataset(name: string, description: string = ""): Promise<TrainingDataset> {
  const response = await fetch(`${API_URL}/api/training/datasets`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name, description }),
  });
  if (!response.ok) throw new Error("Failed to create dataset");
  return response.json();
}

export async function getDataset(datasetId: string): Promise<TrainingDataset & { examples: TrainingExample[] }> {
  const response = await fetch(`${API_URL}/api/training/datasets/${datasetId}`);
  if (!response.ok) throw new Error("Failed to fetch dataset");
  return response.json();
}

export async function deleteDataset(datasetId: string): Promise<void> {
  const response = await fetch(`${API_URL}/api/training/datasets/${datasetId}`, {
    method: "DELETE",
  });
  if (!response.ok) throw new Error("Failed to delete dataset");
}

// ============== Example APIs ==============

export async function addExample(
  datasetId: string,
  data: {
    user_input: string;
    assistant_output: string;
    system_prompt?: string;
    category?: string;
    language?: string;
    is_approved?: boolean;
  }
): Promise<TrainingExample> {
  const response = await fetch(`${API_URL}/api/training/datasets/${datasetId}/examples`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  if (!response.ok) throw new Error("Failed to add example");
  return response.json();
}

export async function updateExample(
  datasetId: string,
  exampleId: string,
  data: Partial<TrainingExample>
): Promise<TrainingExample> {
  const response = await fetch(
    `${API_URL}/api/training/datasets/${datasetId}/examples/${exampleId}`,
    {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    }
  );
  if (!response.ok) throw new Error("Failed to update example");
  return response.json();
}

export async function deleteExample(datasetId: string, exampleId: string): Promise<void> {
  const response = await fetch(
    `${API_URL}/api/training/datasets/${datasetId}/examples/${exampleId}`,
    { method: "DELETE" }
  );
  if (!response.ok) throw new Error("Failed to delete example");
}

export async function approveExample(
  datasetId: string,
  exampleId: string,
  approved: boolean = true
): Promise<void> {
  const response = await fetch(
    `${API_URL}/api/training/datasets/${datasetId}/examples/${exampleId}/approve?approved=${approved}`,
    { method: "POST" }
  );
  if (!response.ok) throw new Error("Failed to approve example");
}

export async function rateExample(
  datasetId: string,
  exampleId: string,
  rating: number
): Promise<void> {
  const response = await fetch(
    `${API_URL}/api/training/datasets/${datasetId}/examples/${exampleId}/rate?rating=${rating}`,
    { method: "POST" }
  );
  if (!response.ok) throw new Error("Failed to rate example");
}

export async function exportDataset(
  datasetId?: string,
  format: "jsonl" | "alpaca" | "sharegpt" = "jsonl",
  onlyApproved: boolean = true
): Promise<string> {
  const params = new URLSearchParams();
  if (datasetId) params.append("dataset_id", datasetId);
  params.append("format", format);
  params.append("only_approved", String(onlyApproved));

  const response = await fetch(`${API_URL}/api/training/datasets/export?${params}`, {
    method: "POST",
  });
  if (!response.ok) throw new Error("Failed to export dataset");
  const data = await response.json();
  return data.file_path;
}

// ============== Training Job APIs ==============

export async function listJobs(): Promise<TrainingJob[]> {
  const response = await fetch(`${API_URL}/api/training/jobs`);
  if (!response.ok) throw new Error("Failed to fetch jobs");
  const data = await response.json();
  return data.jobs;
}

export async function createJob(
  config: Partial<TrainingConfig> = {},
  datasetId?: string
): Promise<TrainingJob> {
  const response = await fetch(`${API_URL}/api/training/jobs`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ config, dataset_id: datasetId }),
  });
  if (!response.ok) throw new Error("Failed to create job");
  return response.json();
}

export async function getJob(jobId: string): Promise<TrainingJob> {
  const response = await fetch(`${API_URL}/api/training/jobs/${jobId}`);
  if (!response.ok) throw new Error("Failed to fetch job");
  return response.json();
}

export async function startJob(jobId: string): Promise<void> {
  const response = await fetch(`${API_URL}/api/training/jobs/${jobId}/start`, {
    method: "POST",
  });
  if (!response.ok) throw new Error("Failed to start job");
}

export async function cancelJob(jobId: string): Promise<void> {
  const response = await fetch(`${API_URL}/api/training/jobs/${jobId}/cancel`, {
    method: "POST",
  });
  if (!response.ok) throw new Error("Failed to cancel job");
}

export async function deleteJob(jobId: string): Promise<void> {
  const response = await fetch(`${API_URL}/api/training/jobs/${jobId}`, {
    method: "DELETE",
  });
  if (!response.ok) throw new Error("Failed to delete job");
}

// ============== Model APIs ==============

export async function listTrainedModels(): Promise<TrainedModel[]> {
  const response = await fetch(`${API_URL}/api/training/models`);
  if (!response.ok) throw new Error("Failed to fetch models");
  const data = await response.json();
  return data.models;
}

export async function listBaseModels(): Promise<BaseModel[]> {
  const response = await fetch(`${API_URL}/api/training/base-models`);
  if (!response.ok) throw new Error("Failed to fetch base models");
  const data = await response.json();
  return data.models;
}

