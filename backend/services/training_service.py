"""Fine-tuning service for local models."""

import asyncio
import json
import logging
import os
import subprocess
import threading
import uuid
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Optional

from pydantic import BaseModel, Field

from services.training_data_service import get_training_data_service

logger = logging.getLogger(__name__)


class TrainingStatus(str, Enum):
    """Training job status."""

    PENDING = "pending"
    PREPARING = "preparing"
    TRAINING = "training"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TrainingConfig(BaseModel):
    """Configuration for a training job."""

    # Base model
    base_model: str = "unsloth/Llama-3.2-1B-Instruct"  # HuggingFace model ID

    # LoRA parameters
    lora_r: int = 16  # LoRA rank
    lora_alpha: int = 32  # LoRA alpha
    lora_dropout: float = 0.05

    # Training parameters
    epochs: int = 3
    batch_size: int = 2
    gradient_accumulation_steps: int = 4
    learning_rate: float = 2e-4
    warmup_steps: int = 10
    max_seq_length: int = 2048

    # Output
    output_name: str = "language-tutor-lora"


class TrainingJob(BaseModel):
    """A training job."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    started_at: Optional[str] = None
    completed_at: Optional[str] = None

    status: TrainingStatus = TrainingStatus.PENDING
    progress: float = 0.0  # 0-100
    current_step: int = 0
    total_steps: int = 0

    config: TrainingConfig
    dataset_id: Optional[str] = None

    # Results
    output_path: Optional[str] = None
    error_message: Optional[str] = None
    metrics: dict = Field(default_factory=dict)


class TrainingService:
    """Service for fine-tuning local models.

    Uses LoRA (Low-Rank Adaptation) for efficient fine-tuning.
    Supports unsloth for fast training on consumer hardware.
    """

    def __init__(self, models_dir: str = "./models", jobs_dir: str = "./training_jobs"):
        """Initialize training service.

        Args:
            models_dir: Directory to store trained models.
            jobs_dir: Directory to store job data.
        """
        self.models_dir = Path(models_dir)
        self.models_dir.mkdir(parents=True, exist_ok=True)

        self.jobs_dir = Path(jobs_dir)
        self.jobs_dir.mkdir(parents=True, exist_ok=True)

        self.jobs_file = self.jobs_dir / "jobs.json"
        self._jobs: dict[str, TrainingJob] = {}
        self._active_job: Optional[str] = None
        self._training_thread: Optional[threading.Thread] = None

        self._load_jobs()
        logger.info("Training service initialized")

    def _load_jobs(self):
        """Load jobs from disk."""
        if self.jobs_file.exists():
            try:
                with open(self.jobs_file, "r") as f:
                    data = json.load(f)
                    for job_data in data.get("jobs", []):
                        job = TrainingJob(**job_data)
                        self._jobs[job.id] = job
                logger.info(f"Loaded {len(self._jobs)} training jobs")
            except Exception as e:
                logger.error(f"Failed to load jobs: {e}")

    def _save_jobs(self):
        """Save jobs to disk."""
        try:
            data = {"jobs": [job.model_dump() for job in self._jobs.values()]}
            with open(self.jobs_file, "w") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save jobs: {e}")

    def list_jobs(self) -> list[dict]:
        """List all training jobs."""
        return [
            {
                "id": job.id,
                "status": job.status,
                "progress": job.progress,
                "created_at": job.created_at,
                "started_at": job.started_at,
                "completed_at": job.completed_at,
                "config": job.config.model_dump(),
                "error_message": job.error_message,
            }
            for job in sorted(
                self._jobs.values(), key=lambda j: j.created_at, reverse=True
            )
        ]

    def get_job(self, job_id: str) -> Optional[TrainingJob]:
        """Get a job by ID."""
        return self._jobs.get(job_id)

    def create_job(
        self,
        config: TrainingConfig,
        dataset_id: Optional[str] = None,
    ) -> TrainingJob:
        """Create a new training job."""
        job = TrainingJob(config=config, dataset_id=dataset_id)
        self._jobs[job.id] = job
        self._save_jobs()
        logger.info(f"Created training job: {job.id}")
        return job

    def start_job(self, job_id: str) -> bool:
        """Start a training job."""
        job = self._jobs.get(job_id)
        if not job:
            return False

        if self._active_job:
            logger.warning("Another job is already running")
            return False

        if job.status not in [TrainingStatus.PENDING, TrainingStatus.FAILED]:
            logger.warning(f"Job {job_id} cannot be started (status: {job.status})")
            return False

        # Start training in background thread
        self._active_job = job_id
        self._training_thread = threading.Thread(
            target=self._run_training, args=(job_id,), daemon=True
        )
        self._training_thread.start()

        return True

    def cancel_job(self, job_id: str) -> bool:
        """Cancel a running training job."""
        job = self._jobs.get(job_id)
        if not job:
            return False

        if job.status == TrainingStatus.TRAINING:
            job.status = TrainingStatus.CANCELLED
            self._active_job = None
            self._save_jobs()
            logger.info(f"Cancelled job: {job_id}")
            return True

        return False

    def delete_job(self, job_id: str) -> bool:
        """Delete a training job."""
        if job_id == self._active_job:
            return False

        if job_id in self._jobs:
            del self._jobs[job_id]
            self._save_jobs()
            return True

        return False

    def _run_training(self, job_id: str):
        """Run the actual training process."""
        job = self._jobs.get(job_id)
        if not job:
            return

        try:
            job.status = TrainingStatus.PREPARING
            job.started_at = datetime.now().isoformat()
            self._save_jobs()

            # Export training data
            training_data_service = get_training_data_service()
            try:
                data_file = training_data_service.export_for_training(
                    dataset_id=job.dataset_id,
                    format="jsonl",
                    only_approved=True,
                )
            except ValueError as e:
                raise ValueError(f"No approved training data available: {e}")

            # Check if unsloth is available
            try:
                import unsloth

                self._train_with_unsloth(job, data_file)
            except ImportError:
                # Fall back to transformers + peft
                logger.warning("unsloth not available, using transformers + peft")
                self._train_with_peft(job, data_file)

            job.status = TrainingStatus.COMPLETED
            job.progress = 100.0
            job.completed_at = datetime.now().isoformat()
            logger.info(f"Training completed: {job_id}")

        except Exception as e:
            logger.error(f"Training failed: {e}")
            job.status = TrainingStatus.FAILED
            job.error_message = str(e)
            job.completed_at = datetime.now().isoformat()

        finally:
            self._active_job = None
            self._save_jobs()

    def _train_with_unsloth(self, job: TrainingJob, data_file: str):
        """Train using unsloth (fastest method)."""
        from unsloth import FastLanguageModel
        from trl import SFTTrainer
        from transformers import TrainingArguments
        from datasets import load_dataset

        job.status = TrainingStatus.TRAINING
        self._save_jobs()

        config = job.config

        # Load model with unsloth
        model, tokenizer = FastLanguageModel.from_pretrained(
            model_name=config.base_model,
            max_seq_length=config.max_seq_length,
            load_in_4bit=True,
        )

        # Add LoRA adapters
        model = FastLanguageModel.get_peft_model(
            model,
            r=config.lora_r,
            lora_alpha=config.lora_alpha,
            lora_dropout=config.lora_dropout,
            target_modules=[
                "q_proj",
                "k_proj",
                "v_proj",
                "o_proj",
                "gate_proj",
                "up_proj",
                "down_proj",
            ],
        )

        # Load dataset
        dataset = load_dataset("json", data_files=data_file, split="train")

        # Format function
        def format_prompts(examples):
            texts = []
            for messages in examples["messages"]:
                text = tokenizer.apply_chat_template(messages, tokenize=False)
                texts.append(text)
            return {"text": texts}

        dataset = dataset.map(format_prompts, batched=True)

        # Calculate steps
        total_steps = (
            len(dataset) // config.batch_size // config.gradient_accumulation_steps
        ) * config.epochs
        job.total_steps = total_steps

        # Output directory
        output_dir = self.models_dir / config.output_name

        # Training arguments
        training_args = TrainingArguments(
            output_dir=str(output_dir),
            num_train_epochs=config.epochs,
            per_device_train_batch_size=config.batch_size,
            gradient_accumulation_steps=config.gradient_accumulation_steps,
            learning_rate=config.learning_rate,
            warmup_steps=config.warmup_steps,
            logging_steps=1,
            save_strategy="epoch",
            fp16=True,
        )

        # Trainer with progress callback
        class ProgressCallback:
            def __init__(self, job, save_fn):
                self.job = job
                self.save_fn = save_fn

            def on_log(self, args, state, control, logs=None, **kwargs):
                if state.global_step > 0:
                    self.job.current_step = state.global_step
                    self.job.progress = (state.global_step / self.job.total_steps) * 100
                    if logs:
                        self.job.metrics.update(logs)
                    self.save_fn()

        trainer = SFTTrainer(
            model=model,
            tokenizer=tokenizer,
            train_dataset=dataset,
            dataset_text_field="text",
            max_seq_length=config.max_seq_length,
            args=training_args,
        )

        # Add callback
        trainer.add_callback(ProgressCallback(job, self._save_jobs))

        # Train
        trainer.train()

        # Save LoRA adapter
        model.save_pretrained(str(output_dir))
        tokenizer.save_pretrained(str(output_dir))

        # Also save as GGUF for llama.cpp
        try:
            model.save_pretrained_gguf(
                str(output_dir / "gguf"), tokenizer, quantization_method="q4_k_m"
            )
            job.output_path = str(output_dir / "gguf")
        except Exception as e:
            logger.warning(f"Could not export to GGUF: {e}")
            job.output_path = str(output_dir)

    def _train_with_peft(self, job: TrainingJob, data_file: str):
        """Train using transformers + peft (fallback method)."""
        from transformers import (
            AutoModelForCausalLM,
            AutoTokenizer,
            TrainingArguments,
            Trainer,
            DataCollatorForSeq2Seq,
        )
        from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
        from datasets import load_dataset
        import torch

        job.status = TrainingStatus.TRAINING
        self._save_jobs()

        config = job.config

        # Load model
        model = AutoModelForCausalLM.from_pretrained(
            config.base_model,
            torch_dtype=torch.float16,
            device_map="auto",
            load_in_4bit=True,
        )

        tokenizer = AutoTokenizer.from_pretrained(config.base_model)
        tokenizer.pad_token = tokenizer.eos_token

        # Prepare for training
        model = prepare_model_for_kbit_training(model)

        # LoRA config
        lora_config = LoraConfig(
            r=config.lora_r,
            lora_alpha=config.lora_alpha,
            lora_dropout=config.lora_dropout,
            target_modules=["q_proj", "k_proj", "v_proj", "o_proj"],
            bias="none",
            task_type="CAUSAL_LM",
        )

        model = get_peft_model(model, lora_config)

        # Load and process dataset
        dataset = load_dataset("json", data_files=data_file, split="train")

        def tokenize_function(examples):
            texts = []
            for messages in examples["messages"]:
                text = tokenizer.apply_chat_template(messages, tokenize=False)
                texts.append(text)

            return tokenizer(
                texts,
                truncation=True,
                max_length=config.max_seq_length,
                padding="max_length",
            )

        tokenized_dataset = dataset.map(tokenize_function, batched=True)

        # Output directory
        output_dir = self.models_dir / config.output_name

        # Training arguments
        training_args = TrainingArguments(
            output_dir=str(output_dir),
            num_train_epochs=config.epochs,
            per_device_train_batch_size=config.batch_size,
            gradient_accumulation_steps=config.gradient_accumulation_steps,
            learning_rate=config.learning_rate,
            warmup_steps=config.warmup_steps,
            logging_steps=1,
            save_strategy="epoch",
            fp16=True,
        )

        # Trainer
        trainer = Trainer(
            model=model,
            args=training_args,
            train_dataset=tokenized_dataset,
            data_collator=DataCollatorForSeq2Seq(tokenizer, padding=True),
        )

        # Train
        trainer.train()

        # Save
        model.save_pretrained(str(output_dir))
        tokenizer.save_pretrained(str(output_dir))
        job.output_path = str(output_dir)

    def list_trained_models(self) -> list[dict]:
        """List all trained models."""
        models = []

        for path in self.models_dir.iterdir():
            if path.is_dir() and (path / "adapter_config.json").exists():
                # LoRA adapter
                models.append(
                    {
                        "name": path.name,
                        "path": str(path),
                        "type": "lora",
                        "created_at": datetime.fromtimestamp(
                            path.stat().st_mtime
                        ).isoformat(),
                    }
                )
            elif path.suffix == ".gguf":
                # GGUF model
                models.append(
                    {
                        "name": path.name,
                        "path": str(path),
                        "type": "gguf",
                        "size_mb": path.stat().st_size / (1024 * 1024),
                        "created_at": datetime.fromtimestamp(
                            path.stat().st_mtime
                        ).isoformat(),
                    }
                )

        return models

    def get_available_base_models(self) -> list[dict]:
        """Get list of recommended base models for fine-tuning."""
        return [
            {
                "id": "unsloth/Llama-3.2-1B-Instruct",
                "name": "Llama 3.2 1B Instruct",
                "description": "Small, fast model for quick training. Good for testing.",
                "size": "1B",
                "vram_required": "6GB",
            },
            {
                "id": "unsloth/Llama-3.2-3B-Instruct",
                "name": "Llama 3.2 3B Instruct",
                "description": "Medium model with good performance/speed balance.",
                "size": "3B",
                "vram_required": "8GB",
            },
            {
                "id": "unsloth/Meta-Llama-3.1-8B-Instruct",
                "name": "Llama 3.1 8B Instruct",
                "description": "Larger model with better language understanding.",
                "size": "8B",
                "vram_required": "16GB",
            },
            {
                "id": "unsloth/Qwen2.5-7B-Instruct",
                "name": "Qwen 2.5 7B Instruct",
                "description": "Excellent multilingual support.",
                "size": "7B",
                "vram_required": "16GB",
            },
            {
                "id": "unsloth/Mistral-7B-Instruct-v0.3",
                "name": "Mistral 7B Instruct v0.3",
                "description": "Strong reasoning and instruction following.",
                "size": "7B",
                "vram_required": "16GB",
            },
        ]


# Singleton instance
_training_service: Optional[TrainingService] = None


def get_training_service() -> TrainingService:
    """Get the training service singleton."""
    global _training_service
    if _training_service is None:
        _training_service = TrainingService()
    return _training_service
