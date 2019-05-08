from bottle import route, run, template

@route('/upload')
def show_upload_form():
    return template('upload')

if __name__ == '__main__':
    run(host='localhost', port=8080)
