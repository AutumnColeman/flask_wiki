from flask import Flask, render_template, request, redirect
from wiki_linkify import wiki_linkify

import pg

db = pg.DB(dbname='Wiki')
app = Flask('Wiki')

@app.route('/')
def main():

    return redirect('/HomePage')

@app.route('/<page_name>')
def placeholder(page_name):
    query = db.query("select * from page where title = '%s'" % page_name)
    result_list = query.namedresult()
    if len(result_list) > 0:
        print result_list
        page_content = result_list[0].page_content
        linkify_content = wiki_linkify(page_content)
        # print page_content
        print linkify_content
        return render_template(
            'view.html',
            page_name = page_name,
            # page_content = query.namedresult()[0].page_content,
            linkify_content = linkify_content
        )

    else:
        return render_template(
            'placeholder.html',
            page_name = page_name
        )


@app.route('/<page_name>/edit')
def edit_page(page_name):
    # page_name = request.args.get('page_name')
    query = db.query("select * from page where title = '%s'" % page_name)
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
    # action = action.form.get('action')
    query = db.query("select * from page where title = '%s'" % page_name)
    if len(result_list) > 0:
        id = result_list[0].id
        db.update('page', {
            'id': id,
            'page_content': page_content
        })
    # id = query.namedresult()[0].id
    #
    # print id

    # db.update(
    #     'page', {
    #     'id': id,
    #     'title': page_name,
    #     'page_content': page_content
    # })

    db.insert(
         'page',
         title=page_name,
         page_content=page_content
    )
    return redirect('/%s' % page_name)

    return "ok"
if __name__ == '__main__':
    app.run(debug=True)
