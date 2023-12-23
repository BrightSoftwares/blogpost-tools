---
author: full
categories:
- kubernetes
date: 2023-02-15
description: How do I access container port?
image: https://res.cloudinary.com/brightsoftwares/image/upload/t_BSBlogImage/v1655551305/pexels-david-dibert-1117210_mlgt9n.jpg
inspiration: https://stackoverflow.com/questions/47261308/docker-access-container-ip-port-directly
lang: en
layout: flexstart-blog-single
post_date: 2023-02-15
pretified: true
seo:
  links:
  - https://m.wikidata.org/wiki/Q15206305
tags: []
title: How do I access docker container IP port directly?
transcribed: true
youtube_video: http://www.youtube.com/watch?v=MkRBZSCyN-8
youtube_video_description: 'In this series I give a practical introduction to Docker.
  Links to more tutorials can be found here: http://www.brunel.ac.uk/~csstnns.'
youtube_video_id: MkRBZSCyN-8
youtube_video_title: 'Docker Training 20/29: Docker Container IP Address and Port
  Number'
---

# 

Hey, we're still learning about basics of container networking We've seen in the last video that we actually run this container, the simple web server and we spoke about a port mapping that this is the host port and this is the container port and we spoke about how we can access that. We did that actually via the web browser and the Curl tool. What we wanted to speak about now is that a networking in general IP Version 4 address This form of something dot something dot something dot something is very limited. The number of IP addresses that we can have is limited and therefore we won't be having containers. You know that have public IP addresses, but rather they containers will have IP addresses. containers have IP addresses and then the services that the containers have on them that the containers publish or the containers offer like for example, a web server or database server or mail server or something like that. They will be exposed port by port. So we will always be playing about with port numbers will be playing about port mappings and things like that to avoid any conflict. So you can have several services running on different port numbers in in general. but we've seen that we can actually find out about the port mapping when we do docker. PS but we don't have to docker. PS if we know the docker I the containers ID We can do dock a port. We spoke about this before, so if you just do docker and and hit enter you'll see a list of arguments. One of them is port. list port mappings or a specific marketing for the container. So what I can do it like I said cuz a dock up port and then what's the container ID is running in the background. isn't it 3:02 d30 to just hit and tab and autocomplete and then I know the container is working on port 8000. but I need to find out what the host port numbers. So I'll do 8,000 and it should give me back the host port number. So this is another way of knowing the external sort of ports. Yeah, the hole the post is port number. Another trick would be to assign the host port number manually. So let's actually let's remove this container first. So kill 3 is very - unless you remove it. so nothing is wrong in the background now. Yeah, right. So when we run the container earlier, let's go back to the command. Yeah, so what we've done earlier, we left it to find a host host port number or randomly or automatically. But now we're going to tell it to explicitly use port 80 or so I can say took around - literally the background and then - P - map 8000 to 80 or 82 8,000 so that the host port number now is 80 and the containers port number is a normal one 8,000 Or let's change it. Maybe let's say do it 88 or something like that. Yeah, so the host port number now is 88 the containers port number is 8000. Let's hit enter should be working. If I do docker PS then I can see here the mapping 888 and 8,000 and if I go there I can say 88 and I should get the same result. and even if I do a curl command with it earlier yes, I should be able to reach in service via port 88 I Hope that makes sense. This is just reported him do the port mapping manually I specify a custom port number rather than leaving it a docker to find a port number under me. Any of the portes Okay, another thing is we spoke about docker containers having not having public IP addresses meaning having internal IP addresses. There is a way of knowing of knowing the IP address of a container and the command I have typed in here already. As you can see, it is a little bit advanced stuff, so docker inspect - - format this argument here and then we pass it the container ID So let's copy this command ctrl C and then paste it there and we need to pass it the ID of our container which is this yeah for you tab got to complete. that's not necessary. The first few characters are fine as long as the unique enter. Now it gives me the containers port number so it can actually ping it if I want And as you can see, the container is reachable but always remember this IP address is not public containers. We don't want to want them to have a public IP addresses. We do the port mapping and that should do the trick for us. So I hope it's making sense now that we are using a web server inside the container, we can publish it, make it public, and other people can access it, will accept requests from different computers. We just need to be aware of this idea of the port mapping and know which port number that we have to use when we try to access that service and all should be fine. Thanks again and I'll see you in my next video.