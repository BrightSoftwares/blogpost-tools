---
layout: flexstart-blog-single
title: "Docker tip : inspect and jq"
author: full
lang: fr
ref: inspectjq_1244
categories: [docker]
description: "This isn’t so much a docker tip, as it is a jq tip. If you haven’t heard of jq, it is a great tool for parsing JSON from the command line. This also makes it a great tool to see what is happening in a container instead of having to use the –format specifier which I can never remember how to use exactly"
image: "https://sergio.afanou.com/assets/images/image-midres-55.jpg"
featured: true
seo:
  links: [ "https://m.wikidata.org/wiki/Q15206305" ]
---

<h3>Docker inspect and jq</h3>

<p>This isn’t so much a docker tip, as it is a jq tip. If you haven’t heard of jq, it is a great tool for parsing JSON from the command line. This also makes it a great tool to see what is happening in a container instead of having to use the –format specifier which I can never remember how to use exactly:</p>

<div class="highlighter-rouge"><div class="highlight"><pre class="highlight"><code># Get network information:
$ docker inspect 4c45aea49180 | jq '.[].NetworkSettings.Networks'
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

# Get the arguments with which the container was started

$ docker inspect 4c45aea49180 | jq '.[].Args'
[
"-server",
"-advertise",
"192.168.99.100",
"-bootstrap-expect",
"1"
]

# Get all the mounted volumes

11:22 $ docker inspect 4c45aea49180 | jq '.[].Mounts'
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
</code></pre></div></div>

<p>And of course also works great for querying other kinds of (docker-esque) APIs that produce JSON (e.g Marathon, Mesos, Consul etc.). JQ provides a very extensive API for accessing and processing JSON. More information can be found here: https://stedolan.github.io/jq/</p>
