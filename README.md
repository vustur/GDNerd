# GDNerd
Python program for spamming geometry dash recent level with chatGPT!
### How does it works
- Login to gd account
- Get random recent level
- Get levels name, description, author and song
- Ask ChatGpt with [prompt and level data](main.py#L144)
- Comment strange thing
### Install
- copy repo
- install packages
- - ```gd-py=="0.11.0"```
- - ```openai```
- - ```colorama```
- find http proxy list and put it in [proxy.txt](proxy.txt)
- run main.py and choose check proxy (9). Valids will be saved in [valid_proxy.txt](valid_proxy.txt)
- configure config.py
- run main.py again and choose start gdnerd (1)
