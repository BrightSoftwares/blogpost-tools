---
ToReview: true
author: full
categories:
- docker
description: It was a fantastic experience hosting my first ever virtual conference
  session. The commute to my home office was great, and I even picked up a coffee
  on the way before my session started. No more waiting in lines, queueing for food,
  or sitting on the conference floor somewhere in a corner to check emails.
image: https://sergio.afanou.com/assets/images/image-midres-28.jpg
lang: en
layout: flexstart-blog-single
ref: top5_questions_howtobecome_a_dockerpoweruser
seo:
  links:
  - https://m.wikidata.org/wiki/Q15206305
silot_terms: devops pipeline
tags:
- docker
- productivity
- poweruser
title: Top 5 Questions from “How to become a Docker Power User” session at DockerCon
  2020
toc: true
---

<p><em>This is a guest post from </em><a href="https://twitter.com/idomyowntricks/"><em>Brian Christner</em></a><em>. Brian is a [[2022-07-21-how-to-run-jenkins-jobs-with-docker|Docker]] Captain since 2016, [[2022-03-27-how-do-i-access-the-host-port-in-a-docker-container|host]] of The Byte podcast, and Co-Founder &amp; Site Reliability Engineer at 56K.Cloud. At 56K.Cloud, he helps companies to adapt technologies and concepts like Cloud, Containers, and DevOps. </em><a href="https://56k.cloud/"><em>56K.Cloud </em></a><em>is a Technology company from Switzerland focusing on Automation, IoT, Containerization, and DevOps.</em></p>

<p>It was a fantastic experience hosting my first ever virtual conference session. The commute to my home office was great, and I even picked up a coffee on the way before my session started. No more waiting in lines, queueing for food, or sitting on the conference floor somewhere in a corner to check emails. </p>

<p>The “<a href="https://www.[[2020-04-03-how-to-setup-your-local-nodejs-development-environment-using-docker|docker]].com/blog/dockercon-2020-and-thats-a-wrap/">DockerCon 2020 that&#8217;s a wrap” blog post</a> highlighted my session &#8220;<a href="https://www.youtube.com/watch?v=sUZxIWDUicA">How to Become a [[2022-08-24-what-is-difference-between-docker-attach-and-exec|Docker]] Power User using VS Code</a>&#8221; session was one of the most popular sessions from DockerCon. [[2022-09-21-how-do-you-ping-a-docker-container-from-the-outside|Docker]] asked if I could write a recap and summarize some of the top questions that appeared in the chat. Absolutely.</p>

<p>Honestly, I liked the presented/audience interaction more than an in-person conference. Typically, a presenter broadcasts their content to a room full of participants, and if you are lucky and plan your session tempo well enough, you still have 5-10 minutes for Q&amp;A at the end. Even with 5-10 minutes, I find it is never enough time to answer questions, and people always walk away as they have to hurry to the next session.</p>

<p>Virtual Events allow the presenters to answer questions in real-time in the chat. Real-time chat is brilliant as I found a lot more questions were being asked compared to in-person sessions. However, we averaged about 5,500 people online during the session, so the chat became fast and furious with Q&amp;A.  </p>

<p>I quickly summarized the Chat transcript of people saying hello from countries/cities around the world. The chat kicked off with people from around the world chiming in to say &#8220;Hello from my home country/city. Just from the chat transcripts and people saying hello, I counted the following:</p>

<p>&nbsp;&nbsp;Argentina 1&nbsp;&nbsp;</p>

<p>&nbsp;&nbsp;Austria	 2&nbsp;&nbsp;</p>

<p>&nbsp;&nbsp;Belgium	 1&nbsp;&nbsp;</p>

<p>&nbsp;&nbsp;Brazil	 4&nbsp;&nbsp;</p>

<p>&nbsp;&nbsp;Canada	 3&nbsp;&nbsp;</p>

<p>&nbsp;&nbsp;Chile	 1&nbsp;&nbsp;</p>

<p>&nbsp;&nbsp;Colombia	 1&nbsp;&nbsp;</p>

<p>&nbsp;&nbsp;Denmark	 3&nbsp;&nbsp;</p>

<p>&nbsp;&nbsp;France	 3&nbsp;&nbsp;</p>

