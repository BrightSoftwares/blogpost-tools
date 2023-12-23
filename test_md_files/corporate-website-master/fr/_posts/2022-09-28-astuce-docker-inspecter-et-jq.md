---
author: Full
categories:
- docker
date: 2022-09-28
description: Ce n'est pas tant une astuce docker qu'une astuce jq. Si vous n'avez
  pas entendu parler de jq, c'est un excellent outil pour analyser JSON à partir de
  la ligne de commande. Cela en fait également un excellent outil pour voir ce qui
  se passe dans un conteneur au lieu d'avoir à utiliser le spécificateur
featured: true
image: https://res.cloudinary.com/brightsoftwares/image/upload/v1639560797/photo-1578403881636-6f4a77a6f9cc_ddsft1.jpg
lang: fr
layout: flexstart-blog-single
post_date: 2022-09-28
pretified: true
ref: inspectjq_1244
title: 'Astuce Docker : inspecter et jq'
seo:
  links: [ "https://m.wikidata.org/wiki/Q15206305" ]
---

# Docker inspecter et jq

Ce n'est pas tant une astuce docker qu'une astuce jq. Si vous n'avez pas entendu parler de jq, c'est un excellent outil pour analyser JSON à partir de la ligne de commande. Cela en fait également un excellent outil pour voir ce qui se passe dans un conteneur au lieu d'avoir à utiliser le spécificateur ```–format``` dont je ne me souviens jamais exactement comment utiliser :

## Obtenir des informations sur le réseau :

{% include codeHeader.html %}
{% raw %}
```
    $ docker inspect 4c45aea49180 | jq '.[].NetworkSettings.Networks'
```
{% endraw %}


La sortie est :

{% raw %}
```
    {
      "bridge": {
        "EndpointID": "ba1b6efba16de99f260e0fa8892fd4685dbe2f79cba37ac0114195e9fad66075",
        "Gateway": "172.17.0.1",
        "IPAddress": "172.17.0.2",
        "IPPrefixLen": 16,
        "IPv6Gateway": "",
        "GlobalIPv6Address": "",
        "GlobalIPv6PrefixLen": 0,
        "MacAddress": "02:42:ac:11:00:02"
      }
    }
    
```
{% endraw %}
   
 
## Récupère les arguments avec lesquels le conteneur a été démarré

{% include codeHeader.html %}
{% raw %}
```
    $ docker inspect 4c45aea49180 | jq '.[].Args'
```
{% endraw %}

La sortie est :

{% raw %}
```
    [
    "-server",
    "-advertise",
    "192.168.99.100",
    "-bootstrap-expect",
    "1"
    ]
```
{% endraw %}
    
    
## Obtenez tous les volumes montés
    
{% include codeHeader.html %}
{% raw %}
```
$ docker inspect 4c45aea49180 | jq '.[].Mounts'
```
{% endraw %}

Production


{% raw %}
```

    [
    {
    "Name": "a8125ffdf6c4be1db4464345ba36b0417a18aaa3a025267596e292249ca4391f",
    "Source": "/mnt/sda1/var/lib/docker/volumes/a8125ffdf6c4be1db4464345ba36b0417a18aaa3a025267596e292249ca4391f/_data",
    "Destination": "/data",
    "Driver": "local",
    "Mode": "",
    "RW": true
    }
    ]
```
{% endraw %}

    

Et bien sûr, cela fonctionne également très bien pour interroger d'autres types d'API (docker-esque) qui produisent du JSON (par exemple, Marathon, Mesos, Consul, etc.). JQ fournit une API très complète pour accéder et traiter JSON. Plus d'informations peuvent être trouvées ici: https://stedolan.github.io/jq/