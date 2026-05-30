"""
Seed the database with a single student's academic data.
Run from backend/: python -m db.seed
"""

import asyncio
from datetime import datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from db.base import AsyncSessionLocal
from db.models import Assignment, Course, Enrollment, Student, Submission


STUDENT = {
    "name": "Alex Johnson",
    "email": "alex.johnson@university.edu",
    "major": "Computer Science",
    "year_of_study": 2,
}

COURSES = [
    {"code": "CS201", "name": "Data Structures & Algorithms", "credits": 4, "semester": "2025-Spring", "teacher": "Dr. Sarah Chen"},
    {"code": "CS210", "name": "Computer Architecture", "credits": 3, "semester": "2025-Spring", "teacher": "Prof. James Miller"},
    {"code": "MATH201", "name": "Discrete Mathematics", "credits": 3, "semester": "2025-Spring", "teacher": "Dr. Priya Nair"},
    {"code": "CS220", "name": "Introduction to Databases", "credits": 3, "semester": "2025-Spring", "teacher": "Prof. Carlos Ruiz"},
    {"code": "ENG101", "name": "Technical Writing", "credits": 2, "semester": "2025-Spring", "teacher": "Ms. Laura Hayes"},
]

now = datetime.now()

ASSIGNMENTS_BY_COURSE = {
    "CS201": [
        {"title": "Homework 1: Big-O Analysis", "type": "homework", "due_date": now - timedelta(days=60), "max_score": 100, "description": "Analyse time complexity of 10 given algorithms."},
        {"title": "Homework 2: Linked Lists", "type": "homework", "due_date": now - timedelta(days=45), "max_score": 100, "description": "Implement singly and doubly linked lists."},
        {"title": "Quiz 1: Sorting Algorithms", "type": "quiz", "due_date": now - timedelta(days=30), "max_score": 50, "description": "In-class quiz covering bubble, merge, and quick sort."},
        {"title": "Midterm Exam", "type": "midterm", "due_date": now - timedelta(days=20), "max_score": 200, "description": "Covers weeks 1–7."},
        {"title": "Project: Graph Traversal", "type": "project", "due_date": now + timedelta(days=10), "max_score": 150, "description": "Implement BFS and DFS with a visualisation component."},
        {"title": "Final Exam", "type": "final", "due_date": now + timedelta(days=30), "max_score": 200, "description": "Comprehensive final covering all topics."},
    ],
    "CS210": [
        {"title": "Lab 1: Logic Gates", "type": "homework", "due_date": now - timedelta(days=55), "max_score": 100, "description": "Simulate basic logic gates."},
        {"title": "Lab 2: Assembly Basics", "type": "homework", "due_date": now - timedelta(days=35), "max_score": 100, "description": "Write simple programs in x86 assembly."},
        {"title": "Midterm Exam", "type": "midterm", "due_date": now - timedelta(days=18), "max_score": 150, "description": "Covers CPU architecture and instruction sets."},
        {"title": "Final Exam", "type": "final", "due_date": now + timedelta(days=32), "max_score": 150, "description": "Full course final."},
    ],
    "MATH201": [
        {"title": "Problem Set 1: Set Theory", "type": "homework", "due_date": now - timedelta(days=58), "max_score": 100, "description": "Problems on sets, relations, and functions."},
        {"title": "Problem Set 2: Proofs", "type": "homework", "due_date": now - timedelta(days=40), "max_score": 100, "description": "Mathematical induction and direct proofs."},
        {"title": "Problem Set 3: Graph Theory", "type": "homework", "due_date": now - timedelta(days=15), "max_score": 100, "description": "Trees, paths, and connectivity."},
        {"title": "Midterm Exam", "type": "midterm", "due_date": now - timedelta(days=22), "max_score": 150, "description": "Covers sets, logic, and proofs."},
        {"title": "Final Exam", "type": "final", "due_date": now + timedelta(days=28), "max_score": 150, "description": "Full course final."},
    ],
    "CS220": [
        {"title": "Assignment 1: ER Diagrams", "type": "homework", "due_date": now - timedelta(days=50), "max_score": 100, "description": "Design an ER diagram for a library system."},
        {"title": "Assignment 2: SQL Queries", "type": "homework", "due_date": now - timedelta(days=25), "max_score": 100, "description": "Write 15 SQL queries against a sample schema."},
        {"title": "Midterm Exam", "type": "midterm", "due_date": now - timedelta(days=16), "max_score": 100, "description": "Covers relational model and basic SQL."},
        {"title": "Project: Database Design", "type": "project", "due_date": now + timedelta(days=15), "max_score": 200, "description": "Design and implement a small relational database for a chosen domain."},
        {"title": "Final Exam", "type": "final", "due_date": now + timedelta(days=35), "max_score": 100, "description": "Full course final."},
    ],
    "ENG101": [
        {"title": "Essay 1: Technical Summary", "type": "homework", "due_date": now - timedelta(days=52), "max_score": 100, "description": "Summarise a technical paper in plain English."},
        {"title": "Essay 2: Proposal Writing", "type": "homework", "due_date": now - timedelta(days=28), "max_score": 100, "description": "Write a project proposal for a software tool."},
        {"title": "Final Report", "type": "final", "due_date": now + timedelta(days=20), "max_score": 150, "description": "Full technical report on a topic of your choice."},
    ],
}

