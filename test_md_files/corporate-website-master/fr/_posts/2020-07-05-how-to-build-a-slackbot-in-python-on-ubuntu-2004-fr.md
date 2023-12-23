---
layout: flexstart-blog-single
title: "How To Build a Slackbot in Python on Ubuntu 20.04"
author: full
lang: fr
ref: slackbot_202007051234
categories: [slack]
description: "Slack is a communication platform designed for workplace productivity. It includes features such as direct messaging, public and private channels, voice and video calls, and bot integrations. A Slackbot is an automated program that can perform a variety of functions in Slack, from sending messages to triggering tasks to alerting on certain events."
featured: true
image: "https://sergio.afanou.com/assets/images/image-midres-31.jpg"
seo:
  links: [ "https://m.wikidata.org/wiki/Q15206305" ]
---

<p><em>The author selected the <a href="https://www.brightfunds.org/funds/tech-education">Tech Education Fund</a> to receive a donation as part of the <a href="https://do.co/w4do-cta">Write for DOnations</a> program.</em></p>

<h3 id="introduction">Introduction</h3>

<p><a href="https://slack.com/">Slack</a> is a communication platform designed for workplace productivity. It includes features such as direct messaging, public and private channels, voice and video calls, and bot integrations. A Slackbot is an automated program that can perform a variety of functions in Slack, from sending messages to triggering tasks to alerting on certain events.</p>

<p>In this tutorial you will build a Slackbot in the <a href="https://www.python.org/">Python</a> programming language. Python is a popular language that prides itself on simplicity and readability. Slack provides a rich <a href="https://github.com/slackapi/python-slackclient">Python Slack API</a> for integrating with Slack to perform common tasks such as sending messages, adding emojis to messages, and much more. Slack also provides a <a href="https://github.com/slackapi/python-slack-events-api">Python Slack Events API</a> for integrating with events in Slack, allowing you to perform actions on events such as messages and mentions.</p>

<p>As a fun proof-of-concept that will demonstrate the power of Python and its Slack APIs, you will build a <code>CoinBot</code>—a Slackbot that monitors a channel and, when triggered, will flip a coin for you. You can then modify your <code>CoinBot</code> to fulfill any number of <em>slightly</em> more practical applications.</p>

<p>Note that this tutorial uses Python 3 and is not compatible with Python 2.</p>

<h2 id="prerequisites">Prerequisites</h2>

<p>In order to follow this guide, you&rsquo;ll need:</p>

<ul>
<li><p>A Slack Workspace that you have the ability to install applications into. If you created the workspace you have this ability. If you don&rsquo;t already have one, you can create one on the <a href="https://slack.com/create">Slack website</a>.</p></li>
<li><p>(Optional) A server or computer with a public IP address for development. We recommend a fresh installation of Ubuntu 20.04, a non-root user with <code>sudo</code> privileges, and SSH enabled. <a href="https://www.digitalocean.com/community/tutorials/initial-server-setup-with-ubuntu-20-04">You can follow this guide to initialize your server and complete these steps</a>.</p></li>
</ul>

<p><span class='note'>You may want to test this tutorial on a server that has a public IP address. Slack will need to be able to send events such as messages to your bot. If you are testing on a local machine you will need to port forward traffic through your firewall to your local system. If you are looking for a way to develop on a cloud server, check out this tutorial on <a href="https://www.digitalocean.com/community/tutorials/how-to-use-visual-studio-code-for-remote-development-via-the-remote-ssh-plugin">How To Use Visual Studio Code for Remote Development via the Remote-SSH Plugin</a>.<br></span></p>

<h2 id="step-1-mdash-creating-the-slackbot-in-the-slack-ui">Step 1 — Creating the Slackbot in the Slack UI</h2>

<p>First create your Slack app in the Slack API Control Panel. Log in to your workspace in Slack via a web browser and navigate to the <a href="https://api.slack.com/apps">API Control Panel</a>. Now click on the <strong>Create an App</strong> button.</p>

<p><img src="https://assets.digitalocean.com/articles/coinbot/h7VWJOX.png" alt="Create Your Slack App"></p>

<p>Next you&rsquo;ll be prompted for the name of your app and to select a development Slack workspace. For this tutorial, name your app <code><span class="highlight">CoinBot</span></code> and select a workspace you have admin access to. Once you have done this click on the <strong>Create App</strong> button.</p>

<p><img src="https://imgur.com/E4hnhMU.png" alt="Name Your Slack App and Select a Workspace"></p>

<p>Once your app is created you&rsquo;ll be presented with the following default app dashboard. This dashboard is where you manage your app by setting permissions, subscribing to events, installing the app into workspaces, and more.</p>

