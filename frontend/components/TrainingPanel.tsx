"use client";

import { useState, useEffect } from "react";
import {
  Database,
  Plus,
  Play,
  Pause,
  Trash2,
  Check,
  X,
  Star,
  Download,
  RefreshCw,
  Loader2,
  Brain,
  Cpu,
  Settings,
  FileText,
  CheckCircle,
  XCircle,
  Clock,
  AlertCircle,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Label } from "@/components/ui/label";
import { cn } from "@/lib/utils";
import {
  listDatasets,
  getDataset,
  createDataset,
  deleteDataset,
  addExample,
  updateExample,
  deleteExample,
  approveExample,
  rateExample,
  exportDataset,
  listJobs,
  createJob,
  getJob,
  startJob,
  cancelJob,
  deleteJob,
  listTrainedModels,
  listBaseModels,
  TrainingDataset,
  TrainingExample,
  TrainingJob,
  TrainingConfig,
  BaseModel,
  TrainedModel,
} from "@/lib/training-api";

// ============== Data Management Tab ==============

function DataManagementTab() {
  const [datasets, setDatasets] = useState<TrainingDataset[]>([]);
  const [selectedDataset, setSelectedDataset] = useState<string | null>(null);
  const [examples, setExamples] = useState<TrainingExample[]>([]);
  const [loading, setLoading] = useState(true);
  const [newDatasetName, setNewDatasetName] = useState("");
  const [showAddExample, setShowAddExample] = useState(false);
  const [newExample, setNewExample] = useState({
    user_input: "",
    assistant_output: "",
    system_prompt: "",
    category: "chat",
    language: "English",
  });

  useEffect(() => {
    loadDatasets();
  }, []);

  useEffect(() => {
    if (selectedDataset) {
      loadExamples(selectedDataset);
    }
  }, [selectedDataset]);

  const loadDatasets = async () => {
    try {
      const data = await listDatasets();
      setDatasets(data);
      if (data.length > 0 && !selectedDataset) {
        setSelectedDataset(data[0].id);
      }
    } catch (err) {
      console.error("Failed to load datasets:", err);
    } finally {
      setLoading(false);
    }
  };

  const loadExamples = async (datasetId: string) => {
    try {
      const data = await getDataset(datasetId);
      setExamples(data.examples || []);
    } catch (err) {
      console.error("Failed to load examples:", err);
    }
  };

  const handleCreateDataset = async () => {
    if (!newDatasetName.trim()) return;
    try {
      const dataset = await createDataset(newDatasetName);
      setDatasets([...datasets, dataset]);
      setSelectedDataset(dataset.id);
      setNewDatasetName("");
    } catch (err) {
      console.error("Failed to create dataset:", err);
    }
  };

  const handleDeleteDataset = async (id: string) => {
    if (!confirm("Are you sure you want to delete this dataset?")) return;
    try {
      await deleteDataset(id);
      setDatasets(datasets.filter((d) => d.id !== id));
      if (selectedDataset === id) {
        setSelectedDataset(datasets[0]?.id || null);
      }
    } catch (err) {
      console.error("Failed to delete dataset:", err);
    }
  };

  const handleAddExample = async () => {
    if (!selectedDataset || !newExample.user_input || !newExample.assistant_output) return;
    try {
      const example = await addExample(selectedDataset, newExample);
      setExamples([...examples, example]);
      setNewExample({
        user_input: "",
        assistant_output: "",
        system_prompt: "",
        category: "chat",
        language: "English",
      });
      setShowAddExample(false);
      loadDatasets(); // Refresh counts
    } catch (err) {
      console.error("Failed to add example:", err);
    }
  };

  const handleApprove = async (exampleId: string, approved: boolean) => {
    if (!selectedDataset) return;
    try {
      await approveExample(selectedDataset, exampleId, approved);
      setExamples(
        examples.map((e) =>
          e.id === exampleId ? { ...e, is_approved: approved } : e
        )
      );
      loadDatasets(); // Refresh counts
    } catch (err) {
      console.error("Failed to approve example:", err);
    }
  };

  const handleRate = async (exampleId: string, rating: number) => {
    if (!selectedDataset) return;
    try {
      await rateExample(selectedDataset, exampleId, rating);
      setExamples(
        examples.map((e) =>
          e.id === exampleId ? { ...e, quality_rating: rating } : e
        )
      );
    } catch (err) {
      console.error("Failed to rate example:", err);
    }
  };

  const handleDeleteExample = async (exampleId: string) => {
    if (!selectedDataset) return;
    if (!confirm("Delete this example?")) return;
    try {
      await deleteExample(selectedDataset, exampleId);
      setExamples(examples.filter((e) => e.id !== exampleId));
      loadDatasets(); // Refresh counts
    } catch (err) {
      console.error("Failed to delete example:", err);
    }
  };

  const handleExport = async () => {
    if (!selectedDataset) return;
    try {
      const filePath = await exportDataset(selectedDataset, "jsonl", true);
      alert(`Exported to: ${filePath}`);
    } catch (err) {
      console.error("Failed to export:", err);
      alert("Export failed. Make sure you have approved examples.");
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Dataset selector */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle className="flex items-center gap-2">
              <Database className="h-5 w-5" />
              Training Datasets
            </CardTitle>
            <div className="flex items-center gap-2">
              <Input
                placeholder="New dataset name"
                value={newDatasetName}
                onChange={(e) => setNewDatasetName(e.target.value)}
                className="w-48"
              />
              <Button size="sm" onClick={handleCreateDataset}>
                <Plus className="h-4 w-4 mr-1" />
                Create
              </Button>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
            {datasets.map((ds) => (
              <div
                key={ds.id}
                className={cn(
                  "rounded-lg border p-4 cursor-pointer transition-all",
                  selectedDataset === ds.id
                    ? "border-primary bg-primary/5"
                    : "hover:border-muted-foreground/50"
                )}
                onClick={() => setSelectedDataset(ds.id)}
              >
                <div className="flex items-start justify-between">
                  <div>
                    <h4 className="font-medium">{ds.name}</h4>
                    <p className="text-sm text-muted-foreground mt-1">
                      {ds.example_count} examples ({ds.approved_count} approved)
                    </p>
                  </div>
                  <Button
                    variant="ghost"
                    size="icon"
                    className="h-8 w-8"
                    onClick={(e) => {
                      e.stopPropagation();
                      handleDeleteDataset(ds.id);
                    }}
                  >
                    <Trash2 className="h-4 w-4" />
                  </Button>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Examples */}
      {selectedDataset && (
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle>Training Examples</CardTitle>
              <div className="flex gap-2">
                <Button variant="outline" size="sm" onClick={handleExport}>
                  <Download className="h-4 w-4 mr-1" />
                  Export
                </Button>
                <Button size="sm" onClick={() => setShowAddExample(true)}>
                  <Plus className="h-4 w-4 mr-1" />
                  Add Example
                </Button>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            {/* Add example form */}
            {showAddExample && (
              <div className="mb-6 p-4 rounded-lg border bg-muted/30">
                <h4 className="font-medium mb-4">Add Training Example</h4>
                <div className="space-y-4">
                  <div>
                    <Label>System Prompt (optional)</Label>
                    <Input
                      value={newExample.system_prompt}
                      onChange={(e) =>
                        setNewExample({ ...newExample, system_prompt: e.target.value })
                      }
                      placeholder="System instructions..."
                    />
                  </div>
                  <div>
                    <Label>User Input *</Label>
                    <Textarea
                      value={newExample.user_input}
                      onChange={(e) =>
                        setNewExample({ ...newExample, user_input: e.target.value })
                      }
                      placeholder="What the user says/asks..."
                    />
                  </div>
                  <div>
                    <Label>Ideal Assistant Output *</Label>
                    <Textarea
                      value={newExample.assistant_output}
                      onChange={(e) =>
                        setNewExample({ ...newExample, assistant_output: e.target.value })
                      }
                      placeholder="How the assistant should respond..."
                    />
                  </div>
                  <div className="flex gap-4">
                    <div>
                      <Label>Category</Label>
                      <Select
                        value={newExample.category}
                        onValueChange={(v) =>
                          setNewExample({ ...newExample, category: v })
                        }
                      >
                        <SelectTrigger className="w-32">
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="chat">Chat</SelectItem>
                          <SelectItem value="correction">Correction</SelectItem>
                          <SelectItem value="exercise">Exercise</SelectItem>
                          <SelectItem value="grammar">Grammar</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                    <div>
                      <Label>Language</Label>
                      <Select
                        value={newExample.language}
                        onValueChange={(v) =>
                          setNewExample({ ...newExample, language: v })
                        }
                      >
                        <SelectTrigger className="w-32">
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="English">English</SelectItem>
                          <SelectItem value="Chinese">Chinese</SelectItem>
                          <SelectItem value="Russian">Russian</SelectItem>
                          <SelectItem value="Japanese">Japanese</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                  </div>
                  <div className="flex gap-2">
                    <Button onClick={handleAddExample}>Add Example</Button>
                    <Button variant="outline" onClick={() => setShowAddExample(false)}>
                      Cancel
                    </Button>
                  </div>
                </div>
              </div>
            )}

            {/* Examples list */}
            <div className="space-y-4">
              {examples.length === 0 ? (
                <p className="text-center text-muted-foreground py-8">
                  No training examples yet. Add some to start training!
                </p>
              ) : (
                examples.map((example) => (
                  <div
                    key={example.id}
                    className={cn(
                      "rounded-lg border p-4",
                      example.is_approved
                        ? "border-green-500/50 bg-green-50/50 dark:bg-green-900/10"
                        : ""
                    )}
                  >
                    <div className="flex items-start justify-between mb-3">
                      <div className="flex items-center gap-2">
                        <span
                          className={cn(
                            "px-2 py-0.5 rounded text-xs font-medium",
                            example.category === "chat"
                              ? "bg-blue-100 text-blue-700"
                              : example.category === "correction"
                              ? "bg-orange-100 text-orange-700"
                              : example.category === "exercise"
                              ? "bg-purple-100 text-purple-700"
                              : "bg-gray-100 text-gray-700"
                          )}
                        >
                          {example.category}
                        </span>
                        <span className="text-xs text-muted-foreground">
                          {example.language}
                        </span>
                        {example.is_approved && (
                          <CheckCircle className="h-4 w-4 text-green-500" />
                        )}
                      </div>
                      <div className="flex items-center gap-1">
                        {/* Star rating */}
                        {[1, 2, 3, 4, 5].map((star) => (
                          <button
                            key={star}
                            onClick={() => handleRate(example.id, star)}
                            className="p-0.5 hover:scale-110 transition-transform"
                          >
                            <Star
                              className={cn(
                                "h-4 w-4",
                                (example.quality_rating || 0) >= star
                                  ? "fill-yellow-400 text-yellow-400"
                                  : "text-gray-300"
                              )}
                            />
                          </button>
                        ))}
                      </div>
                    </div>

                    <div className="space-y-2 text-sm">
                      {example.system_prompt && (
                        <div className="text-muted-foreground italic">
                          System: {example.system_prompt}
                        </div>
                      )}
                      <div>
                        <span className="font-medium text-blue-600">User:</span>{" "}
                        {example.user_input}
                      </div>
                      <div>
                        <span className="font-medium text-green-600">Assistant:</span>{" "}
                        {example.assistant_output}
                      </div>
                    </div>

                    <div className="flex items-center justify-end gap-2 mt-3 pt-3 border-t">
                      <Button
                        variant={example.is_approved ? "outline" : "default"}
                        size="sm"
                        onClick={() => handleApprove(example.id, !example.is_approved)}
                      >
                        {example.is_approved ? (
                          <>
                            <X className="h-4 w-4 mr-1" />
                            Unapprove
                          </>
                        ) : (
                          <>
                            <Check className="h-4 w-4 mr-1" />
                            Approve
                          </>
                        )}
                      </Button>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => handleDeleteExample(example.id)}
                      >
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                ))
              )}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}

// ============== Training Jobs Tab ==============

function TrainingJobsTab() {
  const [jobs, setJobs] = useState<TrainingJob[]>([]);
  const [baseModels, setBaseModels] = useState<BaseModel[]>([]);
  const [trainedModels, setTrainedModels] = useState<TrainedModel[]>([]);
  const [datasets, setDatasets] = useState<TrainingDataset[]>([]);
  const [loading, setLoading] = useState(true);
  const [showNewJob, setShowNewJob] = useState(false);
  const [newJobConfig, setNewJobConfig] = useState<Partial<TrainingConfig>>({
    base_model: "unsloth/Llama-3.2-1B-Instruct",
    epochs: 3,
    batch_size: 2,
    learning_rate: 0.0002,
    output_name: "language-tutor-lora",
  });
  const [selectedDataset, setSelectedDataset] = useState<string>("");

  useEffect(() => {
    loadData();
    const interval = setInterval(loadJobs, 5000); // Poll for job updates
    return () => clearInterval(interval);
  }, []);

  const loadData = async () => {
    try {
      await Promise.all([loadJobs(), loadBaseModels(), loadTrainedModels(), loadDatasets()]);
    } finally {
      setLoading(false);
    }
  };

  const loadJobs = async () => {
    try {
      const data = await listJobs();
      setJobs(data);
    } catch (err) {
      console.error("Failed to load jobs:", err);
    }
  };

  const loadBaseModels = async () => {
    try {
      const data = await listBaseModels();
      setBaseModels(data);
    } catch (err) {
      console.error("Failed to load base models:", err);
    }
  };

  const loadTrainedModels = async () => {
    try {
      const data = await listTrainedModels();
      setTrainedModels(data);
    } catch (err) {
      console.error("Failed to load trained models:", err);
    }
  };

  const loadDatasets = async () => {
    try {
      const data = await listDatasets();
      setDatasets(data);
    } catch (err) {
      console.error("Failed to load datasets:", err);
    }
  };

  const handleCreateJob = async () => {
    try {
      const job = await createJob(newJobConfig, selectedDataset || undefined);
      setJobs([job, ...jobs]);
      setShowNewJob(false);
    } catch (err) {
      console.error("Failed to create job:", err);
    }
  };

  const handleStartJob = async (jobId: string) => {
    try {
      await startJob(jobId);
      loadJobs();
    } catch (err) {
      console.error("Failed to start job:", err);
      alert("Failed to start job. Make sure you have approved training data.");
    }
  };

  const handleCancelJob = async (jobId: string) => {
    try {
      await cancelJob(jobId);
      loadJobs();
    } catch (err) {
      console.error("Failed to cancel job:", err);
    }
  };

  const handleDeleteJob = async (jobId: string) => {
    if (!confirm("Delete this training job?")) return;
    try {
      await deleteJob(jobId);
      setJobs(jobs.filter((j) => j.id !== jobId));
    } catch (err) {
      console.error("Failed to delete job:", err);
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "completed":
        return <CheckCircle className="h-5 w-5 text-green-500" />;
      case "failed":
        return <XCircle className="h-5 w-5 text-red-500" />;
      case "training":
      case "preparing":
        return <Loader2 className="h-5 w-5 text-blue-500 animate-spin" />;
      case "cancelled":
        return <X className="h-5 w-5 text-orange-500" />;
      default:
        return <Clock className="h-5 w-5 text-gray-400" />;
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* New job form */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle className="flex items-center gap-2">
              <Brain className="h-5 w-5" />
              Fine-tune Model
            </CardTitle>
            {!showNewJob && (
              <Button onClick={() => setShowNewJob(true)}>
                <Plus className="h-4 w-4 mr-1" />
                New Training Job
              </Button>
            )}
          </div>
        </CardHeader>
        {showNewJob && (
          <CardContent>
            <div className="grid gap-4 sm:grid-cols-2">
              <div>
                <Label>Base Model</Label>
                <Select
                  value={newJobConfig.base_model}
                  onValueChange={(v) =>
                    setNewJobConfig({ ...newJobConfig, base_model: v })
                  }
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {baseModels.map((m) => (
                      <SelectItem key={m.id} value={m.id}>
                        {m.name} ({m.size}, {m.vram_required} VRAM)
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div>
                <Label>Training Dataset</Label>
                <Select value={selectedDataset} onValueChange={setSelectedDataset}>
                  <SelectTrigger>
                    <SelectValue placeholder="Select dataset" />
                  </SelectTrigger>
                  <SelectContent>
                    {datasets.map((ds) => (
                      <SelectItem key={ds.id} value={ds.id}>
                        {ds.name} ({ds.approved_count} approved)
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div>
                <Label>Epochs</Label>
                <Input
                  type="number"
                  value={newJobConfig.epochs}
                  onChange={(e) =>
                    setNewJobConfig({ ...newJobConfig, epochs: parseInt(e.target.value) })
                  }
                />
              </div>

              <div>
                <Label>Batch Size</Label>
                <Input
                  type="number"
                  value={newJobConfig.batch_size}
                  onChange={(e) =>
                    setNewJobConfig({
                      ...newJobConfig,
                      batch_size: parseInt(e.target.value),
                    })
                  }
                />
              </div>

              <div>
                <Label>Learning Rate</Label>
                <Input
                  type="number"
                  step="0.0001"
                  value={newJobConfig.learning_rate}
                  onChange={(e) =>
                    setNewJobConfig({
                      ...newJobConfig,
                      learning_rate: parseFloat(e.target.value),
                    })
                  }
                />
              </div>

              <div>
                <Label>Output Name</Label>
                <Input
                  value={newJobConfig.output_name}
                  onChange={(e) =>
                    setNewJobConfig({ ...newJobConfig, output_name: e.target.value })
                  }
                />
              </div>
            </div>

            <div className="flex gap-2 mt-4">
              <Button onClick={handleCreateJob}>Create Training Job</Button>
              <Button variant="outline" onClick={() => setShowNewJob(false)}>
                Cancel
              </Button>
            </div>
          </CardContent>
        )}
      </Card>

      {/* Jobs list */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle>Training Jobs</CardTitle>
            <Button variant="outline" size="sm" onClick={loadJobs}>
              <RefreshCw className="h-4 w-4 mr-1" />
              Refresh
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          {jobs.length === 0 ? (
            <p className="text-center text-muted-foreground py-8">
              No training jobs yet. Create one to start fine-tuning!
            </p>
          ) : (
            <div className="space-y-4">
              {jobs.map((job) => (
                <div key={job.id} className="rounded-lg border p-4">
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex items-center gap-3">
                      {getStatusIcon(job.status)}
                      <div>
                        <h4 className="font-medium">{job.config.output_name}</h4>
                        <p className="text-sm text-muted-foreground">
                          {job.config.base_model}
                        </p>
                      </div>
                    </div>
                    <span
                      className={cn(
                        "px-2 py-1 rounded text-xs font-medium",
                        job.status === "completed"
                          ? "bg-green-100 text-green-700"
                          : job.status === "failed"
                          ? "bg-red-100 text-red-700"
                          : job.status === "training"
                          ? "bg-blue-100 text-blue-700"
                          : "bg-gray-100 text-gray-700"
                      )}
                    >
                      {job.status}
                    </span>
                  </div>

                  {(job.status === "training" || job.status === "preparing") && (
                    <div className="mb-3">
                      <div className="flex items-center justify-between text-sm mb-1">
                        <span>Progress</span>
                        <span>{job.progress.toFixed(1)}%</span>
                      </div>
                      <Progress value={job.progress} />
                      {job.current_step > 0 && (
                        <p className="text-xs text-muted-foreground mt-1">
                          Step {job.current_step} / {job.total_steps}
                        </p>
                      )}
                    </div>
                  )}

                  {job.error_message && (
                    <div className="mb-3 p-2 rounded bg-red-50 text-red-700 text-sm flex items-start gap-2">
                      <AlertCircle className="h-4 w-4 mt-0.5" />
                      {job.error_message}
                    </div>
                  )}

                  {job.output_path && (
                    <div className="mb-3 p-2 rounded bg-green-50 text-green-700 text-sm">
                      Output: {job.output_path}
                    </div>
                  )}

                  <div className="flex items-center gap-2 text-xs text-muted-foreground">
                    <span>Created: {new Date(job.created_at).toLocaleString()}</span>
                    {job.started_at && (
                      <span>• Started: {new Date(job.started_at).toLocaleString()}</span>
                    )}
                  </div>

                  <div className="flex items-center justify-end gap-2 mt-3 pt-3 border-t">
                    {job.status === "pending" && (
                      <Button size="sm" onClick={() => handleStartJob(job.id)}>
                        <Play className="h-4 w-4 mr-1" />
                        Start Training
                      </Button>
                    )}
                    {(job.status === "training" || job.status === "preparing") && (
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => handleCancelJob(job.id)}
                      >
                        <Pause className="h-4 w-4 mr-1" />
                        Cancel
                      </Button>
                    )}
                    {(job.status === "completed" ||
                      job.status === "failed" ||
                      job.status === "cancelled" ||
                      job.status === "pending") && (
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => handleDeleteJob(job.id)}
                      >
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Trained models */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Cpu className="h-5 w-5" />
            Trained Models
          </CardTitle>
        </CardHeader>
        <CardContent>
          {trainedModels.length === 0 ? (
            <p className="text-center text-muted-foreground py-8">
              No trained models yet. Complete a training job to see your models here.
            </p>
          ) : (
            <div className="grid gap-3 sm:grid-cols-2">
              {trainedModels.map((model) => (
                <div key={model.path} className="rounded-lg border p-4">
                  <div className="flex items-center gap-2 mb-2">
                    <FileText className="h-5 w-5 text-primary" />
                    <h4 className="font-medium">{model.name}</h4>
                  </div>
                  <div className="text-sm text-muted-foreground">
                    <p>Type: {model.type.toUpperCase()}</p>
                    {model.size_mb && <p>Size: {model.size_mb.toFixed(1)} MB</p>}
                    <p>Created: {new Date(model.created_at).toLocaleDateString()}</p>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}

// ============== Main Component ==============

export function TrainingPanel() {
  return (
    <Tabs defaultValue="data" className="space-y-6">
      <TabsList className="grid w-full grid-cols-2">
        <TabsTrigger value="data" className="flex items-center gap-2">
          <Database className="h-4 w-4" />
          Training Data
        </TabsTrigger>
        <TabsTrigger value="training" className="flex items-center gap-2">
          <Brain className="h-4 w-4" />
          Fine-tuning
        </TabsTrigger>
      </TabsList>

      <TabsContent value="data">
        <DataManagementTab />
      </TabsContent>

      <TabsContent value="training">
        <TrainingJobsTab />
      </TabsContent>
    </Tabs>
  );
}

