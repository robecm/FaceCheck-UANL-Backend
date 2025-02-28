from flask import Blueprint, request, jsonify
from modules.database_modules.exam_database import ExamsDatabase

modify_exam_results_bp = Blueprint('modify_exam_results', __name__)
db = ExamsDatabase()

@modify_exam_results_bp.route('/exam/modify-result', methods=['POST'])
def modify_exam_result():
    try:
        body = request.form if request.form else request.get_json()
        print("Received request body:", body)  # Debugging print
        if not body:
            return jsonify(ExamsDatabase.generate_response(
                success=False,
                error='Request body is missing',
                status_code=400
            )), 400

        # Assume 'results' is always provided
        multiple_results = body.get('results')
        print("Received multiple results:", multiple_results)  # Debugging print
        if not multiple_results:
            return jsonify(ExamsDatabase.generate_response(
                success=False,
                error='No results provided',
                status_code=400
            )), 400

        # Validate and process each result
        for item in multiple_results:
            print("Processing item:", item)  # Debugging print
            score = item.get('score')
            if score is not None:
                try:
                    score = float(score)
                    if not (0 <= score <= 100):
                        return jsonify(ExamsDatabase.generate_response(
                            success=False,
                            error='Score must be between 0 and 100',
                            status_code=400
                        )), 400
                    item['score'] = round(score, 2)
                    print("Validated score:", item['score'])  # Debugging print
                except ValueError:
                    return jsonify(ExamsDatabase.generate_response(
                        success=False,
                        error='Invalid score value: must be a number',
                        status_code=400
                    )), 400

        # Call the bulk modify_exam_results function
        print("Calling modify_exam_results with:", multiple_results)  # Debugging print
        result = db.modify_exam_results(multiple_results)
        print("Result from modify_exam_results:", result)  # Debugging print
        if not result['success']:
            return jsonify(result), result['status_code']

        return jsonify(ExamsDatabase.generate_response(
            success=True,
            data={'message': 'All exam results processed successfully'},
            status_code=200
        )), 200

    except Exception as e:
        print("Exception occurred:", str(e))  # Debugging print
        return jsonify(ExamsDatabase.generate_response(
            success=False,
            error=str(e),
            status_code=500
        )), 500