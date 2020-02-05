# File storage App

Application built for „Programming web and mobile applications”. 

# Technology:

- Python 3.7
- Javascript
- HTML5
- Flask
- Docker-compose
- Redis

# Description:

Application may be used as a cloud for user's files or a hosting.

- web - web client module (receives users files and sends to cdn)
- cdn - REST module (stores files in /tmp/ directory and makes responses for web requests)
- database (stores data about users login)

# Running an application

To run it, just go to the main directory and type:

    docker-compose -f docker-compose.yml up --build

Then, edit your etc/hosts and add:
    
    127.0.0.1 web.company.com
    127.0.0.1 cdn.company.com
    
After that, open your browser and move to "web.company.com".
