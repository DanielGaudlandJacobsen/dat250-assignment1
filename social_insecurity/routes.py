# social_insecurity/routes.py

from flask import (
    flash,
    redirect,
    render_template,
    url_for,
    send_from_directory,
    request,  
)
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from flask import current_app as app
from social_insecurity import sqlite
from social_insecurity.forms import (
    CommentsForm,
    FriendsForm,
    IndexForm,
    PostForm,
    ProfileForm,
)
from social_insecurity.models import User
from werkzeug.utils import secure_filename
from pathlib import Path
from werkzeug.exceptions import abort  # Imported 'abort' for error handling
from mimetypes import guess_type  # Imported for MIME type checking
from wtforms import HiddenField, SubmitField
from flask_wtf import FlaskForm
from flask_wtf.csrf import CSRFProtect
from wtforms.validators import DataRequired
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}  # Defined allowed file extensions

class RequestForm(FlaskForm):
    request_id = HiddenField(validators=[DataRequired()])
    action = HiddenField(validators=[DataRequired()])
    


@app.route("/handle_friend_request", methods=["POST"])
@login_required
def handle_friend_request():
    form = RequestForm()
    if form.validate_on_submit():
        request_id = form.request_id.data
        action = form.action.data
        print(f"Received request_id: {request_id}, action: {action}")

        # Fetch the specific friend request
        get_friend_request = """
          SELECT * FROM FriendRequests
          WHERE id = ? AND to_user_id = ?;
        """
        friend_request = sqlite.query(get_friend_request, (request_id, current_user.id), one=True)

        if not friend_request:
            flash("Invalid friend request.", category="danger")
            return redirect(url_for("friends"))

        if action == "accept":
            # Add the friendship in both directions
            insert_friend = """
              INSERT INTO Friends (u_id, f_id) VALUES (?, ?);
            """
            sqlite.query(insert_friend, (current_user.id, friend_request["from_user_id"]))
            sqlite.query(insert_friend, (friend_request["from_user_id"], current_user.id))
            flash("Friend request accepted!", category="success")
        elif action == "decline":
            flash("Friend request declined.", category="info")
        else:
            flash("Unknown action.", category="danger")
            return redirect(url_for("friends"))

        # Delete the friend request
        delete_request = "DELETE FROM FriendRequests WHERE id = ?;"
        sqlite.query(delete_request, (request_id,))
    else:
        print("Form did not validate")
        print(f"Form data: {request.form}")
        print(f"Form errors: {form.errors}")
        flash("Invalid form submission.", category="danger")
    return redirect(url_for("friends"))

def allowed_file(filename):
    """Check if the file has an allowed extension."""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/", methods=["GET", "POST"])
@app.route("/index", methods=["GET", "POST"])
def index():
    if current_user.is_authenticated:
        return redirect(url_for("stream"))

    form = IndexForm()
    login_form = form.login
    register_form = form.register

    if login_form.validate_on_submit() and login_form.submit.data:
        user = sqlite.get_user_by_username(login_form.username.data)

        if user:
            stored_password_hash = user["password"]
            if stored_password_hash:
                try:
                    if check_password_hash(stored_password_hash, login_form.password.data):
                        user_obj = User(
                            id=user["id"], username=user["username"], password=stored_password_hash
                        )
                        login_user(user_obj, remember=login_form.remember_me.data)
                        flash("Logged in successfully.", category="success")
                        return redirect(url_for("stream"))
                    else:
                        flash("Invalid username or password.", category="danger")
                except ValueError as e:
                    flash("An error occurred while verifying your password.", category="danger")
                    # Optionally log the error e
            else:
                flash("Password not set for this user.", category="danger")
        else:
            flash("Invalid username or password.", category="danger")

    elif register_form.validate_on_submit() and register_form.submit.data:
        hashed_pwd = generate_password_hash(register_form.password.data)
        insert_user = """
            INSERT INTO Users (username, first_name, last_name, password)
            VALUES (?, ?, ?, ?);
            """
        sqlite.query(
            insert_user,
            (
                register_form.username.data,
                register_form.first_name.data,
                register_form.last_name.data,
                hashed_pwd,
            ),
        )
        flash("User successfully created!", category="success")
        return redirect(url_for("index"))

    return render_template("index.html.j2", title="Welcome", form=form)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", category="success")
    return redirect(url_for("index"))  # Ensure this line is reached

  # Optional safeguard return statement
    #return redirect(url_for("index"))  


@app.route("/stream", methods=["GET", "POST"])
@login_required
def stream():
    form = PostForm()

    if form.validate_on_submit():
        filename = None
        if form.image.data:
            filename = secure_filename(form.image.data.filename)
            if not allowed_file(filename):  # Validate file extension
                flash("File type not allowed.", category="danger")
                return redirect(url_for("stream"))
            # Save the file
            upload_folder = Path(app.instance_path) / app.config["UPLOADS_FOLDER_PATH"]
            upload_folder.mkdir(parents=True, exist_ok=True)  # Ensure the upload directory exists
            path = upload_folder / filename
            form.image.data.save(path)
        insert_post = """
          INSERT INTO Posts (u_id, content, image, creation_time)
          VALUES (?, ?, ?, CURRENT_TIMESTAMP);
      """
        sqlite.query(insert_post, (current_user.id, form.content.data, filename))
        flash("Post successfully created!", category="success")
        return redirect(url_for("stream"))

    get_posts = """
        SELECT p.id, p.content, p.image, p.creation_time, 
                u.username,
                (SELECT COUNT(*) FROM Comments WHERE p_id = p.id) AS comment_count
        FROM Posts AS p 
        JOIN Users AS u ON u.id = p.u_id
        WHERE p.u_id IN (
            SELECT f_id FROM Friends WHERE u_id = ?
        ) 
        OR p.u_id = ?
        ORDER BY p.creation_time DESC;
    """
    posts = sqlite.query(get_posts, (current_user.id, current_user.id))
    return render_template("stream.html.j2", title="Stream", form=form, posts=posts)


