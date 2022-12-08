### Backend Project 3

| Group 6         |
| --------------- |
| Himani Tawade   |
| Satish Bisa     |
| Nick Vasquez    |

##### HOW TO RUN THE PROJECT

1. Copy the contents of our [nginx config file](https://github.com/himanitawade/Web-Backend-Project3/blob/master/nginxconfig.txt) into a new file within `/etc/nginx/sites-enabled` called `nginxconfig`. Assuming the nginx service is already running, restart the service using `sudo service nginx restart`.

Nginx Config:

```
server {
    listen 80;
    listen [::]:80;

    server_name tuffix-vm;

    location /registration {
        proxy_pass http://127.0.0.1:5000/registration;
    }

    location /newgame {
        auth_request /auth;
        proxy_pass http://gameservice;
    }

    location /addguess {
            auth_request /auth;
            proxy_pass http://gameservice;
    }

    location /allgames {
            auth_request /auth;
            proxy_pass http://gameservice;
    }

    location /onegame {
        auth_request /auth;
        proxy_pass http://gameservice;
    }


    location = /auth {
           internal;
           proxy_pass http://127.0.0.1:5000/login;
    }

}

upstream gameservice {
    server 127.0.0.1:5200;
    server 127.0.0.1:5300;
    server 127.0.0.1:5400;
}
```

1. Initialize primary, secondary1, and secondary2 directories properly incase the folders are not present

 ```c
      In the var folder...
       
        - add a folder "primary", with folders "data" and "mount" inside of it.
        - add a folder "secondary1" folder with "data" and "mount" inside of it.
        - add a folder "secondary2" folder with "data" and "mount" inside of it.
   ```



2. Start the API (from project folder)

   - foreman start
      // NOTE: if there's an error upon running this where it doesn't recognize hypercorn, log out of Ubuntu and log back in.                  If there is an error regarding ./bin/litefs specifically run "chmod +x ./bin/litefs" first, then retry "foreman start".
      
      After the foreman start is done you will see five instances running user, leader, 3 games names as(primary,secondary1,secondary2)
   
  ```c
      16:53:01 leader.1     | [2022-12-02 16:53:01 -0800] [3425] [INFO] Running on http://127.0.0.1:5100 (CTRL + C to quit)
      16:53:01 user.1       | [2022-12-02 16:53:01 -0800] [3427] [INFO] Running on http://127.0.0.1:5000 (CTRL + C to quit)
      16:53:05 primary.1    | starting subprocess: hypercorn [game --reload --debug --bind game.local.gd:5200 --access-logfile - --error-logfile - --log-level DEBUG]
      16:53:05 secondary2.1 | starting subprocess: hypercorn [game --reload --debug --bind game.local.gd:5400 --access-logfile - --error-logfile - --log-level DEBUG]
      16:53:05 secondary1.1 | starting subprocess: hypercorn [game --reload --debug --bind game.local.gd:5300 --access-logfile - --error-logfile - --log-level DEBUG]
      16:53:06 primary.1    | [2022-12-02 16:53:06 -0800] [3437] [INFO] Running on http://127.0.0.1:5200 (CTRL + C to quit)
      16:53:06 secondary1.1 | [2022-12-02 16:53:06 -0800] [3441] [INFO] Running on http://127.0.0.1:5300 (CTRL + C to quit)
      16:53:06 secondary2.1 | [2022-12-02 16:53:06 -0800] [3439] [INFO] Running on http://127.0.0.1:5400 (CTRL + C to quit)


      
   ```

3. Initialize the databases/database replicas within the var folder (from project folder)

   ```c
      // step 1. give the script permissions to execute
      chmod +x ./bin/init.sh

      // step 2. run the script
      ./bin/init.sh
   ```

4. Populate the word databases

   ```c
      python3 dbpop.py
   ```

5. Test all the endpoints using httpie
   - user
      - register account: `http POST http://tuffix-vm/registration username="yourusername" password="yourpassword"`
    
       Sample Output:
       ```
      {
         "id": 3,
         "password": "tawade",
         "username": "himani"
      }
      ```
     - login {Not accesible}: 'http --auth himani:tawade GET http://tuffix-vm/login'
     Sample Output:
     ```
      HTTP/1.1 404 Not Found
      Connection: keep-alive
      Content-Encoding: gzip
      Content-Type: text/html
      Date: Fri, 18 Nov 2022 21:04:31 GMT
      Server: nginx/1.18.0 (Ubuntu)
      Transfer-Encoding: chunked

      <html>
      <head><title>404 Not Found</title></head>
      <body>
      <center><h1>404 Not Found</h1></center>
      <hr><center>nginx/1.18.0 (Ubuntu)</center>
      </body>
      </html>
      ```
   - game

      NOTE:
        - all functions which WRITE to db are written specifically to the PRIMARY database connection.
        - all functions which READ to db are read specifically from either one of the 3 database connections:
            - PRIMARY
            - SECONDARY1
            - SECONDARY2
          
          *** this is handled by randomly (using random.choice()) selecting a DB connection from a list of them whenever a GET method is called. When executing a GET method, you can see in the terminal the addresses of all the DB connections, and the address of the specific DB that ends up being used for the actual read. This is how we handled the Read Distribution Functionality. 

      - create a new game: `http --auth yourusername:yourpassword POST http://tuffix-vm/newgame`
      
      Sample Output:
      ```
      'http --auth himani:tawade POST http://tuffix-vm/newgame'
      {
         "answerid": 3912,
         "gameid": "b0039f36-6784-11ed-ba4a-615e339a8400",
         "username": "himani"
      }
      ```
      Note - this will return a `gameid`
    - add a guess: `http --auth yourusername:yourpassword PUT http://tuffix-vm/addguess gameid="gameid" word="yourguess"`

    Sample Output:
    ```
      http --auth himani:tawade PUT http://tuffix-vm/addguess gameid="b0039f36-6784-11ed-ba4a-615e339a8400" word="amigo"
     {
        "Accuracy": "XXOOO",
        "guessedWord": "amigo"
     }
     ```
    - display your active games: `http --auth yourusername:yourpassword GET http://tuffix-vm/allgames`

    Sample Output:
    ```
      http --auth himani:tawade GET http://tuffix-vm/allgames
      [
         {
            "gameid": "b0039f36-6784-11ed-ba4a-615e339a8400",
            "gstate": "In-progress",
            "guesses": 1
         }
      ]
      ```
    - display the game status and stats for one game: `http --auth yourusername:yourpassword GET http://tuffix-vm/onegame?id=gameid`
       - example: `.../onegame?id=b97fcbb0-6717-11ed-8689-e9ba279d21b6`
    Sample Output:
    ```
      http --auth himani:tawade GET http://tuffix-vm/onegame?id="b0039f36-6784-11ed-ba4a-615e339a8400"
      [
         {
             "gameid": "b0039f36-6784-11ed-ba4a-615e339a8400",
            "gstate": "In-progress",
            "guesses": 1
          },
          {
             "accuracy": "XXOOO",
             "guessedword": "amigo"
          }
      ]
      ```
     - leader:  Use http://leader.local.gd:5100/docs to access the end points
     
     - results
     - 
         This endpoint is accesible to the people who are registered and will be authenticated with their registeration details
         They can post the result of a game and the number of guesses they made to acheive that finished game result.
         The results end point have two values which will be accepted when you login with a registered user.
     
     ```c
         guesses: accepted value [1 - 6] else an error will be given
         result: ["Win" or "Loss"]
      ```
      
      
         This will generate an output with an average score if you have played multiple games else a new user will be given
         a score according to the number of guesses used to win or 0 if a loss with 6 guesses is given.
         
          Sample Output:
          
    ```
          {
          "username": "mac",
          "averageScore": "6.0",
          "result": "Win",
          "guesses": "1",
          "score": "12",
          "gamecount": "2"
          }
         
    ```
    - Note: averageScore will be used to calculate the top 10 players
    
    - top10scores
    
      This endpoint will list the top 10 players and will give a leader board. This endpoint requires no authentication and will be accesible to everyone
    
       Sample Output:
    ```
          {
          ('len', 6.0)
          ('gen', 6.0)
          ('mac', 5.666666666666667)
          ('jim', 5.0)
          ('himani', 5.0)
          ('ten', 4.0)
          ('ken', 3.0)
          ('fen', 3.0)
          ('den', 1.0)
          ('men', 0.0)
          }
         
    ```
    
         
         
