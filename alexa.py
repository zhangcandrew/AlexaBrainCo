"""
This sample demonstrates a simple skill built with the Amazon Alexa Skills Kit.
The Intent Schema, Custom Slots, and Sample Utterances for this skill, as well
as testing instructions are located at http://amzn.to/1LzFrj6

For additional samples, visit the Alexa Skills Kit Getting Started guide at
http://amzn.to/1LGWsLG
"""

from __future__ import print_function
import pyrebase, random 


# --------------- Firebase tools -----------------------------------------------

# rtype: firebase object
def init_firebase():
	config = {
	  "apiKey": "AIzaSyCtuDnsJOmxqK4JhtEnfLBzryEQYE4mR40",
	  "authDomain": "brain-cocaine.firebaseapp.com",
	  "databaseURL": "https://brain-cocaine.firebaseio.com",
	  "storageBucket": "brain-cocaine.appspot.com"
	}

	firebase = pyrebase.initialize_app(config)
	return firebase

# input param: firebase object
# rtype: firebase database
def init_firebase_db(firebase):
	return firebase.database()

def random_question(db, subject):
	all_questions = db.child(subject).get().val()
	choice = random.choice(list(all_questions.values()))
	question, answer = choice[0], choice[1]
	return question, answer

# --------------- Helpers that build all of the responses ----------------------

def build_speechlet_response(title, output, reprompt_text, should_end_session):
    return {
        'outputSpeech': {
            'type': 'PlainText',
            'text': output
        },
        'card': {
            'type': 'Simple',
            'title': "SessionSpeechlet - " + title,
            'content': "SessionSpeechlet - " + output
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': reprompt_text
            }
        },
        'shouldEndSession': should_end_session
    }


def build_response(session_attributes, speechlet_response):
    return {
        'version': '1.0',
        'sessionAttributes': session_attributes,
        'response': speechlet_response
    }


# --------------- Functions that control the skill's behavior ------------------

def get_welcome_response():
    """ If we wanted to initialize the session to have some attributes we could
    add those here
    """

    session_attributes = {}
    card_title = "Welcome"
    speech_output = "Welcome to Brain Cocaine. " \
                    "What do you want to be quizzed on today?"

    # If the user either does not reply to the welcome message or says something
    # that is not understood, they will be prompted again with this text.
    reprompt_text = "Is there anything you'd like to be quizzed on today?"

    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def handle_session_end_request():
    card_title = "Session Ended"
    speech_output = "Thanks for using cocaine!"

    # Setting this to true ends the session and exits the skill.
    should_end_session = True
    return build_response({}, build_speechlet_response(
        card_title, speech_output, None, should_end_session))

def delete_favorite_color_attributes():
	return {}


def set_color_in_session(intent, session):
    """ Sets the color in the session and prepares the speech to reply to the
    user.
    """

    card_title = intent['name']
    session_attributes = session.get('attributes', {})
    should_end_session = False

    if 'Time' in intent['slots']:
        favorite_color = intent['slots']['Time']['value']
        topic = intent['slots']['Topic']['value']
        session_attributes[topic] = favorite_color

        speech_output = "I now know you want to be quizzed in  " \
                         + favorite_color + " minutes" \
                        " on " + topic \
                        + ". You can make another brainCocaine request by saying, " \
                        " make another quiz request"
        reprompt_text = "Do you want to create a quiz request? " 
    else:
        speech_output = "I didn't ge that. " \
                        "Please try cocaine again."
        reprompt_text = "Do you want me to quiz you? " \
                        "You can ask me to quiz you by saying, " \
                        "quiz me in 5 minutes."
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def get_color_from_session(intent, session):
    session_attributes = {}
    reprompt_text = None

    if intent == "RandomQuestionIntent":
    	question, answer = random_question(session['db'], "arithmetic")
    	session['answer'] = answer
    	speech_output = question
    	should_end_session = False

	elif intent == "AnswerIntent":
		if 'Answer' in intent['slots']:
			if intent['slots']['value'].strip().lower() == session['answer']:
				speech_output = "That's a fantastic answer! Looks like the cocaine works!"
				should_end_session = True
			else:
				speech_output = "That was a good try, maybe you need more cocaine?"
				should_end_session = False

    elif session.get('attributes', {}) != {}:
        topics = session['attributes']
        speech_output = "I will quiz you on  "

        for key, value in topics.items()[:-1]:
        	speech_output += key + ", "

        speech_output += " and "+ topics.items()[-1][0]
        speech_output += ". Aside from those, feel free to use more cocaine."
        should_end_session = True
    else:
        speech_output = "I'm not sure if you want to use cocaine. " \
                        "You should try to make me quiz you."
        should_end_session = False

    # Setting reprompt_text to None signifies that we do not want to reprompt
    # the user. If the user does not respond or says something that is not
    # understood, the session will end.
    return build_response(session_attributes, build_speechlet_response(
        intent['name'], speech_output, reprompt_text, should_end_session))


# --------------- Events ------------------

def on_session_started(session_started_request, session):
    """ Called when the session starts """

    """connect to firebase"""
    firebase = init_firebase()
	db = init_firebase_db(firebase)

	session['db'] = db

    print("on_session_started requestId=" + session_started_request['requestId']
          + ", sessionId=" + session['sessionId'])


def on_launch(launch_request, session):
    """ Called when the user launches the skill without specifying what they
    want
    """

    print("on_launch requestId=" + launch_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # Dispatch to your skill's launch
    return get_welcome_response()


def on_intent(intent_request, session):
    """ Called when the user specifies an intent for this skill """

    print("on_intent requestId=" + intent_request['requestId'] +
          ", sessionId=" + session['sessionId'])

    intent = intent_request['intent']
    intent_name = intent_request['intent']['name']

    # Dispatch to your skill's intent handlers
    if intent_name == "MyColorIsIntent":
        return set_color_in_session(intent, session)
    elif intent_name == "WhatsMyColorIntent":
        return get_color_from_session(intent, session)
    elif intent_name == "RandomQuestionIntent":
    	return get_color_from_session(intent, session)
    elif intent_name == "AMAZON.HelpIntent":
        return get_welcome_response()
    elif intent_name == "AMAZON.CancelIntent" or intent_name == "AMAZON.StopIntent":
        return handle_session_end_request()
    else:
        raise ValueError("Invalid intent")


def on_session_ended(session_ended_request, session):
    """ Called when the user ends the session.

    Is not called when the skill returns should_end_session=true
    """
    print("on_session_ended requestId=" + session_ended_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # add cleanup logic here


# --------------- Main handler ------------------

def lambda_handler(event, context):
    """ Route the incoming request based on type (LaunchRequest, IntentRequest,
    etc.) The JSON body of the request is provided in the event parameter.
    """
    print("event.session.application.applicationId=" +
          event['session']['application']['applicationId'])

    """
    Uncomment this if statement and populate with your skill's application ID to
    prevent someone else from configuring a skill that sends requests to this
    function.
    """
    # if (event['session']['application']['applicationId'] !=
    #         "amzn1.echo-sdk-ams.app.[unique-value-here]"):
    #     raise ValueError("Invalid Application ID")

    if event['session']['new']:
        on_session_started({'requestId': event['request']['requestId']},
                           event['session'])

    if event['request']['type'] == "LaunchRequest":
        return on_launch(event['request'], event['session'])
    elif event['request']['type'] == "IntentRequest":
        return on_intent(event['request'], event['session'])
    elif event['request']['type'] == "SessionEndedRequest":
        return on_session_ended(event['request'], event['session'])
