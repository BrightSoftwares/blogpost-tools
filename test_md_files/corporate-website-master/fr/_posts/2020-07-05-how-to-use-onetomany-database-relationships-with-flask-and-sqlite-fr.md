---
layout: flexstart-blog-single
title: "Comment utiliser les relations de base de données un à plusieurs avec Flask et SQLite"
author: full
lang: fr
ref: flask_sqlite_1239
categories: [database]
description: "Flask est un framework permettant de créer des applications Web à l'aide du langage Python, et SQLite est un moteur de base de données qui peut être utilisé avec Python pour stocker des données d'application. Dans ce didacticiel, vous utiliserez Flask avec SQLite pour créer une application de tâches dans laquelle les utilisateurs peuvent créer des listes d'éléments de tâches. Vous apprendrez à utiliser SQLite avec Flask et comment fonctionnent les relations de base de données un à plusieurs."
image: "https://sergio.afanou.com/assets/images/image-midres-48.jpg"
---





[Flask](http://flask.pocoo.org/) est un framework pour créer des applications Web utilisant le langage Python, et [SQLite](https://sqlite.org/) est un moteur de base de données qui peut être utilisé avec Python pour stocker les données d'application. Dans ce didacticiel, vous utiliserez Flask avec SQLite pour créer une application de tâches dans laquelle les utilisateurs peuvent créer des listes d'éléments de tâches. Vous apprendrez à utiliser SQLite avec Flask et comment fonctionnent les relations de base de données un à plusieurs.

Une _relation de base de données un-à-plusieurs_ est une relation entre deux tables de base de données où un enregistrement dans une table peut référencer plusieurs enregistrements dans une autre table. Par exemple, dans une application de blog, une table pour stocker des publications peut avoir une relation un-à-plusieurs avec une table pour stocker des commentaires. Chaque article peut faire référence à de nombreux commentaires, et chaque commentaire fait référence à un seul article ; par conséquent, **un** post a une relation avec **beaucoup** de commentaires. La table de publication est une _table parente_, tandis que la table de commentaires est une _table enfant_ — un enregistrement dans la table parent peut référencer plusieurs enregistrements dans la table enfant. Ceci est important pour pouvoir accéder aux données associées dans chaque table.

Nous utiliserons SQLite car il est portable et ne nécessite aucune configuration supplémentaire pour fonctionner avec Python. Il est également idéal pour prototyper une application avant de passer à une base de données plus grande telle que MySQL ou Postgres. Pour en savoir plus sur la façon de choisir le bon système de base de données, lisez notre [SQLite vs MySQL vs PostgreSQL : une comparaison des systèmes de gestion de bases de données relationnelles](https://www.digitalocean.com/community/tutorials/sqlite-vs-mysql-vs- postgresql-a-comparison-of-relational-database-management-systems).

## Prérequis

Avant de commencer à suivre ce guide, vous aurez besoin de :

* Un environnement de programmation Python 3 local, suivez le tutoriel de votre distribution dans [Comment installer et configurer un environnement de programmation local pour Python 3](https://www.digitalocean.com/community/tutorial_series/how-to-install -and-set-up-a-local-programming-environment-for-python-3) série pour votre machine locale. Dans ce didacticiel, nous appellerons notre répertoire de projet `flask_todo`.
* Une compréhension des concepts de base de Flask tels que la création d'itinéraires, le rendu de modèles HTML et la connexion à une base de données SQLite. Vous pouvez suivre [Comment créer une application Web à l'aide de Flask en Python 3](https://www.digitalocean.com/community/tutorials/how-to-make-a-web-application-using-flask-in-python -3), si vous n'êtes pas familier avec ces concepts, mais ce n'est pas nécessaire.

## Étape 1 - Création de la base de données


Dans cette étape, vous allez activer votre environnement de programmation, installer Flask, créer la base de données SQLite et la remplir avec des exemples de données. Vous apprendrez à utiliser des clés étrangères pour créer une relation un-à-plusieurs entre des listes et des éléments. Une _clé étrangère_ est une clé utilisée pour associer une table de base de données à une autre table, c'est le lien entre la table enfant et sa table mère.

Si vous n'avez pas encore activé votre environnement de programmation, assurez-vous d'être dans le répertoire de votre projet (`flask_todo`) et utilisez cette commande pour l'activer :

```
source env/bin/activate
```


Once your programming environment is activated, install Flask using the following command:

    pip install flask
    

Once the installation is complete, you can now create the database schema file that contains SQL commands to create the tables you need to store your to-do data. You will need two tables: a table called `lists` to store to-do lists, and an `items` table to store the items of each list.

Open a file called `schema.sql` inside your `flask_todo` directory:

    nano schema.sql
    

Type the following SQL commands inside this file:

flask\_todo/schema.sql

    DROP TABLE IF EXISTS lists;
    DROP TABLE IF EXISTS items;
    
    CREATE TABLE lists (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    title TEXT NOT NULL
    );
    
    CREATE TABLE items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    list_id INTEGER NOT NULL,
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    content TEXT NOT NULL,
    FOREIGN KEY (list_id) REFERENCES lists (id)
    );
    

Save and close the file.

The first two SQL command are `DROP TABLE IF EXISTS lists;` and `DROP TABLE IF EXISTS items;`, these delete any already existing tables named `lists` and `items` so you don’t see confusing behavior. Note that this will delete all of the content you have in the database whenever you use these SQL commands, so ensure you don’t write any important content in the web application until you finish this tutorial and experiment with the final result.

Next, you use `CREATE TABLE lists` to create the `lists` table that will store the to-do lists (such as a study list, work list, home list, and so on) with the following columns:

*   `id`: An integer that represents a _primary key_, this will get assigned a unique value by the database for each entry (i.e. to-do list).
*   `created`: The time the to-do list was created at. `NOT NULL` signifies that this column should not be empty and the `DEFAULT` value is the `CURRENT_TIMESTAMP` value, which is the time at which the list was added to the database. Just like `id`, you don’t need to specify a value for this column, as it will be automatically filled in.
*   `title`: The list title.

Then, you create a table called `items` to store to-do items. This table has an ID, a `list_id` integer column to identify which list an item belongs to, a creation date, and the item’s content. To link an item to a list in the database you use a _foreign key constraint_ with the line `FOREIGN KEY (list_id) REFERENCES lists (id)`. Here the `lists` table is a _parent table_, which is the table that is being referenced by the foreign key constraint, this indicates a list can have multiple items. The `items` table is a _child table_, which is the table the constraint applies to. This means items belong to a single list. The `list_id` column references the `id` column of the `lists` parent table.

Since a list can have **many** items, and an item belongs to only **one** list, the relationship between the `lists` and `items` tables is a _one-to-many_ relationship.

Next, you will use the `schema.sql` file to create the database. Open a file named `init_db.py` inside the `flask_todo` directory:

    nano init_db.py
    

Then add the following code:

flask\_todo/init\_db.py

    import sqlite3
    
    connection = sqlite3.connect('database.db')
    
    with open('schema.sql') as f:
    connection.executescript(f.read())
    
    cur = connection.cursor()
    
    cur.execute("INSERT INTO lists (title) VALUES (?)", ('Work',))
    cur.execute("INSERT INTO lists (title) VALUES (?)", ('Home',))
    cur.execute("INSERT INTO lists (title) VALUES (?)", ('Study',))
    
    cur.execute("INSERT INTO items (list_id, content) VALUES (?, ?)",
    (1, 'Morning meeting')
    )
    
    cur.execute("INSERT INTO items (list_id, content) VALUES (?, ?)",
    (2, 'Buy fruit')
    )
    
    cur.execute("INSERT INTO items (list_id, content) VALUES (?, ?)",
    (2, 'Cook dinner')
    )
    
    cur.execute("INSERT INTO items (list_id, content) VALUES (?, ?)",
    (3, 'Learn Flask')
    )
    
    cur.execute("INSERT INTO items (list_id, content) VALUES (?, ?)",
    (3, 'Learn SQLite')
    )
    
    connection.commit()
    connection.close()
    

Save and close the file.

Here you connect to a file called `database.db` that will be created once you execute this program. You then open the `schema.sql` file and run it using the [`executescript()`](https://docs.python.org/3/library/sqlite3.html#sqlite3.Connection.executescript) method that executes multiple SQL statements at once.

Running `schema.sql` will create the `lists` and `items` tables. Next, using a [Cursor object](https://docs.python.org/3/library/sqlite3.html#cursor-objects), you execute a few `INSERT` SQL statements to create three lists and five to-do items.

You use the `list_id` column to link each item to a list via the list’s `id` value. For example, the `Work` list was the first insertion into the database, so it will have the ID `1`. This is how you can link the `Morning meeting` to-do item to `Work`—the same rule applies to the other lists and items.

Finally, you commit the changes and close the connection.

Run the program:

    python init_db.py
    

After execution, a new file called `database.db` will appear in your `flask_todo` directory.

You’ve activated your environment, installed Flask, and created the SQLite database. Next, you’ll retrieve the lists and items from the database and display them in the application’s homepage.

Step 2 — Displaying To-do Items
-------------------------------

In this step, you will connect the database you created in the previous step to a Flask application that displays the to-do lists and the items of each list. You will learn how to use SQLite joins to query data from two tables and how to group to-do items by their lists.

First, you will create the application file. Open a file named `app.py` inside the `flask_todo` directory:

    nano app.py
    

And then add the following code to the file:

flask\_todo/app.py

    from itertools import groupby
    import sqlite3
    from flask import Flask, render_template, request, flash, redirect, url_for
    
    def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn
    
    app = Flask(**name**)
    app.config['SECRET_KEY'] = 'this should be a secret random string'
    
    @app.route('/')
    def index():
    conn = get_db_connection()
    todos = conn.execute('SELECT i.content, l.title FROM items i JOIN lists l \
     ON i.list_id = l.id ORDER BY l.title;').fetchall()
    
        lists = {}
    
        for k, g in groupby(todos, key=lambda t: t['title']):
            lists[k] = list(g)
    
        conn.close()
        return render_template('index.html', lists=lists)
    
    

Save and close the file.

The `get_db_connection()` function opens a connection to the `database.db` database file and then sets the [`row_factory`](https://docs.python.org/3/library/sqlite3.html#sqlite3.Connection.row_factory) attribute to `sqlite3.Row`. In this way you can have name-based access to columns; this means that the database connection will return rows that behave like regular Python dictionaries. Lastly, the function returns the `conn` connection object you’ll be using to access the database.

In the `index()` view function, you open a database connection and execute the following SQL query:

    SELECT i.content, l.title FROM items i JOIN lists l ON i.list_id = l.id ORDER BY l.title;
    

You then retrieve its results by using the `fetchall()` method and save the data in a variable called `todos`.

In this query, you use `SELECT` to get the content of the item and the title of the list it belongs to by joining both the `items` and `lists` tables (with the table aliases `i` for `items` and `l` for `lists`). With the join condition `i.list_id = l.id` after the `ON` keyword, you will get each row from the `items` table with every row from the `lists` table where the `list_id` column of the `items` table matches the `id` of the `lists` table. You then use `ORDER BY` to order the results by list titles.

To understand this query better, open the [Python REPL](https://www.digitalocean.com/community/tutorials/how-to-work-with-the-python-interactive-console) in your `flask_todo` directory:

    python
    

To understand the SQL query, examine the contents of the `todos` variable by running this small program:

    from app import get_db_connection
    conn = get_db_connection()
    todos = conn.execute('SELECT i.content, l.title FROM items i JOIN lists l \
    ON i.list_id = l.id ORDER BY l.title;').fetchall()
    for todo in todos:
        print(todo['title'], ':', todo['content'])
    

You first import the `get_db_connection` from the `app.py` file then open a connection and execute the query (note that this is the same SQL query you have in your `app.py` file). In the `for` loop you print the title of the list and the content of each to-do item.

The output will be as follows:

    OutputHome : Buy fruit
    Home : Cook dinner
    Study : Learn Flask
    Study : Learn SQLite
    Work : Morning meeting
    

Close the REPL using `CTRL + D`.

Now that you understand how SQL joins work and what the query achieves, let’s return back to the `index()` view function in your `app.py` file. After declaring the `todos` variable, you group the results using the following code:

    lists = {}
    
    for k, g in groupby(todos, key=lambda t: t['title']):
    lists[k] = list(g)
    

You first declare an empty dictionary called `lists`, then use a `for` loop to go through a grouping of the results in the `todos` variable by the list’s title. You use the [`groupby()`](https://docs.python.org/3.5/library/itertools.html#itertools.groupby) function you imported from the `itertools` standard library. This function will go through each item in the `todos` variable and generate a group of results for each key in the `for` loop.

`k` represents list titles (that is, `Home`, `Study`, `Work`), which are extracted using the function you pass to the `key` parameter of the `groupby()` function. In this case the function is `lambda t: t['title']` that takes a to-do item and returns the title of the list (as you have done before with `todo['title']` in the previous for loop). `g` represents the group that contains the to-do items of each list title. For example, in the first iteration, `k` will be `'Home'`, while `g` is an [iterable](https://docs.python.org/3/glossary.html#term-iterable) that will contain the items `'Buy fruit'` and `'Cook dinner'`.

This gives us a representation of the one-to-many relationship between lists and items, where each list title has several to-do items.

When running the `app.py` file, and after the `for` loop finishes execution, `lists` will be as follows:

    Output{'Home': [<sqlite3.Row object at 0x7f9f58460950>,
              <sqlite3.Row object at 0x7f9f58460c30>],
     'Study': [<sqlite3.Row object at 0x7f9f58460b70>,
               <sqlite3.Row object at 0x7f9f58460b50>],
     'Work': [<sqlite3.Row object at 0x7f9f58460890>]}
    

Each `sqlite3.Row` object will contain the data you retrieved from the `items` table using the SQL query in the `index()` function. To represent this data better, let’s make a program that goes through the `lists` dictionary and displays each list and its items.

Open a file called `list_example.py` in your `flask_todo` directory:

    nano list_example.py
    

Then add the following code:

flask\_todo/list\_example.py

    
    from itertools import groupby
    from app import get_db_connection
    
    conn = get_db_connection()
    todos = conn.execute('SELECT i.content, l.title FROM items i JOIN lists l \
     ON i.list_id = l.id ORDER BY l.title;').fetchall()
    
    lists = {}
    
    for k, g in groupby(todos, key=lambda t: t['title']):
    lists[k] = list(g)
    
    for list*, items in lists.items():
    print(list*)
    for item in items:
    print(' ', item['content'])
    

Save and close the file.

This is very similar to the content in your `index()` view function. The last `for` loop here illustrates how the `lists` dictionary is structured. You first go through the dictionary’s items, print the list title (which is in the `list_` variable), then go through each group of to-do items that belong to the list and print the content value of the item.

Run the `list_example.py` program:

    python list_example.py
    

Here is the output of `list_example.py`:

    OutputHome
         Buy fruit
         Cook dinner
    Study
         Learn Flask
         Learn SQLite
    Work
         Morning meeting
    

Now that you understand each part of the `index()` function, let’s create a base template and create the `index.html` file you rendered using the line `return render_template('index.html', lists=lists)`.

In your `flask_todo` directory, create a `templates` directory and open a file called `base.html` inside it:

    mkdir templates
    nano templates/base.html
    

Add the following code inside `base.html`, note that you’re using [Bootstrap](https://getbootstrap.com/) here. If you are not familiar with HTML templates in Flask, see [Step 3 of How To Make a Web Application Using Flask in Python 3](https://www.digitalocean.com/community/tutorials/how-to-make-a-web-application-using-flask-in-python-3#step-3-%E2%80%94-using-html-templates):

flask\_todo/templates/base.html

    <!doctype html>
    <html lang="en">
      <head>
        <!-- Required meta tags -->
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
    
        <!-- Bootstrap CSS -->
        <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/css/bootstrap.min.css" integrity="sha384-ggOyR0iXCbMQv3Xipma34MD+dH/1fQ784/j6cY/iJTQUOhcWr7x9JvoRxT2MZw1T" crossorigin="anonymous">
    
        <title>{ block title } { endblock }</title>
    
    </head>
    <body>
    <nav class="navbar navbar-expand-md navbar-light bg-light">
    <a class="navbar-brand" href="">FlaskTodo</a>
    <button class="navbar-toggler" type="button" data-toggle="collapse" data-target="#navbarNav" aria-controls="navbarNav" aria-expanded="false" aria-label="Toggle navigation">
    <span class="navbar-toggler-icon"></span>
    </button>
    <div class="collapse navbar-collapse" id="navbarNav">
    <ul class="navbar-nav">
    <li class="nav-item active">
    <a class="nav-link" href="#">About</a>
    </li>
    </ul>
    </div>
    </nav>
    <div class="container">
    { block content } { endblock }
    </div>
    
        <!-- Optional JavaScript -->
        <!-- jQuery first, then Popper.js, then Bootstrap JS -->
        <script src="https://code.jquery.com/jquery-3.3.1.slim.min.js" integrity="sha384-q8i/X+965DzO0rT7abK41JStQIAqVgRVzpbzo5smXKp4YfRvH+8abtTE1Pi6jizo" crossorigin="anonymous"></script>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.14.7/umd/popper.min.js" integrity="sha384-UO2eT0CpHqdSJQ6hJty5KVphtPhzWj9WO1clHTMGa3JDZwrnQq4sF86dIHNDz0W1" crossorigin="anonymous"></script>
        <script src="https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/js/bootstrap.min.js" integrity="sha384-JjSmVgyd0p3pXB1rRibZUAYoIIy6OrQ6VrjIEaFf/nJGzIxFDsf4x0xIM+B07jRM" crossorigin="anonymous"></script>
    
    </body>
    </html>
    

Save and close the file.

Most of the code in the preceding block is standard HTML and code required for Bootstrap. The `<meta>` tags provide information for the web browser, the `<link>` tag links the Bootstrap CSS files, and the `<script>` tags are links to JavaScript code that allows some additional Bootstrap features. Check out the [Bootstrap documentation](https://getbootstrap.com/) for more information.

Next, create the `index.html` file that will extend this `base.html` file:

    nano templates/index.html
    

Add the following code to `index.html`:

flask\_todo/templates/index.html

    { extends 'base.html' }
    
    { block content }
    <h1>{ block title } Welcome to FlaskTodo { endblock }</h1>
    { for list, items in lists.items() }
    <div class="card" style="width: 18rem; margin-bottom: 50px;">
    <div class="card-header">
    <h3>{{ list }}</h3>
    </div>
    <ul class="list-group list-group-flush">
    { for item in items }
    <li class="list-group-item">{{ item['content'] }}</li>
    { endfor }
    </ul>
    </div>
    { endfor }
    { endblock }
    

Here you use a `for` loop to go through each item of the `lists` dictionary, you display the list title as a card header inside an `<h3>` tag, and then use a list group to display each to-do item that belongs to the list in an `<li>` tag. This follows the same rules explained in the `list_example.py` program.

You will now set the environment variables Flask needs and run the application using the following commands:

    export FLASK_APP=app
    export FLASK_ENV=development
    flask run
    

Once the development server is running, you can visit the URL `http://127.0.0.1:5000/` in your browser. You will see a web page with the “Welcome to FlaskTodo” and your list items.

![Home Page](https://assets.digitalocean.com/articles/flask_sqlite/image_welcome.png)

You can now type `CTRL + C` to stop your development server.

You’ve created a Flask application that displays the to-do lists and the items of each list. In the next step, you will add a new page for creating new to-do items.

Step 3 — Adding New To-do Items
-------------------------------

In this step, you will make a new route for creating to-do items, you will insert data into database tables, and associate items with the lists they belong to.

First, open the `app.py` file:

    nano app.py
    

Then, add a new `/create` route with a view function called `create()` at the end of the file:

flask\_todo/app.py

    ...
    @app.route('/create/', methods=('GET', 'POST'))
    def create():
        conn = get_db_connection()
        lists = conn.execute('SELECT title FROM lists;').fetchall()
    
        conn.close()
        return render_template('create.html', lists=lists)
    

Save and close the file.

Because you will use this route to insert new data to the database via a web form, you allow both GET and POST requests using `methods=('GET', 'POST')` in the `app.route()` decorator. In the `create()` view function, you open a database connection then get all the list titles available in the database, close the connection, and render a `create.html` template passing it the list titles.

Next, open a new template file called `create.html`:

    nano templates/create.html
    

Add the following HTML code to `create.html`:

flask\_todo/templates/create.html

    { extends 'base.html' }
    
    { block content }
    <h1>{ block title } Create a New Item { endblock }</h1>
    
    <form method="post">
    <div class="form-group">
    <label for="content">Content</label>
    <input type="text" name="content"
    placeholder="Todo content" class="form-control"
    value="{{ request.form['content'] }}"></input>
    </div>
    
        <div class="form-group">
            <label for="list">List</label>
            <select class="form-control" name="list">
                { for list in lists }
                    { if list['title'] == request.form['list'] }
                        <option value="{{ request.form['list'] }}" selected>
                            {{ request.form['list'] }}
                        </option>
                    { else }
                        <option value="{{ list['title'] }}">
                            {{ list['title'] }}
                        </option>
                    { endif }
                { endfor }
            </select>
        </div>
        <div class="form-group">
            <button type="submit" class="btn btn-primary">Submit</button>
        </div>
    
    </form>
    { endblock }
    

Save and close the file.

You use `request.form` to access the form data that is stored in case something goes wrong with your form submission (for example, if no to-do content was provided). In the `<select>` element, you loop through the lists you retrieved from the database in the `create()` function. If the list title is equal to what is stored in `request.form` then the selected option is that list title, otherwise, you display the list title in a normal non-selected `<option>` tag.

Now, in the terminal, run your Flask application:

    flask run
    

Then visit `http://127.0.0.1:5000/create` in your browser, you will see a form for creating a new to-do item, note that the form doesn’t work yet because you have no code to handle POST requests that get sent by the browser when submitting the form.

Type `CTRL + C` to stop your development server.

Next, let’s add the code for handling POST requests to the `create()` function and make the form function properly, open `app.py`:

    nano app.py
    

Then edit the `create()` function to look like so:

flask\_todo/app.py

    ...
    @app.route('/create/', methods=('GET', 'POST'))
    def create():
        conn = get_db_connection()
    
        if request.method == 'POST':
            content = request.form['content']
            list_title = request.form['list']
    
            if not content:
                flash('Content is required!')
                return redirect()
    
            list_id = conn.execute('SELECT id FROM lists WHERE title = (?);',
                                     (list_title,)).fetchone()['id']
            conn.execute('INSERT INTO items (content, list_id) VALUES (?, ?)',
                         (content, list_id))
            conn.commit()
            conn.close()
            return redirect()
    
        lists = conn.execute('SELECT title FROM lists;').fetchall()
    
        conn.close()
        return render_template('create.html', lists=lists)
    
    

Save and close the file.

Inside the `request.method == 'POST'` condition you get the to-do item’s content and the list’s title from the form data. If no content was submitted, you send the user a message using the `flash()` function and redirect to the index page. If this condition was not triggered, then you execute a `SELECT` statement to get the list ID from the provided list title and save it in a variable called `list_id`. You then execute an `INSERT INTO` statement to insert the new to-do item into the `items` table. You use the `list_id` variable to link the item to the list it belongs to. Finally, you commit the transaction, close the connection, and redirect to the index page.

As a last step, you will add a link to `/create` in the navigation bar and display flashed messages below it, to do this, open `base.html`:

    nano templates/base.html
    

Edit the file by adding a new `<li>` navigation item that links to the `create()` view function. Then display the flashed messages using a `for` loop above the `content` block. These are available in the [`get_flashed_messages()` Flask function](https://flask.palletsprojects.com/en/1.1.x/patterns/flashing/):

flask\_todo/templates/base.html

    <nav class="navbar navbar-expand-md navbar-light bg-light">
        <a class="navbar-brand" href="">FlaskTodo</a>
        <button class="navbar-toggler" type="button" data-toggle="collapse" data-target="#navbarNav" aria-controls="navbarNav" aria-expanded="false" aria-label="Toggle navigation">
            <span class="navbar-toggler-icon"></span>
        </button>
        <div class="collapse navbar-collapse" id="navbarNav">
            <ul class="navbar-nav">
            <li class="nav-item active">
                <a class="nav-link" href="">New</a>
            </li>
    
            <li class="nav-item active">
                <a class="nav-link" href="#">About</a>
            </li>
            </ul>
        </div>
    
    </nav>
    <div class="container">
    { for message in get_flashed_messages() }
     <div class="alert alert-danger">{{ message }}</div>
    { endfor }
    {block content } { endblock }
    </div>
    

Save and close the file.

Now, in the terminal, run your Flask application:

    flask run
    

A new link to `/create` will appear in the navigation bar. If you navigate to this page and try to add a new to-do item with no content, you’ll receive a flashed message saying **Content is required!**. If you fill in the content form, a new to-do item will appear on the index page.

In this step, you have added the ability to create new to-do items and save them to the database.

You can find the source code for this project in [this repository](https://github.com/do-community/flask-todo).

Conclusion
----------

You now have an application to manage to-do lists and items. Each list has several to-do items and each to-do item belongs to a single list in a one-to-many relationship. You learned how to use Flask and SQLite to manage multiple related database tables, how to use _foreign keys_ and how to retrieve and display related data from two tables in a web application using SQLite joins.

Furthermore, you grouped results using the `groupby()` function, inserted new data to the database, and associated database table rows with the tables they are related to. You can learn more about foreign keys and database relationships from the [SQLite documentation](https://www.sqlite.org/foreignkeys.html).

You can also read more of our [Python Framework content](https://www.digitalocean.com/community/tags/python-frameworks). If you want to check out the `sqlite3` Python module, read our tutorial on [How To Use the sqlite3 Module in Python 3](https://www.digitalocean.com/community/tutorials/how-to-use-the-sqlite3-module-in-python-3).
