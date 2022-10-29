from flask import Flask, render_template, request, escape, session, copy_current_request_context
from search_for_letters import search4letters
from dbase import DatabaseConnection, ConnectionError, CredentialsError, SQLError
from check_login_status import check_status
from threading import Thread

app = Flask(__name__)
app.secret_key = 'NotGuessable'

app.config['dbconfig'] = {'host':'127.0.0.1',
                          'user':'rahul',
                          'password':'tere_naam',
                          'database':'searchwebDB',}

print(app.config)

try:
    with DatabaseConnection(app.config['dbconfig']) as cursor:
        _SQL = """ select * from credentials """
        cursor.execute(_SQL)
        app.config['id'] = cursor.fetchall()

except Exception as err:
    print('***** The credentials could not be fetched:', str(err))


@app.route('/')
@app.route('/entry')
def entry() -> 'html':
    return render_template('entry.html',
                           the_title='Welcome to SEARCH FOR LETTERS on the web!')


@app.route('/search4', methods=['POST'])
def do_search() -> 'html':

    @copy_current_request_context
    def log_request(req: 'flask_request', res: str) -> None:

        """'req' and 'res' are nothing but argument names which will be
        substituted as 'request'(flask object) and 'results'
        (str obtained from search4letters) respectively."""

        # with open('collected_data.log', 'a') as log:
        #    print(req.form, req.remote_addr, req.user_agent, res, sep=('|'), file=log)

        try:
            with DatabaseConnection(app.config['dbconfig']) as cursor:
                _SQL = """insert into log
                          (phrase, letters, ip, browser_string, results)
                           values
                          (%s, %s, %s, %s, %s)"""

                cursor.execute(_SQL, (req.form['phrase'],
                                      req.form['letters'], 
                                      req.remote_addr, 
                                      req.user_agent.browser, 
                                      res))

        except ConnectionError as err:
            print('***** Could not connect with the databse :', str(err))
        except CredentialsError as err:
            print('***** User Id error:', str(err))
        except SQLError as err:
            print('***** The SQL Query seems Invalid:', str(err))
        except Exception as err:
            print('***** Some error occured', str(err))

        return None


    phrase = request.form['phrase']   # Never put a comma (,) after a var. else it will be regarded as a tuple.
    letters = request.form['letters']
    title = 'Here Are Your Results :'
    results = str(search4letters(phrase, letters))
    
    try:    # This try/except doesn't handle exceptions for log_request calls.
        t = Thread(target=log_request, args=(request, results))
        t.start()

        # log_request(request, results)

    except Exception as err:
        print('***** Error creating thread:', str(err))

    return render_template('results.html',
                           the_title=title,
                           the_phrase=phrase,
                           the_letters=letters,
                           the_results=results,)


@app.route('/login', methods=['GET', 'POST'])
def login() -> None:
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        try:
            if [(username, password)] == app.config['id']:
                session['logged_in'] = True
                return 'Success!'
            else:
                return 'Incorrect Username or Password'
        except Exception as err:
            print('***** Error occured:', str(err))
            return 'Error.'
    return render_template('login.html', the_title='Fill the following form to log in.')


@app.route('/logout')
def logout() -> str:
    if 'logged_in' in session:
        session.pop('logged_in')
    return 'You are logged out.'


@app.route('/viewlog')
@check_status
def show_log() -> 'html':
#     with open('collected_data.log') as log:
#         contents=[]

# # This for loop populates 'contents' as a list of lists.
# # The list of lists is convertible to a html table using jinja2's for loop.

#         for line in log:
#             contents.append([])
#             for item in line.split('|'):
#                 contents[-1].append(escape(item))

    try:
        with DatabaseConnection(app.config['dbconfig']) as cursor:
            _SQL = """ select * from log """
            cursor.execute(_SQL)
            contents = cursor.fetchall()

    except ConnectionError as err:
        print('***** Could not connect with the databse :', str(err))
    except CredentialsError as err:
        print('***** User Id error:', str(err))
    except SQLError as err:
        print('***** The SQL Query seems Invalid:', str(err))
    except Exception as err:
        print('***** Some error occured', str(err))
        return 'Error.'

    titles = ('S/N', 'Time', 'Phrase', 'Letters', 'Remote Address', 'Browser', 'Search Results')

    return render_template('viewlog.html',
                           the_title='Welcome to the logs!',
                           the_data=contents,
                           the_row_title=titles)


if __name__ == '__main__':
    app.run(debug=True,)

    # Add argument 'port=80' in app.run(), then run this python file as 'sudo'.
    # Do 'lsof -i :x' in terminal to see any processes/daemons using protocol port no. 'x'.
