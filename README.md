# Simple local PC API for a Windows Host machine

## How to use

- define your own `ACCESS_TOKEN` inside an .env
- install code locally as a service (e.g. using NSSM)
- connect to same wifi as host machine
- Make a GET-Request to the following URL: <br>
  `<host-pc-ip>:5000/<api>?token=<ACCESS_TOKEN>`

## Current APIs

- shutdown (hibernate)

- restart

- sleep

- status: extensive PC diagnostics <br>
  (3 discs hardcoded at the moment)

- status.json
