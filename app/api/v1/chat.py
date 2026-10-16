"""Chat and Triage API Endpoints (v1).

Serves:
- POST /api/v1/chat: Master multi-turn conversation and 119 emergency escalation endpoint.
- POST /api/v1/chat/stream: Server-Sent Events (SSE) streaming endpoint.
- GET  /api/v1/chat/session/{session_id}: Session inspection.
- DELETE /api/v1/chat/session/{session_id}: Session reset.
"""

from __future__ import annotations

import asyncio
import json
from typing import AsyncGenerator, Optional

from fastapi import APIRouter, HTTPException, Query, status
from fastapi.responses import StreamingResponse

from app.orchestrator.supervisor import SupervisorOrchestrator
from app.schemas.chat import ChatRequest, SessionDetailResponse
from app.schemas.supervisor import SupervisorResponse

router = APIRouter()

# Singleton supervisor orchestrator instance for API serving
_supervisor = SupervisorOrchestrator()


def get_supervisor() -> SupervisorOrchestrator:
    """Returns singleton supervisor orchestrator."""
    return _supervisor


async def _sse_event_generator(
    req: ChatRequest, supervisor: SupervisorOrchestrator
) -> AsyncGenerator[str, None]:
    """Generates Server-Sent Events (SSE) stream for chat turns."""
    try:
        # Emit initial processing event
        yield f"event: status\ndata: {json.dumps({'status': 'PROCESSING', 'message': '0ms Red Flag 가드레일 및 증상 분석 중...'}, ensure_ascii=False)}\n\n"
        await asyncio.sleep(0.01)

        # Process through FSM pipeline
        response = await supervisor.process_turn(
            user_message=req.user_message,
            session_id=req.session_id,
            user_lat=req.user_lat,
            user_lon=req.user_lon,
            user_address=req.user_address,
            force_matching=req.force_matching,
            patient_age_months=req.age_months,
            patient_temperature=req.temperature,
        )


        # If emergency escalation triggered, emit high-priority emergency event immediately
        if response.is_emergency:
            emergency_payload = json.dumps(
                {
                    "is_emergency": True,
                    "message": response.message,
                    "emergency_guide": response.emergency_guide,
                },
                ensure_ascii=False,
            )
            yield f"event: emergency\ndata: {emergency_payload}\n\n"

        # Emit milestone status event
        yield f"event: status\ndata: {json.dumps({'status': 'RESOLVED', 'step': response.current_step, 'turn': response.turn_count}, ensure_ascii=False)}\n\n"

        # Emit chunked tokens of the response message
        words = response.message.split(" ")
        for i, word in enumerate(words):
            chunk = word + (" " if i < len(words) - 1 else "")
            payload = json.dumps({"delta": chunk}, ensure_ascii=False)
            yield f"event: delta\ndata: {payload}\n\n"
            await asyncio.sleep(0.01)

        # Emit final structured payload
        final_data = json.dumps(response.model_dump(), ensure_ascii=False)
        yield f"event: result\ndata: {final_data}\n\n"

        # Emit completion indicator
        yield "event: done\ndata: [DONE]\n\n"
    except Exception as e:
        err_payload = json.dumps({"error": str(e)}, ensure_ascii=False)
        yield f"event: error\ndata: {err_payload}\n\n"


@router.post(
    "",
    response_model=SupervisorResponse,
    summary="부모-에이전트 실시간 상담 및 트라이아지",
    description="자연어 증상을 입력받아 0ms Red Flag 검사, Gemini 3.8 문진, Zero-LLM 시설 매칭, 출동 가이드를 일괄 처리합니다.",
)
async def chat_turn(req: ChatRequest):
    """Processes a conversational turn with the patient supervisor."""
    supervisor = get_supervisor()

    if req.stream:
        return StreamingResponse(
            _sse_event_generator(req, supervisor),
            media_type="text/event-stream",
            headers={"Cache-Control": "no-cache", "Connection": "keep-alive"},
        )

    response = await supervisor.process_turn(
        user_message=req.user_message,
        session_id=req.session_id,
        user_lat=req.user_lat,
        user_lon=req.user_lon,
        user_address=req.user_address,
        force_matching=req.force_matching,
        patient_age_months=req.age_months,
        patient_temperature=req.temperature,
    )

    return response


@router.post(
    "/stream",
    summary="부모-에이전트 SSE 실시간 스트리밍 상담",
    description="Server-Sent Events (SSE) 방식으로 단어 단위 델타 토큰 및 최종 정형 결과를 스트리밍합니다.",
)
async def chat_stream(req: ChatRequest):
    """Streams conversational turn output via Server-Sent Events (SSE)."""
    supervisor = get_supervisor()
    return StreamingResponse(
        _sse_event_generator(req, supervisor),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive"},
    )


@router.get(
    "/session/{session_id}",
    response_model=SessionDetailResponse,
    summary="세션 상태 및 대화 이력 조회",
    description="특정 session_id의 현재 임상 변수 및 FSM 진행 상태를 조회합니다.",
)
async def get_session_detail(session_id: str):
    """Inspects active session state and accumulated clinical variables."""
    supervisor = get_supervisor()
    state = await supervisor.session_manager.get_session(session_id)
    if not state:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"세션 ID '{session_id}'를 찾을 수 없습니다.",
        )

    return SessionDetailResponse(
        session_id=state.session_id,
        current_step=state.current_step,
        turn_count=state.turn_count,
        is_red_flag=state.is_red_flag,
        red_flag_reason=state.red_flag_reason,
        age_months=state.age_months,
        temperature=state.temperature,
        duration_hours=state.duration_hours,
        symptoms=state.symptoms,
        created_at=state.created_at,
        updated_at=state.updated_at,
        messages=state.conversation_history,
    )


@router.delete(
    "/session/{session_id}",
    summary="세션 삭제 및 초기화",
    description="지정된 session_id의 메모리 세션을 즉시 삭제합니다.",
)
async def reset_session(session_id: str):
    """Deletes the active session from memory."""
    supervisor = get_supervisor()
    deleted = await supervisor.session_manager.delete_session(session_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"세션 ID '{session_id}'가 존재하지 않습니다.",
        )
    return {"status": "SUCCESS", "message": f"세션 '{session_id}'가 삭제되었습니다."}


@router.get(
    "/sessions",
    summary="활성 세션 통계",
    description="현재 메모리에 유지 중인 활성 세션 총 개수를 반환합니다.",
)
async def get_session_stats():
    """Returns active session count."""
    supervisor = get_supervisor()
    count = supervisor.session_manager.count()
    return {"active_sessions_count": count}
