# Streamlabs Chatbot Hype Meter Overlay
A Python script for use in [Streamlabs Chatbots's](https://streamlabs.com/chatbot) built-in scripting feature which monitors chat for given keywords, and then an web overlay using Websocket events. 
The script can also optionally switch scenes and activate sources within OBS using OBSRemote. 
You can check out the functionality on [Github](https://github.com/HyperNeon/Streamlabs-Chatbot-Hype-Meter-Overlay)

Video Tutorial: [YouTube](https://youtu.be/ZifIbMVmTBc)

This script will monitor all Twitch/YouTube/Mixer chat and look for a list of keywords or emotes that are configured in the Script Settings. It will then monitor hype levels over time and send websocket events to the JavaScript handlers in the overlays. There are 3 provided overlays which can be used as a starting point, but the idea is really to use those to customize your own version for your channel. The HypeGuage in particular has a whole host of features that allow for deep customization by tweaking the settings in accordance with this site: https://bernii.github.io/gauge.js/. The Spicy Meter is an alternative example that shows how this script can be used to simply unhide 1 image on top of another to draw a meter filling up effect. Finally, when the hype level reaches 100%, you have the option to trigger scene changes and source activation for a perioud of time within OBS if desired and using OBSRemote.

Aside from the Javascript and HTML customizations, the script allows you to customize:
* The list of phrases to match on in chat
* How many matches constitutes 100% meter
* Whether to count multiple matches within the same chat messages as a single match or multiple
* How long the lookback window should be for tracking messages
* Whether to allow the meter to surpass 100%
* Whether the meter should be reset to 0 after reaching 100%
* How long to wait after reaching 100% before resetting
* Whether a cooldown period should be enabled after a reset before beginning tracking again
* OBSRemote - Whether or not to activate a given scene and how long to wait after reaching 100% before doing so
* OBSRemote - Whether or not to activate a given source and how long to wait after reaching 100% before doing so
* OBSRemote - How long to leave the given source aftive before disabling it again


Additionally, there are 3 commands that can be used to manually override the Hype Meter:
* !freezehypemeter - Pauses the meter from counting any additional messages or triggering OBSRemote events. 
* !unfreezehypemeter - Puts back the meter into a normal state after a pause
* !maxhypemeter - Automatically sets the meter to 100% and triggers any events configured to happen at that time
These commands are only usable by chatters with the configured permission level or above. 

Although the script is called "Hype Meter" it can really be used to track any type of chat activity over time if configured properly. For example: you could automatically track specific word usage over several hours, by simply setting the LookbackMinutes to several hours which essentially removes any decay of the meter. In these situations you may also want to update the BlockLengthSeconds and TickTimeSeconds to only be every few minutes rather than seconds since you'll be tracking data over a longer period. You can also track any Chat Activity, not just specific phrase matches, by leaving the "HypePhrases" field empty, which effectively matches every chat message.

Streamers using Streamlabs Chatbot Hype Meter Overlay:
* https://www.twitch.tv/gametangent
* https://www.twitch.tv/casperthespicyghost

### Installation
This script is meant to be run from within the Scripts module in [Streamlabs Chatbots's](https://streamlabs.com/chatbot).
Instructions for installing a new script in the bot can be found here: [Offical Chatbot Documention](https://streamlabs.com/chatbot#Documentation.pdf).
Everything else you need for configuring the bot can be found within the tooltips that appear when hovering over each configuration parameter in the UI.

### Contributing
I'd love it if you'd like to help out making this thing better. Simply fork the repo and submit a PR and I'll be glad to take a look at it. Also feel free to reach out to me with any questions and check out the [Chatbot Discord](https://discordapp.com/invite/J4QMG5m). I go by GameTangent in the Discord.
