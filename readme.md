# CoroBot
A discord bot based on official French hospitalization data, creating graphs based on user request.
The data is available [here](https://www.data.gouv.fr/fr/datasets/donnees-hospitalieres-relatives-a-lepidemie-de-covid-19/#_).

## What does it do ?
Discord users can type in the chat things such as :
```    
    +Coro Indre 01-08-2020 01-09-2020
    +Coro Indre 01-08-2020
    +Coro 36 hosp
    +Coro Île-de-France
    +Coro help
    +Coro dep
```
And the bot will generate a matplotlib figure, then send it in a nice embed.
![Example](https://github.com/LukaP-BB/CoroBot/blob/master/images/Capture.PNG)
I tried to make the argument parsing as user-friendly as possible :
- the arguments can be given in any order
- the departments can be given by their code or their name
- all arguments are optional
- if any of <hosp, rea, rad, dc> is given, the graph will show the data for only given args, else, it will show all data available
    - hosp : hospitalizations by day
    - res : persons in reanimation by day
    - rad : sum of people back home
    - dc : sum of deceded people

## Wanna use it ?
Feel free to use this code and host this bot wherever you want. Just send me a little message if you do, It would make my day.
```
git pull https://github.com/LukaP-BB/CoroBot.git
pip install -r requirements.txt
```