<p><img src="https://assets.digitalocean.com/articles/coinbot/ZjFaS1i.png" alt="Default Slack App Panel"></p>

<p>In order for your app to be able to post messages to a channel you need to grant the app permissions to send messages. To do this, click the <strong>Permissions</strong> button in the control panel.</p>

<p><img src="https://assets.digitalocean.com/articles/coinbot/IVcN8qg.png" alt="Select the Permissions Button in the Control Panel"></p>

<p>When you arrive at the <strong>OAuth &amp; Permissions</strong> page, scroll down until you find the <strong>Scopes</strong> section of the page. Then find the <strong>Bot Token Scopes</strong> subsection in the scope and click on <strong>Add an OAuth Scope</strong> button.</p>

<p><img src="https://assets.digitalocean.com/articles/coinbot/wQnTSQr.png" alt="Select the Add an OAuth Scope Button"></p>

<p>Click on that button and then type <code>chat:write</code>. Select that permission to add it to your bot. This will allow the app to post messages to channels that it can access. For more information on the available permissions refer to <a href="https://api.slack.com/scopes">Slack&rsquo;s Documentation</a>.</p>

<p><img src="https://assets.digitalocean.com/articles/coinbot/unQYPeL.png" alt="Add the chat:write Permission"></p>

<p>Now that you&rsquo;ve added the appropriate permission it is time to install your app into your Slack workspace. Scroll back up on the <strong>OAuth &amp; Permissions</strong> page and click the <strong>Install App to Workspace</strong> button at the top.</p>

<p><img src="https://assets.digitalocean.com/articles/coinbot/SiSxQB1.png" alt="Install App to Workspace"></p>

<p>Click this button and review the actions that the app can perform in the channel. Once you are satisfied, click the <strong>Allow</strong> button to finish the installation.</p>

<p><img src="https://assets.digitalocean.com/articles/coinbot/lWUBsYR.png" alt="Install App to Workspace"></p>

<p>Once the bot is installed you&rsquo;ll be presented with a <strong>Bot User OAuth Access Token</strong> for your app to use when attempting to perform actions in the workspace. Go ahead and copy this token; you&rsquo;ll need it later.</p>

<p><img src="https://assets.digitalocean.com/articles/coinbot/m1M9Ilt.png" alt="Save the Access Token"></p>

<p>Finally, add your newly installed bot into a channel within your workspace. If you haven&rsquo;t created a channel yet you can use the <em>#general</em> channel that is created by default in your Slack workspace. Locate the app in the <strong>Apps</strong> section of the navigation bar in your Slack client and click on it. Once you&rsquo;ve done that open the <strong>Details</strong> menu in the top right hand side. If your Slack client isn&rsquo;t full-screened it will look like an <code>i</code> in a circle.</p>

<p><img src="https://assets.digitalocean.com/articles/coinbot/OJ5yTXP.png" alt="Click on the App Details Icon"></p>

<p>To finish adding your app to a channel, click on the <strong>More</strong> button represented by three dots in the details page and select <strong>Add this app to a channel&hellip;</strong>. Type your channel into the modal that appears and click <strong>Add</strong>.</p>

<p><img src="https://assets.digitalocean.com/articles/coinbot/ojUMqeI.png" alt="Add App to a Channel"></p>

<p>You&rsquo;ve now successfully created your app and added it to a channel within your Slack workspace. After you write the code for your app it will be able to post messages in that channel. In the next section you&rsquo;ll start writing the Python code that will power <code>CoinBot</code>.</p>

<h2 id="step-2-mdash-setting-up-your-python-developer-environment">Step 2 — Setting Up Your Python Developer Environment</h2>

<p>First let&rsquo;s set up your Python environment so you can develop the Slackbot.</p>

<p>Open a terminal and install <code>python3</code> and the relevant tools onto your system:</p>
<pre class="code-pre command prefixed"><code><ul class="prefixed"><li class="line" prefix="$">sudo apt install python3 python3-venv
</li></ul></code></pre>
<p>Next you will create a virtual environment to isolate your Python packages from the system installation of Python. To do this, first create a directory into which you will create your virtual environment. Make a new directory at <code>~/.venvs</code>:</p>
<pre class="code-pre command prefixed"><code><ul class="prefixed"><li class="line" prefix="$">mkdir ~/.venvs
</li></ul></code></pre>
<p>Now create your Python virtual environment:</p>
<pre class="code-pre command prefixed"><code><ul class="prefixed"><li class="line" prefix="$">python3 -m venv ~/.venvs/slackbot
</li></ul></code></pre>
<p>Next, activate your virtual environment so you can use its Python installation and install packages:</p>
<pre class="code-pre command prefixed"><code><ul class="prefixed"><li class="line" prefix="$">source ~/.venvs/slackbot/bin/activate
</li></ul></code></pre>
<p>Your shell prompt will now show the virtual environment in parenthesis. It will look something like this:</p>
<pre class="code-pre custom_prefix prefixed"><code><ul class="prefixed"><li class="line" prefix="(slackbot)sammy@slackbotserver:$">
</li></ul></code></pre>
<p>Now use <code>pip</code> to install the necessary Python packages into your virtual environment:</p>
<pre class="code-pre custom_prefix prefixed"><code><ul class="prefixed"><li class="line" prefix="(slackbot)sammy@slackbotserver:$">pip install slackclient slackeventsapi Flask
</li></ul></code></pre>
<p><code>slackclient</code> and <code>slackeventsapi</code> facilitate Python&rsquo;s interaction with Slack&rsquo;s APIs. <code>Flask</code> is a popular micro web framework that you will use to deploy your app:</p>

