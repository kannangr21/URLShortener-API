# URL-Shortener FastAPI

This is an API developed using Python's [FastAPI](https://fastapi.tiangolo.com/) framework.

## Prerequisites

- Python 3.5 or above
- Any Browser or Postman for testing the API
- SQL Database
- Git to clone the repo.

## Installation

- Clone the repository  
    -> Run `git clone https://github.com/kannangr21/URLShortener-API` in the terminal.
- Create a virtual environment if needed. 
- Move to the directory and in the terminal, run the command `pip install -r requirements.txt` to install the dependancies.
- After installation, Configure `JWT_SECRET` in `main.py/line 29` and run the command `uvicorn main:app --reload`
- Check http://127.0.0.1:8000/ to check the status of the server.

## Testing

- In the hyperlink http://127.0.0.1:8000/docs, the API documentation with all the endpoints can be tested.
- Or, using Postman all the endpoints can be tested manually.

### To test the short URL

- The `/{shortCode}` endpoint can't be tested either in docs or postman.
- To test this endpoint, manually open a tab and enter the hyperlink http://127.0.0.1:8000/{shortCode} which redirects to the original link.

## Features

1. OAuth2 Authentication.
2. Customization of short code.
3. QR Code for shortUrl which will be returned as base64 string.
4. User profile updation.

## Troubleshooting

For any inconvenience in the API, raise an issue [here](https://github.com/kannangr21/URLShortener-API/issues/new).