<p>&nbsp;&nbsp;Germany	 3&nbsp;&nbsp;</p>

<p>&nbsp;&nbsp;Greece	 2&nbsp;&nbsp;</p>

<p>&nbsp;&nbsp;Guatemala	 1&nbsp;&nbsp;</p>

<p>&nbsp;&nbsp;Italy	 	 1&nbsp;&nbsp;</p>

<p>&nbsp;&nbsp;Korea	 	 1&nbsp;&nbsp;</p>

<p>&nbsp;&nbsp;Mexico	 1&nbsp;&nbsp;</p>

<p>&nbsp;&nbsp;My chair	 1&nbsp;&nbsp;</p>

<p>&nbsp;&nbsp;Netherlands	 2&nbsp;&nbsp;</p>

<p>&nbsp;&nbsp;Poland	 2&nbsp;&nbsp;</p>

<p>&nbsp;&nbsp;Portugal	 2&nbsp;&nbsp;</p>

<p>&nbsp;&nbsp;Saudi Arabia	 1&nbsp;&nbsp;</p>

<p>&nbsp;&nbsp;South Africa	 4&nbsp;&nbsp;</p>

<p>&nbsp;&nbsp;Spain	 	 1&nbsp;&nbsp;</p>

<p>&nbsp;&nbsp;Switzerland	 3&nbsp;&nbsp;</p>

<p>&nbsp;&nbsp;UK		 3&nbsp;&nbsp;</p>

<p>&nbsp;&nbsp;USA		 15&nbsp;&nbsp;</p>

<p>  <strong>TOTAL</strong>   <strong>62</strong> </p>

<p><strong>Top 5 Questions</strong></p>

<p>Based on the Chat transcript, we summarized the top 5 questions/requests.</p>

<ol><li>The number one asked question was for the link to the demo code. VS Code demo Repo &#8211; <a href="https://github.com/vegasbrianc/vscode-[[2022-01-15-how-do-i-connect-mysql-workbench-to-mysql-inside-docker|docker]]-demo">https://github.com/vegasbrianc/vscode-[[2023-04-11-explore-your-container-with-docker-run|docker]]-demo</a></li><li>Does VS Code support VIM/Emacs keybindings? Yes, and yes. You can either install the <a href="https://marketplace.visualstudio.com/items?itemName=vscodevim.vim">VIM</a> or <a href="https://marketplace.visualstudio.com/items?itemName=vscodeemacs.emacs">Emacs</a> keybinding emulation to transform VS Code to your favorite editor keybinding shortcuts.</li><li>We had several [[2020-08-04-docker-tip-inspect-and-less|docker]]-compose questions ranging from can I run X with [[2020-08-04-docker-tip-inspect-and-grep|docker]]-compose to can I run [[2020-08-04-docker-tip-inspect-and-jq|docker]]-compose in production. Honestly, you can run docker-compose in production, but it depends on your application and [[2022-07-27-jenkins-ci-pipeline-scripts-not-permitted-to-use-method-groovy-lang-groovyobject|use]] case. Please have a look at the <a href="https://github.com/dockersamples/example-voting-app">Docker Voting Application</a>, highlighting the different [[2022-01-15-3-ways-to-connect-your-dolibarr-container-to-local-database|ways]] you can run the same application stack. Additionally, <a href="https://docs.docker.com/compose/">docker-compose documentation</a> is an excellent resource.</li><li>VS Code Debugging &#8211; This is a really powerful tool. If you select the Debug option when bootstrapping your project Debug is built in by [[2022-07-14-the-trustanchors-parameter-must-be-non-empty-on-linux-or-why-is-the-default-truststore-empty|default]]. Otherwise, you can <a href="https://code.visualstudio.com/docs/containers/debug-common">add the debug code manually</a>&nbsp;</li><li>Docker context is one of the latest features to arrive in the VS Code Docker extension. A few questions asked how to setup Docker contexts and how to use it. At the moment, you still need to set up a Docker Context using the terminal. I would highly recommend reading the<a href="https://www.docker.com/blog/how-to-deploy-on-remote-docker-hosts-with-docker-compose/"> blog post</a> by Anca Lordache wrote about using Docker Context as it provides a [[2022-08-31-a-complete-tutorial-about-jenkins-file|complete]] end-to-end set up of using Context with remote hosts</li></ol>

