
const Alexa = require('ask-sdk-core');
const Util = require('./util');
const Common = require('./common');

// The namespace of the custom directive to be sent by this skill
const NAMESPACE = 'Custom.Mindstorms.Gadget';

// The name of the custom directive to be sent this skill
const NAME_CONTROL = 'control';

const LaunchRequestHandler = {
    canHandle(handlerInput) {
        return Alexa.getRequestType(handlerInput.requestEnvelope) === 'LaunchRequest';
    },
    handle: async function(handlerInput) {

        let request = handlerInput.requestEnvelope;
        let { apiEndpoint, apiAccessToken } = request.context.System;
        let apiResponse = await Util.getConnectedEndpoints(apiEndpoint, apiAccessToken);
        if ((apiResponse.endpoints || []).length === 0) {
            return handlerInput.responseBuilder
            .speak(`I couldn't find an EV3 Brick connected to this Echo device. Please check to make sure your EV3 Brick is connected, and try again.`)
            .getResponse();
        }

        // Store the gadget endpointId to be used in this skill session
        let endpointId = apiResponse.endpoints[0].endpointId || [];
        Util.putSessionAttribute(handlerInput, 'endpointId', endpointId);

        return handlerInput.responseBuilder
            .speak("Welcome to table service, you can ask me for spices and I will deliver.")
            .reprompt("Which spice do you want?")
            .getResponse();
    }
};


// Move band to test the function

const MoveIntentHandler = {
    canHandle(handlerInput) {
        return Alexa.getRequestType(handlerInput.requestEnvelope) === 'IntentRequest'
            && Alexa.getIntentName(handlerInput.requestEnvelope) === 'MoveIntent';
    },
    handle: function (handlerInput) {
        const request = handlerInput.requestEnvelope;
        const direction = Alexa.getSlotValue(request, 'Direction');

        // Duration is optional, use default if not available
        const duration = Alexa.getSlotValue(request, 'Duration') || "2";

        // Get data from session attribute
        const attributesManager = handlerInput.attributesManager;
        const speed = attributesManager.getSessionAttributes().speed || "50";
        const endpointId = attributesManager.getSessionAttributes().endpointId || [];

        // Construct the directive with the payload containing the move parameters
        const directive = Util.build(endpointId, NAMESPACE, NAME_CONTROL,
            {
                type: 'move',
                direction: direction,
                duration: duration,
                speed: speed
            });

        const speechOutput = (direction === "brake")
            ?  "Applying brake"
            : `${direction} ${duration} seconds at ${speed} percent speed`;

        return handlerInput.responseBuilder
            .speak(speechOutput)
            .reprompt("awaiting command")
            .addDirective(directive)
            .getResponse();
    }
};

// Hnadling of the band and deliver the spice
const GetMeSpiceHandler = {
    canHandle(handlerInput) {
        return Alexa.getRequestType(handlerInput.requestEnvelope) === 'IntentRequest'
            && Alexa.getIntentName(handlerInput.requestEnvelope) === 'DeliverSpice';
    },
    handle: function (handlerInput) {
        const request = handlerInput.requestEnvelope;
        const spicename = Alexa.getSlotValue(request, 'Spice');

        // Get data from session attribute
        const attributesManager = handlerInput.attributesManager;
        //const speed = attributesManager.getSessionAttributes().speed || "50";
        const speed = "5";
        const endpointId = attributesManager.getSessionAttributes().endpointId || [];
     
        
        //Default Parameter not used:
        let directionband  = "LEFT";
        let durationband = 5;
   
          const directive = Util.build(endpointId, NAMESPACE, NAME_CONTROL,
            {
                type: 'deliver',
                direction: directionband,
                duration: durationband,
                speed: speed,
                spice: spicename
                
            });    
            
       
            
        const speechOutput = spicename + "will be delivered";

        return handlerInput.responseBuilder
            .speak(speechOutput)
            .reprompt("too much spices are unhealthy")
            .addDirective(directive)
            .getResponse();
    }
};

// The SkillBuilder acts as the entry point for your skill, routing all request and response
// payloads to the handlers above. Make sure any new handlers or interceptors you've
// defined are included below. The order matters - they're processed top to bottom.
exports.handler = Alexa.SkillBuilders.custom()
    .addRequestHandlers(
        LaunchRequestHandler,
        GetMeSpiceHandler,
        MoveIntentHandler,
        Common.HelpIntentHandler,
        Common.CancelAndStopIntentHandler,
        Common.SessionEndedRequestHandler,
        Common.IntentReflectorHandler, // make sure IntentReflectorHandler is last so it doesn't override your custom intent handlers
    )
    .addRequestInterceptors(Common.RequestInterceptor)
    .addErrorHandlers(
        Common.ErrorHandler,
    )
    .lambda();