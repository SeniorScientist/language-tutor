"""Training API endpoints."""

import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field

from services.training_data_service import (
    TrainingDataService,
    get_training_data_service,
    TrainingExample,
)
from services.training_service import (
    TrainingService,
    get_training_service,
    TrainingConfig,
    TrainingStatus,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/training", tags=["training"])


# ============== Training Data Endpoints ==============


class CreateDatasetRequest(BaseModel):
    name: str
    description: str = ""


class AddExampleRequest(BaseModel):
    user_input: str
    assistant_output: str
    system_prompt: str = ""
    category: str = "general"
    language: str = "English"
    is_approved: bool = False


class UpdateExampleRequest(BaseModel):
    user_input: Optional[str] = None
    assistant_output: Optional[str] = None
    system_prompt: Optional[str] = None
    category: Optional[str] = None
    is_approved: Optional[bool] = None
    quality_rating: Optional[int] = None


@router.get("/datasets")
async def list_datasets(
    service: TrainingDataService = Depends(get_training_data_service),
):
    """List all training datasets."""
    return {"datasets": service.list_datasets()}


@router.post("/datasets")
async def create_dataset(
    request: CreateDatasetRequest,
    service: TrainingDataService = Depends(get_training_data_service),
):
    """Create a new training dataset."""
    dataset = service.create_dataset(request.name, request.description)
    return {
        "id": dataset.id,
        "name": dataset.name,
        "description": dataset.description,
    }


@router.get("/datasets/{dataset_id}")
async def get_dataset(
    dataset_id: str,
    service: TrainingDataService = Depends(get_training_data_service),
):
    """Get a dataset with all examples."""
    dataset = service.get_dataset(dataset_id)
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")

    return {
        "id": dataset.id,
        "name": dataset.name,
        "description": dataset.description,
        "example_count": dataset.example_count,
        "approved_count": dataset.approved_count,
        "examples": [e.model_dump() for e in dataset.examples],
    }


@router.delete("/datasets/{dataset_id}")
async def delete_dataset(
    dataset_id: str,
    service: TrainingDataService = Depends(get_training_data_service),
):
    """Delete a dataset."""
    if service.delete_dataset(dataset_id):
        return {"success": True}
    raise HTTPException(status_code=404, detail="Dataset not found")


@router.post("/datasets/{dataset_id}/examples")
async def add_example(
    dataset_id: str,
    request: AddExampleRequest,
    service: TrainingDataService = Depends(get_training_data_service),
):
    """Add a training example to a dataset."""
    example = service.add_example(
        dataset_id=dataset_id,
        user_input=request.user_input,
        assistant_output=request.assistant_output,
        system_prompt=request.system_prompt,
        category=request.category,
        language=request.language,
        is_approved=request.is_approved,
    )

    if not example:
        raise HTTPException(status_code=404, detail="Dataset not found")

    return example.model_dump()


@router.put("/datasets/{dataset_id}/examples/{example_id}")
async def update_example(
    dataset_id: str,
    example_id: str,
    request: UpdateExampleRequest,
    service: TrainingDataService = Depends(get_training_data_service),
):
    """Update a training example."""
    updates = {k: v for k, v in request.model_dump().items() if v is not None}
    example = service.update_example(dataset_id, example_id, **updates)

    if not example:
        raise HTTPException(status_code=404, detail="Example not found")

    return example.model_dump()


@router.delete("/datasets/{dataset_id}/examples/{example_id}")
async def delete_example(
    dataset_id: str,
    example_id: str,
    service: TrainingDataService = Depends(get_training_data_service),
):
    """Delete a training example."""
    if service.delete_example(dataset_id, example_id):
        return {"success": True}
    raise HTTPException(status_code=404, detail="Example not found")


@router.post("/datasets/{dataset_id}/examples/{example_id}/approve")
async def approve_example(
    dataset_id: str,
    example_id: str,
    approved: bool = True,
    service: TrainingDataService = Depends(get_training_data_service),
):
    """Approve or unapprove a training example."""
    if service.approve_example(dataset_id, example_id, approved):
        return {"success": True, "approved": approved}
    raise HTTPException(status_code=404, detail="Example not found")


@router.post("/datasets/{dataset_id}/examples/{example_id}/rate")
async def rate_example(
    dataset_id: str,
    example_id: str,
    rating: int = Query(..., ge=1, le=5),
    service: TrainingDataService = Depends(get_training_data_service),
):
    """Rate a training example (1-5 stars)."""
    if service.rate_example(dataset_id, example_id, rating):
        return {"success": True, "rating": rating}
    raise HTTPException(status_code=404, detail="Example not found")


@router.post("/datasets/export")
async def export_dataset(
    dataset_id: Optional[str] = None,
    format: str = Query(default="jsonl", regex="^(jsonl|alpaca|sharegpt)$"),
    only_approved: bool = True,
    service: TrainingDataService = Depends(get_training_data_service),
):
    """Export training data for fine-tuning."""
    try:
        file_path = service.export_for_training(
            dataset_id=dataset_id,
            format=format,
            only_approved=only_approved,
        )
        return {"success": True, "file_path": file_path}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ============== Training Job Endpoints ==============


class CreateJobRequest(BaseModel):
    config: TrainingConfig = Field(default_factory=TrainingConfig)
    dataset_id: Optional[str] = None


@router.get("/jobs")
async def list_jobs(
    service: TrainingService = Depends(get_training_service),
):
    """List all training jobs."""
    return {"jobs": service.list_jobs()}


@router.post("/jobs")
async def create_job(
    request: CreateJobRequest,
    service: TrainingService = Depends(get_training_service),
):
    """Create a new training job."""
    job = service.create_job(
        config=request.config,
        dataset_id=request.dataset_id,
    )
    return {
        "id": job.id,
        "status": job.status,
        "config": job.config.model_dump(),
    }


@router.get("/jobs/{job_id}")
async def get_job(
    job_id: str,
    service: TrainingService = Depends(get_training_service),
):
    """Get a training job."""
    job = service.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    return {
        "id": job.id,
        "status": job.status,
        "progress": job.progress,
        "current_step": job.current_step,
        "total_steps": job.total_steps,
        "created_at": job.created_at,
        "started_at": job.started_at,
        "completed_at": job.completed_at,
        "config": job.config.model_dump(),
        "output_path": job.output_path,
        "error_message": job.error_message,
        "metrics": job.metrics,
    }


@router.post("/jobs/{job_id}/start")
async def start_job(
    job_id: str,
    service: TrainingService = Depends(get_training_service),
):
    """Start a training job."""
    if service.start_job(job_id):
        return {"success": True, "message": "Job started"}
    raise HTTPException(status_code=400, detail="Cannot start job")


@router.post("/jobs/{job_id}/cancel")
async def cancel_job(
    job_id: str,
    service: TrainingService = Depends(get_training_service),
):
    """Cancel a running training job."""
    if service.cancel_job(job_id):
        return {"success": True, "message": "Job cancelled"}
    raise HTTPException(status_code=400, detail="Cannot cancel job")


@router.delete("/jobs/{job_id}")
async def delete_job(
    job_id: str,
    service: TrainingService = Depends(get_training_service),
):
    """Delete a training job."""
    if service.delete_job(job_id):
        return {"success": True}
    raise HTTPException(status_code=400, detail="Cannot delete job")


# ============== Model Management Endpoints ==============


@router.get("/models")
async def list_models(
    service: TrainingService = Depends(get_training_service),
):
    """List all trained models."""
    return {"models": service.list_trained_models()}


@router.get("/base-models")
async def list_base_models(
    service: TrainingService = Depends(get_training_service),
):
    """List recommended base models for fine-tuning."""
    return {"models": service.get_available_base_models()}