<p>Now that you have your developer environment set up, you can start writing your Python Slackbot:</p>

<h2 id="step-3-mdash-creating-the-slackbot-message-class-in-python">Step 3 — Creating the Slackbot Message Class in Python</h2>

<p>Messages in Slack are sent via a <a href="https://api.slack.com/reference/surfaces/formatting">specifically formatted JSON payload</a>. This is an example of the JSON that your Slackbot will craft and send as a message:</p>
<pre class="code-pre "><code class="code-highlight language-json">{
   "channel":"channel",
   "blocks":[
      {
         "type":"section",
         "text":{
            "type":"mrkdwn",
            "text":"Sure! Flipping a coin....\n\n"
         }
      },
      {
         "type":"section",
         "text":{
            "type":"mrkdwn",
            "text":"*flips coin* The result is Tails."
         }
      }
   ]
}
</code></pre>
<p>You could manually craft this JSON and send it, but instead let&rsquo;s build a Python class that not only crafts this payload, but also simulates a coin flip.</p>

<p>First use the <code>touch</code> command to create a file named <code>coinbot.py</code>:</p>
<pre class="code-pre custom_prefix prefixed"><code><ul class="prefixed"><li class="line" prefix="(slackbot)sammy@slackbotserver:$">touch coinbot.py
</li></ul></code></pre>
<p>Next, open this file with <code>nano</code> or your favorite text editor:</p>
<pre class="code-pre custom_prefix prefixed"><code><ul class="prefixed"><li class="line" prefix="(slackbot)sammy@slackbotserver:$">nano coinbot.py
</li></ul></code></pre>
<p>Now add the following lines of code to import the relevant libraries for your app. The only library you need for this class is the <code>random</code> library from the Python Standard Library. This library will allow us to simulate a coin flip.</p>

<p>Add the following lines to <code>coinbot.py</code> to import all of the necessary libraries:</p>
<div class="code-label " title="coinbot.py">coinbot.py</div><pre class="code-pre "><code class="code-highlight language-python"># import the random library to help us generate the random numbers
import random
</code></pre>
<p>Next, create your <code>CoinBot</code> class and an instance of this class<br>
to craft the message payload. Add the following lines to <code>coinbot.py</code> to create the <code>CoinBot</code> class:</p>
<div class="code-label " title="coinbot.py">coinbot.py</div><pre class="code-pre "><code class="code-highlight language-python">...
class CoinBot:
</code></pre>
<p>Now indent by one and create the constants, constructors, and methods necessary for your class. First let&rsquo;s create the constant that will hold the base of your message payload. This section specifies that this constant is of the section type and that the text is formatted via markdown. It also specifies what text you wish to display. You can read more about the different payload options in the <a href="https://api.slack.com/reference/messaging/payload">official Slack message payload documentation</a>. </p>

<p>Append the following lines to <code>coinbot.py</code> to create the base template for the payload:</p>
<div class="code-label " title="coinbot.py">coinbot.py</div><pre class="code-pre "><code class="code-highlight language-python">...
    # Create a constant that contains the default text for the message
    COIN_BLOCK = {
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": (
                "Sure! Flipping a coin....\n\n"
            ),
        },
    }
</code></pre>
<p>Next create a constructor for your class so that you can create a separate instance of your bot for every request. Don&rsquo;t worry about memory overhead here; the Python garbage collector will clean up these instances once they are no longer needed.  This code sets the recipient channel based on a parameter passed to the constructor.</p>

<p>Append the following lines to <code>coinbot.py</code> to create the constructor:</p>
<div class="code-label " title="coinbot.py">coinbot.py</div><pre class="code-pre "><code class="code-highlight language-python">...
    # The constructor for the class. It takes the channel name as the a
    # parameter and sets it as an instance variable.
    def __init__(self, channel):
        self.channel = channel
