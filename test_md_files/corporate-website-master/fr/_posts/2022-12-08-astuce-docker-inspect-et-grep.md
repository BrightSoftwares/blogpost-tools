---
ToReview: true
author: full
categories:
- docker
date: 2022-12-08
description: Ce n'est pas tant une astuce docker, qu'une astuce jq. Si vous n'avez
  pas entendu parler de jq, c'est un excellent outil pour analyser JSON à partir de
  la ligne de commande. Cela en fait également un excellent outil pour voir ce qui
  se passe dans un conteneur au lieu d'avoir à utiliser le spécificateur -format dont
  je ne me souviens jamais exactement comment utiliserCe n'est pas tant une astuce
  docker, qu'une astuce jq. Si vous n'avez pas entendu parler de jq, c'est un excellent
  outil pour analyser JSON à partir de la ligne de commande. Cela en fait également
  un excellent outil pour voir ce qui se passe dans un conteneur au lieu d'avoir à
  utiliser le spécificateur -format dont je ne me souviens jamais exactement comment
  utiliser
image: https://sergio.afanou.com/assets/images/image-midres-15.jpg
lang: fr
layout: flexstart-blog-single
pretified: true
ref: inspectgrepdocker_1243
title: 'Astuce Docker : inspect et grep'
seo:
  links: [ "https://m.wikidata.org/wiki/Q15206305" ]
---

### Docker inspecte et grep

Ce n'est pas tant une astuce [[2020-08-04-docker-tip-inspect-and-jq|docker]], qu'une astuce jq. Si vous n'avez pas entendu parler de jq, c'est un excellent outil pour analyser JSON à partir de la ligne de commande. Cela en fait également un excellent outil pour voir ce qui se passe dans un conteneur au lieu d'avoir à utiliser le spécificateur -format dont je ne me souviens jamais exactement comment utiliser:

    # Obtenir des informations sur le réseau :
    docker $ inspecter 4c45aea49180 | jq '.[].RéseauParamètres.Réseaux'
    {
      "pont": {
        "ID du point de terminaison": "ba1b6efba16de99f260e0fa8892fd4685dbe2f79cba37ac0114195e9fad66075",
        "Passerelle": "172.17.0.1",
        "AdresseIP": "172.17.0.2",
        "IPPrefixLen": 16,
        "Passerelle IPv6": "",
        "GlobalIPv6Address": "",
        "GlobalIPv6PrefixLen": 0,
        "MacAddress": "02:42:ac:11:00:02"
      }
    }
    
    # Récupère les arguments avec lesquels le conteneur a été démarré
    
    docker $ inspecter 4c45aea49180 | jq '.[].Args'
    [
    "-serveur",
    "-afficher",
    "192.168.99.100",
    "-bootstrap-attend",
    "1"
    ]
    
    # Obtenez tous les volumes montés
    
    11:22 docker $ inspecte 4c45aea49180 | jq '.[].Montages'
    [
    {
    "Nom": "a8125ffdf6c4be1db4464345ba36b0417a18aaa3a025267596e292249ca4391f",
    "Source": "/mnt/sda1/var/lib/docker/volumes/a8125ffdf6c4be1db4464345ba36b0417a18aaa3a025267596e292249ca4391f/_data",
    "Destination": "/données",
    "Pilote": "local",
    "Mode": "",
    "RW": vrai
    }
    ]
    

Et bien sûr, cela fonctionne également très bien pour interroger d'autres types d'API (docker-esque) qui produisent du JSON (par exemple, Marathon, Mesos, Consul, etc.). JQ fournit une API très complète pour accéder et traiter JSON. Plus d'informations peuvent être trouvées ici: https://stedolan.github.io/jq/