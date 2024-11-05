"""Provides all forms used in the Social Insecurity application.

This file is used to define all forms used in the application.
It is imported by the social_insecurity package.

Example:
    from flask import Flask
    from app.forms import LoginForm

    app = Flask(__name__)

    # Use the form
    form = LoginForm()
    if login_form.validate_on_submit() and login_form.login.submit.data:
        username = form.username.data
"""

from datetime import datetime
from typing import cast

from flask_wtf import FlaskForm
from wtforms import (
    BooleanField,
    DateField,
    FileField,
    FormField,
    PasswordField,
    StringField,
    SubmitField,
    TextAreaField,
)
from wtforms.validators import (
    DataRequired,
    EqualTo,
    Length,
    ValidationError,
)
import bleach

# Defines all forms in the application, these will be instantiated by the template,
# and the routes.py will read the values of the fields

# Custom validator to sanitize input
def sanitize_input(form, field):
    # Clean the input data by stripping disallowed tags and attributes
    field.data = bleach.clean(
        field.data,
        tags=[],  # Disallow all tags
        attributes={},  # Disallow all attributes
        strip=True  # Remove disallowed tags completely
    )

class LoginForm(FlaskForm):
    """Provides the login form for the application."""

    username = StringField(
        label="Username",
        render_kw={"placeholder": "Username"},
        validators=[DataRequired(), Length(min=3, max=25), sanitize_input]
    )
    password = PasswordField(
        label="Password",
        render_kw={"placeholder": "Password"},
        validators=[DataRequired(), Length(min=6, max=100), sanitize_input]
    )
    remember_me = BooleanField(
        label="Remember me"
    )  # TODO: It would be nice to have this feature implemented, probably by using cookies
    submit = SubmitField(label="Sign In")


class RegisterForm(FlaskForm):
    """Provides the registration form for the application."""

    first_name = StringField(
        label="First Name",
        render_kw={"placeholder": "First Name"},
        validators=[sanitize_input]
    )
    last_name = StringField(
        label="Last Name",
        render_kw={"placeholder": "Last Name"},
        validators=[sanitize_input]
    )
    username = StringField(
        label="Username",
        render_kw={"placeholder": "Username"},
        validators=[DataRequired(), Length(min=3, max=25), sanitize_input]
    )
    password = PasswordField(
        label="Password",
        render_kw={"placeholder": "Password"},
        validators=[DataRequired(), Length(min=6, max=100), sanitize_input]
    )
    confirm_password = PasswordField(
        label="Confirm Password",
        render_kw={"placeholder": "Confirm Password"},
        validators=[DataRequired(), EqualTo("password", message="Passwords must match"), sanitize_input],
    )
    submit = SubmitField(label="Sign Up")


class IndexForm(FlaskForm):
    """Provides the composite form for the index page."""

    login = cast(LoginForm, FormField(LoginForm))
    register = cast(RegisterForm, FormField(RegisterForm))


class PostForm(FlaskForm):
    """Provides the post form for the application."""

    content = TextAreaField(
        label="New Post",
        render_kw={"placeholder": "What are you thinking about?"},
        validators=[DataRequired(), Length(max=500), sanitize_input],
    )
    image = FileField(label="Image")
    submit = SubmitField(label="Post")


class CommentsForm(FlaskForm):
    """Provides the comment form for the application."""

    comment = TextAreaField(
        label="New Comment",
        render_kw={"placeholder": "What do you have to say?"},
        validators=[DataRequired(), Length(max=300), sanitize_input],
    )
    submit = SubmitField(label="Comment")


class FriendsForm(FlaskForm):
    """Provides the friend form for the application."""

    username = StringField("Username", validators=[DataRequired(), sanitize_input])
    submit = SubmitField("Add Friend")


class ProfileForm(FlaskForm):
    """Provides the profile form for the application."""

    education = StringField(
        label="Education",
        render_kw={"placeholder": "Highest education"},
        validators=[sanitize_input]
    )
    employment = StringField(
        label="Employment",
        render_kw={"placeholder": "Current employment"},
        validators=[sanitize_input]
    )
    music = StringField(
        label="Favorite song",
        render_kw={"placeholder": "Favorite song"},
        validators=[sanitize_input]
    )
    movie = StringField(
        label="Favorite movie",
        render_kw={"placeholder": "Favorite movie"},
        validators=[sanitize_input]
    )
    nationality = StringField(
        label="Nationality",
        render_kw={"placeholder": "Your nationality"},
        validators=[sanitize_input]
    )
    birthday = DateField(label="Birthday", default=datetime.now())
    submit = SubmitField(label="Update Profile")