from flask import Blueprint, request, jsonify
from flask_security import roles_required
from application.models import db, Subject, Chapter, Quiz, Question, User
from jobs.tasks import export_all_users_performance_csv
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime

admin_bp = Blueprint('admin_bp', __name__, url_prefix='/admin')

def commit_or_rollback():
    try:
        db.session.commit()
        return True, None
    except SQLAlchemyError as e:
        db.session.rollback()
        return False, str(e)


@admin_bp.route('/subjects', methods=['POST'])
@roles_required('admin')
def create_subject():
    data = request.json
    subject = Subject(name=data['name'])
    db.session.add(subject)
    success, error = commit_or_rollback()
    if success:
        return jsonify({'message': 'Subject created'}), 201
    return jsonify({'error': error}), 400

@admin_bp.route('/subjects', methods=['GET'])
@roles_required('admin')
def get_subjects():
    subjects = Subject.query.all()
    return jsonify([{'id': s.id, 'name': s.name} for s in subjects])

@admin_bp.route('/subjects/<int:subject_id>', methods=['PUT'])
@roles_required('admin')
def update_subject(subject_id):
    data = request.json
    subject = Subject.query.get_or_404(subject_id)
    subject.name = data['name']
    success, error = commit_or_rollback()
    if success:
        return jsonify({'message': 'Subject updated'})
    return jsonify({'error': error}), 400

@admin_bp.route('/subjects/delete', methods=['POST'])
@roles_required('admin')
def delete_multiple_subjects():
    data = request.json
    ids = data.get('ids', [])
    if not isinstance(ids, list):
        return jsonify({'error': 'Invalid data format'}), 400

    try:
        for subject_id in ids:
            subject = Subject.query.get(subject_id)
            if subject:
                db.session.delete(subject)
        db.session.commit()
        return jsonify({'message': 'Subjects deleted'}), 200
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/subjects/<int:subject_id>/chapters', methods=['POST'])
@roles_required('admin')
def create_chapter(subject_id):
    data = request.json
    chapter = Chapter(name=data['name'], subject_id=subject_id)
    db.session.add(chapter)
    success, error = commit_or_rollback()
    if success:
        return jsonify({'message': 'Chapter created'}), 201
    return jsonify({'error': error}), 400

@admin_bp.route('/subjects/<int:subject_id>/chapters', methods=['GET'])
@roles_required('admin')
def get_chapters(subject_id):
    chapters = Chapter.query.filter_by(subject_id=subject_id).all()
    return jsonify([{'id': c.id, 'name': c.name} for c in chapters])

@admin_bp.route('/chapters', methods=['GET'])
@roles_required('admin')
def get_all_chapters():
    chapters = Chapter.query.all()
    return jsonify({
        "chapters": [
            {"id": c.id, "name": c.name, "subject_id": c.subject_id}
            for c in chapters
        ]
    })

@admin_bp.route('/chapters/<int:chapter_id>', methods=['PUT'])
@roles_required('admin')
def update_chapter(chapter_id):
    data = request.json
    chapter = Chapter.query.get_or_404(chapter_id)
    chapter.name = data['name']
    success, error = commit_or_rollback()
    if success:
        return jsonify({'message': 'Chapter updated'})
    return jsonify({'error': error}), 400

@admin_bp.route('/chapters/<int:chapter_id>', methods=['DELETE'])
@roles_required('admin')
def delete_chapter(chapter_id):
    chapter = Chapter.query.get_or_404(chapter_id)
    db.session.delete(chapter)
    success, error = commit_or_rollback()
    if success:
        return jsonify({'message': 'Chapter deleted'})
    return jsonify({'error': error}), 400


@admin_bp.route('/quizzes', methods=['GET'])
@roles_required('admin')
def get_all_quizzes():
    try:
        quizzes = Quiz.query.all()
        quiz_list = []
        for quiz in quizzes:
            quiz_list.append({
                "id": quiz.id,
                "name": quiz.name,
                "subject": quiz.chapter.subject.name if quiz.chapter and quiz.chapter.subject else "Unknown",
                "chapter": quiz.chapter.name if quiz.chapter else "Unknown",
                "date": quiz.date_of_quiz.isoformat() if quiz.date_of_quiz else "",
                "time": quiz.time_of_quiz.strftime("%H:%M") if quiz.time_of_quiz else "",
                "duration": quiz.duration_seconds
            })
        return jsonify(quiz_list)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@admin_bp.route("/quizzes", methods=["POST"])
@roles_required("admin")
def create_quiz():
    try:
        data = request.get_json(force=True)

        name = data.get("name")
        chapter_id = data.get("chapter_id")
        date_str = data.get("date")
        time_str = data.get("time")
        duration_seconds = data.get("duration")

        if not all([name, chapter_id, date_str, duration_seconds]):
            return jsonify({"error": "Missing required fields"}), 400

        try:
            date_of_quiz = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            return jsonify({"error": "Invalid date format. Use YYYY-MM-DD"}), 400
        
        try:
            time_of_quiz = datetime.strptime(time_str, "%H:%M").time()
        except ValueError:
            return jsonify({"error": "Invalid time format. Use HH:MM"}), 400

        quiz = Quiz(
            name=name,
            chapter_id=chapter_id,
            date_of_quiz=date_of_quiz,
            time_of_quiz=time_of_quiz,
            duration_seconds=duration_seconds,
        )
        db.session.add(quiz)
        db.session.commit()

        return jsonify({"message": "Quiz created", "quiz_id": quiz.id}), 201

    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"error": "Database error", "details": str(e)}), 500

