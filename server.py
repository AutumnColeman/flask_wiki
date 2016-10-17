from flask import Flask, render_template, request, redirect, Markup, session, flash
from wiki_linkify import wiki_linkify
from datetime import datetime
import pg, socket, markdown



db = pg.DB(dbname='Wiki')
app = Flask('Wiki')

app.secret_key = 'password'

@app.route('/')
def main():

    return render_template(
        'login.html'
        )

@app.route('/submit_login', methods=['POST'])
def submit_login():
    username = request.form.get('username')
    password = request.form.get('password')
    query = db.query("select * from users where username = $1", username)
    result_list = query.namedresult()
    # flash('$1, you have submitted your login information!', username)
    if len(result_list) > 0:
        user = result_list[0]
        if user.password == password:
            session['username'] = user.username
            return render_template(
                'index.html'
            )
        else:
            flash('Invalid username or password')
            return redirect('/')
    else:
        return redirect('/')

@app.route('/signup')
def sign_up():
    return render_template(
        'signup.html'
        # pass session['username'] to site?
    )

@app.route('/signup_save', methods=['POST'])
def save_sign_up():
    username = request.form.get('username')
    password = request.form.get('password')
    query = db.query("select * from users where username = $1", username)
    result_list = query.namedresult()
    db.insert(
         'users',
         username=username,
         password=password
    )

    return redirect('/')


@app.route('/<page_name>')
def view_page(page_name):
    query = db.query("select * from page where title = $1", page_name)
    result_list = query.namedresult()
    if len(result_list) > 0:
        print result_list
        page_content = result_list[0].page_content
        page_content = page_content.replace('<', '&lt;').replace('>', '&gt;')
        page_content = wiki_linkify(page_content)
        parsed_content = Markup(markdown.markdown(page_content))

        print page_content
        return render_template(
            'view.html',
            page_name = page_name,
            # page_content = query.namedresult()[0].page_content,
            page_content = parsed_content
        )

    else:
        return render_template(
            'placeholder.html',
            page_name = page_name
        )


@app.route('/<page_name>/edit')
def edit_page(page_name):
    # page_name = request.args.get('page_name')
    query = db.query("select * from page where title = $1", page_name)
    result_list = query.namedresult()
    if len(result_list) > 0:
        page = result_list[0]
        return render_template(
            'edit.html',
            page_name = page_name,
            page_content=page.page_content
            )
    else:
        return render_template(
            'edit.html',
            page_name=page_name
        )
        # page_content = query.namedresult()[0]

@app.route('/<page_name>/save', methods=['POST'])
def save_edit(page_name):
    page_content = request.form.get('page_content')
    id = request.form.get('id')
    title = request.form.get('title')
    query = db.query("select * from page where title = $1", page_name)
    result_list = query.namedresult()
    if len(result_list) > 0:
        id = result_list[0].id
        db.update('page', {
            'id': id,
            'page_content': page_content,
            'last_modified_date': datetime.now(),
            'author_name': socket.gethostbyname(socket.gethostname())
        })

    else:
        db.insert(
             'page',
             title=page_name,
             page_content=page_content
        )
    return redirect('/%s' % page_name)

    return "ok"
if __name__ == '__main__':
    app.run(debug=True)
