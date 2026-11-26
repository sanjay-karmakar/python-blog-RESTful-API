import os
from dotenv import load_dotenv
from datetime import date

from flask import Flask, render_template, redirect, url_for, request
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired
from flask_bootstrap import Bootstrap5
from flask_ckeditor import CKEditor, CKEditorField

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, Float, String, Text

'''
Make sure the required packages are installed: 
Open the Terminal in PyCharm (bottom left). 

On Windows type:
python -m pip install -r requirements.txt

On MacOS type:
pip3 install -r requirements.txt

This will install the packages from the requirements.txt for this project.
'''

load_dotenv()

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")
Bootstrap5(app)

# 2. Initialize CKEditor on your Flask app
ckeditor = CKEditor(app)


class Base(DeclarativeBase):
	pass


DB_HOST = os.environ.get("DB_HOST")
DB_USER = os.environ.get("DB_USER")
DB_PASS = os.environ.get("DB_PASSWORD", "")
DB_NAME = os.environ.get("DB_NAME")

app.config['SQLALCHEMY_DATABASE_URI'] = (
	f"mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}/{DB_NAME}"
)
db = SQLAlchemy(model_class=Base)
db.init_app(app)


# CONFIGURE TABLE
class BlogPost(db.Model):
	__tablename__ = "posts"
	id: Mapped[int] = mapped_column(Integer, primary_key=True)
	title: Mapped[str] = mapped_column(String(250), nullable=False)
	subtitle: Mapped[str] = mapped_column(String(250), nullable=False)
	date: Mapped[str] = mapped_column(String(250), nullable=False)
	body: Mapped[str] = mapped_column(Text, nullable=False)
	author: Mapped[str] = mapped_column(String(250), nullable=False)
	img_url: Mapped[str] = mapped_column(String(250), nullable=False)


with app.app_context():
	db.create_all()


@app.route('/')
def get_all_posts():
	# TODO: Query the database for all the posts. Convert the data to a python list.
	result = db.session.execute(db.select(BlogPost).order_by(BlogPost.date))
	posts = result.scalars().all()

	return render_template("index.html", all_posts=posts)


# TODO: Add a route so that you can click on individual posts.
@app.route('/post/<int:post_id>')
def show_post(post_id):
	# TODO: Retrieve a BlogPost from the database based on the post_id
	requested_post = db.get_or_404(BlogPost, post_id)
	return render_template("post.html", post=requested_post)


# TODO: Creation of FORM
class PostForm(FlaskForm):
	title = StringField(label="Blog Post Title", validators=[DataRequired()])
	subtitle = StringField(label="Subtitle", validators=[DataRequired()])
	date = StringField(label="Date", validators=[DataRequired()])
	body = CKEditorField(label="Blog Content", validators=[DataRequired()])
	author = StringField(label="Author", validators=[DataRequired()])
	img_url = StringField(label="Blog Image URL", validators=[DataRequired()])
	submit = SubmitField(label="Submit")

# TODO: add_new_post() to create a new blog post
@app.route('/new-post', methods=['GET','POST'])
def add_new_post():
	add_new_post_form = PostForm()

	if add_new_post_form.validate_on_submit():
		new_post = BlogPost(
			title=add_new_post_form.title.data,
			subtitle=add_new_post_form.subtitle.data,
			date=add_new_post_form.date.data,
			body=add_new_post_form.body.data,
			author=add_new_post_form.author.data,
			img_url=add_new_post_form.img_url.data,
		)
		db.session.add(new_post)
		db.session.commit()

		return redirect(url_for("get_all_posts"))

	return render_template("make-post.html", form=add_new_post_form, is_edit=False)

# TODO: edit_post() to change an existing blog post
@app.route('/edit-post/<int:post_id>')
def edit_post(post_id):
	post_data = db.get_or_404(BlogPost, post_id)
	edit_post_form = PostForm(obj=post_data)

	return render_template("make-post.html", form=edit_post_form, post=post_data, is_edit=True)

# TODO: delete_post() to remove a blog post from the database

# Below is the code from previous lessons. No changes needed.
@app.route("/about")
def about():
	return render_template("about.html")


@app.route("/contact")
def contact():
	return render_template("contact.html")


if __name__ == "__main__":
	app.run(debug=True)
