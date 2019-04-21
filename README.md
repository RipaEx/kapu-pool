# ARK pool distribution software
This software is created by lisk delegate "dakk", please consider a small donation if you
use this software: "2324852447570841050L" for lisk or "7725849364280821971S" for shift or
"AZAXtswaWS4v8eYMzJRjpd5pN3wMBj8Rmk" for ark.


## Configuration
Fork this repo; edit config.json and modify the first lines with your settings:

- **coin**: the coin you need to use based on the ARK 2.0 codebase
- **pubkey**: your delegate pubkey
- **percentage**: percentage to distribute
- **secret**: your passphrases.json file should contains two objects PASSPHRASE and SECOND_PASSPHRASE
- secondsecret: deprecated
- **node**: the DPOS network node where you get forging info
- nodepay: deprecated
- **minpayout**: the minimum amount for a payout
- **skip**: a list of address to skip
- **donations**: a list of object (address: amount) for send static amount every payout
- **donationspercentage**: a list of object (address: percentage) for send static percentage every payout
- **logfile**: file where you want to write pending and sent amounts

Now edit docs/index.html and customize the webpage.

Finally edit docs/poollogs.json and put:
- **lastpayout**: the unixtimestamp of your last payout or the date of pool starting 
- **lastforged**: the forged amount recorded in your last payout or the forged amount of pool starting

## Running it

First install requests:

`npm install`

Then start it:

`npm start`

or if you want to use another config file:

`npm start -- -c config2.json`

It produces a file "payments.json" with all payments so you can run it at separate stage:
`node payments.js`

To display the pool frontend, enable docs-site on github repository settings.


## Batch mode

The script is also runnable by cron using the -y argument:
`npm start -- -y`
