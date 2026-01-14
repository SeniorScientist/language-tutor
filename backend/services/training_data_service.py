"""Training data management service."""

import json
import logging
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class TrainingExample(BaseModel):
    """A single training example."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())

    # Input/output pair
    system_prompt: str = ""
    user_input: str
    assistant_output: str

    # Metadata
    category: str = "general"  # chat, correction, exercise, grammar
    language: str = "English"
    quality_rating: Optional[int] = None  # 1-5 rating
    is_approved: bool = False  # Human-approved for training


class TrainingDataset(BaseModel):
    """A collection of training examples."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str = ""
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    examples: list[TrainingExample] = Field(default_factory=list)

    @property
    def example_count(self) -> int:
        return len(self.examples)

    @property
    def approved_count(self) -> int:
        return sum(1 for e in self.examples if e.is_approved)


class TrainingDataService:
    """Service for managing training data.

    Stores training examples that can be used for fine-tuning.
    """

    def __init__(self, data_dir: str = "./training_data"):
        """Initialize training data service.

        Args:
            data_dir: Directory to store training data.
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.datasets_file = self.data_dir / "datasets.json"
        self._datasets: dict[str, TrainingDataset] = {}
        self._load_datasets()
        logger.info(f"Training data service initialized at {self.data_dir}")

    def _load_datasets(self):
        """Load datasets from disk."""
        if self.datasets_file.exists():
            try:
                with open(self.datasets_file, "r") as f:
                    data = json.load(f)
                    for ds_data in data.get("datasets", []):
                        ds = TrainingDataset(**ds_data)
                        self._datasets[ds.id] = ds
                logger.info(f"Loaded {len(self._datasets)} datasets")
            except Exception as e:
                logger.error(f"Failed to load datasets: {e}")
                self._datasets = {}

        # Create default dataset if none exist
        if not self._datasets:
            default_ds = TrainingDataset(
                name="Default Training Data",
                description="Auto-collected training examples from user interactions",
            )
            self._datasets[default_ds.id] = default_ds
            self._save_datasets()

    def _save_datasets(self):
        """Save datasets to disk."""
        try:
            data = {"datasets": [ds.model_dump() for ds in self._datasets.values()]}
            with open(self.datasets_file, "w") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save datasets: {e}")

    def list_datasets(self) -> list[dict]:
        """List all datasets with summary info."""
        return [
            {
                "id": ds.id,
                "name": ds.name,
                "description": ds.description,
                "example_count": ds.example_count,
                "approved_count": ds.approved_count,
                "created_at": ds.created_at,
                "updated_at": ds.updated_at,
            }
            for ds in self._datasets.values()
        ]

    def get_dataset(self, dataset_id: str) -> Optional[TrainingDataset]:
        """Get a dataset by ID."""
        return self._datasets.get(dataset_id)

    def create_dataset(self, name: str, description: str = "") -> TrainingDataset:
        """Create a new dataset."""
        ds = TrainingDataset(name=name, description=description)
        self._datasets[ds.id] = ds
        self._save_datasets()
        logger.info(f"Created dataset: {ds.id}")
        return ds

    def delete_dataset(self, dataset_id: str) -> bool:
        """Delete a dataset."""
        if dataset_id in self._datasets:
            del self._datasets[dataset_id]
            self._save_datasets()
            logger.info(f"Deleted dataset: {dataset_id}")
            return True
        return False

    def add_example(
        self,
        dataset_id: str,
        user_input: str,
        assistant_output: str,
        system_prompt: str = "",
        category: str = "general",
        language: str = "English",
        is_approved: bool = False,
    ) -> Optional[TrainingExample]:
        """Add a training example to a dataset."""
        ds = self._datasets.get(dataset_id)
        if not ds:
            # Use first available dataset
            ds = next(iter(self._datasets.values()), None)
            if not ds:
                return None

        example = TrainingExample(
            system_prompt=system_prompt,
            user_input=user_input,
            assistant_output=assistant_output,
            category=category,
            language=language,
            is_approved=is_approved,
        )

        ds.examples.append(example)
        ds.updated_at = datetime.now().isoformat()
        self._save_datasets()

        logger.info(f"Added example to dataset {dataset_id}: {example.id}")
        return example

    def update_example(
        self, dataset_id: str, example_id: str, **updates
    ) -> Optional[TrainingExample]:
        """Update a training example."""
        ds = self._datasets.get(dataset_id)
        if not ds:
            return None

        for i, ex in enumerate(ds.examples):
            if ex.id == example_id:
                # Update fields
                for key, value in updates.items():
                    if hasattr(ex, key):
                        setattr(ex, key, value)
                ds.updated_at = datetime.now().isoformat()
                self._save_datasets()
                return ex

        return None

    def delete_example(self, dataset_id: str, example_id: str) -> bool:
        """Delete a training example."""
        ds = self._datasets.get(dataset_id)
        if not ds:
            return False

        for i, ex in enumerate(ds.examples):
            if ex.id == example_id:
                ds.examples.pop(i)
                ds.updated_at = datetime.now().isoformat()
                self._save_datasets()
                logger.info(f"Deleted example: {example_id}")
                return True

        return False

    def approve_example(
        self, dataset_id: str, example_id: str, approved: bool = True
    ) -> bool:
        """Approve or unapprove a training example."""
        result = self.update_example(dataset_id, example_id, is_approved=approved)
        return result is not None

    def rate_example(self, dataset_id: str, example_id: str, rating: int) -> bool:
        """Rate a training example (1-5)."""
        rating = max(1, min(5, rating))
        result = self.update_example(dataset_id, example_id, quality_rating=rating)
        return result is not None

    def get_approved_examples(
        self, dataset_id: Optional[str] = None
    ) -> list[TrainingExample]:
        """Get all approved examples, optionally from a specific dataset."""
        examples = []

        datasets = (
            [self._datasets[dataset_id]] if dataset_id else self._datasets.values()
        )

        for ds in datasets:
            examples.extend([e for e in ds.examples if e.is_approved])

        return examples

    def export_for_training(
        self,
        dataset_id: Optional[str] = None,
        format: str = "jsonl",
        only_approved: bool = True,
    ) -> str:
        """Export training data in a format suitable for fine-tuning.

        Args:
            dataset_id: Optional specific dataset to export.
            format: Export format ('jsonl', 'alpaca', 'sharegpt').
            only_approved: Only include approved examples.

        Returns:
            Path to exported file.
        """
        if only_approved:
            examples = self.get_approved_examples(dataset_id)
        else:
            examples = []
            datasets = (
                [self._datasets[dataset_id]] if dataset_id else self._datasets.values()
            )
            for ds in datasets:
                examples.extend(ds.examples)

        if not examples:
            raise ValueError("No examples to export")

        export_dir = self.data_dir / "exports"
        export_dir.mkdir(exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        if format == "jsonl":
            # OpenAI/Standard JSONL format
            export_file = export_dir / f"training_{timestamp}.jsonl"
            with open(export_file, "w") as f:
                for ex in examples:
                    messages = []
                    if ex.system_prompt:
                        messages.append({"role": "system", "content": ex.system_prompt})
                    messages.append({"role": "user", "content": ex.user_input})
                    messages.append(
                        {"role": "assistant", "content": ex.assistant_output}
                    )
                    f.write(json.dumps({"messages": messages}) + "\n")

        elif format == "alpaca":
            # Alpaca format for many fine-tuning tools
            export_file = export_dir / f"training_{timestamp}_alpaca.json"
            data = []
            for ex in examples:
                data.append(
                    {
                        "instruction": ex.system_prompt
                        or "You are a helpful language tutor.",
                        "input": ex.user_input,
                        "output": ex.assistant_output,
                    }
                )
            with open(export_file, "w") as f:
                json.dump(data, f, indent=2)

        elif format == "sharegpt":
            # ShareGPT format
            export_file = export_dir / f"training_{timestamp}_sharegpt.json"
            data = []
            for ex in examples:
                conversations = []
                if ex.system_prompt:
                    conversations.append({"from": "system", "value": ex.system_prompt})
                conversations.append({"from": "human", "value": ex.user_input})
                conversations.append({"from": "gpt", "value": ex.assistant_output})
                data.append({"conversations": conversations})
            with open(export_file, "w") as f:
                json.dump(data, f, indent=2)

        else:
            raise ValueError(f"Unknown format: {format}")

        logger.info(f"Exported {len(examples)} examples to {export_file}")
        return str(export_file)

    def auto_collect_from_chat(
        self,
        user_message: str,
        assistant_response: str,
        system_prompt: str = "",
        language: str = "English",
        category: str = "chat",
    ):
        """Auto-collect a chat interaction as potential training data.

        These are stored but not approved - user can review and approve later.
        """
        # Get default dataset
        default_ds = next(iter(self._datasets.values()), None)
        if not default_ds:
            return

        self.add_example(
            dataset_id=default_ds.id,
            user_input=user_message,
            assistant_output=assistant_response,
            system_prompt=system_prompt,
            category=category,
            language=language,
            is_approved=False,  # Needs human review
        )


# Singleton instance
_training_data_service: Optional[TrainingDataService] = None


def get_training_data_service() -> TrainingDataService:
    """Get the training data service singleton."""
    global _training_data_service
    if _training_data_service is None:
        _training_data_service = TrainingDataService()
    return _training_data_service
