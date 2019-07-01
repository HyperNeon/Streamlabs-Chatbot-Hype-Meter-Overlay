1. Right click on Hype Meter Script and click "Insert API Key"
2. Create a browser source in obs and link it to whichever overlay.html file in the script folder you'd like
3. Configure the settings for the script in the Bot. Make sure you hit "Save Settings". Specific configuration details can be found in the tooltips
4. Tweak HTML/Javascript files as desired to make a super Hype Overlay
5. People with configured permission level can override the meter with !freezehypemeter, !unfreezehypemeter, and !maxhypemeter
	- !freezehypemeter: Prevents the meter from doing anything. It will not increment up, but it will still go down over time
	- !unfreezehypemeter: Starts tracking again after a freeze
	- !maxhypemeter: Overrides tracking and bumps the meter straight to 100%
6. Profit!