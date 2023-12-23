---
author: full
categories:
- kubernetes
date: 2021-12-10 13:28:16.611000+00:00
description: There are several APIs in Kubernetes. A ConfigMap is one of these. It
  is an object which helps to storing some non-confidential data. The data is in the
  form of key-value pairs. Some use envrionment variables. In this blog post, we will
  see how you can show multi-value lines. Working with Kubernetes Helm, I went to
  the documentation.
image: https://sergio.afanou.com/assets/images/image-midres-25.jpg
lang: en
layout: flexstart-blog-single
ref: KubernetesHelmhowtoshowMultilineProperties
seo:
  links:
  - https://www.wikidata.org/wiki/Q22661306
silot_terms: container docker kubernetes
tags:
- helm
- automation
- docker
- container
title: Multiline Properties in kubernetes Helm with ConfigMaps
toc: true
---

There are several APIs in [[2020-08-12-play-with-kubernetes-with-minikube|Kubernetes]]. A ConfigMap is one of these. It is an object which helps to storing some non-confidential data. The data is in the form of key-value pairs. Some [[2021-12-14-how-to-use-local-docker-images-with-minikube|use]] envrionment variables. In this blog post, we will see how you can show multi-value lines. 

Working with [[2023-04-04-should-a-docker-container-run-as-root-or-user.md|Kubernetes Helm]], I went to the documentation. The link to the documentation is [here](https://helm.sh/docs/chart_template_guide/accessing_files/). 

In [[2023-12-18-understanding-helm-chart-structure-for-easier-deployment|Helm]]'s v3 documentation, in the section **Accessing [[2022-07-28-how-to-copy-files-from-host-to-docker-container|Files]] Inside Templates**, you have an [[2023-08-25-docker-exec-bash-example|example]] of 3 properties (toml) [[2022-07-28-how-to-copy-files-from-host-to-docker-container|files]]; where each file has only one key/value pair.



The configmap.yaml looks like this. It contains one config.toml for simplicity.


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


I was happy with it. Then I add a second line to the config.toml file.



config.toml
```


replicaCount=1
foo=bar
```


Then boom, I get an Error: 

```
INSTALLATION FAILED: YAML parse error on deploy/templates/configmap.yaml: error converting YAML to JSON: yaml: line 9: could not find expected ':'
```

Digging in this error, I found a solution.

## The solution

[[2022-01-11-how-to-fix-cannot-tcp-connect-from-outside-virtual-machine-network-traffic-not-forwarded-to-service-port|Helm]] will read in that file, but as it is a text __templating engine__,  It does not understand that I was trying to [[2023-12-22-convert-docker-compose-to-kubernetes|compose]] a YAML file.

As a consquence, it was not helping me in the error. 

That's actually why you will see so many, many templates in the wild with 

{% raw %}
```{{ .thing | indent 8 }}``` 
{% endraw %}

or 

{% raw %}
```{{ .otherThing | toYaml }}``` 
{% endraw %}

-- because you need to help [[2023-11-01-helm-charts-the-package-manager-for-kubernetes|Helm]] know in what context it is emitting the text.



So, in my specific case, I needed to indent the filter with a value of 4 because mycurrent template has two spaces for the key indent level, and two more spaces for the value block scalar


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


I hope this quick post will help someone in his research.
[[2023-12-15-release-management-with-tiller-in-helm-version-2|Helm]] is a very powerfull tool in the [[2020-08-13-work-with-kubernetes-with-minikube|Kubernetes]] world. It is very useful when [[2020-04-03-how-to-set-up-the-codeserver-cloud-ide-platform-on-digitalocean-kubernetes|building code-server on Digital Ocean]].

Inspiration from [this post](https://stackoverflow.com/questions/70297885/helms-v3-example-doesnt-show-multi-line-properties-get-yaml-to-json-parse-err).