@app.route("/comments/<string:username>/<int:post_id>", methods=["GET", "POST"])
@login_required
def comments(username: str, post_id: int):
    comments_form = CommentsForm()
    user = sqlite.get_user_by_username(username)

    if not user:
        abort(404)  # Added error handling if user does not exist

    if comments_form.validate_on_submit():
        insert_comment = """
          INSERT INTO Comments (p_id, u_id, comment, creation_time)
          VALUES (?, ?, ?, CURRENT_TIMESTAMP);
      """
        sqlite.query(insert_comment, (post_id, current_user.id, comments_form.comment.data))
        flash("Comment successfully added!", category="success")
        return redirect(url_for("comments", username=username, post_id=post_id))

    get_post = "SELECT * FROM Posts JOIN Users ON Posts.u_id = Users.id WHERE Posts.id = ?;"
    get_comments = """
      SELECT Comments.*, Users.username
      FROM Comments
      JOIN Users ON Comments.u_id = Users.id
      WHERE Comments.p_id = ?
      ORDER BY Comments.creation_time DESC;
  """
    post = sqlite.query(get_post, (post_id,), one=True)
    comments = sqlite.query(get_comments, (post_id,))

    if not post:
        abort(404)  # Added error handling if post does not exist

    return render_template(
        "comments.html.j2", title="Comments", username=username, form=comments_form, post=post, comments=comments
    )


@app.route("/friends", methods=["GET", "POST"])
@login_required
def friends():
    friends_form = FriendsForm()
    request_form = RequestForm()

    if friends_form.validate_on_submit():
        friend_username = friends_form.username.data
        friend = sqlite.get_user_by_username(friend_username)

        if friend is None:
            flash("User does not exist!", category="warning")
        elif friend["id"] == current_user.id:
            flash("You cannot send a friend request to yourself!", category="warning")
        else:
            # Check if a friend request already exists
            existing_request = sqlite.query(
                "SELECT * FROM FriendRequests WHERE from_user_id = ? AND to_user_id = ?;",
                (current_user.id, friend["id"]),
                one=True,
            )
            if existing_request:
                flash("Friend request already sent!", category="warning")
            else:
                # Create a new friend request
                insert_request = """
                  INSERT INTO FriendRequests (from_user_id, to_user_id)
                  VALUES (?, ?);
              """
                sqlite.query(insert_request, (current_user.id, friend["id"]))
                flash("Friend request sent!", category="success")
                print(f"Friend request sent from user {current_user.id} to user {friend['id']}")

    # Get list of current friends
    get_friends = """
      SELECT Users.*
      FROM Friends
      JOIN Users ON Friends.f_id = Users.id
      WHERE Friends.u_id = ?;
  """
    friends = sqlite.query(get_friends, (current_user.id,))

    # Get incoming friend requests
    get_friend_requests = """
      SELECT FriendRequests.*, Users.username
      FROM FriendRequests
      JOIN Users ON FriendRequests.from_user_id = Users.id
      WHERE FriendRequests.to_user_id = ?;
  """
    friend_requests = sqlite.query(get_friend_requests, (current_user.id,))
    print(f"Friend requests for user {current_user.id}: {friend_requests}")

    return render_template(
        "friends.html.j2",
        title="Friends",
        friends=friends,
        form=friends_form,
        friend_requests=friend_requests,
        request_form=request_form,
    )

@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    profile_form = ProfileForm()

    if profile_form.validate_on_submit():
        update_profile = """
          UPDATE Users
          SET education = ?, employment = ?,
              music = ?, movie = ?,
              nationality = ?, birthday = ?
          WHERE id = ?;
      """
        sqlite.query(
            update_profile,
            (
                profile_form.education.data,
                profile_form.employment.data,
                profile_form.music.data,
                profile_form.movie.data,
                profile_form.nationality.data,
                profile_form.birthday.data,
                current_user.id,
            ),
        )
        flash("Profile successfully updated!", category="success")
        return redirect(url_for("profile"))

    get_user = sqlite.get_user_by_id(current_user.id)
    return render_template(
        "profile.html.j2", title="Profile", user=get_user, form=profile_form, username=current_user.username
    )


@app.route("/uploads/<path:filename>")
def uploads(filename):
    """Serve uploaded files securely."""
    uploads_folder = Path(app.instance_path) / app.config["UPLOADS_FOLDER_PATH"]
    full_path = uploads_folder / filename
    if uploads_folder not in full_path.parents:
        abort(403)  # Prevent directory traversal attacks
    if not full_path.exists():
        abort(404)
    mime_type, _ = guess_type(str(full_path))
    if not mime_type or not mime_type.startswith("image/"):
        abort(403)
    return send_from_directory(uploads_folder, filename)
