---
author: full
categories:
- kubernetes
date: 2022-07-28
description: "Il existe plusieurs API dans Kubernetes. Un ConfigMap est l'un d'entre eux. C'est un objet qui permet de stocker certaines données non confidentielles. Les données se présentent sous la forme de paires clé-valeur. Certains utilisent des variables d'environnement. Dans cet article de blog, nous verrons comment vous pouvez afficher des lignes à valeurs multiples."
image: https://res.cloudinary.com/brightsoftwares/image/upload/t_BSBlogImage/v1656239545/pexels-kimani-marley-12355827_am1jzp.jpg
lang: fr
layout: flexstart-blog-single
pretified: true
ref: KubernetesHelmhowtoshowMultilineProperties
tags:
- helm
- automation
- docker
- container
title: Propriétés multilignes dans kubernetes Helm avec ConfigMaps
seo:
  links: [ "https://www.wikidata.org/wiki/Q22661306" ]
---

Il existe plusieurs API dans Kubernetes. Un ConfigMap est l'un d'entre eux. C'est un objet qui permet de stocker certaines données non confidentielles. Les données se présentent sous la forme de paires clé-valeur. Certains utilisent des variables d'environnement. Dans cet article de blog, nous verrons comment vous pouvez afficher des lignes à valeurs multiples.

En travaillant avec Kubernetes Helm, je suis allé à la documentation. Le lien vers la documentation est [ici](https://helm.sh/docs/chart_template_guide/accessing_files/).

Dans la documentation de Helm v3, dans la section **Accessing Files Inside Templates**, vous avez un exemple de 3 fichiers de propriétés (toml) ; où chaque fichier n'a qu'une seule paire clé/valeur.



Le configmap.yaml ressemble à ceci. Il contient un config.toml pour plus de simplicité.


{% raw %}
```
apiVersion: v1
kind: ConfigMap
metadata:
  name: {{ .Release.Name }}-config
data:
  {{- $files := .Files }}
  {{- range tuple "config.toml" }}
  {{ . }}: |-
    {{ $files.Get . }}
  {{- end }}
```
{% endraw %}


J'en étais content. Ensuite, j'ajoute une deuxième ligne au fichier config.toml.



config.toml
```


replicaCount=1
foo=bar
```


Alors boum, j'obtiens une erreur :

```
INSTALLATION FAILED: YAML parse error on deploy/templates/configmap.yaml: error converting YAML to JSON: yaml: line 9: could not find expected ':'
```

En creusant dans cette erreur, j'ai trouvé une solution.

## La solution

Helm lira dans ce fichier, mais comme il s'agit d'un __moteur de création de modèles__ de texte, il ne comprend pas que j'essayais de composer un fichier YAML.

Par conséquent, cela ne m'aidait pas dans l'erreur.

C'est en fait pourquoi vous verrez tant de modèles dans la nature avec

{% raw %}
```{{ .thing | indent 8 }}```
{% endraw %}

ou

{% raw %}
```{{ .otherThing | toYaml }}```
{% endraw %}

-- parce que vous devez aider Helm à savoir dans quel contexte il émet le texte.



Donc, dans mon cas spécifique, j'avais besoin d'indenter le filtre avec une valeur de 4 car mon modèle actuel a deux espaces pour le niveau d'indentation de la clé et deux autres espaces pour le scalaire du bloc de valeur


{% raw %}
```
data:

  {{- $files := .Files }}
  {{- range tuple "config.toml" }}
  {{ . }}: |-
{{ $files.Get . | indent 4 }}
{{/* notice this ^^^ template expression is flush left,
because the 'indent' is handling whitespace, not the golang template itself */}}
  {{- end }}
```
{% endraw %}


J'espère que ce post rapide aidera quelqu'un dans ses recherches.

Inspiration de [ce post](https://stackoverflow.com/questions/70297885/helms-v3-example-doesnt-show-multi-line-properties-get-yaml-to-json-parse-err).