<p><strong>Bonus question!</strong></p>

<p>The most requested question during the session is a link to the Cat GIF’s so here you go.</p>

<iframe src="https://giphy.com/embed/JIX9t2j0ZTN9S" width="480" height="480" frameBorder="0" class="giphy-embed" allowFullScreen></iframe><p><a href="https://giphy.com/gifs/JIX9t2j0ZTN9S">via GIPHY</a></p>

<p><strong>More Information</strong></p>

<ul><li>That’s a wrap Blog post:- <a href="https://www.docker.com/blog/dockercon-2020-and-thats-a-wrap/">https://www.docker.com/blog/dockercon-2020-and-thats-a-wrap/</a></li><li>Become a Docker Power User With Microsoft Visual Studio Code &#8211; <a href="https://docker.events.cube365.net/docker/dockercon/content/Videos/4YkHYPnoQshkmnc26">https://docker.events.cube365.net/docker/dockercon/content/Videos/4YkHYPnoQshkmnc26</a>&nbsp;&nbsp;</li><li>Code used in the talk and demo &#8211; <a href="https://github.com/vegasbrianc/vscode-docker-demo">https://github.com/vegasbrianc/vscode-docker-demo</a></li><li>VIM Keybinding &#8211; <a href="https://marketplace.visualstudio.com/items?itemName=vscodevim.vim">https://marketplace.visualstudio.com/items?itemName=vscodevim.vim</a></li><li>Emacs Keybinding &#8211; <a href="https://marketplace.visualstudio.com/items?itemName=vscodeemacs.emacs">https://marketplace.visualstudio.com/items?itemName=vscodeemacs.emacs</a></li><li>Docker Voting Application &#8211; <a href="https://github.com/dockersamples/example-voting-app">https://github.com/dockersamples/example-voting-app</a></li><li>docker-compose documentation &#8211; <a href="https://docs.docker.com/compose/">https://docs.docker.com/compose/</a></li><li>VS Code Debug &#8211; <a href="https://code.visualstudio.com/docs/containers/debug-common">https://code.visualstudio.com/docs/containers/debug-common</a></li><li>How to deploy on remote Docker hosts with docker-compose &#8211; <a href="https://www.docker.com/blog/how-to-deploy-on-remote-docker-hosts-with-docker-compose/">https://www.docker.com/blog/how-to-deploy-on-remote-docker-hosts-with-docker-compose/</a></li></ul>

<p>Additional links mentioned during the session</p>

<ul><li>2020 Stackoverflow Survey &#8211; <a href="https://insights.stackoverflow.com/survey/2020#technology-most-loved-dreaded-and-wanted-platforms-loved5">https://insights.stackoverflow.com/survey/2020#technology-most-loved-dreaded-and-wanted-platforms-loved5</a></li><li>VS Code Containers [[2022-09-07-overview-on-jenkins|overview]] documentation &#8211; <a href="https://code.visualstudio.com/docs/containers/overview">https://code.visualstudio.com/docs/containers/overview</a></li><li>Awesome VS Code List &#8211; <a href="https://code.visualstudio.com/docs/containers/overview">https://code.visualstudio.com/docs/containers/overview</a></li><li>Compose Spec &#8211; <a href="https://www.compose-spec.io/">https://www.compose-spec.io/</a></li></ul>

<p><strong>Find out more about 56K.Cloud</strong></p>

<p>We love Cloud, IoT, Containers, DevOps, and Infrastructure as Code. If you are interested in chatting connect with us on <a href="https://twitter.com/56kcloud">Twitter</a> or drop us an email: info@56K.Cloud. We hope you found this article helpful. If there is anything you would like to contribute or you have questions, please let us know!<br></p>
<p>The post <a rel="nofollow" href="https://www.docker.com/blog/top-5-questions-from-how-to-become-a-docker-power-user-session-at-dockercon-2020/">Top 5 Questions from “How to become a Docker Power User” session at DockerCon 2020</a> appeared first on <a rel="nofollow" href="https://www.docker.com/blog">Docker Blog</a>.</p>