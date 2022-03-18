#!/usr/bin/env python3
# The print statements go to the console or web server access log or error log; they do not go to the web page.

from flask import Flask, render_template, request, make_response
import flask
print(f"flask {flask.__version__}")

app = Flask(__name__)

app.config["APPLICATION_ROOT"] = "/recommendit" # IDK if this actually does anything.

import os
import common
import pandas as pd
print(f"pandas {pd.__version__}")
import pyarrow  # Not refrenced in MY code, but is actually required by pandas bc I call read_feather.
print(f"pyarrow {pyarrow.__version__}")
from pathlib import Path

# Decide if running on dev host or public host, so path can be automatically changed. Basis: comcast isp vs amazon.com?
#import subprocess
#myip = subprocess.run(["wget", "-q", "-O", "-", "http://checkip.amazonaws.com"], capture_output=True)
#isDevHost = "a.b.c.d" in str(myip.stdout) # I am NOT showing everyone my dev ip addr!
# Put this env var into my env before running this python on dev host using bash terminal, like: export ISTHISMYDEVHOST=YES
#isDevHost = 'ISTHISMYDEVHOST' in os.environ
#if isDevHost:
#	print("Detected as running on dev web host.")
	#adfpath = Path('ar_model_part1_confmin0003_train_2018_janfeb_saved_jan242022_feather')
	#edfpath = Path('ar_model_part2_confmin0003_train_2018_janfeb_saved_jan242022_feather')
#	adfpath = Path('ar_model_part1_confmin0003_train_2018_janfeb_saved_mar162022_feather')
#	edfpath = Path('ar_model_part2_confmin0003_train_2018_janfeb_saved_mar162022_feather')
#else:
#	print("Detected as running on public web host.")
	#adfpath = Path('/usr/local/etc/recommendit/ar_model_part1_confmin0003_train_2018_janfeb_saved_jan242022_feather')
	#edfpath = Path('/usr/local/etc/recommendit/ar_model_part2_confmin0003_train_2018_janfeb_saved_jan242022_feather')
#	adfpath = Path('/usr/local/etc/recommendit/ar_model_part1_confmin0003_train_2018_janfeb_saved_mar162022_feather')
#	edfpath = Path('/usr/local/etc/recommendit/ar_model_part2_confmin0003_train_2018_janfeb_saved_mar162022_feather')

# In advance, set these env vars on the host.
# In Azure cloud: Portal | Home | wackysubs App Service | Settings | Configuration | Application Settings
# In Amazon EC2: Just set an env var in a startup script
adfpath = Path(os.environ['WACKYSUBSDATAPATHPART1'])
edfpath = Path(os.environ['WACKYSUBSDATAPATHPART2'])

print(f"Loading part 1 of model from path {adfpath}")
adf = pd.read_feather(adfpath);
print(f"Loading part 2 of model from path {edfpath}")
edf = pd.read_feather(edfpath);

@app.context_processor
def GetAllSubreddits():
    return dict(allsubreddits=sorted(edf.columns))

@app.route('/')
def index():
    return render_template('index.html', confMin=0.05)

# User keying in a subreddit, so offer a partially matching list.
@app.route('/offersubreddits', methods=["GET"])
def offersubreddits():
	q = request.args.get("q")
	subreddits = [subreddit for subreddit in edf.columns if subreddit.startswith(q)]
	return render_template("offersubreddits.html", subreddits=subreddits)


def GetFavsList():
	favs = request.cookies.get('favs')
	if favs is None:
		favs = ''
	favsList = [f for f in favs.split(";") if f != '']
	favsList = sorted(list(set(favsList)))	
	return favsList

# User clicked button to run the recommender system
# Check the value of the action property of the submit button to decide action
@app.route('/formaction', methods=["GET"])
def formaction():
	baction = request.args.get('baction')
	if 'query' == baction: 
		confMin = 0.01 if None == request.args.get('confMin') else request.args.get('confMin')
		searchTerm = request.args.get('searchTerm') # add 2 more searchTerm later
		if searchTerm is None or searchTerm == '':
			favsList = GetFavsList()
			return render_template('index.html', favorites=favsList)
		searchList=[searchTerm]
		recommendations = []
		if set(searchList).issubset(edf.columns):
			df = common.QueryModel(adf, edf, searchList, exactMatch=True, confMin=confMin)
			recommendations = common.QueryResultList(df) # [np.array(['Jokes'], dtype=object), np.array(['Showerthoughts'], dtype=object), ...
			recommendations = [list(a)[0] for a in recommendations] # ['Jokes', 'Showerthoughts', ...
			resp = make_response(render_template('index.html', recommendations=recommendations, searchList=searchList, searchTerm=searchTerm, confMin=confMin))
			# Every time they Find an item, add that to their favorites, but No duplicates, no empty strings.
			favsList = GetFavsList() + searchList
			favsList = sorted(favsList)
			favs = ';'.join(favsList)
			resp.set_cookie('favs', favs) 
			return resp
		else:
			return render_template('index.html', confMin=0.05) # no such subreddit

	elif 'showfavs' == baction:
		favsList = GetFavsList()
		return render_template('index.html', favorites=favsList)
	elif 'delete' == baction:
		favsList = GetFavsList()
		item = request.args.get('delete')
		if item in favsList:
			favsList.remove(item)
		resp = make_response(render_template('index.html', favorites=favsList, baction='showfavs')) # show the (new) favs
		favs = ';'.join(favsList) # cookiefy the list
		resp.set_cookie('favs', favs) # set the favs into cookie
		return resp
	else:
		print(f"Bad parameter value in baction:*{baction}*")


if __name__ == "__main__":
    app.run()
