# wackysubs

I created the files xxx.wsgi and xxx.conf only for the Amazon AWS EC2 version of wackysubs because it is using Apache web server. The Azure version will not use these files.

You can find wacky subreddits at reddit by using this web app. It used data mining to find usage patterns of humans with regard to which subreddits they commented at, and so presumably they liked. 

The mlxtend library and its fpgrowth function with its association rules modeling were used as the data science algorithm to make the pattern discoveries. 

The model's training code is not in this repository at this time. This here is the website code only.
