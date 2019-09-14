# NLP Service
This is some experimentation I'm doing with Natural Language Processing.

The core components of this experimentation at this point are:
  1. A python API and CLI for downloading and processing tweets from twitter.
  2. A python API and CLI for building a tensorflow model of groups
     of tweets, in order to do predictive text in the style of those tweets.
  3. A Django server for managing and displaying of the data.
  4. An ELK stack for doing analysis of the data.
  
  
# Status
I just started working on this, so there's still a lot to do. 
Here's my TODO list:
  - [x] Build twitter python api
  - [x] Download some sample data from my favorite twitter 
  accounts (@dog_rates and @NateSilver538)
  - [ ] Learn keras/tensorflow, and build an initial model 
  for predicting tweets
  - [ ] Finish setting up Django with postgres, with celery 
  for doing the processing steps.  Redis probably for the celery
  backend.
  - [ ] Set up ELK stack, insert initial tweet data into ELK stack.
  - [ ] Build some initial Kibana visualizations for tweet analysis.
  - [ ] Initial deploy for demo.