</code></pre>
<p>Now write the code that simulates to flip a coin. We&rsquo;ll randomly generate a one or zero, representing heads or tails respectively.</p>

<p>Append the following lines to <code>coinbot.py</code> to simulate the coin flip and return the crafted payload:</p>
<div class="code-label " title="coinbot.py">coinbot.py</div><pre class="code-pre "><code class="code-highlight language-python">...
    # Generate a random number to simulate flipping a coin. Then return the 
    # crafted slack payload with the coin flip message.
    def _flip_coin(self):
        rand_int =  random.randint(0,1)
        if rand_int == 0:
            results = "Heads"
        else:
            results = "Tails"

        text = f"The result is {results}"

        return {"type": "section", "text": {"type": "mrkdwn", "text": text}},

</code></pre>

<p>Finally, create a method that crafts and returns the entire message payload, including the data from your constructor, by calling your <code>_flip_coin</code> method.</p>

<p>Append the following lines to <code>coinbot.py</code> to create the method that will generate the finished payload:</p>
<div class="code-label " title="coinbot.py">coinbot.py</div><pre class="code-pre "><code class="code-highlight language-python">...
    # Craft and return the entire message payload as a dictionary.
    def get_message_payload(self):
        return {
            "channel": self.channel,
            "blocks": [
                self.COIN_BLOCK,
                *self._flip_coin(),
            ],
        }
</code></pre>
<p>You are now finished with the <code>CoinBot</code> class and it is ready for testing. Before continuing, verify that your finished file, <code>coinbot.py</code>, contains the following:</p>
<div class="code-label " title="coinbot.py">coinbot.py</div><pre class="code-pre "><code class="code-highlight language-python"># import the random library to help us generate the random numbers
import random

# Create the CoinBot Class

class CoinBot:

    # Create a constant that contains the default text for the message
    COIN_BLOCK = {
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": (
                "Sure! Flipping a coin....\n\n"
            ),
        },
    }

    # The constructor for the class. It takes the channel name as the a
    # parameter and then sets it as an instance variable
    def __init__(self, channel):
        self.channel = channel

    # Generate a random number to simulate flipping a coin. Then return the
    # crafted slack payload with the coin flip message.
    def _flip_coin(self):
        rand_int =  random.randint(0,1)
        if rand_int == 0:
            results = "Heads"
        else:
            results = "Tails"

        text = f"The result is {results}"

        return {"type": "section", "text": {"type": "mrkdwn", "text": text}},

    # Craft and return the entire message payload as a dictionary.
    def get_message_payload(self):
        return {
            "channel": self.channel,
            "blocks": [
                self.COIN_BLOCK,
                *self._flip_coin(),
            ],
        }

</code></pre>

<p>Save and close the file.</p>

<p>Now that you have a Python class ready to do the work for your Slackbot, let&rsquo;s ensure that this class produces a useful message payload and that you can send it to your workspace.</p>

<h2 id="step-4-mdash-testing-your-message">Step 4 — Testing Your Message</h2>

<p>Now let&rsquo;s test that this class produces a proper payload. Create a file named<br>
<code>coinbot_test.py</code>:</p>
<pre class="code-pre custom_prefix prefixed"><code><ul class="prefixed"><li class="line" prefix="(slackbot)sammy@slackbotserver:$">nano coinbot_test.py
</li></ul></code></pre>
<p>Now add the following code. <strong>Be sure to change the channel name in the instantiation of the coinbot class <code>coin_bot = coinbot("#<span class="highlight">YOUR_CHANNEL_HERE</span>")</code></strong>. This code will create a Slack client in Python that will send a message to the channel you specify that you have already installed the app into:</p>
<div class="code-label " title="coinbot_test.py">coinbot_test.py</div><pre class="code-pre "><code class="code-highlight language-python">from slack import WebClient
from coinbot import CoinBot
import os

# Create a slack client

slack_web_client = WebClient(token=os.environ.get("SLACK_TOKEN"))

# Get a new CoinBot

coin_bot = CoinBot("#<span class="highlight">YOUR_CHANNEL_HERE</span>")

# Get the onboarding message payload

message = coin_bot.get_message_payload()

# Post the onboarding message in Slack

slack_web_client.chat_postMessage(\*\*message)
</code></pre>

<p>Save and close the file.</p>

