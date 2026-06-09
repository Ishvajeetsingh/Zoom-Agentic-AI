from __future__ import annotations

import sys
from pathlib import Path
from datetime import datetime, timezone, timedelta

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.db.models.meeting import Meeting
from app.db.models.transcript import Transcript
from app.db.models.transcript_segment import TranscriptSegment
from app.db.models.transcript_chunk import TranscriptChunk
from app.db.models.question import Question


MEETING_DATA = {
    "source": "zoom",
    "zoom_meeting_id": "89102234567",
    "zoom_uuid": "abcd1234-5678-efgh-9012-ijkl3456mnop",
    "account_id": "acc_98765432",
    "host_id": "host_00112233",
    "host_email": "sarah.chen@example.com",
    "topic": "Q2 Product Roadmap Review",
    "start_time": datetime(2026, 5, 28, 14, 0, 0, tzinfo=timezone.utc),
    "timezone": "America/New_York",
    "duration_minutes": 45,
    "participant_count": 8,
    "metadata_json": {
        "agenda": "Review Q2 product roadmap priorities and timeline",
        "recurrence": "bi-weekly",
    },
}

TRANSCRIPT_DATA = {
    "source_format": "zoom_vtt",
    "status": "completed",
    "transcript_filename": "Q2_Product_Roadmap_Review_20260528.vtt",
    "raw_file_path": "transcripts/raw/2026/05/28/abc123.vtt",
    "processed_file_path": "transcripts/processed/2026/05/28/abc123.json",
    "zoom_file_id": "file_abc123def456",
    "zoom_recording_type": "audio_transcript",
    "file_type": "transcript",
    "file_extension": "vtt",
    "file_size_bytes": 48256,
    "recording_start": datetime(2026, 5, 28, 14, 0, 0, tzinfo=timezone.utc),
    "recording_end": datetime(2026, 5, 28, 14, 45, 0, tzinfo=timezone.utc),
    "language": "en",
    "segment_count": 10,
    "word_count": 2340,
    "cleaned_segment_count": 10,
    "cleaned_word_count": 2295,
    "chunk_count": 3,
    "question_count": 10,
    "generation_model": "qwen3:8b",
    "checksum_sha256": "a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2",
    "metadata_json": {
        "download_method": "zoom_api",
        "processing_version": "1.0",
    },
}

