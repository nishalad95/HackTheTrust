'use strict';

/**
 * Firstly, I'd like to apologise for the rather hacky attempt at building this alexa lambda function.
 * Learning the alexa specific API is difficult at 3am, and that happens to be when most of this was put together.
 * 
 * To produce a 'viable' demo, I had to fake and mimic most of the proper interaction between intents. For example,
 * we are using preset questions, that would exist in a datastore somewhere not hardcoded. We also don't validate the provided answer.
 * You can literally say anything and it would be correct >.< haha.
 * 
 * But what it does do, is demo the flow of interaction for this intent. Given more time we could integrate the back end correctly.
 */


const Alexa = require('alexa-sdk');

const APP_ID = 'amzn1.ask.skill.cc9fd1df-0a60-4f3b-9a9b-b6109858e640';
const SKILL_NAME = 'Sensei';
const HELP_MESSAGE = 'You can say "test me on my history questions"';
const HELP_REPROMPT = 'What can I help you with?';
const STOP_MESSAGE = 'Goodbye!';

const data = [
    {
        id: 1,
        userId: 'amzn1.ask.account.AEGOVOTCJHAC35LPC3Z52NLWI3V2PVOXJWG3AFQBRNKVH476WHLUBX2BVXX4JOVURQ3LW3SAZO5INLH6IGBDOVYK6GZZPIBAM5BJ5O2YNA7ITKWXACH4E7XNJMEWVR2ECO6ZPG55DWHSJ5BY7BGWPIX3Z5OPEGOM3CYLDMEWWCPL7T3ILM6B3AO7D43V7WSZ35QHFRKV6FUJFXQ',
        question: 'Which is the best team at the Prince\'s Trust Hackathon 2018',
        answer: 'Team Virtuous'
    },
    {
        id: 2,
        userId: 'amzn1.ask.account.AEGOVOTCJHAC35LPC3Z52NLWI3V2PVOXJWG3AFQBRNKVH476WHLUBX2BVXX4JOVURQ3LW3SAZO5INLH6IGBDOVYK6GZZPIBAM5BJ5O2YNA7ITKWXACH4E7XNJMEWVR2ECO6ZPG55DWHSJ5BY7BGWPIX3Z5OPEGOM3CYLDMEWWCPL7T3ILM6B3AO7D43V7WSZ35QHFRKV6FUJFXQ',
        question: 'What year did the second world war start',
        answer: '1939'
    },
    {
        id: 2,
        userId: 'amzn1.ask.account.AEGOVOTCJHAC35LPC3Z52NLWI3V2PVOXJWG3AFQBRNKVH476WHLUBX2BVXX4JOVURQ3LW3SAZO5INLH6IGBDOVYK6GZZPIBAM5BJ5O2YNA7ITKWXACH4E7XNJMEWVR2ECO6ZPG55DWHSJ5BY7BGWPIX3Z5OPEGOM3CYLDMEWWCPL7T3ILM6B3AO7D43V7WSZ35QHFRKV6FUJFXQ',
        question: 'What year was the Tower of London built',
        answer: 'The year 1066'
    }

];

const instructions = `Welcome to Sensei, <break strength="medium" />
    I can help quiz you on questions of your choosing, and help improve your knowledge! <break strength="medium" />
    You can ask me to "add a question"; or "test me on my maths questions"`;

const handlers = {
    'LaunchRequest': function() {
        this.emit(':ask', instructions);
    },
    'TestMeIntent': async function() {

        if (this.event.session.attributes.questions === undefined && this.event.session.new === true) {
            // New session, add all the questions
            let qs = data.filter((d) => {
                return d.userId === this.event.session.user.userId;
            });

            console.log('All questions: ' + qs);

            if (qs.length < 1) {
                this.response.speak('You haven\'t added any questions, you can added a question and answer by saying "Add a new question"');
                this.emit(':responseReady');
                return;
            }

            this.event.session.attributes.chosen = qs.pop();
            this.event.session.attributes.questions = qs;

            let qMsg = 'Okay, here\'s your first question: ' + this.event.session.attributes.chosen.question + '?';

            this.emit(':ask', qMsg);
            return;

        } else if (this.event.session.attributes.questions.length > 0) {
            // Existing session, get the selected question
            let q = this.event.session.attributes.chosen;

            // Pretend to check the answer...
            // For the sake of a demo, every answer will be correct

            // Take the next question
            this.event.session.attributes.chosen = this.event.session.attributes.questions.pop();

            let sequenceTerm = 'next';
            if (this.event.session.attributes.questions.length === 0) {
                sequenceTerm = 'final';
                this.event.session.attributes.isFinalQuestion = true;
            }

            let qMsg = 'That\'s correct! <break strength="strong" /> Here\'s your ' + sequenceTerm + ' question: ' + this.event.session.attributes.chosen.question + '?';
            this.emit(':ask', qMsg);
            return;
        }

        this.response.speak('Great work, you answered every question correctly. Thanks for playing. <break strength="strong" /> <prosody volume="x-loud">Go team virtuous!</prosody>.');
        this.emit(':responseReady');
    },
    'AMAZON.HelpIntent': function() {
        const speechOutput = HELP_MESSAGE;
        const reprompt = HELP_REPROMPT;

        this.response.speak(speechOutput).listen(reprompt);
        this.emit(':responseReady');
    },
    'AMAZON.CancelIntent': function() {
        this.response.speak(STOP_MESSAGE);
        this.emit(':responseReady');
    },
    'AMAZON.StopIntent': function() {
        this.response.speak(STOP_MESSAGE);
        this.emit(':responseReady');
    },
    'Unhandled'() {
        console.error('problem', this.event);
        this.emit(':ask', 'Uh Oh... we seem to have encountered a problem. Naughty code!');
    },
};

exports.handler = function(event, context, callback) {
    const alexa = Alexa.handler(event, context, callback);
    alexa.APP_ID = APP_ID;
    alexa.registerHandlers(handlers);
    alexa.execute();
};