<p>Before you can run this file you will need to export the Slack token that you saved in Step 1 as an environment variable:</p>
<pre class="code-pre custom_prefix prefixed"><code><ul class="prefixed"><li class="line" prefix="(slackbot)sammy@slackbotserver:$">export SLACK_TOKEN="<span class="highlight">your_bot_user_token</span>"
</li></ul></code></pre>
<p>Now test this file and verify that the payload is produced and sent by running the following script in your terminal. Make sure that your virtual environment is activated. You can verify this by seeing the <code>(slackbot)</code> text at the front of your bash prompt. Run this command you will receive a message from your Slackbot with the results of a coin flip:</p>
<pre class="code-pre custom_prefix prefixed"><code><ul class="prefixed"><li class="line" prefix="(slackbot)sammy@slackbotserver:$">python coinbot_test.py
</li></ul></code></pre>
<p>Check the channel that you installed your app into and verify that your bot did indeed send the coin flip message. Your result will be heads or tails.</p>

<p><img src="https://assets.digitalocean.com/articles/coinbot/NPfnw0k.png" alt="Coin Flip Test"></p>

<p>Now that you&rsquo;ve verified that your Slackbot can flip a coin, create a message, and deliver the message, let&rsquo;s create a <a href="https://flask.palletsprojects.com/en/1.1.x/">Flask</a> to perpetually run this app and make it simulate a coin flip and share the results whenever it sees certain text in messages sent in the channel.</p>

<h2 id="step-5-mdash-creating-a-flask-application-to-run-your-slackbot">Step 5 — Creating a Flask Application to Run Your Slackbot</h2>

<p>Now that you have a functioning application that can send messages to your Slack workspace, you need to create a long running process so your bot can listen to messages sent in the channel and reply to them if the text meets certain criteria. You&rsquo;re going to use the Python web framework <a href="https://flask.palletsprojects.com/en/1.1.x/">Flask</a> to run this process and listen for events in your channel.</p>

<p><span class='note'>In this section you will be running your Flask application from a server with a public IP address so that the Slack API can send you events. If you are running this locally on your personal workstation you will need to forward the port from your personal firewall to the port that will be running on your workstation. These ports can be the same, and this tutorial will be set up to use port <code>3000</code>.<br></span></p>

<p>First adjust your firewall settings to allow traffic through port <code>3000</code>:</p>
<pre class="code-pre custom_prefix prefixed"><code><ul class="prefixed"><li class="line" prefix="(slackbot)sammy@slackbotserver:$">sudo ufw allow 3000
</li></ul></code></pre>
<p>Now check the status of <code>ufw</code>:</p>
<pre class="code-pre custom_prefix prefixed"><code><ul class="prefixed"><li class="line" prefix="(slackbot)sammy@slackbotserver:$">sudo ufw status
</li></ul></code></pre>
<p>You will see an output like this:</p>
<pre class="code-pre "><code><div class="secondary-code-label " title="Output">Output</div>Status: active

To Action From

---

OpenSSH ALLOW Anywhere
3000 ALLOW Anywhere
OpenSSH (v6) ALLOW Anywhere (v6)
3000 (v6) ALLOW Anywhere (v6)
</code></pre>

<p>Now create the file for your Flask app. Name this file <code>app.py</code>:</p>
<pre class="code-pre custom_prefix prefixed"><code><ul class="prefixed"><li class="line" prefix="(slackbot)sammy@slackbotserver:$">touch app.py
</li></ul></code></pre>
<p>Next, open this file in your favorite text editor:</p>
<pre class="code-pre custom_prefix prefixed"><code><ul class="prefixed"><li class="line" prefix="(slackbot)sammy@slackbotserver:$">nano app.py
</li></ul></code></pre>
<p>Now add the following import <code>statements</code>. You&rsquo;ll import the following libraries for the following reasons:</p>

<ul>
<li><code>import os</code> - To access environment variables</li>
<li><code>import logging</code> - To log the events of the app</li>
<li><code>from flask import Flask</code> - To create a Flask app</li>
<li><code>from slack import WebClient</code> - To send messages via Slack</li>
<li><code>from slackeventsapi import SlackEventAdapter</code> - To receive events from Slack and process them</li>
<li><code>from coinbot import CoinBot</code> - To create an instance of your CoinBot and generate the message payload.</li>
</ul>

<p>Append the following lines to <code>app.py</code> to import all of the necessary libraries:</p>
<div class="code-label " title="app.py">app.py</div><pre class="code-pre "><code class="code-highlight language-python">import os
import logging
from flask import Flask
from slack import WebClient
from slackeventsapi import SlackEventAdapter
from coinbot import CoinBot
</code></pre>
<p>Now create your Flask app and register a Slack Event Adapter to your Slack app at the <code>/slack/events</code> endpoint. This will create a route in your Slack app where Slack events will be sent and ingested. To do this you will need to get another token from your Slack app, which you will do later in the tutorial. Once you get this variable you will export it as an environment variable named <code>SLACK_EVENTS_TOKEN</code>. Go ahead and write your code to read it in when creating the <code>SlackEventAdapter</code>, even though you haven&rsquo;t set the token yet.</p>