SEGMENTS_DATA = [
    {
        "sequence_number": 1,
        "start_time": 0.000,
        "end_time": 12.500,
        "speaker": "Sarah Chen",
        "text": "Good afternoon everyone. Thanks for joining the Q2 product roadmap review. Let's start by recapping what we accomplished in Q1 and then dive into our priorities for next quarter.",
        "cleaned_text": "Good afternoon everyone. Thanks for joining the Q2 product roadmap review. Let's start by recapping what we accomplished in Q1 and then dive into our priorities for next quarter.",
    },
    {
        "sequence_number": 2,
        "start_time": 12.500,
        "end_time": 28.750,
        "speaker": "Sarah Chen",
        "text": "In Q1 we successfully launched the new dashboard analytics module, completed the API v2 migration, and onboarded 12 new enterprise clients which exceeded our target by 20%.",
        "cleaned_text": "In Q1 we successfully launched the new dashboard analytics module, completed the API v2 migration, and onboarded 12 new enterprise clients which exceeded our target by 20%.",
    },
    {
        "sequence_number": 3,
        "start_time": 29.000,
        "end_time": 47.200,
        "speaker": "Marcus Williams",
        "text": "On the engineering side, we reduced our average API response time from 340 milliseconds to 180 milliseconds. The infrastructure migration to the new cloud provider is 75% complete and on track for finishing by mid-April.",
        "cleaned_text": "On the engineering side, we reduced our average API response time from 340 milliseconds to 180 milliseconds. The infrastructure migration to the new cloud provider is 75% complete and on track for finishing by mid-April.",
    },
    {
        "sequence_number": 4,
        "start_time": 47.500,
        "end_time": 65.300,
        "speaker": "Sarah Chen",
        "text": "Great progress Marcus. Now for Q2 priorities. Number one is the AI-powered search feature. This has been the top requested item from our enterprise clients and we've allocated three full engineering squads to it.",
        "cleaned_text": "Great progress Marcus. Now for Q2 priorities. Number one is the AI-powered search feature. This has been the top requested item from our enterprise clients and we've allocated three full engineering squads to it.",
    },
    {
        "sequence_number": 5,
        "start_time": 65.500,
        "end_time": 85.800,
        "speaker": "Priya Patel",
        "text": "From a design perspective, we finalized the UX wireframes for AI search last week. The interface includes a natural language input bar, filter chips for narrowing results, and a preview panel that shows document snippets without requiring users to open files.",
        "cleaned_text": "From a design perspective, we finalized the UX wireframes for AI search last week. The interface includes a natural language input bar, filter chips for narrowing results, and a preview panel that shows document snippets without requiring users to open files.",
    },
    {
        "sequence_number": 6,
        "start_time": 86.000,
        "end_time": 108.400,
        "speaker": "James O'Brien",
        "text": "For the data layer, we're building a vector embedding pipeline. Each document gets chunked, embedded using our fine-tuned model, and stored in the vector database. Retrieval uses hybrid search combining semantic similarity with keyword matching for best results.",
        "cleaned_text": "For the data layer, we're building a vector embedding pipeline. Each document gets chunked, embedded using our fine-tuned model, and stored in the vector database. Retrieval uses hybrid search combining semantic similarity with keyword matching for best results.",
    },
    {
        "sequence_number": 7,
        "start_time": 108.500,
        "end_time": 125.600,
        "speaker": "Sarah Chen",
        "text": "Priority number two is the collaboration workspace. This includes real-time document co-editing, threaded comments, and presence indicators so teams can see who else is viewing or editing a document at the same time.",
        "cleaned_text": "Priority number two is the collaboration workspace. This includes real-time document co-editing, threaded comments, and presence indicators so teams can see who else is viewing or editing a document at the same time.",
    },
    {
        "sequence_number": 8,
        "start_time": 126.000,
        "end_time": 148.300,
        "speaker": "Lin Wei",
        "text": "Security review is scheduled for week three of Q2. We need to ensure the real-time collaboration layer passes our SOC 2 compliance requirements. The main areas of focus are encryption in transit, access control granularity, and audit logging for all document actions.",
        "cleaned_text": "Security review is scheduled for week three of Q2. We need to ensure the real-time collaboration layer passes our SOC 2 compliance requirements. The main areas of focus are encryption in transit, access control granularity, and audit logging for all document actions.",
    },
    {
        "sequence_number": 9,
        "start_time": 148.500,
        "end_time": 170.200,
        "speaker": "Marcus Williams",
        "text": "Priority three is performance optimization. We want to bring page load time under 2 seconds across the entire application. This requires database query optimization, implementing Redis caching for frequently accessed data, and lazy loading for the dashboard widgets.",
        "cleaned_text": "Priority three is performance optimization. We want to bring page load time under 2 seconds across the entire application. This requires database query optimization, implementing Redis caching for frequently accessed data, and lazy loading for the dashboard widgets.",
    },
    {
        "sequence_number": 10,
        "start_time": 170.500,
        "end_time": 195.000,
        "speaker": "Sarah Chen",
        "text": "Perfect. Let's align on timelines. AI search targets beta release by end of May, collaboration workspace enters internal testing by mid-June, and performance improvements should ship incrementally throughout the quarter. Any blockers or concerns before we break into team huddles?",
        "cleaned_text": "Perfect. Let's align on timelines. AI search targets beta release by end of May, collaboration workspace enters internal testing by mid-June, and performance improvements should ship incrementally throughout the quarter. Any blockers or concerns before we break into team huddles?",
    },
]

CHUNKS_DATA = [
    {
        "chunk_index": 0,
        "text": "Good afternoon everyone. Thanks for joining the Q2 product roadmap review. Let's start by recapping what we accomplished in Q1 and then dive into our priorities for next quarter. In Q1 we successfully launched the new dashboard analytics module, completed the API v2 migration, and onboarded 12 new enterprise clients which exceeded our target by 20%. On the engineering side, we reduced our average API response time from 340 milliseconds to 180 milliseconds. The infrastructure migration to the new cloud provider is 75% complete and on track for finishing by mid-April.",
        "word_count": 82,
        "start_time": 0.000,
        "end_time": 47.200,
        "speakers": ["Sarah Chen", "Marcus Williams"],
        "segment_range_start": 0,
        "segment_range_end": 2,
    },
    {
        "chunk_index": 1,
        "text": "Great progress Marcus. Now for Q2 priorities. Number one is the AI-powered search feature. This has been the top requested item from our enterprise clients and we've allocated three full engineering squads to it. From a design perspective, we finalized the UX wireframes for AI search last week. The interface includes a natural language input bar, filter chips for narrowing results, and a preview panel that shows document snippets without requiring users to open files. For the data layer, we're building a vector embedding pipeline. Each document gets chunked, embedded using our fine-tuned model, and stored in the vector database. Retrieval uses hybrid search combining semantic similarity with keyword matching for best results.",
        "word_count": 104,
        "start_time": 47.500,
        "end_time": 108.400,
        "speakers": ["Sarah Chen", "Priya Patel", "James O'Brien"],
        "segment_range_start": 3,
        "segment_range_end": 5,
    },
    {
        "chunk_index": 2,
        "text": "Priority number two is the collaboration workspace. This includes real-time document co-editing, threaded comments, and presence indicators so teams can see who else is viewing or editing a document at the same time. Security review is scheduled for week three of Q2. We need to ensure the real-time collaboration layer passes our SOC 2 compliance requirements. The main areas of focus are encryption in transit, access control granularity, and audit logging for all document actions. Priority three is performance optimization. We want to bring page load time under 2 seconds across the entire application. This requires database query optimization, implementing Redis caching for frequently accessed data, and lazy loading for the dashboard widgets. Perfect. Let's align on timelines. AI search targets beta release by end of May, collaboration workspace enters internal testing by mid-June, and performance improvements should ship incrementally throughout the quarter.",
        "word_count": 125,
        "start_time": 108.500,
        "end_time": 195.000,
        "speakers": ["Sarah Chen", "Lin Wei", "Marcus Williams"],
        "segment_range_start": 6,
        "segment_range_end": 9,
    },
]

