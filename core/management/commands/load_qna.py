# core/management/commands/load_qna.py
import json
from pathlib import Path
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from core.models import Question, Answer # Import both models
from django.db import transaction # Import transaction for atomic user creation

class Command(BaseCommand):
    help = 'Loads questions and answers from JSON, assigning authorship to a "dummy_loader" user.'

    def add_arguments(self, parser):
        parser.add_argument(
            'json_file_path',
            type=str,
            help='Path to the JSON file containing question and answer data.',
        )

    @transaction.atomic # Ensure user creation/fetch and data loading are atomic
    def handle(self, *args, **options):
        json_file_path = Path(options['json_file_path'])
        dummy_username = "dummy_loader"

        if not json_file_path.exists():
            raise CommandError(f"Error: JSON file not found at '{json_file_path}'")

        # --- Get or Create Dummy User ---
        try:
            dummy_user, created = User.objects.get_or_create(
                username=dummy_username,
                defaults={
                    'first_name': 'Dummy',
                    'last_name': 'Loader',
                    'email': 'dummy@example.com',
                    'is_staff': False,
                    'is_active': True,
                }
            )
            if created:
                # Set a default unusable password if the user is newly created
                dummy_user.set_unusable_password()
                dummy_user.save()
                self.stdout.write(self.style.SUCCESS(f"Created dummy user '{dummy_username}'."))
            else:
                self.stdout.write(f"Using existing dummy user '{dummy_username}'.")
        except Exception as e:
             raise CommandError(f"Error finding or creating dummy user '{dummy_username}': {e}")


        # --- Load and Process JSON Data ---
        self.stdout.write(f"Loading Q&A data from {json_file_path}...")
        try:
            with open(json_file_path, 'r', encoding='utf-8') as f:
                qna_data = json.load(f)
        except json.JSONDecodeError:
            raise CommandError(f"Error: Could not decode JSON from '{json_file_path}'.")
        except Exception as e:
             raise CommandError(f"Error reading file '{json_file_path}': {e}")

        if not isinstance(qna_data, list):
            raise CommandError("Error: JSON file should contain a list of question objects.")

        # --- Create Questions and Answers using Dummy User ---
        questions_created_count = 0
        answers_created_count = 0
        items_skipped_count = 0
        total_questions_in_json = len(qna_data)

        self.stdout.write(f"Attempting to load {total_questions_in_json} questions and answers...")

        for i, q_data in enumerate(qna_data):
            # --- Validate Question Data ---
            if not isinstance(q_data, dict) or \
               'question_title' not in q_data or \
               'question_content' not in q_data or \
               'answers' not in q_data or \
               not isinstance(q_data['answers'], list):
                self.stderr.write(f"Warning: Skipping invalid question data structure at index {i}: {str(q_data)[:100]}...")
                items_skipped_count += 1
                continue

            try:
                # --- Process Question ---
                question, q_created = Question.objects.get_or_create(
                    title=q_data['question_title'],
                    defaults={
                        'content': q_data['question_content'],
                        'author': dummy_user # Use the dummy user
                    }
                )

                if q_created:
                    questions_created_count += 1
                    action = "Created"
                else:
                    action = "Found existing"

                # --- Process Answers for this Question ---
                current_answers_created = 0
                for a_data in q_data['answers']:
                    if not isinstance(a_data, dict) or 'content' not in a_data:
                        self.stderr.write(f"Warning: Skipping invalid answer data for question '{question.title[:50]}...': {a_data}")
                        continue

                    try:
                        answer, a_created = Answer.objects.get_or_create(
                            question=question,
                            content=a_data['content'],
                            defaults={'author': dummy_user} # Use the dummy user
                        )
                        if a_created:
                            answers_created_count += 1
                            current_answers_created +=1

                    except Exception as e:
                        self.stderr.write(self.style.ERROR(f"Error creating answer for question '{question.title[:50]}...': {e}"))

                # Report progress based on question action and answers created
                if q_created or current_answers_created > 0:
                     self.stdout.write(f"{action} question '{question.title[:50]}...' (author: {dummy_username}) and created {current_answers_created} new answers (author: {dummy_username}).")
                elif not q_created and current_answers_created == 0:
                     self.stdout.write(f"Found existing question '{question.title[:50]}...' with no new answers created.")


            except Exception as e:
                self.stderr.write(self.style.ERROR(f"Error processing question data {q_data}: {e}"))
                items_skipped_count += 1

            # Optional Progress Update
            if (i + 1) % 10 == 0:
                self.stdout.write(f"--- Processed {i + 1}/{total_questions_in_json} entries ---")


        self.stdout.write(self.style.SUCCESS(f"\nFinished loading data."))
        self.stdout.write(f"Created {questions_created_count} new questions.")
        self.stdout.write(f"Created {answers_created_count} new answers.")
        if items_skipped_count > 0:
            self.stdout.write(f"Skipped {items_skipped_count} questions/answers due to invalid data or errors.")