<p>Append the following lines to <code>app.py</code> to create the Flask app and register the events adapter into this app:</p>
<div class="code-label " title="app.py">app.py</div><pre class="code-pre "><code class="code-highlight language-python">...
# Initialize a Flask app to host the events adapter
app = Flask(__name__)

# Create an events adapter and register it to an endpoint in the slack app for event ingestion.

slack_events_adapter = SlackEventAdapter(os.environ.get("SLACK_EVENTS_TOKEN"), "/slack/events", app)
</code></pre>

<p>Next create a web client object that will allow your app to perform actions in the workspace, specifically to send messages. This is similar to what you did when you tested your <code>coinbot.py</code> file previously.</p>

<p>Append the following line to <code>app.py</code> to create this <code>slack_web_client</code>:</p>
<div class="code-label " title="app.py">app.py</div><pre class="code-pre "><code class="code-highlight language-python">...
# Initialize a Web API client
slack_web_client = WebClient(token=os.environ.get("SLACK_TOKEN"))
</code></pre>
<p>Now create a function that can be called that will create an instance of <code>CoinBot</code>, and then use this instance to create a message payload and pass the message payload to the Slack web client for delivery. This function will take in a single parameter, <code>channel</code>, which will specify what channel receives the message.</p>

<p>Append the following lines to <code>app.py</code> to create this function:</p>
<div class="code-label " title="app.py">app.py</div><pre class="code-pre "><code class="code-highlight language-python">...
def flip_coin(channel):
    """Craft the CoinBot, flip the coin and send the message to the channel
    """
    # Create a new CoinBot
    coin_bot = CoinBot(channel)

    # Get the onboarding message payload
    message = coin_bot.get_message_payload()

    # Post the onboarding message in Slack
    slack_web_client.chat_postMessage(**message)

</code></pre>

<p>Now that you have created a function to handle the messaging aspects of your app, create one that monitors Slack events for a certain action and then executes your bot. You&rsquo;re going to configure your app to respond with the results of a simulated coin flip when it sees the phrase &ldquo;Hey Sammy, Flip a coin&rdquo;. You&rsquo;re going to accept any version of this—case won&rsquo;t prevent the app from responding.</p>

<p>First decorate your function with the <code>@slack_events_adapter.on</code> syntax that allows your function to receive events. Specify that you only want the <code>message</code> events and have your function accept a payload parameter containing all of the necessary Slack information. Once you have this payload you will parse out the text and analyze it. Then, if it receives the activation phrase, your app will send the results of a simulated coin flip.</p>

<p>Append the following code to <code>app.py</code> to receive, analyze, and act on incoming messages:</p>
<div class="code-label " title="app.py">app.py</div><pre class="code-pre "><code class="code-highlight language-python"># When a 'message' event is detected by the events adapter, forward that payload
# to this function.
@slack_events_adapter.on("message")
def message(payload):
    """Parse the message event, and if the activation string is in the text,
    simulate a coin flip and send the result.
    """

    # Get the event data from the payload
    event = payload.get("event", {})

    # Get the text from the event that came through
    text = event.get("text")

    # Check and see if the activation phrase was in the text of the message.
    # If so, execute the code to flip a coin.
    if "hey sammy, flip a coin" in text.lower():
        # Since the activation phrase was met, get the channel ID that the event
        # was executed on
        channel_id = event.get("channel")

        # Execute the flip_coin function and send the results of
        # flipping a coin to the channel
        return flip_coin(channel_id)

</code></pre>

<p>Finally, create a <code>main</code> section that will create a logger so you can see the internals of your application as well as launch the app on your external IP address on port <code>3000</code>. In order to ingest the events from Slack, such as when a new message is sent, you must test your application on a public-facing IP address.</p>

<p>Append the following lines to <code>app.py</code> to set up your main section:</p>
<div class="code-label " title="app.py">app.py</div><pre class="code-pre "><code class="code-highlight language-python">if __name__ == "__main__":
    # Create the logging object
    logger = logging.getLogger()

    # Set the log level to DEBUG. This will increase verbosity of logging messages
    logger.setLevel(logging.DEBUG)

    # Add the StreamHandler as a logging handler
    logger.addHandler(logging.StreamHandler())

    # Run your app on your externally facing IP address on port 3000 instead of
    # running it on localhost, which is traditional for development.
    app.run(host='0.0.0.0', port=3000)

</code></pre>

<p>You are now finished with the Flask app and it is ready for testing. Before you move on verify that your finished file, <code>app.py</code> contains the following:</p>
<div class="code-label " title="app.py">app.py</div><pre class="code-pre "><code class="code-highlight language-python">import os
import logging
from flask import Flask
from slack import WebClient
from slackeventsapi import SlackEventAdapter
from coinbot import CoinBot

