from __future__ import annotations

import json
import uuid

from app.integrations.ollama.client import GenerationResponse
from app.services.question_service import QuestionService
from app.workflows.nodes import finalize_node
from app.workflows.state import WorkflowState, WorkflowStatus


def _make_response(raw_json: str) -> GenerationResponse:
    return GenerationResponse(
        model="qwen3:8b",
        response=raw_json,
        done=True,
        total_duration_ns=1_000_000_000,
        load_duration_ns=100_000,
        prompt_eval_count=50,
        eval_count=200,
    )


class TestParseQuestionsArrayFormat:
    def test_plain_array(self) -> None:
        raw = json.dumps([
            {
                "question_text": "What is the capital of France?",
                "question_type": "mcq",
                "options": ["A: Paris", "B: London", "C: Berlin", "D: Madrid"],
                "correct_answer": "A",
                "explanation": "Paris is the capital of France.",
                "difficulty": "easy",
            }
        ])
        result = QuestionService()._parse_questions(_make_response(raw))
        assert len(result) == 1
        assert result[0].question_text == "What is the capital of France?"


class TestParseQuestionsDictWrapping:
    def test_questions_key(self) -> None:
        raw = json.dumps({"questions": [
            {
                "question_text": "Q1?",
                "question_type": "mcq",
                "options": ["A: a", "B: b", "C: c", "D: d"],
                "correct_answer": "A",
                "explanation": "Because.",
                "difficulty": "medium",
            }
        ]})
        result = QuestionService()._parse_questions(_make_response(raw))
        assert len(result) == 1

    def test_result_key(self) -> None:
        raw = json.dumps({"result": [
            {
                "question_text": "Q2?",
                "question_type": "mcq",
                "options": ["A: a", "B: b", "C: c", "D: d"],
                "correct_answer": "B",
                "explanation": "Reason here.",
                "difficulty": "hard",
            }
        ]})
        result = QuestionService()._parse_questions(_make_response(raw))
        assert len(result) == 1

    def test_results_key(self) -> None:
        raw = json.dumps({"results": [
            {
                "question_text": "Q3?",
                "question_type": "mcq",
                "options": ["A: a", "B: b", "C: c", "D: d"],
                "correct_answer": "C",
                "explanation": "Explained.",
                "difficulty": "easy",
            }
        ]})
        result = QuestionService()._parse_questions(_make_response(raw))
        assert len(result) == 1

    def test_mcq_questions_key(self) -> None:
        raw = json.dumps({"mcq_questions": [
            {
                "question_text": "Q4?",
                "question_type": "mcq",
                "options": ["A: a", "B: b", "C: c", "D: d"],
                "correct_answer": "D",
                "explanation": "Yep.",
                "difficulty": "medium",
            }
        ]})
        result = QuestionService()._parse_questions(_make_response(raw))
        assert len(result) == 1

    def test_data_key(self) -> None:
        raw = json.dumps({"data": [
            {
                "question_text": "Q5?",
                "question_type": "mcq",
                "options": ["A: a", "B: b", "C: c", "D: d"],
                "correct_answer": "A",
                "explanation": "Sure.",
                "difficulty": "hard",
            }
        ]})
        result = QuestionService()._parse_questions(_make_response(raw))
        assert len(result) == 1


class TestParseQuestionsAutoUnwrap:
    def test_single_list_key_auto_unwrap(self) -> None:
        raw = json.dumps({"assessment_items": [
            {
                "question_text": "Q6?",
                "question_type": "mcq",
                "options": ["A: a", "B: b", "C: c", "D: d"],
                "correct_answer": "B",
                "explanation": "Auto-unwrapped.",
                "difficulty": "easy",
            }
        ]})
        result = QuestionService()._parse_questions(_make_response(raw))
        assert len(result) == 1

    def test_multiple_list_keys_no_auto_unwrap(self) -> None:
        raw = json.dumps({"list_a": [1], "list_b": [2]})
        result = QuestionService()._parse_questions(_make_response(raw))
        assert result == []


class TestParseQuestionsRejection:
    def test_dict_with_no_list_values(self) -> None:
        raw = json.dumps({"error": "something", "status": "ok"})
        result = QuestionService()._parse_questions(_make_response(raw))
        assert result == []

    def test_non_dict_non_list(self) -> None:
        raw = '"just a string"'
        result = QuestionService()._parse_questions(_make_response(raw))
        assert result == []

    def test_empty_response(self) -> None:
        result = QuestionService()._parse_questions(
            GenerationResponse(model="test", response="", done=True)
        )
        assert result == []


