# MyNotesAPI

MyNotesAPI is an API interface for a mobile app I am developing. My school doesn't have an app to view your grades and
if you want to do that anyway, you have to discuss for an awfully long time. So I thought I'd write an app that allows
you to view all of your grades directly and thus your grade point average.

# Endpoints

MyNotes is only a small project, so it doesn't need that many endpoints.
Here is a list of all endpoints:

## /register

This endpoint is used to register a new user. It requires a username and a password.

### Parameters:

- <strong>username</strong>: The username of the user in plaintext
- <strong>password</strong>: The password of the user in base64 encoded

### Returns:

JSON object with the following parameters:

- <strong>status</strong>: The status of the request. 200 if successful, 500 if not (500 is also returned if the client
  made a mistake)
- <strong>error</strong>: Boolean value indicating if an error occured
- <strong>access_token</strong>: The access token of the user. This is used to authenticate the user for other endpoints
- <strong>refresh_token</strong>: The refresh token of the user. This is used to refresh the access token
- <strong>expires_at</strong>: The time at which the access token expires (in seconds since epoch)
- <strong>user_id</strong>: The ID of the user

## /login

This endpoint is used to log in a user. It requires a username and a password.

### Parameters:

- <strong>username</strong>: The username of the user in plaintext
- <strong>password</strong>: The password of the user <strong>hashed with SHA512</strong>

### Returns:

JSON object with the following parameters:

- <strong>status</strong>: The status of the request. 200 if successful, 500 if not (500 is also returned if the client
  made a mistake)
- <strong>error</strong>: Boolean value indicating if an error occured
- <strong>access_token</strong>: The access token of the user. This is used to authenticate the user for other endpoints
- <strong>refresh_token</strong>: The refresh token of the user. This is used to refresh the access token
- <strong>expires_at</strong>: The time at which the access token expires (in seconds since epoch)
- <strong>user_id</strong>: The ID of the user

## /refresh_token

This endpoint is used to refresh the access token of a user. It requires a refresh token and a user ID.

### Parameters:

- <strong>refresh_token</strong>: The refresh token of the user
- <strong>user_id</strong>: The ID of the user

### Returns:

JSON object with the following parameters:

- <strong>status</strong>: The status of the request. 200 if successful, 500 if not (500 is also returned if the client
  made a mistake)
- <strong>error</strong>: Boolean value indicating if an error occured
- <strong>access_token</strong>: The access token of the user. This is used to authenticate the user for other endpoints
- <strong>expires_at</strong>: The time at which the access token expires (in seconds since epoch)
- <strong>user_id</strong>: The ID of the user

### /get_subjects

This endpoint is used to get all subjects of a user. It requires an access token and a user ID.

### Parameters:

- <strong>access_token</strong>: The access token of the user
- <strong>user_id</strong>: The ID of the user

### Returns:

JSON object with the following parameters:

- <strong>status</strong>: The status of the request. 200 if successful, 500 if not (500 is also returned if the client
  made a mistake)
- <strong>error</strong>: Boolean value indicating if an error occured
- <strong>subjects</strong>: Array of all subjects of the user. Each subject is a JSON object with the following
  parameters:
    - <strong>name</strong>: The name of the subject
    - <strong>note_count</strong>: The number of notes in the subject
    - <strong>gpa</strong>: The grade point average of the subject

### /get_subject

This endpoint is used to get a specific subject of a user. It requires an access token, a user ID and a subject name.

### Parameters:

- <strong>access_token</strong>: The access token of the user
- <strong>user_id</strong>: The ID of the user
- <strong>subject</strong>: The name of the subject (case-sensitive)

### Returns:

JSON object with the following parameters:

- <strong>status</strong>: The status of the request. 200 if successful, 500 if not (500 is also returned if the client
  made a mistake)
- <strong>error</strong>: Boolean value indicating if an error occured
- <strong>subject</strong>: JSON object with the following parameters:
    - <strong>name</strong>: The name of the subject
    - <strong>note_count</strong>: The number of notes in the subject
    - <strong>gpa</strong>: The grade point average of the subject
- <strong>notes</strong>: Array of all notes in the subject. Each note is a JSON object with the following parameters:
    - <strong>id</strong>: The ID of the note
    - <strong>subject</strong>: The name of the subject
    - <strong>note</strong>: The note
    - <strong>weight</strong>: The weight of the note
    - <strong>release_date</strong>: The date on which the note was released from the teacher
    - <strong>created_at</strong>: The date on which the note was created in the app

### /add_note

This endpoint is used to add a note into the database. It requires an access token, a user ID, a subject name, a note,
a weight and a release date.

### Parameters:

- <strong>access_token</strong>: The access token of the user
- <strong>user_id</strong>: The ID of the user
- <strong>subject</strong>: The name of the subject (case-sensitive)
- <strong>note</strong>: The note
- <strong>weight</strong>: The weight of the note
- <strong>user_id</strong>: The ID of the user
- <strong>release_date</strong>: The date on which the note was released from the teacher

### Returns:

JSON object with the following parameters:

- <strong>status</strong>: The status of the request. 200 if successful, 500 if not (500 is also returned if the client
  made a mistake)
- <strong>error</strong>: Boolean value indicating if an error occured
- <strong>note_id</strong>: The ID of the note

### /get_note

This endpoint is used to get a specific note of a user. It requires an access token, a user ID and a note ID.

### Parameters:

- <strong>access_token</strong>: The access token of the user
- <strong>user_id</strong>: The ID of the user
- <strong>note_id</strong>: The ID of the note

### Returns:

JSON object with the following parameters:

- <strong>status</strong>: The status of the request. 200 if successful, 500 if not (500 is also returned if the client
  made a mistake)
- <strong>error</strong>: Boolean value indicating if an error occured
- <strong>note</strong>: JSON object with the following parameters:
    - <strong>id</strong>: The ID of the note
    - <strong>subject</strong>: The name of the subject
    - <strong>note</strong>: The note
    - <strong>weight</strong>: The weight of the note
    - <strong>user_id</strong>: The ID of the user
    - <strong>release_date</strong>: The date on which the note was released from the teacher
    - <strong>created_at</strong>: The date on which the note was created in the app