# Initialize a Flask app to host the events adapter

app = Flask(**name**)

# Create an events adapter and register it to an endpoint in the slack app for event injestion.

slack_events_adapter = SlackEventAdapter(os.environ.get("SLACK_EVENTS_TOKEN"), "/slack/events", app)

# Initialize a Web API client

slack_web_client = WebClient(token=os.environ.get("SLACK_TOKEN"))

def flip_coin(channel):
"""Craft the CoinBot, flip the coin and send the message to the channel
""" # Create a new CoinBot
coin_bot = CoinBot(channel)

    # Get the onboarding message payload
    message = coin_bot.get_message_payload()

    # Post the onboarding message in Slack
    slack_web_client.chat_postMessage(**message)

# When a 'message' event is detected by the events adapter, forward that payload

# to this function.

@slack_events_adapter.on("message")
def message(payload):
"""Parse the message event, and if the activation string is in the text,
simulate a coin flip and send the result.
"""

    # Get the event data from the payload
    event = payload.get("event", {})

    # Get the text from the event that came through
    text = event.get("text")

    # Check and see if the activation phrase was in the text of the message.
    # If so, execute the code to flip a coin.
    if "hey sammy, flip a coin" in text.lower():
        # Since the activation phrase was met, get the channel ID that the event
        # was executed on
        channel_id = event.get("channel")

        # Execute the flip_coin function and send the results of
        # flipping a coin to the channel
        return flip_coin(channel_id)

if **name** == "**main**": # Create the logging object
logger = logging.getLogger()

    # Set the log level to DEBUG. This will increase verbosity of logging messages
    logger.setLevel(logging.DEBUG)

    # Add the StreamHandler as a logging handler
    logger.addHandler(logging.StreamHandler())

    # Run our app on our externally facing IP address on port 3000 instead of
    # running it on localhost, which is traditional for development.
    app.run(host='0.0.0.0', port=3000)

</code></pre>

<p>Save and close the file.</p>

<p>Now that your Flask app is ready to serve your application let&rsquo;s test it out.</p>

<h2 id="step-6-mdash-running-your-flask-app">Step 6 — Running Your Flask App</h2>

<p>Finally, bring everything together and execute your app.</p>

<p>First, add your running application as an authorized handler for your Slackbot.</p>

<p>Navigate to the <strong>Basic Information</strong> section of your app in the <a href="https://api.slack.com">Slack UI</a>. Scroll down until you find the <strong>App Credentials</strong> section.</p>

<p><img src="https://assets.digitalocean.com/articles/coinbot/lLB1jEB.png" alt="Slack Signing Secret"></p>

<p>Copy the <strong>Signing Secret</strong> and export it as the environment variable <code>SLACK_EVENTS_TOKEN</code>:</p>
<pre class="code-pre custom_prefix prefixed"><code><ul class="prefixed"><li class="line" prefix="(slackbot)sammy@slackbotserver:$">export SLACK_EVENTS_TOKEN="<span class="highlight">MY_SIGNING_SECRET_TOKEN</span>"
</li></ul></code></pre>
<p>With this you have all the necessary API tokens to run your app. Refer to Step 1 if you need a refresher on how to export your <code>SLACK_TOKEN</code>. Now you can start your app and verify that it is indeed running. Ensure that your virtual environment is activated and run the following command to start your Flask app:</p>
<pre class="code-pre custom_prefix prefixed"><code><ul class="prefixed"><li class="line" prefix="(slackbot)sammy@slackbotserver:$">python3 app.py
</li></ul></code></pre>
<p>You will see an output like this:</p>
<pre class="code-pre "><code>(slackbot) [20:04:03] sammy:coinbot$ python app.py
 * Serving Flask app "app" (lazy loading)
 * Environment: production
   WARNING: This is a development server. Do not use it in a production deployment.
   Use a production WSGI server instead.
 * Debug mode: off
 * Running on http://0.0.0.0:3000/ (Press CTRL+C to quit)
</code></pre>
<p>To verify that your app is up, open a new terminal window and <code>curl</code> the IP address of your server with the correct port at <code>/slack/events</code>:</p>
<pre class="code-pre command prefixed"><code><ul class="prefixed"><li class="line" prefix="$">curl http://<span class="highlight">YOUR_IP_ADDRESS</span>:3000/slack/events
</li></ul></code></pre>
<p><code>curl</code> will return the following:</p>
<pre class="code-pre "><code><div class="secondary-code-label " title="Output">Output</div>These are not the slackbots you're looking for.
</code></pre>
<p>Receiving the message <code>These are not the slackbots you're looking for.</code>, indicates that your app is up and running.</p>

