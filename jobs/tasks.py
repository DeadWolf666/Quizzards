import os
import csv
from celery import Celery, shared_task
from datetime import datetime, timedelta
from flask import current_app
from application.models import db, User, Quiz, Score
import smtplib
from email.mime.text import MIMEText

EXPORT_DIR = os.path.join(os.getcwd(), "exports")
os.makedirs(EXPORT_DIR, exist_ok=True)

def make_celery(app):
    celery = Celery(app.import_name)
    celery.conf.update(broker_url=app.config["BROKER_URL"], result_backend=app.config["RESULT_BACKEND"])

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery


def send_email(config, to_email, subject, html_body):
    server = config["MAIL_SERVER"]
    port = config["MAIL_PORT"]
    username = config["MAIL_USERNAME"]
    password = config["MAIL_PASSWORD"]
    sender = config["MAIL_DEFAULT_SENDER"]

    msg = MIMEText(html_body, "html")
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = to_email

    try:
        with smtplib.SMTP(server, port) as smtp:
            smtp.starttls()
            smtp.login(username, password)
            smtp.sendmail(sender, [to_email], msg.as_string())
        print(f"[Email Sent] {to_email} - {subject}")
    except Exception as e:
        print(f"[Email Error] {to_email}: {e}")


@shared_task(name="send_daily_quiz_reminders")
def send_daily_quiz_reminders():
    app = current_app._get_current_object()
    tomorrow = datetime.now().date() + timedelta(days=1)
    quizzes = Quiz.query.filter(Quiz.date_of_quiz == tomorrow).all()

    if not quizzes:
        print("No quizzes tomorrow.")
        return "No quizzes tomorrow."

    for quiz in quizzes:
        chapter_name = quiz.chapter.name if quiz.chapter else "Unknown Chapter"
        for user in User.query.all():
            subject = f"Reminder: {quiz.name} is scheduled for tomorrow!"
            body = f"""
                <h3>Quiz Reminder</h3>
                <p>The quiz <b>{quiz.name}</b> (Chapter: {chapter_name})
                is scheduled on <b>{quiz.date_of_quiz}</b> at <b>{quiz.time_of_quiz}</b>.</p>
                <p>Login to your Quizzards account to attempt it.</p>
            """
            send_email(app.config, user.email, subject, body)

    return f"Reminders sent for {len(quizzes)} quizzes."