@admin_bp.route('/chapters/<int:chapter_id>/quizzes', methods=['GET'])
@roles_required('admin')
def get_quizzes(chapter_id):
    quizzes = Quiz.query.filter_by(chapter_id=chapter_id).all()
    return jsonify([{'id': q.id, 'name': q.name} for q in quizzes])

@admin_bp.route('/quizzes/<int:quiz_id>', methods=['PUT'])
@roles_required('admin')
def update_quiz(quiz_id):
    data = request.json
    quiz = Quiz.query.get_or_404(quiz_id)

    try:
        quiz.name = data['name']
        if data.get('date_of_quiz'):
            quiz.date_of_quiz = datetime.strptime(data['date_of_quiz'], "%Y-%m-%d").date()
        if data.get('time_of_quiz'):
            quiz.time_of_quiz = datetime.strptime(data['time_of_quiz'], "%H:%M").time()
        quiz.duration_seconds = data.get('duration_seconds')
        quiz.chapter_id = data.get('chapter_id')

        success, error = commit_or_rollback()
        if success:
            return jsonify({'message': 'Quiz updated'})
        return jsonify({'error': error}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@admin_bp.route('/quizzes/<int:quiz_id>', methods=['DELETE'])
@roles_required('admin')
def delete_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    db.session.delete(quiz)
    success, error = commit_or_rollback()
    if success:
        return jsonify({'message': 'Quiz deleted'})
    return jsonify({'error': error}), 400


@admin_bp.route('/quizzes/<int:quiz_id>/questions', methods=['POST'])
@roles_required('admin')
def create_question(quiz_id):
    data = request.json
    question = Question(
        content=data['content'],
        quiz_id=quiz_id,
        option1=data.get('option1'),
        option2=data.get('option2'),
        option3=data.get('option3'),
        option4=data.get('option4'),
        correct_option=data.get('correct_option')
    )
    db.session.add(question)
    success, error = commit_or_rollback()
    if success:
        return jsonify({'message': 'Question created'}), 201
    return jsonify({'error': error}), 400

@admin_bp.route('/quizzes/<int:quiz_id>/questions', methods=['GET'])
@roles_required('admin')
def get_questions(quiz_id):
    questions = Question.query.filter_by(quiz_id=quiz_id).all()
    return jsonify({
        "questions": [
            {
                'id': q.id,
                'content': q.content,
                'option1': q.option1,
                'option2': q.option2,
                'option3': q.option3,
                'option4': q.option4,
                'correct_option': q.correct_option,
            } for q in questions
        ]
    })

@admin_bp.route('/questions/<int:question_id>', methods=['PUT'])
@roles_required('admin')
def update_question(question_id):
    data = request.json
    question = Question.query.get_or_404(question_id)
    question.content = data['content']
    question.option1 = data.get('option1')
    question.option2 = data.get('option2')
    question.option3 = data.get('option3')
    question.option4 = data.get('option4')
    question.correct_option = data.get('correct_option')
    success, error = commit_or_rollback()
    if success:
        return jsonify({'message': 'Question updated'})
    return jsonify({'error': error}), 400

@admin_bp.route('/questions/<int:question_id>', methods=['DELETE'])
@roles_required('admin')
def delete_question(question_id):
    question = Question.query.get_or_404(question_id)
    db.session.delete(question)
    success, error = commit_or_rollback()
    if success:
        return jsonify({'message': 'Question deleted'})
    return jsonify({'error': error}), 400


@admin_bp.route('/users', methods=['GET'])
@roles_required('admin')
def list_users():
    users = User.query.all()
    result = []
    for u in users:
        if any(role.name == "admin" for role in u.roles):
            continue

        user_data = {
            'id': u.id,
            'email': u.email,
            'roles': [role.name for role in u.roles],
            'active': u.active,
            'quizzes': []
        }

        for score in u.scores:
            quiz_data = {
                'id': score.quiz.id,
                'name': score.quiz.name,
                'score_id': score.id,
                'date': score.quiz.date_of_quiz.isoformat() if score.quiz.date_of_quiz else "",
                'score': score.total_scored,
                'details': []
            }

            for d in score.details:
                quiz_data['details'].append({
                    'question': d.question.content,
                    'options': [
                        d.question.option1, d.question.option2,
                        d.question.option3, d.question.option4
                    ],
                    'user_answer': d.user_answer,
                    'correct_answer': d.correct_answer
                })

            user_data['quizzes'].append(quiz_data)

        result.append(user_data)

    return jsonify(result)

@admin_bp.route('/summary', methods=['GET'])
@roles_required('admin')
def get_summary():
    data = {
        'num_subjects': Subject.query.count(),
        'num_chapters': Chapter.query.count(),
        'num_quizzes': Quiz.query.count(),
        'num_users': User.query.count()
    }
    return jsonify(data)

@admin_bp.route("/export-all-users", methods=["POST"])
@roles_required("admin")
def export_all_users():
    from main import celery
    try:
        task = export_all_users_performance_csv.delay()
        return jsonify({"message": "Export started", "task_id": task.id}), 202
    except Exception as e:
        return jsonify({"error": str(e)}), 500
