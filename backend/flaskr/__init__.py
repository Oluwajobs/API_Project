import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from itsdangerous import json
from sqlalchemy.sql.expression import func
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    """
    @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    """
    CORS(app, resources={r"/api/*": {"origins": "*"}}) # Done


    """
    @TODO: Use the after_request decorator to set Access-Control-Allow
    """
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET, PATCH, POST, DELETE, OPTIONS')
        return response

    
    # Function for paginating the questions
    QUESTIONS_PER_PAGE = 10
    def paginate_questions(request, selection):
        page = request.args.get('page', 1, type=int)
        start = (page - 1) * QUESTIONS_PER_PAGE
        end = start + QUESTIONS_PER_PAGE

        questions = [question.format() for question in selection]  # the selection is the db query
        current_questions = questions[start:end]

        return current_questions  # returns only 10 question using the start value as starting index

    """
    @TODO:
    Create an endpoint to handle GET requests
    for all available categories.

    # Done
    """
    @app.route('/categories', methods=['GET'])
    def get_categories():
        
        categories = Category.query.all()
        category = {}
        for item in categories:
            category[item.id] = item.type
        
        return jsonify({
            'categories': category
        })

    """
    @TODO:
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.
    
    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions.
    
    # Done
    """
    @app.route('/questions')
    def get_questions():
        selection = Question.query.order_by(Question.id).all()
        categories = Category.query.all()
        current_questions = paginate_questions(request, selection)

        category = {}
        for item in categories:
            category[item.id] = item.type

        if len(current_questions) ==0:
            abort(404)
        
        return jsonify({
            'questions': current_questions,
            'total_questions': len(Question.query.all()),
            'categories': category,
            'current_category': " ",
        })

    """
    @TODO:
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    """
    @app.route('/question/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):
        if not isinstance(question_id, int):
            abort(400)
        try:
            question = Question.query.filter(Question.id==question_id).one_or_none()

            if question is None:
                abort(404)  # not found
            question.delete()

            return jsonify({
                "success": True,
                "deleted": question_id,
            })
        except:
            abort(422)

    """
    @TODO:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    
    # Done
    """
    @app.route('/questions/search', methods=['POST'])  # Check endpoint in front
    def create_question():
        body = request.get_json()

        question = body.get('question', None)
        answer = body.get('answer', None)
        category = body.get('category', None)
        difficulty = body.get('difficulty', None)

        try:
            new_question = Question(question=question, answer=answer, category=category, difficulty=difficulty)
            
            new_question.insert()

            selection = Question.query.order_by(Question.id).all()
            current_questions = paginate_questions(request, selection)

            return jsonify({
                'success': True,
                'created':new_question.id,
                'questions': current_questions,
                'total_questions': len(Question.query.all())
            })
        except:
            abort(422)  # unprocessable
    """
    @TODO:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.

    # Done
    """
    @app.route('/search', methods=['POST'])
    def search_questions():
        body = request.get_json()
        search_term = body.get('search', None)
        try:
            if 'search' in body:
                selection = Question.query.order_by(Question.id).filter(Question.question.ilike(f"%{search_term}%")).all()
                search_questions = paginate_questions(request, selection)

                return jsonify({
                    'success': True,
                    'search_term': search_term,
                    'question': search_questions,
                    'total_questions_in_search': len(search_questions)
                })

          
        except:
            abort(422)

    """
    @TODO:
    Create a GET endpoint to get questions based on category.
    
    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.

    # Done
    """
    @app.route('/categories/<int:category_id>/questions')
    def get_questions_by_category(category_id):
        if not isinstance(category_id, int) or category_id == 0:
            abort(400)

        try:
            selection = Question.query.order_by(Question.id).filter(Question.category==category_id).all()
            questions_by_category = paginate_questions(request, selection)

            return jsonify({
                "success": True,
                "questions": questions_by_category,
                "total_questions": len(selection),
                'current_category': category_id
            })
        except:
            abort(422)  #unprocessable

    """
    @TODO:
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    """

    @app.route('/quizzes', methods=['POST'])
    def get_quiz_questions():
        body = request.get_json() # gets a json that consist of all previous questions and a chosen category- also in json
        category = body.get('category')
        prev_questions = body.get('prev_questions')

        if not (prev_questions or category):
            abort(400)

        category_id = category['id']
        previous_questions = [q for q in prev_questions]
        previous_questions_id = [q['id'] for q in previous_questions]

        if category_id == '0':
            questions = Question.query.filter(~Question.id.in_(prev_questions)).order_by(Question.id)
        else:
            questions = Question.query.filter(Question.category==category_id, ~Question.id.in_(previous_questions_id)).order_by(Question.id)

        question = questions.order_by(func.random()).first()

        if not question:
            return jsonify({})
        return jsonify({
            "success": True,
            "question": question.format()
        })

        # try:

            
        #     category_id = category.get('id')  # gets the id from the category object
        #     selection = Question.query.filter(Question.category==category_id).filter(Question.id.in_(prev_questions)).order_by(Question.id)

        #     # if not category_id:
        #     #     selection = Question.query.filter(~Question.id.in_(prev_questions)).order_by(Question.id)
            
        #     # else:
        #     #     selection = Question.query.filter(Question.category==category_id, ~Question.id.in_(prev_questions)).order_by(Question.id)

        #     # question = selection.order_by(func.random()).first()
        #     #     question = selection.first()
            
        #     # if not question:
        #     #     return jsonify({})
            
        #     return jsonify({
        #         'category': category_id,
        #         'selection': selection.first().format(),
                
        #     })
        #     # return jsonify({
        #     #     'success': True,
        #     #     'question': question.format()
        #     # })
        
        # except:
        #     abort(422)

    """
    @TODO:
    Create error handlers for all expected errors
    including 404 and 422.
    """

    @app.errorhandler(400)
    def page_not_found(error):
        return jsonify({
            "success": False,
            "message":"This page does not exist",
            "error": 400,
            
            })

    @app.errorhandler(404)
    def bad_request(error):
        return jsonify({
            "success": False,
            "message":"Bad request",
            "error": 404,
            
            })
    
    @app.errorhandler(422)
    def request_not_processable(error):
        return jsonify({
            "success": False,
            "message":"Request cannot be processed",
            "error": 422,

        })
    
    @app.errorhandler(500)
    def server_error(error):
        return jsonify({
            "success": False,
            "message":"Server Error",
            "error": 500,
            
            })

    return app