QUESTIONS_DATA = [
    {
        "chunk_index": 0,
        "question_type": "mcq",
        "question_text": "By what percentage did the team exceed its Q1 enterprise client onboarding target?",
        "options": [
            {"label": "A", "text": "10%"},
            {"label": "B", "text": "15%"},
            {"label": "C", "text": "20%"},
            {"label": "D", "text": "25%"},
        ],
        "correct_answer": "C",
        "explanation": "Sarah Chen stated the team onboarded 12 new enterprise clients which exceeded the target by 20%.",
        "difficulty": "easy",
    },
    {
        "chunk_index": 0,
        "question_type": "mcq",
        "question_text": "What was the reduction in average API response time achieved in Q1?",
        "options": [
            {"label": "A", "text": "From 340ms to 200ms"},
            {"label": "B", "text": "From 340ms to 180ms"},
            {"label": "C", "text": "From 400ms to 180ms"},
            {"label": "D", "text": "From 280ms to 160ms"},
        ],
        "correct_answer": "B",
        "explanation": "Marcus Williams reported reducing the average API response time from 340 milliseconds to 180 milliseconds.",
        "difficulty": "easy",
    },
    {
        "chunk_index": 0,
        "question_type": "mcq",
        "question_text": "What percentage of the infrastructure migration to the new cloud provider has been completed?",
        "options": [
            {"label": "A", "text": "50%"},
            {"label": "B", "text": "60%"},
            {"label": "C", "text": "75%"},
            {"label": "D", "text": "90%"},
        ],
        "correct_answer": "C",
        "explanation": "Marcus Williams stated that the infrastructure migration is 75% complete and on track for mid-April completion.",
        "difficulty": "easy",
    },
    {
        "chunk_index": 1,
        "question_type": "mcq",
        "question_text": "What is the top Q2 priority identified in the roadmap review?",
        "options": [
            {"label": "A", "text": "Performance optimization"},
            {"label": "B", "text": "Collaboration workspace"},
            {"label": "C", "text": "AI-powered search feature"},
            {"label": "D", "text": "Infrastructure migration"},
        ],
        "correct_answer": "C",
        "explanation": "Sarah Chen identified the AI-powered search feature as the number one Q2 priority, noting it was the top request from enterprise clients.",
        "difficulty": "easy",
    },
    {
        "chunk_index": 1,
        "question_type": "mcq",
        "question_text": "Which design elements are included in the AI search interface according to the UX wireframes?",
        "options": [
            {"label": "A", "text": "Search bar, tag cloud, and full document viewer"},
            {"label": "B", "text": "Natural language input, filter chips, and preview panel"},
            {"label": "C", "text": "Voice input, category tabs, and sidebar results"},
            {"label": "D", "text": "Keyword input, sort dropdown, and thumbnail grid"},
        ],
        "correct_answer": "B",
        "explanation": "Priya Patel described the interface as including a natural language input bar, filter chips for narrowing results, and a preview panel showing document snippets.",
        "difficulty": "medium",
    },
    {
        "chunk_index": 1,
        "question_type": "mcq",
        "question_text": "What two search strategies are combined in the hybrid retrieval approach for the AI search feature?",
        "options": [
            {"label": "A", "text": "Boolean search and wildcard matching"},
            {"label": "B", "text": "Semantic similarity and keyword matching"},
            {"label": "C", "text": "Fuzzy search and exact phrase matching"},
            {"label": "D", "text": "Regular expression and full-text search"},
        ],
        "correct_answer": "B",
        "explanation": "James O'Brien explained that retrieval uses hybrid search combining semantic similarity with keyword matching for best results.",
        "difficulty": "medium",
    },
    {
        "chunk_index": 2,
        "question_type": "mcq",
        "question_text": "Which three capabilities are part of the collaboration workspace feature?",
        "options": [
            {"label": "A", "text": "Video conferencing, screen sharing, and chat"},
            {"label": "B", "text": "Real-time co-editing, threaded comments, and presence indicators"},
            {"label": "C", "text": "Version control, code review, and merge requests"},
            {"label": "D", "text": "Task boards, time tracking, and sprint planning"},
        ],
        "correct_answer": "B",
        "explanation": "Sarah Chen listed real-time document co-editing, threaded comments, and presence indicators as the collaboration workspace capabilities.",
        "difficulty": "easy",
    },
    {
        "chunk_index": 2,
        "question_type": "mcq",
        "question_text": "What are the three focus areas for the SOC 2 compliance security review of the collaboration feature?",
        "options": [
            {"label": "A", "text": "Data residency, user authentication, and API rate limiting"},
            {"label": "B", "text": "Encryption at rest, password policies, and session timeout"},
            {"label": "C", "text": "Encryption in transit, access control granularity, and audit logging"},
            {"label": "D", "text": "Two-factor authentication, firewall rules, and vulnerability scanning"},
        ],
        "correct_answer": "C",
        "explanation": "Lin Wei specified encryption in transit, access control granularity, and audit logging for all document actions as the three security focus areas.",
        "difficulty": "medium",
    },
    {
        "chunk_index": 2,
        "question_type": "mcq",
        "question_text": "What is the target page load time for the performance optimization priority?",
        "options": [
            {"label": "A", "text": "Under 1 second"},
            {"label": "B", "text": "Under 2 seconds"},
            {"label": "C", "text": "Under 3 seconds"},
            {"label": "D", "text": "Under 5 seconds"},
        ],
        "correct_answer": "B",
        "explanation": "Marcus Williams stated the goal is to bring page load time under 2 seconds across the entire application.",
        "difficulty": "easy",
    },
    {
        "chunk_index": 2,
        "question_type": "mcq",
        "question_text": "What is the target timeline for the collaboration workspace to enter internal testing?",
        "options": [
            {"label": "A", "text": "End of April"},
            {"label": "B", "text": "End of May"},
            {"label": "C", "text": "Mid-June"},
            {"label": "D", "text": "End of June"},
        ],
        "correct_answer": "C",
        "explanation": "Sarah Chen stated that the collaboration workspace enters internal testing by mid-June, while AI search targets beta by end of May.",
        "difficulty": "medium",
    },
]