<p>Now leave this Flask application running while you finish configuring your app in the <a href="https://api.slack.com">Slack UI</a>.</p>

<p>First grant your app the appropriate permissions so that it can listen to messages and respond accordingly. Click on <strong>Event Subscriptions</strong> in the UI sidebar and toggle the <strong>Enable Events</strong> radio button.</p>

<p><img src="https://assets.digitalocean.com/articles/coinbot/lLB1jEB.png" alt="Enable Events Button"></p>

<p>Once you&rsquo;ve done that, type in your IP address, port, and <code>/slack/events</code> endpoint into the <strong>Request URL</strong> field. Don&rsquo;t forget the <code>HTTP</code> protocol prefix. Slack will make an attempt to connect to your endpoint. Once it has successfully done so you&rsquo;ll see a green check mark with the word <strong>Verified</strong> next to it.</p>

<p><img src="https://assets.digitalocean.com/articles/coinbot/9wqUJwd.png" alt="Event Subscriptions Request URL"></p>

<p>Next, expand the <strong>Subscribe to bot events</strong> and add the <code>message.channels</code> permission to your app. This will allow your app to receive messages from your channel and process them.</p>

<p><img src="https://assets.digitalocean.com/articles/coinbot/sCYYhM8.png" alt="Subscribe to bot events permissions"></p>

<p>Once you&rsquo;ve done this you will see the event listed in your <strong>Subscribe to bot events</strong> section. Next click the green <strong>Save Changes</strong> button in the bottom right hand corner.</p>

<p><img src="https://assets.digitalocean.com/articles/coinbot/NLNbmB4.png" alt="Confirm and Save changes"></p>

<p>Once you do this you&rsquo;ll see a yellow banner across the top of the screen informing you that you need to reinstall your app for the following changes to apply. Every time you change permissions you&rsquo;ll need to reinstall your app. Click on the <strong>reinstall your app</strong> link in this banner to reinstall your app.</p>

<p><img src="https://assets.digitalocean.com/articles/coinbot/s9WyZWs.png" alt="Reinstall your app banner"></p>

<p>You&rsquo;ll be presented with a confirmation screen summarizing the permissions your bot will have and asking if you want to allow its installation. Click on the green <strong>Allow</strong> button to finish the installation process.</p>

<p><img src="https://assets.digitalocean.com/articles/coinbot/KQrNqzK.png" alt="Reinstall confirmation"></p>

<p>Now that you&rsquo;ve done this your app should be ready. Go back to the channel that you installed <code>CoinBot</code> into and send a message containing the phrase <em>Hey Sammy, Flip a coin</em> in it. Your bot will flip a coin and reply with the results. Congrats! You&rsquo;ve created a Slackbot!</p>

<p><img src="https://assets.digitalocean.com/articles/coinbot/8SoSu5A.png" alt="Hey Sammy, Flip a coin"></p>

<h2 id="conclusion">Conclusion</h2>

<p>Once you are done developing your application and you are ready to move it to production, you&rsquo;ll need to deploy it to a server. This is necessary because the Flask development server is not a secure production environment. You&rsquo;ll be better served if you deploy your app using a <a href="https://wsgi.readthedocs.io/en/latest/index.html">WSGI</a> and maybe even securing a domain name and giving your server a DNS record. There are many options for deploying Flask applications, some of which are listed below:</p>

<ul>
<li><a href="https://www.digitalocean.com/community/tutorials/how-to-serve-flask-applications-with-gunicorn-and-nginx-on-ubuntu-20-04">Deploy your Flask application to Ubuntu 20.04 using Gunicorn and Nginx</a></li>
<li><a href="https://www.digitalocean.com/community/tutorials/how-to-serve-flask-applications-with-uwsgi-and-nginx-on-ubuntu-20-04">Deploy your Flask application to Ubuntu 20.04 using uWSGI and Nginx</a></li>
<li><a href="https://www.digitalocean.com/community/tutorials/how-to-build-and-deploy-a-flask-application-using-docker-on-ubuntu-18-04">Deploy your Flask Application Using Docker on Ubuntu 18.04</a></li>
</ul>

<p>There are many more ways to deploy your application than just these. As always, when it comes to deployments and infrastucture, do what works best for <em>you</em>.</p>

<p>In any case, you now have a Slackbot that you can use to flip a coin to help you make decisions, like what to eat for lunch.</p>

<p>You can also take this base code and modify it to fit your needs, whether it be automated support, resource management, pictures of cats, or whatever you can think of. You can view the complete Python Slack API docs <a href="https://slack.dev/python-slackclient/">here</a>.</p>