@shared_task(name="send_monthly_performance_reports")
def send_monthly_performance_reports():
    app = current_app._get_current_object()
    today = datetime.now()
    first_of_this_month = today.replace(day=1)
    first_of_last_month = (first_of_this_month - timedelta(days=1)).replace(day=1)

    users = User.query.all()
    count = 0

    for user in users:
        scores = Score.query.filter(
            Score.user_id == user.id,
            Score.time_stamp_of_attempt >= first_of_last_month,
            Score.time_stamp_of_attempt < first_of_this_month
        ).all()

        if not scores:
            body = f"""
                <h3>Your Monthly Performance Report</h3>
                <p>Hi <b>{user.email}</b>,</p>
                <p>You didn't attempt any quizzes last month.</p>
                <p>Tip: Regular practice improves performance! 
                Check out upcoming quizzes at the Quizzards website.</p>
            """
            send_email(app.config, user.email, "Your Monthly Quiz Performance Report", body)
            continue

        total_score = 0
        total_possible = 0
        total_correct = 0
        total_questions = 0

        quiz_list_html = ""

        for s in scores:
            quiz = s.quiz
            chapter_name = quiz.chapter.name if quiz.chapter else "Unknown Chapter"
            question_count = len(quiz.questions)

            correct_answers = sum(1 for d in s.details if d.user_answer == d.correct_answer)
            incorrect_answers = len(s.details) - correct_answers

            total_score += s.total_scored
            total_possible += question_count
            total_correct += correct_answers
            total_questions += len(s.details)

            question_breakdown_html = ""
            for d in s.details:
                q = d.question

                if d.user_answer is None:
                    user_answer_html = f"<span style='color:gray;'>Not Attempted</span>"
                elif d.user_answer == d.correct_answer:
                    user_answer_html = f"<span style='color:green; font-weight:bold;'>{d.user_answer}</span> ✅"
                else:
                    user_answer_html = f"<span style='color:red; font-weight:bold;'>{d.user_answer}</span> ❌"

                def option_html(opt):
                    if opt == d.correct_answer:
                        return f"<li style='color:green;'><b>{opt}</b> ✔️</li>"
                    return f"<li>{opt}</li>"

                question_breakdown_html += f"""
                    <div style="margin-bottom:10px;">
                        <p><b>Q:</b> {q.content}</p>
                        <ul>
                            {option_html(q.option1)}
                            {option_html(q.option2)}
                            {option_html(q.option3)}
                            {option_html(q.option4)}
                        </ul>
                        <p><b>Your Answer:</b> {user_answer_html}</p>
                        <p><b>Correct Answer:</b> <span style='color:green; font-weight:bold;'>{d.correct_answer}</span></p>
                    </div>
                    <hr>
                """

            quiz_list_html += f"""
                <li>
                    <b>{quiz.name}</b> (Chapter: {chapter_name})<br>
                    Score: {s.total_scored}/{question_count} 
                    ({(s.total_scored/question_count)*100:.1f}%)<br>
                    Correct: {correct_answers} | Incorrect: {incorrect_answers}
                    <br><br>
                    <details>
                        <summary style="cursor:pointer; color:#007BFF; font-weight:bold;">View Question-by-Question Breakdown</summary>
                        <div style="margin-top:10px;">
                            {question_breakdown_html}
                        </div>
                    </details>
                </li>
                <br>
            """

        overall_accuracy = (total_correct / total_questions * 100) if total_questions > 0 else 0
        total_percentage = (total_score / total_possible * 100) if total_possible > 0 else 0

        body = f"""
            <h3>Your Monthly Performance Report</h3>
            <p>Hi <b>{user.email}</b>,</p>
            <p>Here is your detailed performance report for 
            <b>{first_of_last_month.strftime('%B %Y')}</b>:</p>
            
            <p><b>Total Quizzes Attempted:</b> {len(scores)}</p>
            <p><b>Total Score:</b> {total_score}/{total_possible} 
            ({total_percentage:.1f}%)</p>
            <p><b>Overall Accuracy:</b> {overall_accuracy:.1f}%</p>

            <h4>Quiz-wise Breakdown:</h4>
            <ul>
                {quiz_list_html}
            </ul>

            <p style="color: #555;">Keep learning and aim for even higher accuracy next month! 🚀</p>
        """
        send_email(app.config, user.email, "Your Monthly Quiz Performance Report", body)
        count += 1

    return f"Reports sent to {count} users."

# @shared_task
# def export_user_history_csv(user_id):
#     """Export a specific user's quiz history as CSV"""
#     user = User.query.get(user_id)
#     if not user:
#         return None

#     file_name = f"user_{user_id}_history_{datetime.now().strftime('%Y%m%d%H%M%S')}.csv"
#     file_path = os.path.join(EXPORT_DIR, file_name)

#     with open(file_path, mode="w", newline="") as csv_file:
#         writer = csv.writer(csv_file)
#         writer.writerow(["Quiz Name", "Date", "Score"])

#         for score in user.scores:
#             writer.writerow([
#                 score.quiz.name,
#                 score.time_stamp_of_attempt.strftime("%Y-%m-%d %H:%M:%S"),
#                 score.total_scored
#             ])

#     return file_path


@shared_task
def export_all_users_performance_csv():
    """Export all users' performance data as CSV"""
    file_name = f"all_users_performance_{datetime.now().strftime('%Y%m%d%H%M%S')}.csv"
    file_path = os.path.join(EXPORT_DIR, file_name)

    with open(file_path, mode="w", newline="") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(["User Email", "Quiz Name", "Date", "Score"])

        scores = Score.query.all()
        for score in scores:
            writer.writerow([
                score.user.email,
                score.quiz.name,
                score.time_stamp_of_attempt.strftime("%Y-%m-%d %H:%M:%S"),
                score.total_scored
            ])

    return file_path
