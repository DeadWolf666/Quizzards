from flask import Blueprint, jsonify, request
from flask_security import login_required, roles_required, current_user
from datetime import datetime, timedelta
from application.models import db, Quiz, Question, Score, ScoreDetail
# from jobs.tasks import export_user_history_csv

user_bp = Blueprint('user_bp', __name__, url_prefix='/user')

@user_bp.route('/subjects')
@roles_required('user')
def get_subjects_with_quizzes():
    subjects = []
    from application.models import Subject
    for subject in Subject.query.all():
        chapters = []
        for chapter in subject.chapters:
            quizzes = []
            for quiz in chapter.quizzes:
                quizzes.append({
                    "id": quiz.id,
                    "name": quiz.name,
                    "date": quiz.date_of_quiz.strftime("%Y-%m-%d"),
                    "time": quiz.time_of_quiz.strftime("%H:%M"),
                    "duration": quiz.duration_seconds
                })
            chapters.append({
                "id": chapter.id,
                "name": chapter.name,
                "quizzes": quizzes
            })
        subjects.append({
            "id": subject.id,
            "name": subject.name,
            "chapters": chapters
        })
    return jsonify({"subjects": subjects}), 200

@user_bp.route('/quiz/<int:quiz_id>')
@roles_required('user')
def fetch_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)

    now = datetime.now()
    quiz_start = datetime.combine(quiz.date_of_quiz, quiz.time_of_quiz)
    quiz_end = quiz_start + timedelta(seconds=quiz.duration_seconds)
    remaining_time = int((quiz_end - now).total_seconds())
    existing_attempt = Score.query.filter_by(user_id=current_user.id, quiz_id=quiz.id).first()

    if now < quiz_start:
        return jsonify({"error": "Quiz has not started yet"}), 403
    if now > quiz_end:
        return jsonify({"error": "Quiz has expired"}), 403
    if existing_attempt:
        return jsonify({"error": "You have already attempted this quiz"}), 403

    questions_data = []
    for q in quiz.questions:
        questions_data.append({
            "id": q.id,
            "content": q.content,
            "options": [q.option1, q.option2, q.option3, q.option4]
        })

    return jsonify({
        "id": quiz.id,
        "name": quiz.name,
        "duration": remaining_time,
        "questions": questions_data
    }), 200

@user_bp.route('/quiz/<int:quiz_id>/submit', methods=['POST'])
@roles_required('user')
def submit_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)

    quiz_start = datetime.combine(quiz.date_of_quiz, quiz.time_of_quiz)
    quiz_end = quiz_start + timedelta(seconds=quiz.duration_seconds)
    now = datetime.now()
    if now > quiz_end:
        return jsonify({"error": "Quiz has expired"}), 403

    data = request.get_json()
    answers = data.get("answers", {})

    score = 0
    total = len(quiz.questions)

    score_entry = Score(
        quiz_id=quiz.id,
        user_id=current_user.id,
        total_scored=0
    )
    db.session.add(score_entry)
    db.session.flush()

    for question in quiz.questions:
        user_answer = answers.get(str(question.id))
        correct = question.correct_option

        if user_answer and user_answer == correct:
            score += 1

        detail = ScoreDetail(
            score_id=score_entry.id,
            question_id=question.id,
            user_answer=user_answer,
            correct_answer=correct
        )
        db.session.add(detail)

    score_entry.total_scored = score
    db.session.commit()

    return jsonify({
        "score": score,
        "total": total
    }), 200

@user_bp.route('/scores')
@roles_required('user')
def past_scores():
    scores = Score.query.filter_by(user_id=current_user.id).order_by(Score.time_stamp_of_attempt.desc()).all()
    scores_data = []
    for s in scores:
        scores_data.append({
            "id": s.id,
            "quiz_name": s.quiz.name,
            "time_stamp_of_attempt": s.time_stamp_of_attempt.isoformat(),
            "total_scored": s.total_scored
        })
    return jsonify({"scores": scores_data}), 200

@user_bp.route('/scores/<int:score_id>/details')
@roles_required('user')
def get_score_details(score_id):
    score = Score.query.get_or_404(score_id)
    if score.user_id != current_user.id:
        return jsonify({"error": "Unauthorized"}), 403

    details_data = []
    for d in score.details:
        details_data.append({
            "question": d.question.content,
            "options": [d.question.option1, d.question.option2, d.question.option3, d.question.option4],
            "user_answer": d.user_answer,
            "correct_answer": d.correct_answer
        })
    
    return jsonify({"details": details_data}), 200

# @user_bp.route("/export-history", methods=["POST"])
# @login_required
# def export_user_history():
#     from main import celery
#     user_id = current_user.id
#     try:
#         task = export_user_history_csv.delay(user_id)
#         return jsonify({"message": "Export started", "task_id": task.id}), 202
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500
