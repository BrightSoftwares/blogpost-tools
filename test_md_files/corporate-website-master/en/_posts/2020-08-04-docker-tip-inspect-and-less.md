---
ToReview: true
author: Full
categories:
- docker
description: This isn’t so much a docker tip, as it is a jq tip. If you haven’t heard
  of jq, it is a great tool for parsing JSON from the command line. This also makes
  it a great tool to see what is happening in a container instead of having to use
  the –format specifier which I can never remember how to use exactly
image: https://sergio.afanou.com/assets/images/image-midres-15.jpg
lang: en
layout: flexstart-blog-single
ref: dockertip_inspectless_1245
seo:
  links:
  - https://m.wikidata.org/wiki/Q15206305
silot_terms: devops pipeline
tags:
- docker
- jq
- json
title: 'Docker tip : inspect and less'
toc: true
---

# Docker inspect and less

This isn’t so much a [[2021-12-14-how-to-use-local-docker-images-with-minikube|docker]] [[2020-08-04-docker-tip-inspect-and-grep|tip]], as it is a jq [[2020-08-04-docker-tip-inspect-and-jq|tip]]. If you haven’t heard of [jq](https://stedolan.github.io/jq/), it is a great tool for parsing JSON from the command line. 

[[2020-04-03-top-5-questions-from-how-to-become-a-docker-power-user-session-at-dockercon-2020|This post]] might also interest you. 

This also makes it a great tool to see what is happening in a [[2022-09-21-how-do-you-ping-a-docker-container-from-the-outside|container]] instead of having to [[2022-07-27-jenkins-ci-pipeline-scripts-not-permitted-to-use-method-groovy-lang-groovyobject|use]] the –format specifier which I can never remember how to use exactly:

## Get network information:

In this example, we will use jq to view the data returned by the inpect command.

{% include codeHeader.html %}
{% raw %}
```
docker inspect 4c45aea49180 | jq '.[].NetworkSettings.Networks'
```
{% endraw %}

Here is the result you will get.

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



## Get the arguments with which the container was started

In this one we will get the arguments

{% include codeHeader.html %}
{% raw %}
```
docker inspect 4c45aea49180 | jq '.[].Args'
```
{% endraw %}


You get these results :

```
[
    "-server",
    "-advertise",
    "192.168.99.100",
    "-bootstrap-expect",
    "1"
]
```


## Get all the mounted volumes

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

As you can see, jq simplifes a lot the viewing of your json data. 
No more scrolling through large json.

Not only for [[2022-07-21-how-to-run-jenkins-jobs-with-docker|docker]], it works with other tools like  Marathon, Mesos, Consul etc.

More information can be found here: https://stedolan.github.io/jq/