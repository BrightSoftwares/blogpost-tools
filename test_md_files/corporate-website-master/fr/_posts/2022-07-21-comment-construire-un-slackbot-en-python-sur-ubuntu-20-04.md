---
author: full
categories:
  - slack
date: 2022-07-21
description: "Slack est une plateforme de communication conçue pour la productivité au travail. Il comprend des fonctionnalités telles que la messagerie directe, les canaux publics et privés, les appels vocaux et vidéo et les intégrations de robots. Un Slackbot est un programme automatisé qui peut exécuter diverses fonctions dans Slack, de l'envoi de messages au déclenchement de tâches en passant par l'alerte sur certains événements."
featured: true
image: https://res.cloudinary.com/brightsoftwares/image/upload/t_BSBlogImage/v1656238946/pexels-kindel-media-8566526_hegdrb.jpg
lang: fr
layout: flexstart-blog-single
pretified: true
ref: slackbot_202007051234
tags:
- slack
- bot
- ubuntu
- python
title: Comment construire un Slackbot en Python sur Ubuntu 20.04
---

[Slack](https://slack.com/) est une plateforme de communication conçue pour la productivité au travail. Il comprend des fonctionnalités telles que la messagerie directe, les canaux publics et privés, les appels vocaux et vidéo et les intégrations de robots. Un Slackbot est un programme automatisé qui peut exécuter diverses fonctions dans Slack, de l'envoi de messages au déclenchement de tâches en passant par l'alerte sur certains événements.

Dans ce didacticiel, vous allez créer un Slackbot dans le langage de programmation [Python](https://www.python.org/). Python est un langage populaire qui se targue de simplicité et de lisibilité. Slack fournit une [API Python Slack](https://github.com/slackapi/python-slackclient) riche pour s'intégrer à Slack afin d'effectuer des tâches courantes telles que l'envoi de messages, l'ajout d'emojis aux messages, et bien plus encore. Slack fournit également une [API Python Slack Events](https://github.com/slackapi/python-slack-events-api) pour l'intégration aux événements dans Slack, vous permettant d'effectuer des actions sur des événements tels que des messages et des mentions.

En tant que preuve de concept amusante qui démontrera la puissance de Python et de ses API Slack, vous construirez un `CoinBot` - un Slackbot qui surveille un canal et, lorsqu'il est déclenché, lancera une pièce pour vous. Vous pouvez ensuite modifier votre `CoinBot` pour remplir n'importe quel nombre d'applications _légèrement_ plus pratiques.

Notez que ce tutoriel utilise Python 3 et n'est pas compatible avec Python 2.

## Conditions préalables

Pour suivre ce guide, vous aurez besoin de :

* Un espace de travail Slack dans lequel vous avez la possibilité d'installer des applications. Si vous avez créé l'espace de travail, vous avez cette possibilité. Si vous n'en avez pas déjà un, vous pouvez en créer un sur le ``[site Web de Slack](https://slack.com/create).``

* (Facultatif) Un serveur ou un ordinateur avec une adresse IP publique pour le développement. Nous recommandons une nouvelle installation d'Ubuntu 20.04, un utilisateur non root avec les privilèges "sudo" et SSH activé. [Vous pouvez suivre ce guide pour initialiser votre serveur et effectuer ces étapes](https://www.digitalocean.com/community/tutorials/initial-server-setup-with-ubuntu-20-04).

<span class="note">Vous pouvez tester ce didacticiel sur un serveur disposant d'une adresse IP publique. Slack devra pouvoir envoyer des événements tels que des messages à votre bot. Si vous testez sur une machine locale, vous devrez rediriger le trafic via votre pare-feu vers votre système local. Si vous cherchez un moyen de développer sur un serveur cloud, consultez ce tutoriel sur [Comment utiliser le code Visual Studio pour le développement à distance via le plugin Remote-SSH](https://www.digitalocean.com/community/tutorials /how-to-use-visual-studio-code-for-remote-development-via-the-remote-ssh-plugin).
</span>

## Étape 1 - Création du Slackbot dans l'interface utilisateur Slack

Créez d'abord votre application Slack dans le panneau de configuration de l'API Slack. Connectez-vous à votre espace de travail dans Slack via un navigateur Web et accédez au [Panneau de configuration de l'API] (https://api.slack.com/apps). Cliquez maintenant sur le bouton **Créer une application**.

![Créez votre application Slack](https://assets.digitalocean.com/articles/coinbot/h7VWJOX.png)

Ensuite, vous serez invité à entrer le nom de votre application et à sélectionner un espace de travail Slack de développement. Pour ce didacticiel, nommez votre application `<span class="highlight">CoinBot</span>` et sélectionnez un espace de travail auquel vous avez un accès administrateur. Une fois que vous avez fait cela, cliquez sur le bouton **Créer une application**.

![Nommez votre application Slack et sélectionnez un espace de travail](https://imgur.com/E4hnhMU.png)

Une fois votre application créée, le tableau de bord d'application par défaut suivant vous sera présenté. Ce tableau de bord vous permet de gérer votre application en définissant des autorisations, en vous abonnant à des événements, en installant l'application dans des espaces de travail, etc.

![Panneau d'application Slack par défaut](https://assets.digitalocean.com/articles/coinbot/ZjFaS1i.png)

Pour que votre application puisse publier des messages sur un canal, vous devez accorder à l'application les autorisations d'envoyer des messages. Pour ce faire, cliquez sur le bouton **Autorisations** dans le panneau de configuration.

![Sélectionnez le bouton Autorisations dans le panneau de configuration](https://assets.digitalocean.com/articles/coinbot/IVcN8qg.png)

Lorsque vous arrivez sur la page **OAuth & Permissions**, faites défiler vers le bas jusqu'à ce que vous trouviez la section **Scopes** de la page. Recherchez ensuite la sous-section **Bot Token Scopes** dans la portée et cliquez sur le bouton **Add an OAuth Scope**.

![Sélectionnez le bouton Ajouter une portée OAuth](https://assets.digitalocean.com/articles/coinbot/wQnTSQr.png)

Cliquez sur ce bouton puis tapez `chat:write`. Sélectionnez cette autorisation pour l'ajouter à votre bot. Cela permettra à l'application de publier des messages sur les canaux auxquels elle peut accéder. Pour plus d'informations sur les autorisations disponibles, consultez la [documentation de Slack](https://api.slack.com/scopes).

![Ajouter le chat : permission d'écriture](https://assets.digitalocean.com/articles/coinbot/unQYPeL.png)

Maintenant que vous avez ajouté l'autorisation appropriée, il est temps d'installer votre application dans votre espace de travail Slack. Remontez sur la page **OAuth et autorisations** et cliquez sur le bouton **Installer l'application sur l'espace de travail** en haut.

![Installer l'application sur l'espace de travail](https://assets.digitalocean.com/articles/coinbot/SiSxQB1.png)

Cliquez sur ce bouton et passez en revue les actions que l'application peut effectuer dans le canal. Une fois que vous êtes satisfait, cliquez sur le bouton **Autoriser** pour terminer l'installation.

![Installer l'application sur l'espace de travail](https://assets.digitalocean.com/articles/coinbot/lWUBsYR.png)

Une fois le bot installé, vous recevrez un **jeton d'accès OAuth de l'utilisateur du bot** que votre application pourra utiliser lorsque vous tenterez d'effectuer des actions dans l'espace de travail. Allez-y et copiez ce jeton ; vous en aurez besoin plus tard.

![Enregistrer le jeton d'accès](https://assets.digitalocean.com/articles/coinbot/m1M9Ilt.png)

Enfin, ajoutez votre bot nouvellement installé dans un canal de votre espace de travail. Si vous n'avez pas encore créé de canal, vous pouvez utiliser le canal _#general_ qui est créé par défaut dans votre espace de travail Slack. Localisez l'application dans la section **Applications** de la barre de navigation de votre client Slack et cliquez dessus. Une fois que vous avez fait cela, ouvrez le menu ** Détails ** en haut à droite. Si votre client Slack n'est pas en plein écran, il ressemblera à un "i" dans un cercle.

![Cliquez sur l'icône des détails de l'application](https://assets.digitalocean.com/articles/coinbot/OJ5yTXP.png)

Pour terminer l'ajout de votre application à un canal, cliquez sur le bouton **Plus** représenté par trois points dans la page de détails et sélectionnez **Ajouter cette application à un canal…**. Tapez votre chaîne dans le modal qui apparaît et cliquez sur **Ajouter**.

![Ajouter une application à un canal](https://assets.digitalocean.com/articles/coinbot/ojUMqeI.png)

Vous avez maintenant créé avec succès votre application et l'avez ajoutée à un canal dans votre espace de travail Slack. Après avoir écrit le code de votre application, celle-ci pourra publier des messages sur ce canal. Dans la section suivante, vous commencerez à écrire le code Python qui alimentera `CoinBot`.

## Étape 2 - Configuration de votre environnement de développement Python

Commençons par configurer votre environnement Python afin que vous puissiez développer le Slackbot.

Ouvrez un terminal et installez `python3` et les outils appropriés sur votre système :
```
    sudo apt install python3 python3-venv
``

Next you will create a virtual environment to isolate your Python packages from the system installation of Python. To do this, first create a directory into which you will create your virtual environment. Make a new directory at ``~/.venvs``:

``
    mkdir ~/.venvs
``

Now create your Python virtual environment:

``
    python3 -m venv ~/.venvs/slackbot
```

Ensuite, activez votre environnement virtuel afin de pouvoir utiliser son installation Python et ses packages d'installation :

``
    source ~/.venvs/slackbot/bin/activate
```

Your shell prompt will now show the virtual environment in parenthesis. It will look something like this:

Now use `pip` to install the necessary Python packages into your virtual environment:

``
    pip install slackclient slackeventsapi Flask
``

`slackclient` and `slackeventsapi` facilitate Python’s interaction with Slack’s APIs. `Flask` is a popular micro web framework that you will use to deploy your app:

Now that you have your developer environment set up, you can start writing your Python Slackbot:

## Step 3 — Creating the Slackbot Message Class in Python

Messages in Slack are sent via a [specifically formatted JSON payload](https://api.slack.com/reference/surfaces/formatting). This is an example of the JSON that your Slackbot will craft and send as a message:

``
    {
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
```

Vous pouvez créer manuellement ce JSON et l'envoyer, mais à la place, construisons une classe Python qui non seulement crée cette charge utile, mais simule également un tirage au sort.

Utilisez d'abord la commande `touch` pour créer un fichier nommé `coinbot.py` :

``
    toucher coinbot.py
``

Ensuite, ouvrez ce fichier avec `nano` ou votre éditeur de texte préféré :

``
    nano coinbot.py
``

Ajoutez maintenant les lignes de code suivantes pour importer les bibliothèques pertinentes pour votre application. La seule bibliothèque dont vous avez besoin pour cette classe est la bibliothèque "random" de la bibliothèque standard Python. Cette librairie va nous permettre de simuler un coin flip.

Ajoutez les lignes suivantes à `coinbot.py` pour importer toutes les bibliothèques nécessaires :

```
<div class="code-label " title="coinbot.py">coinbot.py</div>

    # import the random library to help us generate the random numbers
    import random
```


Ensuite, créez votre classe `CoinBot` et une instance de cette classe
pour fabriquer la charge utile du message. Ajoutez les lignes suivantes à `coinbot.py` pour créer la classe `CoinBot` :

``
<div class="code-label " title="coinbot.py">coinbot.py</div>

    ...
    classe CoinBot :
```

Now indent by one and create the constants, constructors, and methods necessary for your class. First let’s create the constant that will hold the base of your message payload. This section specifies that this constant is of the section type and that the text is formatted via markdown. It also specifies what text you wish to display. You can read more about the different payload options in the [official Slack message payload documentation](https://api.slack.com/reference/messaging/payload).

Append the following lines to `coinbot.py` to create the base template for the payload:

``
<div class="code-label " title="coinbot.py">coinbot.py</div>

    ...
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
```

Créez ensuite un constructeur pour votre classe afin de pouvoir créer une instance distincte de votre bot pour chaque requête. Ne vous inquiétez pas de la surcharge de mémoire ici; le ramasse-miettes Python nettoiera ces instances une fois qu'elles ne seront plus nécessaires. Ce code définit le canal destinataire en fonction d'un paramètre passé au constructeur.

Ajoutez les lignes suivantes à `coinbot.py` pour créer le constructeur :

``
<div class="code-label " title="coinbot.py">coinbot.py</div>

```
# Le constructeur de la classe. Il prend le nom du canal comme a
# paramètre et le définit comme une variable d'instance.
def __init__(soi, canal):
	self.canal = canal
```


Now write the code that simulates to flip a coin. We’ll randomly generate a one or zero, representing heads or tails respectively.

Append the following lines to `coinbot.py` to simulate the coin flip and return the crafted payload:

```
<div class="code-label " title="coinbot.py">coinbot.py</div>

    ...
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
```

Finally, create a method that crafts and returns the entire message payload, including the data from your constructor, by calling your `_flip_coin` method.

Append the following lines to `coinbot.py` to create the method that will generate the finished payload:

``
<div class="code-label " title="coinbot.py">coinbot.py</div>

```
        # Craft and return the entire message payload as a dictionary.
        def get_message_payload(self):
            return {
                "channel": self.channel,
                "blocks": [
                    self.COIN_BLOCK,
                    *self._flip_coin(),
                ],
            }
```

You are now finished with the `CoinBot` class and it is ready for testing. Before continuing, verify that your finished file, `coinbot.py`, contains the following:

``
<div class="code-label " title="coinbot.py">coinbot.py</div>
```
    # import the random library to help us generate the random numbers
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
```

Save and close the file.

Now that you have a Python class ready to do the work for your Slackbot, let’s ensure that this class produces a useful message payload and that you can send it to your workspace.

## Step 4 — Testing Your Message

Now let’s test that this class produces a proper payload. Create a file named  
`coinbot_test.py`:

```
    nano coinbot_test.py
```

Ajoutez maintenant le code suivant. **Assurez-vous de changer le nom du canal dans l'instanciation de la classe coinbot `coin_bot = coinbot("#<span class="highlight">YOUR_CHANNEL_HERE</span>")`**. Ce code créera un client Slack en Python qui enverra un message au canal que vous spécifiez et dans lequel vous avez déjà installé l'application :


coinbot_test.py

à partir du mou importer WebClient
de coinbot importer CoinBot
importer le système d'exploitation

```

# Créer un client mou

slack_web_client = WebClient(token=os.environ.get("SLACK_TOKEN"))

# Obtenez un nouveau CoinBot

coin_bot = CoinBot("#VOTRE_CANAL_ICI")

# Obtenir la charge utile du message d'intégration

message = coin_bot.get_message_payload()

# Publier le message d'intégration dans Slack

slack_web_client.chat_postMessage(\*\*message)

```

Enregistrez et fermez le fichier.

Avant de pouvoir exécuter ce fichier, vous devrez exporter le jeton Slack que vous avez enregistré à l'étape 1 en tant que variable d'environnement :

    export SLACK_TOKEN="your_bot_user_token"

Testez maintenant ce fichier et vérifiez que la charge utile est produite et envoyée en exécutant le script suivant dans votre terminal. Assurez-vous que votre environnement virtuel est activé. Vous pouvez le vérifier en voyant le texte `(slackbot)` au début de votre invite bash. Courircette commande, vous recevrez un message de votre Slackbot avec les résultats d'un tirage au sort :

    python coinbot_test.py

Vérifiez le canal sur lequel vous avez installé votre application et vérifiez que votre bot a bien envoyé le message de pile ou face. Votre résultat sera pile ou face.

![Coin Flip Test](https://assets.digitalocean.com/articles/coinbot/NPfnw0k.png)

Maintenant que vous avez vérifié que votre Slackbot peut lancer une pièce, créer un message et transmettre le message, créons un [Flask](https://flask.palletsprojects.com/en/1.1.x/) à exécuter en permanence cette application et lui faire simuler un tirage au sort et partager les résultats chaque fois qu'il voit un certain texte dans les messages envoyés dans le canal.

## Étape 5 - Création d'une application Flask pour exécuter votre Slackbot

Maintenant que vous disposez d'une application fonctionnelle capable d'envoyer des messages à votre espace de travail Slack, vous devez créer un long processus afin que votre bot puisse écouter les messages envoyés dans le canal et y répondre si le texte répond à certains critères. Vous allez utiliser le framework Web Python [Flask](https://flask.palletsprojects.com/en/1.1.x/) pour exécuter ce processus et écouter les événements de votre canal.

<span class="note">Dans cette section, vous exécuterez votre application Flask à partir d'un serveur avec une adresse IP publique afin que l'API Slack puisse vous envoyer des événements. Si vous l'exécutez localement sur votre poste de travail personnel, vous devrez rediriger le port de votre pare-feu personnel vers le port qui s'exécutera sur votre poste de travail. Ces ports peuvent être identiques et ce didacticiel sera configuré pour utiliser le port "3000".
</span>

Ajustez d'abord les paramètres de votre pare-feu pour autoriser le trafic via le port "3000" :

``
    sudo ufw autoriser 3000
``

Vérifiez maintenant le statut de `ufw` :

``
    statut sudo ufw
``

Vous verrez une sortie comme celle-ci :

``
    Statut de sortie : actif

    À l'action de

    ---

    OpenSSH AUTORISER n'importe où
    3000 AUTORISER n'importe où
    OpenSSH (v6) AUTORISER n'importe où (v6)
    3000 (v6) AUTORISER n'importe où (v6)
``

Créez maintenant le fichier pour votre application Flask. Nommez ce fichier `app.py` :

``
    toucher app.py
``

Ensuite, ouvrez ce fichier dans votre éditeur de texte préféré :

``
    nano app.py
``

Ajoutez maintenant les "instructions" d'importation suivantes. Vous allez importer les bibliothèques suivantes pour les raisons suivantes :

```
*   `import os` - To access environment variables
*   `import logging` - To log the events of the app
*   `from flask import Flask` - To create a Flask app
*   `from slack import WebClient` - To send messages via Slack
*   `from slackeventsapi import SlackEventAdapter` - To receive events from Slack and process them
*   `from coinbot import CoinBot` - To create an instance of your CoinBot and generate the message payload.
```

Ajoutez les lignes suivantes à `app.py` pour importer toutes les bibliothèques nécessaires :

```
<div class="code-label " title="app.py">app.py</div>

    import os
    import logging
    from flask import Flask
    from slack import WebClient
    from slackeventsapi import SlackEventAdapter
    from coinbot import CoinBot
```

Créez maintenant votre application Flask et enregistrez un adaptateur d'événements Slack dans votre application Slack au point de terminaison `/slack/events`. Cela créera un itinéraire dans votre application Slack où les événements Slack seront envoyés et ingérés. Pour ce faire, vous devrez obtenir un autre jeton de votre application Slack, ce que vous ferez plus tard dans le didacticiel. Une fois que vous aurez obtenu cette variable, vous l'exporterez en tant que variable d'environnement nommée `SLACK_EVENTS_TOKEN`. Allez-y et écrivez votre code pour le lire lors de la création du `SlackEventAdapter`, même si vous n'avez pas encore défini le jeton.

Ajoutez les lignes suivantes à `app.py` pour créer l'application Flask et enregistrer l'adaptateur d'événements dans cette application :

``
<div class="code-label " title="app.py">app.py</div>

```
    # Initialiser une application Flask pour héberger l'adaptateur d'événements
    app = flacon (__nom__)

    # Créez un adaptateur d'événements et enregistrez-le sur un point de terminaison dans l'application Slack pour l'ingestion d'événements.

    slack_events_adapter = SlackEventAdapter(os.environ.get("SLACK_EVENTS_TOKEN"), "/slack/events", app)
```

Next create a web client object that will allow your app to perform actions in the workspace, specifically to send messages. This is similar to what you did when you tested your `coinbot.py` file previously.

Append the following line to `app.py` to create this `slack_web_client`:

```
<div class="code-label " title="app.py">app.py</div>

    ...
    # Initialiser un client API Web
    slack_web_client = WebClient(token=os.environ.get("SLACK_TOKEN"))
```

Now create a function that can be called that will create an instance of `CoinBot`, and then use this instance to create a message payload and pass the message payload to the Slack web client for delivery. This function will take in a single parameter, `channel`, which will specify what channel receives the message.

Append the following lines to `app.py` to create this function:

``
<div class="code-label " title="app.py">app.py</div>

```
    def flip_coin(channel):
        """Craft the CoinBot, flip the coin and send the message to the channel
        """
        # Create a new CoinBot
        coin_bot = CoinBot(channel)

        # Get the onboarding message payload
        message = coin_bot.get_message_payload()

        # Post the onboarding message in Slack
        slack_web_client.chat_postMessage(**message)
```


Maintenant que vous avez créé une fonction pour gérer les aspects de messagerie de votre application, créez-en une qui surveille les événements Slack pour une certaine action, puis exécute votre bot. Vous allez configurer votre application pour qu'elle réponde avec les résultats d'un lancer de pièce simulé lorsqu'elle voit la phrase "Hey Sammy, lancez une pièce". Vous allez accepter n'importe quelle version de ce cas - le cas n'empêchera pas l'application de répondre.

Commencez par décorer votre fonction avec la syntaxe `@slack_events_adapter.on` qui permet à votre fonction de recevoir des événements. Spécifiez que vous ne voulez que les événements `message` et que votre fonction accepte un paramètre de charge utile contenant toutes les informations Slack nécessaires. Une fois que vous avez cette charge utile, vous analyserez le texte et l'analyserez. Ensuite, si elle reçoit la phrase d'activation, votre application enverra les résultats d'un tirage au sort simulé.

Ajoutez le code suivant à `app.py` pour recevoir, analyser et agir sur les messages entrants :

``
<div class="code-label " title="app.py">app.py</div>

```
    # Lorsqu'un événement 'message' est détecté par l'adaptateur d'événements, transférez cette charge utile
    # à cette fonction.
    @slack_events_adapter.on("message")
    def message (charge utile):
        """Analysez l'événement de message, et si la chaîne d'activation est dans le texte,
        simuler un tirage au sort et envoyer le résultat.
        """

        # Obtenir les données d'événement à partir de la charge utile
        événement = charge utile.get("événement", {})

        # Obtenez le texte de l'événement qui s'est produit
        texte = événement.get("texte")

        # Vérifiez et voyez si la phrase d'activation était dans le texte du message.
        # Si oui, exécutez le code pour lancer une pièce.
        si "hey sammy, lancez une pièce" dans text.lower() :
            # Puisque la phrase d'activation a été rencontrée, obtenez l'ID de canal que l'événement
            # a été exécuté le
            channel_id = event.get("canal")

            # Exécutez la fonction flip_coin et envoyez les résultats de
            # lancer une pièce sur le canal
            retourner flip_coin(channel_id)
```

Enfin, créez une section "principale" qui créera un enregistreur afin que vous puissiez voir les composants internes de votre application et lancer l'application sur votre adresse IP externe sur le port "3000". Afin d'ingérer les événements de Slack, comme lorsqu'un nouveau message est envoyé, vous devez tester votre application sur une adresse IP publique.

Ajoutez les lignes suivantes à `app.py` pour configurer votre section principale :

``
<div class="code-label " title="app.py">app.py</div>

```
    si __nom__ == "__main__":
        # Créer l'objet de journalisation
        logger = logging.getLogger()

        # Définissez le niveau de journalisation sur DEBUG. Cela augmentera la verbosité des messages de journalisation
        logger.setLevel(logging.DEBUG)

        # Ajoutez le StreamHandler en tant que gestionnaire de journalisation
        logger.addHandler(logging.StreamHandler())

        # Exécutez votre application sur votre adresse IP externe sur le port 3000 au lieu de
        # l'exécutant sur localhost, ce qui est traditionnel pour le développement.
        app.run(hôte='0.0.0.0', port=3000)
```


You are now finished with the Flask app and it is ready for testing. Before you move on verify that your finished file, `app.py` contains the following:

``
<div class="code-label " title="app.py">app.py</div>

```
    import os
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
```


Save and close the file.

Now that your Flask app is ready to serve your application let’s test it out.

## Step 6 — Running Your Flask App

Finally, bring everything together and execute your app.

First, add your running application as an authorized handler for your Slackbot.

Navigate to the **Basic Information** section of your app in the [Slack UI](https://api.slack.com). Scroll down until you find the **App Credentials** section.

![Slack Signing Secret](https://assets.digitalocean.com/articles/coinbot/lLB1jEB.png)

Copy the **Signing Secret** and export it as the environment variable `SLACK_EVENTS_TOKEN`:

``
    export SLACK_EVENTS_TOKEN="MY_SIGNING_SECRET_TOKEN"
``

With this you have all the necessary API tokens to run your app. Refer to Step 1 if you need a refresher on how to export your `SLACK_TOKEN`. Now you can start your app and verify that it is indeed running. Ensure that your virtual environment is activated and run the following command to start your Flask app:

```
    python3 app.py
```

You will see an output like this:

``
    (slackbot) [20:04:03] sammy:coinbot$ python app.py
     * Serving Flask app "app" (lazy loading)
     * Environment: production
       WARNING: This is a development server. Do not use it in a production deployment.
       Use a production WSGI server instead.
     * Debug mode: off
     * Running on http://0.0.0.0:3000/ (Press CTRL+C to quit)



Pour vérifier que votre application est opérationnelle, ouvrez une nouvelle fenêtre de terminal et `curl` l'adresse IP de votre serveur avec le port correct à `/slack/events` :

```
    curl http://YOUR_IP_ADDRESS:3000/slack/events
```


`curl` renverra ce qui suit :

    Sortie Ce ne sont pas les slackbots que vous recherchez.

La réception du message "Ce ne sont pas les slackbots que vous recherchez." indique que votre application est opérationnelle.

Maintenant, laissez cette application Flask en cours d'exécution pendant que vous terminez la configuration de votre application dans [l'interface utilisateur Slack] (https://api.slack.com).

Accordez d'abord à votre application les autorisations appropriées afin qu'elle puisse écouter les messages et répondre en conséquence. Cliquez sur **Abonnements aux événements** dans la barre latérale de l'interface utilisateur et activez le bouton radio **Activer les événements**.

![Activer le bouton des événements](https://assets.digitalocean.com/articles/coinbot/lLB1jEB.png)

Une fois que vous avez fait cela, saisissez votre adresse IP, votre port et le point de terminaison `/slack/events` dans le champ **Request URL**. N'oubliez pas le préfixe de protocole "HTTP". Slack tentera de se connecter à votre point de terminaison. Une fois que cela a été fait avec succès, vous verrez une coche verte avec le mot **Verified** à côté.

![URL de demande d'abonnement aux événements](https://assets.digitalocean.com/articles/coinbot/9wqUJwd.png)

Ensuite, développez **S'abonner aux événements du bot** et ajoutez l'autorisation "message.channels" à votre application. Cela permettra à votre application de recevoir des messages de votre canal et de les traiter.

![S'abonner aux autorisations des événements du bot](https://assets.digitalocean.com/articles/coinbot/sCYYhM8.png)

Une fois que vous avez fait cela, vous verrez l'événement répertorié dans votre section **S'abonner aux événements du bot**. Cliquez ensuite sur le bouton vert **Enregistrer les modifications** dans le coin inférieur droit.

![Confirmer et enregistrer les modifications](https://assets.digitalocean.com/articles/coinbot/NLNbmB4.png)

Une fois que vous avez fait cela, vous verrez une bannière jaune en haut de l'écran vous informant que vous devez réinstaller votre application pour que les modifications suivantes s'appliquent. Chaque fois que vous modifiez les autorisations, vous devrez réinstaller votre application. Cliquez sur le lien **réinstaller votre application** dans cette bannière pour réinstaller votre application.

![Réinstallez la bannière de votre application](https://assets.digitalocean.com/articles/coinbot/s9WyZWs.png)

Un écran de confirmation résumant les autorisations dont disposera votre bot et vous demandant si vous souhaitez autoriser son installation s'affichera. Cliquez sur le bouton vert **Autoriser** pour terminer le processus d'installation.

![Confirmation de réinstallation](https://assets.digitalocean.com/articles/coinbot/KQrNqzK.png)

Maintenant que vous avez fait cela, votre application devrait être prête. Revenez au canal sur lequel vous avez installé `CoinBot` et envoyez un message contenant la phrase _Hey Sammy, Flip a coin_. Votre bot lancera une pièce et répondra avec les résultats. Félicitations! Vous avez créé un Slackbot !

![Hey Sammy, lancez une pièce](https://assets.digitalocean.com/articles/coinbot/8SoSu5A.png)

## Conclusion

Une fois que vous avez terminé de développer votre application et que vous êtes prêt à la mettre en production, vous devrez la déployer sur un serveur. Cela est nécessaire car le serveur de développement Flask n'est pas un environnement de production sécurisé. Vous serez mieux servi si vous déployez votre application en utilisant un [WSGI](https://wsgi.readthedocs.io/en/latest/index.html) et peut-être même en sécurisant un nom de domaine et en donnant à votre serveur un enregistrement DNS. Il existe de nombreuses options pour déployer des applications Flask, dont certaines sont répertoriées ci-dessous :

* [Déployez votre application Flask sur Ubuntu 20.04 en utilisant Gunicorn et Nginx](https://www.digitalocean.com/community/tutorials/how-to-serve-flask-applications-with-gunicorn-and-nginx-on-ubuntu-20-04)
* [Déployez votre application Flask sur Ubuntu 20.04 en utilisant uWSGI et Nginx](https://www.digitalocean.com/community/tutorials/how-to-serve-flask-applications-with-uwsgi-and-nginx-on-ubuntu -20-04)
* [Déployez votre application Flask à l'aide de Docker sur Ubuntu 18.04](https://www.digitalocean.com/community/tutorials/how-to-build-and-deploy-a-flask-application-using-docker-on-ubuntu -18-04)

Il existe de nombreuses autres façons de déployer votre application que celles-ci. Comme toujours, lorsqu'il s'agit de déploiements et d'infrastructures, faites ce qui fonctionne le mieux pour _vous_.

Dans tous les cas, vous avez maintenant un Slackbot que vous pouvez utiliser pour lancer une pièce afin de vous aider à prendre des décisions, comme quoi manger pour le déjeuner.

Vous pouvez également prendre ce code de base et le modifier en fonction de vos besoins, qu'il s'agisse d'un support automatisé, de la gestion des ressources, d'images de chats ou de tout ce à quoi vous pouvez penser. Vous pouvez consulter la documentation complète de l'API Python Slack [ici](https://slack.dev/python-slackclient/).
