---
ToReview: true
author: full
categories:
- productivity
description: "Iâ\x80\x99m going to go with the good olâ\x80\x99 â\x80\x9CIt depends.â\x80\x9D
  However, I first want to commend you for actually owning your own cable modem instead
  of coughing up $14 or so each month for Comcast to rent you one of their *meh* modem/router
  combinations. Thereâ\x80\x99s no reason you should be paying a fee to rent that
  which you can purchase yourself. Of course, this also means that youâ\x80\x99ll
  have to buy a new cable modem if, or when, your internet plan exceeds your modemâ\x80\x99s
  capabilities."
image: https://sergio.afanou.com/assets/images/image-midres-50.jpg
lang: en
layout: flexstart-blog-single
ref: stuckworkingfromhome_1242
silot_terms: diy desktop computing
title: Do I Need a New Cable Modem If I'm Stuck Working From Home?
toc: true
---

### The question:

_I have to work from home for a fancy tech company and it takes too long to download and upload my work. I upgraded my internet plan with Comcast, but does that mean I also need to get a new cable modem?_

### The correct answer:

I\xe2\x80\x99m going to go with the good ol\xe2\x80\x99 \xe2\x80\x9cIt depends.\xe2\x80\x9d However, I first want to commend you for actually owning your own cable modem [[2023-01-03-cannot-upgrade-to-windows-11-try-linux-instead|instead]] of coughing up $14 or so each month for Comcast to rent you one of their _meh_ modem/router combinations. There\xe2\x80\x99s no reason you should be paying a fee to rent that which you can purchase yourself. Of course, this also means that you\xe2\x80\x99ll have to buy a new cable modem if, or when, your internet plan exceeds your modem\xe2\x80\x99s capabilities.

In this case, I asked my friend for more information, and he mentioned that he had bumped up to a 300Mbps plan from Comcast. He didn\xe2\x80\x99t mention what his service plan was before that, so there _is_ the possibility that he would need to buy a new cable modem to be able to max out on those speeds\xe2\x80\x94download speeds, that is, since \xe2\x80\x9c300Mbps,\xe2\x80\x9d as we know, doesn\xe2\x80\x99t mean 300Mbps both ways.

As it turns out, his [Netgear CM500](https://www.netgear.com/home/products/networking/cable-modems-routers/CM500.aspx) cable modem was more than up for the task. A quick Google search confirms that it supports speeds of up to 680Mbps\xe2\x80\x94more than enough for a 300Mbps plan. And while I could get into the technical details of what \xe2\x80\x9c16x4" means as part of its configuration, that\xe2\x80\x99s irrelevant for most people. It\xe2\x80\x99s compatible with [Comcast](https://www.xfinity.com/support/devices/) and, most importantly, Comcast itself certifies that it\xe2\x80\x99ll support 300Mbps speeds.

That bit is important, because you should never assume that a manufacturer is correct when it comes to cable modems. Double-check with your ISP\xe2\x80\x99s list of compatible cable modems to confirm that whatever you own, or are looking to purchase, works with the company\xe2\x80\x99s service _and_ can handle whatever speeds you\xe2\x80\x99re expecting. If you don\xe2\x80\x99t see your modem on the list, or don\xe2\x80\x99t see a list at all, give them a ring.

To note: If you also get [[2020-09-01-how-to-send-and-receive-faxes-online-without-a-fax-machine-or-phone-line|phone]] service through your ISP, the kind of thing where you\xe2\x80\x99re actually connecting a VOIP phone to your modem, then you\xe2\x80\x99ll probably need a more souped-up (and expensive) cable modem. Them\xe2\x80\x99s the breaks; don\xe2\x80\x99t buy a new, cheap, typical modem and assume that it\xe2\x80\x99ll work with your VOIP setup.

### But maybe it\xe2\x80\x99s not the cable modem...

I also think it\xe2\x80\x99s important to know that upgrading your service plan through your ISP, and buying a new cable modem, might _not_ actually give you the speed boosts you\xe2\x80\x99re expecting. If your wifi setup at home is crappy or underpowered, or if you\xe2\x80\x99re trying to access your files from a location that\xe2\x80\x99s fairly far away from your primary router\xe2\x80\x94or there\xe2\x80\x99s a lot of stuff (including walls) between it and you\xe2\x80\x94then your wireless setup might be more to blame than your service plan.

Honestly, I\xe2\x80\x99d investigate that first. Look up whatever service tier you\xe2\x80\x99re paying for on your ISP\xe2\x80\x99s monthly bill, and walk around your house\xe2\x80\x94running either [fast.com](https://fast.com/) or [speedtest.net](https://www.speedtest.net/) at various points\xe2\x80\x94to see whether you\xe2\x80\x99re getting that maximum speed in the places you usually use your various devices. If not, fixing your wireless setup should be priority one, _then_ worry about faster internet services from your ISP.

And how do you do that, you ask? To start, make sure your router is in a central location within your house. That might involve you stringing ethernet cable along floors and ceilings to get it there, rather than the tiny closet in the extreme corner of your house that\xe2\x80\x99s farthest away from your work-at-home desk. This will pay dividends, trust me. (And if you\xe2\x80\x99re quarantined, you have plenty of time for projects like these!)

Beyond that, if you\xe2\x80\x99re extending your router\xe2\x80\x99s signal with a wifi extender or mesh setup, know that each \xe2\x80\x9chop\xe2\x80\x9d you make in the chain\xe2\x80\x94from a router, to an extender, to another extender, to your laptop\xe2\x80\x94can cut your throughput in half each time. Unless your mesh setup has a dedicated backhaul connection, and your access points are located close enough to one another to benefit from a strong connection, simply extending your network to where you need wireless coverage can get you online, but it might be painfully slow.

As always, use wired Ethernet wherever possible for the best possible speeds. Grab a dongle and connect your laptop to your wall\xe2\x80\x99s Ethernet port (using a solid Cat6 cable, since I like to future-proof and it\xe2\x80\x99s hardly more expensive than a Cat5 or Cat5e). Use Ethernet cables to connect your access points and router to one another, annoying as it might be, rather than extending your wireless network using wifi.

It\xe2\x80\x99s a pain in the butt, I know. But I just converted a house from an all-wireless setup to wired, and now the family can finally enjoy the _gigabit_ ethernet speeds they\xe2\x80\x99ve been paying for\xe2\x80\x94speeds they *never *had, since they were relying on a crappy cable modem/router and extender \xe2\x80\x9cpods\xe2\x80\x9d to try and fill their house with wireless connectivity. They could have saved a ton of money by dialing back their internet plan to match the capabilities of their network; that, or they could have upgraded their network, as I did, with access points connected to a primary switch (and router) via Ethernet cable and actually enjoyed the super-fast speeds they were paying for.

That\xe2\x80\x99s just my long-winded way to say that your internet plan might not be what you should first blame for slow internet speeds at home. It\xe2\x80\x99s a part of the equation, sure, but you\xe2\x80\x99ll want to make sure your wireless network is up to snuff, too. If, or when, you upgrade your plan and get a new cable modem that supports it (if applicable), make sure you\xe2\x80\x99re doing the same process\xe2\x80\x94walking around your house, testing your speeds, and fixing up your wifi network\xe2\x80\x94to make sure you\xe2\x80\x99re not just paying your ISP for service you\xe2\x80\x99ll never see.

Looking for improving your internet connection speed? Take a look at [[2020-07-28-why-do-my-download-speeds-differ-so-drastically-between-computers|this tutorial]].