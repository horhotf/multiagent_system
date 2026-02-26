from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.core.orchestrator import orchestrator
from app.db import pg
from app.models import ArtifactResponse, GenericResponse, ObjectGenerateRequest, QueryRequest, TextValidateRequest

router = APIRouter(prefix="/v1", tags=["v1"])


@router.post("/query", response_model=GenericResponse)
def query(request: QueryRequest) -> GenericResponse:
    try:
        payload = orchestrator.run_query(request.mode, request.query, request.context)
        return GenericResponse(**payload)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.post("/object/generate", response_model=GenericResponse)
def object_generate(request: ObjectGenerateRequest) -> GenericResponse:
    try:
        context = dict(request.variables)
        if request.object_type:
            context["object_type"] = request.object_type
        payload = orchestrator.run_query("json_object", request.query, context)
        return GenericResponse(**payload)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.post("/text/validate", response_model=GenericResponse)
def text_validate(request: TextValidateRequest) -> GenericResponse:
    try:
        payload = orchestrator.run_query("validate_text", request.text, {"policy": request.policy} if request.policy else {})
        return GenericResponse(**payload)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("/artifacts/{artifact_id}", response_model=ArtifactResponse)
def artifact_get(artifact_id: int) -> ArtifactResponse:
    row = pg.fetch_one("SELECT id, task_id, artifact_type, path, metadata FROM artifacts WHERE id = %s", (artifact_id,))
    if not row:
        raise HTTPException(status_code=404, detail="Artifact not found")
    return ArtifactResponse(**row)
