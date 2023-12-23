---
ToReview: true
author: Full
categories:
- docker
date: 2022-12-14
description: "Cela en fait également un excellent outil pour voir ce qui se passe dans un conteneur au lieu d'avoir à utiliser le spécificateur -format dont je ne me souviens jamais exactement comment utiliser"
image: https://sergio.afanou.com/assets/images/image-midres-15.jpg
lang: fr
layout: flexstart-blog-single
post_date: 2022-12-14
pretified: true
ref: dockertip_inspectless_1245
tags:
- docker
- jq
- json
title: 'Astuce Docker : inspecter et moins'
seo:
  links: [ "https://m.wikidata.org/wiki/Q15206305" ]
---

# Docker inspecte et moins

Ce n'est pas tant une astuce [[2021-12-14-how-to-use-local-docker-images-with-minikube|docker]] qu'une astuce jq. Si vous n'avez pas entendu parler de [jq](https://stedolan.github.io/jq/), c'est un excellent outil pour analyser JSON à partir de la ligne de commande.

[[2020-04-03-top-5-questions-from-how-to-become-a-docker-power-user-session-at-dockercon-2020|Cet article]] pourrait également vous intéresser.

Cela en fait également un excellent outil pour voir ce qui se passe dans un conteneur au lieu d'avoir à utiliser le spécificateur -format dont je ne me souviens jamais exactement comment utiliser:

## Obtenir des informations sur le réseau :

Dans cet exemple, nous utiliserons jq pour afficher les données renvoyées par la commande inpect.

{% include codeHeader.html %}
{% raw %}
```
docker inspect 4c45aea49180 | jq '.[].NetworkSettings.Networks'
```
{% endraw %}

Voici le résultat que vous obtiendrez.

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



## Récupère les arguments avec lesquels le conteneur a été démarré

Dans celui-ci, nous aurons les arguments

{% include codeHeader.html %}
{% raw %}
```
docker inspect 4c45aea49180 | jq '.[].Args'
```
{% endraw %}


Vous obtenez ces résultats :

```
[
    "-server",
    "-advertise",
    "192.168.99.100",
    "-bootstrap-expect",
    "1"
]
```


## Obtenez tous les volumes montés

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



# Conclusion

Comme vous pouvez le voir, jq simplifie beaucoup la visualisation de vos données json.
Plus besoin de faire défiler les gros fichiers JSON.

Non seulement pour docker, cela fonctionne avec d'autres outils comme Marathon, Mesos, Consul etc.

Plus d'informations peuvent être trouvées ici: https://stedolan.github.io/jq/