from flask import Flask, render_template, request
from search_system import run, SearchSystem

STORAGE_PATH = 'C:/Users/Repositories/itis/information-searching/crawler/storage/'
app = Flask(__name__, template_folder='view')
search_sys = SearchSystem()


def get_file_content(filename):
    result = ''
    try:
        with open(STORAGE_PATH + filename, encoding='utf-8', errors='ignore') as file:
            lines = file.readlines()
            for line in lines:
                result += line
            return result
    except:
        return result


@app.route('/', methods=['GET', 'POST'])
def index():
    match request.method:
        case 'GET':
            return render_template('main.html')
        case 'POST':
            input_value = request.form['input_value']
            result = run(input_value, search_sys)
            if result:
                return render_template('result.html', input_value=input_value, result=result[:10])
            else:
                return render_template('empty_result.html', input_value=input_value)
        case _:
            return render_template('empty_result.html')


@app.route('/file/<filename>', methods=['GET'])
def get_file(filename):
    return get_file_content(filename)


app.run()