# Scores for past assignments (indexed by course code, then assignment title)
# None means not yet submitted (for future assignments)
SCORES: dict[str, dict[str, float | None]] = {
    "CS201": {
        "Homework 1: Big-O Analysis": 88,
        "Homework 2: Linked Lists": 76,
        "Quiz 1: Sorting Algorithms": 42,
        "Midterm Exam": 158,
        "Project: Graph Traversal": None,
        "Final Exam": None,
    },
    "CS210": {
        "Lab 1: Logic Gates": 95,
        "Lab 2: Assembly Basics": 82,
        "Midterm Exam": 110,
        "Final Exam": None,
    },
    "MATH201": {
        "Problem Set 1: Set Theory": 91,
        "Problem Set 2: Proofs": 85,
        "Problem Set 3: Graph Theory": 78,
        "Midterm Exam": 120,
        "Final Exam": None,
    },
    "CS220": {
        "Assignment 1: ER Diagrams": 93,
        "Assignment 2: SQL Queries": 89,
        "Midterm Exam": 87,
        "Project: Database Design": None,
        "Final Exam": None,
    },
    "ENG101": {
        "Essay 1: Technical Summary": 84,
        "Essay 2: Proposal Writing": 90,
        "Final Report": None,
    },
}

ATTENDANCE: dict[str, float] = {
    "CS201": 90.0,
    "CS210": 85.0,
    "MATH201": 95.0,
    "CS220": 88.0,
    "ENG101": 100.0,
}

FEEDBACK: dict[str, dict[str, str]] = {
    "CS201": {
        "Midterm Exam": "Good understanding of trees and heaps. Review dynamic programming for the final.",
        "Homework 2: Linked Lists": "Correct implementation but could improve edge-case handling.",
    },
    "CS210": {
        "Lab 2: Assembly Basics": "Clean code. Try to optimise register usage.",
    },
    "MATH201": {
        "Problem Set 2: Proofs": "Proofs are mostly correct but need more formal notation.",
    },
}


async def seed(db: AsyncSession) -> None:
    student = Student(**STUDENT)
    db.add(student)
    await db.flush()

    course_map: dict[str, Course] = {}
    for course_data in COURSES:
        course = Course(**course_data)
        db.add(course)
        await db.flush()
        course_map[course.code] = course

    assignment_map: dict[str, dict[str, Assignment]] = {}
    for code, assignments in ASSIGNMENTS_BY_COURSE.items():
        course = course_map[code]
        assignment_map[code] = {}
        for a_data in assignments:
            assignment = Assignment(course_id=course.id, **a_data)
            db.add(assignment)
            await db.flush()
            assignment_map[code][assignment.title] = assignment

    for code, course in course_map.items():
        grade_scores = [
            s for s in SCORES[code].values() if s is not None
        ]
        current_grade = round(sum(grade_scores) / len(grade_scores), 2) if grade_scores else None
        enrollment = Enrollment(
            student_id=student.id,
            course_id=course.id,
            current_grade=current_grade,
            attendance_pct=ATTENDANCE[code],
        )
        db.add(enrollment)

    for code, assignments in assignment_map.items():
        for title, assignment in assignments.items():
            score = SCORES[code].get(title)
            submitted_at = assignment.due_date - timedelta(hours=2) if score is not None else None
            feedback = FEEDBACK.get(code, {}).get(title)
            submission = Submission(
                student_id=student.id,
                assignment_id=assignment.id,
                score=score,
                submitted_at=submitted_at,
                feedback=feedback,
            )
            db.add(submission)

    await db.commit()
    print(f"Seeded student '{student.name}' with {len(COURSES)} courses and all assignments.")


async def main() -> None:
    async with AsyncSessionLocal() as db:
        await seed(db)


if __name__ == "__main__":
    asyncio.run(main())
