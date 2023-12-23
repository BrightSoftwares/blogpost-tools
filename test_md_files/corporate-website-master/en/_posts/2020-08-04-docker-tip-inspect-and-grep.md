---
ToReview: true
author: full
categories:
- docker
description: 'This isn’t so much a docker tip, as it is a jq tip. If you haven’t heard
  of jq, it is a great tool for parsing JSON from the command line. This also makes
  it a great tool to see what is happening in a container instead of having to use
  the –format specifier which I can never remember how to use exactly:'
image: https://sergio.afanou.com/assets/images/image-midres-15.jpg
lang: en
layout: flexstart-blog-single
ref: inspectgrepdocker_1243
seo:
  links:
  - https://m.wikidata.org/wiki/Q15206305
silot_terms: devops pipeline
title: 'Docker tip : inspect and grep'
toc: true
---

### Docker inspect and grep

This isn’t so much a [[2020-08-04-docker-tip-inspect-and-jq|docker]] [[2020-08-04-docker-tip-inspect-and-less|tip]], as it is a jq tip. If you haven’t heard of jq, it is a great tool for parsing JSON from the command line. This also makes it a great tool to see what is happening in a [[2022-09-21-how-do-you-ping-a-docker-container-from-the-outside|container]] instead of having to [[2022-07-27-jenkins-ci-pipeline-scripts-not-permitted-to-use-method-groovy-lang-groovyobject|use]] the –format specifier which I can never remember how to use exactly:

    # Get network information:
    $ [[2022-07-21-how-to-run-jenkins-jobs-with-docker|docker]] inspect 4c45aea49180 | jq '.[].NetworkSettings.Networks'
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
    
    # Get the arguments with which the [[2022-01-15-3-ways-to-connect-your-dolibarr-container-to-local-database|container]] was started
    
    $ [[2020-04-03-how-to-setup-your-local-nodejs-development-environment-using-docker|docker]] inspect 4c45aea49180 | jq '.[].Args'
    [
    "-server",
    "-advertise",
    "192.168.99.100",
    "-bootstrap-expect",
    "1"
    ]
    
    # Get all the mounted volumes
    
    11:22 $ [[2022-08-24-what-is-difference-between-docker-attach-and-exec|docker]] inspect 4c45aea49180 | jq '.[].Mounts'
    [
    {
    "Name": "a8125ffdf6c4be1db4464345ba36b0417a18aaa3a025267596e292249ca4391f",
    "Source": "/mnt/sda1/var/lib/[[2022-01-15-how-do-i-connect-mysql-workbench-to-mysql-inside-docker|docker]]/volumes/a8125ffdf6c4be1db4464345ba36b0417a18aaa3a025267596e292249ca4391f/_data",
    "Destination": "/data",
    "Driver": "local",
    "Mode": "",
    "RW": true
    }
    ]
    

And of course also works great for querying other kinds of ([[2022-03-27-how-do-i-access-the-host-port-in-a-docker-container|docker]]-esque) APIs that produce JSON (e.g Marathon, Mesos, Consul etc.). JQ provides a very extensive API for accessing and processing JSON. More information can be found here: https://stedolan.github.io/jq/