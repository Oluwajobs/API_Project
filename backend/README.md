# Trivia API Backend

## Getting Started

### Install Dependencies

1. **Python 3.9** 

Visit https://www.python.org/downloads/ to download the latest version of Python for your platform and follow instructions in the  [python docs](https://docs.python.org/3/using/unix.html#getting-and-installing-the-latest-version-of-python)

2. **Virtual Environment**  

We recommend working within a virtual environment whenever using Python for projects. This keeps your dependencies for each project separate and organized. Instructions for setting up a virual environment for your platform can be found in the [python docs](https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/)

3. **PIP Dependencies** 

Once your virtual environment is setup and running, install the required dependencies by navigating to the `/backend` directory and running:

```bash
pip install -r requirements.txt
```

#### Key Pip Dependencies

- [Flask](http://flask.pocoo.org/) is a lightweight backend microservices framework. Flask is required to handle requests and responses.

- [SQLAlchemy](https://www.sqlalchemy.org/) is the Python SQL toolkit and ORM we'll use to handle the lightweight SQL database. You'll primarily work in `app.py`and can reference `models.py`.

- [Flask-CORS](https://flask-cors.readthedocs.io/en/latest/#) is the extension we'll use to handle cross-origin requests from our frontend server.

### Set up the Database

With Postgres running, create a `trivia` database:

```bash
createbd trivia
```

Populate the database using the `trivia.psql` file provided. From the `backend` folder in terminal run:

```bash
psql trivia < trivia.psql
```

### Run the Server

From within the `backend` directory first ensure you are working using your created virtual environment.

To run the server, execute:

```bash
export FLASK_APP=flaskr
flask run --reload
```
Setting the `FLASK_APP` variable to `flaskr` directs flask to use the `flaskr` directory and the `__init__.py` file to find the flask application.

The `--reload` flag will detect file changes to your app and restart the server automatically.


### API Documentation

The front end of the application uses our own implemented AI for all CRUD operations. You can modify endpoints in your own way, however remember to update the client (`frontend`) otherwise you will get unexpected errors.


#### Error Handling

Errors are returned as JSON objects in the following format:
```
{
  "success":False
  "message": "Not Found"
  "error": 404
}
```
The API will return one of the following 4 error message when a request is unsuccessful:
- 400: Bad Request
- 404: Not Found
- 422: Unprocessable Entity
- 500: Internal Server error

#### Endpoints

`GET '/categories'`

- General

  - Fetches a dictionary of categories in which the keys are the ids and the value is the corresponding string of the category
  - Request Arguments: None
  - Returns: An object with a single key, `categories`, that contains an object of `id: category_string` key: value pairs.

- Sample

  `curl http://127.0.0.1:5000/categories `

  ```json
  {
    "1": "Science",
    "2": "Art",
    "3": "Geography",
    "4": "History",
    "5": "Entertainment",
    "6": "Sports"
  }
  ```

`GET '/questions'`

- General

  - Fetches a list of questions to be displayed. The questions are orderd by id and filtered according to the current page number.
  - Query results are paginated to show 10 questions per page.
  - Request Arguments: `page` (default page number is 1)
  - Returns: An object that consist of a list of `questions`, the `total number of questions`, a dictionary of `categories` and a `success` key.

- Sample

   `curl http://127.0.0.1:5000/questions`

   ```json
  {
    "questions": [
      
      {
        "answer": "Apollo 13",
        "category": 5,
        "difficulty": 4,
        "id": 2,
        "question": "What movie earned Tom Hanks his third straight Oscar nomination, in 1996?"}

    ],
    "total_questions": 19,
    "categories": {
      "1": "Science",
      "2": "Art",
      "3": "Geography",
      "4": "History",
      "5": "Entertainment",
      "6": "Sports"
    },
    "success": true
  }

   ```

`POST '/questions'`

- General

  - Creates a new question in the database using the `question`, `difficulty`, `category`, and `answer` data collected from the client.
  - Returns: a `success` value, the new created `question` object and the new `total_questions` in the database.

- Sample

  `curl http://127.0.0.1:5000/questions -X POST -H "Content-Type: application/json" -d '{"question": "Which company is the leading cloud service provider?", "answer":"AWS", "category": 1, "difficulty": 3}'` 

  ```json
  {
    "questions":{
      "answer":"AWS","category":1,"difficulty":3,"id":30,"question":"Which company is the leading cloud service provider?"
      },

      "success": true,
      "total_questions":23
    } 
  ```

`GET '/categories/<int:category_id>/questions'`

- General

  - Fetches the questions that belong to a specific category. The questions are ordered by `id` paginated to display 10 results at a time.
  - Request Arguments: `category_id` of type integer.
  - Returns: a `success` value, a list of `questions`, the count of the `total_questions`, and the `current_category` of questions.

- Sample

  `curl http://127.0.0.1:5000/categories/1/questions`

  ```json
  {
    "current_category":1,

    "questions":[
      {"answer":"The Liver","category":1,"difficulty":4,"id":20,"question":"What is the heaviest organ in the human body?"},
      {"answer":"Alexander Fleming","category":1,"difficulty":3,"id":21,"question":"Who discovered penicillin?"},
      {"answer":"Blood","category":1,"difficulty":4,"id":22,"question":"Hematology is a branch of medicine involving the study of what?"},
      {"answer":"AWS","category":1,"difficulty":3,"id":30,"question":"Which company is the leading cloud service provider?"}],

      "success":true,
      "total_questions":4
  }

  ```

`POST '/questions/search'`

- General

  - Fetches questions based on a search term from the client. 
  - Returns: a list of `questions` for whom the search term is a substring of the question. the `search_term`, `total_questions` and a `successs` value.

- Sample

  `curl http://127.0.0.1:5000/questions/search -X POST -H "Content-Type: application/json" -d '{"searchTerm":"po"}'`

  ```json
  {
    "questions":[
      {"answer":"Jackson Pollock","category":2,"difficulty":2,"id":19,"question":"Which American artist was a pioneer of Abstract Expressionism, and a leading exponent of action painting?"}
      ],
      
      "search_term":"po",
      
      "success": true,
      "total_questions":1
      
  } 
  ```

`POST '/quizzes'`

- General
  - Fetches questions for player to play the quiz
  - Request Body: Takes a dictionary with key of `category` and a list of `prev_questions` parameters.
  - Returns: A random `question` object within the given categorywhich is not one of the previous questions, and a `success` value.

- Sample

  `curl http://127.0.0.1:5000/quizzes -X POST -H "Content-Type: application/json" -d '{"quiz_category": {"id": 2, "type":"Art"}, "previous_questions": [1, 2, 3]}'`

  ```json
  {
    "question":{"answer":"Escher","category":2,"difficulty":1,"id":16,"question":"Which Dutch graphic artist\u2013initials M C was a creator of optical illusions?"},
    "success":true
    
  } 
  ```

`DELETE '/questions/<int:question_id>'`

- General
  - Takes a question id in the endpoint and deletes a question in the data base with the corresponding id
  - Request Argument: a `question_id` of type integer
  - Returns: `success` value and the `id` of the `deleted` question

- Sample
  `curl http:127.0.0.1:5000/questions/19 -X DELETE`

  ```json
  {
    "id": 19,
    "success": true,

  }
  ```

## Testing

To deploy the tests, run

```bash
dropdb trivia_test
createdb trivia_test
psql trivia_test < trivia.psql
python test_flaskr.py
```
