import pytest

from flask import session


def test_register(client):
    # Check that we retrieve the register page.
    response_code = client.get('/authentication/register').status_code
    assert response_code == 200

    # Check that we can register a user successfully, supplying a valid username and password.
    response = client.post(
        '/authentication/register',
        data={'username': 'gmichael', 'password': 'CarelessWhisper1984'}
    )
    assert response.headers['Location'] == 'http://localhost/authentication/login'


@pytest.mark.parametrize(('username', 'password', 'message'), (
        ('', '', b'Your username is required'),
        ('cj', '', b'Your username is too short'),
        ('test', '', b'Your password is required'),

        ('fmercury', 'Test#6^0', b'Your username is already taken - please supply another'),
))
def test_register_with_invalid_input(client, username, password, message):
    # Check that attempting to register with invalid combinations of username and password generate appropriate error
    # messages.
    response = client.post(
        '/authentication/register',
        data={'username': username, 'password': password}
    )
    assert message in response.data


def test_login(client, auth):
    # Check that we can retrieve the login page.
    status_code = client.get('/authentication/login').status_code
    assert status_code == 200

    # Check that a successful login generates a redirect to the homepage.
    response = auth.login()
    assert response.headers['Location'] == 'http://localhost/'

    # Check that a session has been created for the logged-in user.
    with client:
        client.get('/')
        assert session['username'] == 'thorke'


def test_logout(client, auth):
    # Login a user.
    auth.login()

    with client:
        # Check that logging out clears the user's session.
        auth.logout()
        assert 'user_id' not in session


def test_index(client):
    # Check that we can retrieve the home page.
    response = client.get('/')
    assert response.status_code == 200



def test_login_required_to_review(client):
    response = client.post('/review')
    assert response.headers['Location'] == 'http://localhost/authentication/login'


def test_review(client, auth):
    # Login a user.
    auth.login()

    # Check that we can retrieve the review page.
    response = client.get('/review?movie=2')

    response = client.post(
        '/review',
        data={'review': 'Whello', 'movie_id': 2}
    )
    assert response.headers['Location'] == 'http://localhost/movies_by_date?date=2012-01-01&view_reviews_for=2'


@pytest.mark.parametrize(('review', 'messages'), (
        ('Who thinks Trump is a fuckwit?', (b'Your review must not contain profanity')),
        ('Hey', (b'Your review is too short')),
        ('ass', (b'Your review is too short', b'Your review must not contain profanity')),
))
def test_review_with_invalid_input(client, auth, review, messages):
    # Login a user.
    auth.login()

    # Attempt to review on an movie.
    response = client.post(
        '/review',
        data={'review': review, 'movie_id': 2}
    )
    # Check that supplying invalid review text generates appropriate error messages.
    for message in messages:
        assert message in response.data


def test_movies_without_date(client):
    # Check that we can retrieve the movies page.
    response = client.get('/movies_by_date')
    assert response.status_code == 200

    # Check that without providing a date query parameter the page includes the first movie.
    assert b'head' in response.data
    assert b'head' in response.data


def test_movies_with_date(client):
    # Check that we can retrieve the movies page.
    response = client.get('/movies_by_date?date=2020-02-29')
    assert response.status_code == 302



def test_movies_with_review(client):
    # Check that we can retrieve the movies page.
    response = client.get('/movies_by_date?date=2020-02-28&view_reviews_for=1')
    assert response.status_code == 302



def test_movies_with_genre(client):
    # Check that we can retrieve the movies page.
    response = client.get('/movies_by_genre?genre=Health')
    assert response.status_code == 200

