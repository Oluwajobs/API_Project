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

  
    CORS(app, resources={r"/api/*": {"origins": "*"}}) # Done


    
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

   
    @app.route('/categories', methods=['GET'])
    def get_categories():
        
        categories = Category.query.all()
        category = {}
        for item in categories:
            category[item.id] = item.type
        
        return jsonify({
            'categories': category,
            'success': True,
        })

  
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
            'success': True,
        })

    
    @app.route('/questions/<int:question_id>', methods=['DELETE'])
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

 
    @app.route('/questions', methods=['POST'])  # Check endpoint in front
    def create_question():
        body = request.get_json()

        question = body.get('question', None)
        answer = body.get('answer', None)
        category = body.get('category', None)
        difficulty = body.get('difficulty', None)

        try:
            new_question = Question(question=question, answer=answer, category=category, difficulty=difficulty)
            
            new_question.insert()

            return jsonify({
                'success': True,
                'questions': new_question.format(),
                'total_questions': len(Question.query.all())
            })
        except:
            abort(405)  # unprocessable
    
    @app.route('/questions/search', methods=['POST'])
    def search_questions():
        body = request.get_json()
        search_term = body.get('searchTerm', None)
        try:
            if 'searchTerm' in body:
                selection = Question.query.order_by(Question.id).filter(Question.question.ilike(f"%{search_term}%")).all()
                search_questions = paginate_questions(request, selection)

                return jsonify({
                    'success': True,
                    'search_term': search_term,
                    'questions': search_questions,
                    'total_questions': len(search_questions),
                    
                })

          
        except:
            abort(422)

    
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
                "current_category": category_id
            })
        except:
            abort(422)  #unprocessable

   

    @app.route('/quizzes', methods=['POST'])
    def get_quiz_questions():
        body = request.get_json() # gets a json that consist of all previous questions and a chosen category- also in json
        category = body.get('quiz_category')
        prev_questions = body.get('previous_questions')

        try:
            if not (prev_questions or category):
                abort(400)

            category_id = int(category['id'])
            previous_questions = [q for q in prev_questions]
            # previous_questions_id = [q['id'] for q in previous_questions]

            if category_id == 0:
                questions = Question.query.filter(~Question.id.in_(previous_questions)).order_by(Question.id)
            else:
                questions = Question.query.filter(Question.category==category_id, ~Question.id.in_(previous_questions)).order_by(Question.id)

            question = questions.order_by(func.random()).first()

            if not question:
                return jsonify({})
            return jsonify({
                "success": True,
                "question": question.format()
            })
        except:
            abort(422)



    @app.errorhandler(400)
    def page_not_found(error):
        return jsonify({
            "success": False,
            "message":"Bad Request",
            "error": 400,
            
            }), 400

    @app.errorhandler(404)
    def bad_request(error):
        return jsonify({
            "success": False,
            "message":"Resource Not Found",
            "error": 404,
            
            }), 404
    
    @app.errorhandler(405)
    def bad_request(error):
        return jsonify({
            "success": False,
            "message":"Method Not Allowed",
            "error": 405,
            
            }), 405
    
    @app.errorhandler(422)
    def request_not_processable(error):
        return jsonify({
            "success": False,
            "message":"Request cannot be processed",
            "error": 422,

        }), 422
    
    @app.errorhandler(500)
    def server_error(error):
        return jsonify({
            "success": False,
            "message":"Server Error",
            "error": 500,
            
            }), 500

    return app

