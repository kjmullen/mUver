
## mUver

Final Project by Kevin Mullen

for the February '16 - May '16 cohort at The Iron Yard

Build Status | Coverage
--- | ---
[![Build Status](https://travis-ci.org/kjmullen/mUver.svg?branch=master)](https://travis-ci.org/kjmullen/mUver) | [![Coverage Status](https://coveralls.io/repos/github/kjmullen/mUver/badge.svg?branch=master)](https://coveralls.io/github/kjmullen/mUver?branch=master)


## Synopsis

mUver is a micro move solution. A system that pairs users with truck owners. Contained in this project is the back end written in python/django. An API was created with django rest framework to be paired with a React front end created by my partner.

[Our Demo Day powerpoint presentation](https://docs.google.com/presentation/d/15FMtrV3NrOA0ygXYOWTTNKTDBTiZWhGB_7e-kDY9xtM/edit?usp=sharing)

## Features
Stripe with Managed Accounts - Payments made directly to users.

Twilio - Text notifications

GEODjango - Distance calculations from addresses

## To Do

Get test coverage above 90% + more docstrings

'Distance From' calcuation for job listings needs HTTPS

Add more Twilio Functionality (responding to text to make changes to a current job)

Fix known front end bugs + adding registration + password/phone number/address validation messages (if input invalid)