class TestThinkingTokenStripping:
    def test_thinking_tokens_removed(self) -> None:
        inner = json.dumps({"questions": [
            {
                "question_text": "Q?",
                "question_type": "mcq",
                "options": ["A: a", "B: b", "C: c", "D: d"],
                "correct_answer": "A",
                "explanation": "Reason.",
                "difficulty": "easy",
            }
        ]})
        raw = "\u003Cthink\u003ELet me analyze the transcript...\nStep 1: Identify key points.\n\u003C/think\u003E" + inner
        result = QuestionService()._parse_questions(_make_response(raw))
        assert len(result) == 1
        assert result[0].question_text == "Q?"

    def test_no_thinking_tokens_unchanged(self) -> None:
        raw = json.dumps({"questions": [
            {
                "question_text": "Q?",
                "question_type": "mcq",
                "options": ["A: a", "B: b", "C: c", "D: d"],
                "correct_answer": "A",
                "explanation": "Reason.",
                "difficulty": "easy",
            }
        ]})
        result = QuestionService()._parse_questions(_make_response(raw))
        assert len(result) == 1


class TestBalancedBraceExtraction:
    def test_trailing_non_json_text(self) -> None:
        inner_obj = json.dumps({"questions": [
            {
                "question_text": "Q?",
                "question_type": "mcq",
                "options": ["A: a", "B: b", "C: c", "D: d"],
                "correct_answer": "A",
                "explanation": "Reason.",
                "difficulty": "medium",
            }
        ]})
        raw = inner_obj + "\nHere are your questions!"
        result = QuestionService()._parse_questions(_make_response(raw))
        assert len(result) == 1

    def test_leading_text_before_json(self) -> None:
        inner_obj = json.dumps({"questions": [
            {
                "question_text": "Q?",
                "question_type": "mcq",
                "options": ["A: a", "B: b", "C: c", "D: d"],
                "correct_answer": "B",
                "explanation": "Because.",
                "difficulty": "hard",
            }
        ]})
        raw = "Sure! Here are the questions:\n" + inner_obj
        result = QuestionService()._parse_questions(_make_response(raw))
        assert len(result) == 1

    def test_trailing_extra_brace(self) -> None:
        inner_obj = json.dumps({"questions": [
            {
                "question_text": "Q?",
                "question_type": "mcq",
                "options": ["A: a", "B: b", "C: c", "D: d"],
                "correct_answer": "C",
                "explanation": "Yep.",
                "difficulty": "easy",
            }
        ]})
        raw = inner_obj + "}"
        result = QuestionService()._parse_questions(_make_response(raw))
        assert len(result) == 1

    def test_incomplete_json_returns_empty(self) -> None:
        raw = '{"questions": [{"question_text": "broken'
        result = QuestionService()._parse_questions(_make_response(raw))
        assert result == []


class TestLLMErrorDictHandling:
    def test_error_dict_returns_empty(self) -> None:
        raw = json.dumps({"error": "Invalid JSON format. Please fix your response."})
        result = QuestionService()._parse_questions(_make_response(raw))
        assert result == []


class TestFinalizeNodeZeroQuestions:
    def test_zero_questions_returns_failed(self) -> None:
        state: WorkflowState = WorkflowState(
            transcript_id=uuid.uuid4(),
            meeting_id=uuid.uuid4(),
            status=WorkflowStatus.PERSISTING,
            current_node="persist_questions",
            error=None,
            chunks=[],
            chunks_loaded=3,
            questions_raw=[],
            questions_generated=0,
            questions_by_chunk={},
            questions_valid=[],
            questions_invalid=[],
            questions_validated=0,
            questions_unique=[],
            duplicates_removed=0,
            questions_persisted=0,
            total_questions=0,
            model_used="qwen3:8b",
            total_prompt_tokens=None,
            total_completion_tokens=None,
            total_duration_seconds=None,
            metadata={},
        )
        result = finalize_node(state)
        assert result["status"] == WorkflowStatus.FAILED
        assert "0 valid questions" in result["error"]

    def test_nonzero_questions_returns_completed(self) -> None:
        state: WorkflowState = WorkflowState(
            transcript_id=uuid.uuid4(),
            meeting_id=uuid.uuid4(),
            status=WorkflowStatus.PERSISTING,
            current_node="persist_questions",
            error=None,
            chunks=[],
            chunks_loaded=3,
            questions_raw=[],
            questions_generated=5,
            questions_by_chunk={},
            questions_valid=[],
            questions_invalid=[],
            questions_validated=5,
            questions_unique=["q1", "q2", "q3"],
            duplicates_removed=0,
            questions_persisted=3,
            total_questions=0,
            model_used="qwen3:8b",
            total_prompt_tokens=None,
            total_completion_tokens=None,
            total_duration_seconds=None,
            metadata={},
        )
        result = finalize_node(state)
        assert result["status"] == WorkflowStatus.COMPLETED
        assert result["total_questions"] == 3