def seed() -> dict:
    engine = create_engine(settings.database_url, pool_pre_ping=True)
    Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = Session()

    try:
        meeting = Meeting(**MEETING_DATA)
        session.add(meeting)
        session.flush()

        transcript_data = {**TRANSCRIPT_DATA, "meeting_id": meeting.id}
        transcript = Transcript(**transcript_data)
        session.add(transcript)
        session.flush()

        segments = []
        for seg_data in SEGMENTS_DATA:
            segment = TranscriptSegment(
                transcript_id=transcript.id,
                meeting_id=meeting.id,
                **seg_data,
            )
            session.add(segment)
            segments.append(segment)
        session.flush()

        chunks = []
        for chunk_data in CHUNKS_DATA:
            segment_ids_json = chunk_data.pop("segment_ids", [])
            if not segment_ids_json:
                start_idx = chunk_data.get("segment_range_start", 0)
                end_idx = chunk_data.get("segment_range_end", 0)
                segment_ids_json = [
                    str(segments[i].segment_id) for i in range(start_idx, end_idx + 1)
                ]
            chunk = TranscriptChunk(
                transcript_id=transcript.id,
                meeting_id=meeting.id,
                segment_ids=segment_ids_json,
                **chunk_data,
            )
            session.add(chunk)
            chunks.append(chunk)
        session.flush()

        chunk_by_index = {c.chunk_index: c for c in chunks}

        for q_data in QUESTIONS_DATA:
            chunk_idx = q_data.pop("chunk_index")
            chunk_obj = chunk_by_index.get(chunk_idx)
            question = Question(
                transcript_id=transcript.id,
                meeting_id=meeting.id,
                chunk_id=chunk_obj.chunk_id if chunk_obj else None,
                **q_data,
            )
            session.add(question)
        session.flush()

        session.commit()

        counts = {
            "meetings": 1,
            "transcripts": 1,
            "transcript_segments": len(segments),
            "transcript_chunks": len(chunks),
            "questions": len(QUESTIONS_DATA),
        }

        print("Seed completed successfully!")
        print(f"  Meeting ID:    {meeting.id}")
        print(f"  Transcript ID: {transcript.id}")
        print()
        for table, count in counts.items():
            print(f"  {table}: {count}")

        return counts
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


if __name__ == "__main__":
    seed()
