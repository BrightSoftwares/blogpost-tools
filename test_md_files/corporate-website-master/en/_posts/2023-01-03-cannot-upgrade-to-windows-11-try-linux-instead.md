---
author: full
categories:
- linux
date: 2023-01-03
description: Conceptually linux is very different from windows pretty much across the board some of these differences are primarily visual while others are much more fundamental if  you've heard of linux before you've probably heard that it's open now evangelists will tell you that that means free is in speech and this is true in that anyone can take a look at the source code and modify it as they see fit. 
image: https://res.cloudinary.com/brightsoftwares/image/upload/t_BSBlogImage/v1673424714/brightsoftwares.com.blog/r-O95aZ6wvI.jpg
lang: en
layout: flexstart-blog-single
post_date: 2023-11-30
pretified: true
ref: cannot-upgrade-to-windows-11-try-linux-instead
tags:
- windows
- linux
- windows11
title: Cannot upgrade to Windows 11, try Linux instead
silot_terms: diy desktop computing
transcribed: true
youtube_video: https://www.youtube.com/watch?v=_Ua-d9OeUOg&ab_channel=LinusTechTips
youtube_video_id: _Ua-d9OeUOg
toc: true
---

Conceptually linux is very different from windows pretty much across the board some of these differences are primarily visual while others are much more fundamental if  you've heard of linux before you've probably heard that it's open now evangelists will tell you that that means free is in speech and this is true in that anyone can take a look at the source code and modify it as they see fit. 

Or you got into the same I did before: you installed a windows update and then your computer won't boot anymore. For more information on how to Help! Windows Won't Boot Correctly After a Recent OS Update, check out our comprehensive guide on [[2020-08-11-help-windows-wont-boot-correctly-after-a-recent-os-update.md|Help! Windows Won't Boot Correctly After a Recent OS Update]]. You may want to save your data first before switching your Operating System. If you're interested, our blog post on [[2020-08-11-how-do-i-get-my-data-off-an-old-computer.md|restore old computer]] has everything you need to know.



But what it means in practice is that not only is it able to support a wide variety of hardware it's also extremely customizable with desktops that can mimic the look and feel of any existing operating system or be something entirely unique you get control.

Not only that you'll hear people say that it breathes new life into old pcs
but why is that the reason is that the open nature of linux means that it comes in many different flavors known as distributions or distros.

There are distros with lighter or heavier system requirements dramatically different aesthetics and even different ways of installing software.

Now here's some good full feature desktop oriented ones if you've got one that you like best let us know why down below our example for today is going to be PopOs by system 76.

![](https://res.cloudinary.com/brightsoftwares/image/upload/v1652909907/brightsoftwares.com.blog/gn26m5mnzfwsimwyzkip.png)


## Why choose PopOS?

It is a good recommendation for new users not only because it's part of the
well-known and well-documented ubuntu and debian lineage but it's also because it has a number of features and same defaults that make it friendlier and easier to get up and  running.

![](https://res.cloudinary.com/brightsoftwares/image/upload/v1652909989/brightsoftwares.com.blog/tfyvsxv0byvxqzscc0jy.png)


Start by downloading the iso now pop comes in two flavors one that includes the very special nvidia driver and one for everyone else you can use either but it's easiest to download the iso that best matches your system to reduce the number of steps required during installation.

The internet speed plays a great role on the download experience. If you have internet speed issues, our blog post on [[2020-07-28-why-do-my-download-speeds-differ-so-drastically-between-computers.md|Why Do My Download Speeds Differ So Drastically Between Computers?]] explains how you can improve things.



![](https://res.cloudinary.com/brightsoftwares/image/upload/v1652910181/brightsoftwares.com.blog/dgapx4wl0fvvm2q0k8hu.png)


Now you could just burn it if you've got an optical drive and a blank dvd
but if like most of us all you've got is a flash drive you can grab one of a couple of
different tools the easiest of which being balina etcher.

### Flash your drive with Balena Etcher

![](https://res.cloudinary.com/brightsoftwares/image/upload/v1652910244/brightsoftwares.com.blog/qjbvu8iff9cimksrbli0.png)


It's so easy in fact that it's just three steps:

1. Select the iso 
2. Select the flash drive and then 
3. click flash 

For pop os that's all you need to do but if you've got an image.

For a different distro for example that fails to flash this way we look to a more versatile tool like rufus.

### Flash your drive with Rufus

![](https://res.cloudinary.com/brightsoftwares/image/upload/v1652910514/brightsoftwares.com.blog/czd1tph2fpmm3svimob1.png)

Looking at the main window ignore the, persistent partition size slider for now and look at the partition scheme option.

![](https://res.cloudinary.com/brightsoftwares/image/upload/v1652910442/brightsoftwares.com.blog/zci1lwfk2ojv2mbglbdp.png)

For most people MBR  is perfectly fine because it supports both legacy bios boot and UEFI. 


![](https://res.cloudinary.com/brightsoftwares/image/upload/v1652910689/brightsoftwares.com.blog/ega4yq0ilcdkmzqsh8dg.png)

You'll rarely need to use the advanced options but the fixes for old bios's can help if you've got a very  old computer that you're trying to boot.

![](https://res.cloudinary.com/brightsoftwares/image/upload/v1652910749/brightsoftwares.com.blog/nzma4dkuvrfvly0oxoex.png)

For file system you'll almost always want to choose FAT32 now NTFS supports files that are larger than 4Gb but it's less compatible overall.

You'll also always always want to choose the default cluster size larger clusters can improve transfer performance for larger files at the expense of smaller files and vice
versa.

Finally you can choose to create an extended label in icon files which just makes your flash drive show up in a fancier way on windows if you fancy like that all that's left
is to click start and wait for it to do its thing.

![](https://res.cloudinary.com/brightsoftwares/image/upload/v1652910879/brightsoftwares.com.blog/mwrewwauxhmp0aqb1ju5.png)

If all went well you're now the proud owner of a flash drive with linux on it.


## Install the OS

Time to plug it in the computer and give it a whirl! 

Power on your pc and enter the bios.

### Configure to boot from the flash drive

We will need to first make sure the flash drive is shown up and is first in the boot order and second we need to make sure that secure boot is disabled otherwise you'll just get this fun message when you try to boot.

Fedora and Ubuntu both support it but as far as i know every other distro out there including PopOS does not unless you do it yourself. 

In most desktop bioses disabling the qubit requires the key store to be deleted like this but laptops all-in-ones and pre-builts may have a simple toggle.

Save and Exit and you should be booting from your flash drive. 
You can do it after the first screen you'll be treated to an impressive looking array of very technical messages as linux boots up. 


These make troubleshooting a lot easier if it stops part way through. Some distros cover them up with a boot screen but you can usually hit escape to show them again. 

It may take a little while to boot after the final message so give it a minute before assuming something is going wrong. 

If all goes well you'll be looking at the popos desktop and an install popos window will come right up choose your language and region.

Then choose your keyboard layout english us default will work for most but you can choose alternative layouts here like dvorak and cola mac.

Next popos will give you the option of customizing your install.

If you're super eager to get going you can go through the installer now. But if you'd like to poke around in an environment where you can't break anything
now is a great time to do that by clicking try demo mode this is pretty much the same thing you're going to get after a default install. 

it's also a great opportunity to make sure that all your hardware is up and
running particularly your audio your networking and your display driver.

Once you're finished poking around it's time to come back to the installer
a clean install is the most straightforward so let's go ahead and choose that option.

Choose the drive you want to install to and then you'll be brought to the
account setup screen a username will automatically generate based on your full name
but you can change it if you prefer.

![](https://res.cloudinary.com/brightsoftwares/image/upload/v1672678186/brightsoftwares.com.blog/supa396qooixigyutzvy.png)


Click next choose a password.

Then the next step is to install the files once it's finished reboot and you'll
boot right into PopOS!

### Boot into PopOs

Now if you don't make sure it's selected as a default boot device in your bios
it should show up as pop os like so.

![](https://res.cloudinary.com/brightsoftwares/image/upload/v1672678278/brightsoftwares.com.blog/f7jbkfmid7luktymp5z7.png)


Once you're booted into pop os log in and you'll be greeted with the post install
setup unlike a certain other operating system. This only features a single privacy setting with everything else being things like typing, time zone and how you want your docked and top part or logan function.

I like it best when it's set up like this but you're not limited to any one layout.

![](https://res.cloudinary.com/brightsoftwares/image/upload/v1672678384/brightsoftwares.com.blog/zwvnfgxwnnouyfi3sxsa.png)


It's kind of a not windows looking setup similar to a different desktop environment called Plasma.

Depending on how fresh your Iso was. Popshop will ping you at this point saying that there are updates available. 

### Install your Apps

Now This is your app store. Go ahead and launch it and click the installed tab to download any updates that are waiting. Then you can start to install your apps. It's ridiculously easy to do 

discord: One click 
Obs: one click 
Steam: one click 

![](https://res.cloudinary.com/brightsoftwares/image/upload/v1672678457/brightsoftwares.com.blog/ywekf7esfeyj5az3qrdp.png)


Needing game performance metrics and logging grab go relay emulators. They've got Retroarch, Dolphin, Maim, Dosbox. You never even had to open a browser. 
I hate opening browsers. Now that's not to say that the interface is perfect. 



Clicking on a category will just give you an alphabetical listing of software with no subcategories or filters, which can be overwhelming to say the least. When you're just browsing and advanced, users will notice that some under the hood packages aren't listed at all, with no obvious way to change that. 


You can install the synaptic package manager to get both of those features, though the only problem is that it's far less user friendly. Thankfully, if there's something that you need that's simply not available at all, you can add an extra source in Popshop settings. 

![](https://res.cloudinary.com/brightsoftwares/image/upload/v1672678510/brightsoftwares.com.blog/ippathld2t6akan1dpmo.png)


most software has a launchpad or personal package archive that you can add there. As the name suggests, these are curated by the authors or users rather than the regular operating system maintainers, so only use these for software you trust 

wine. The software that allows you to run Windows programs on Linux is a good example of this because the version included in Popshop is quite old. However, the developers have decided to host their own and provide instructions separately, so we'll have to use the terminal instead. Now, don't worry too much, this isn't very common and because we trust Wine, we can just copy these commands and paste them into the terminal, like So.


once you're done, go ahead and type this command to finally install the latest stable version of Wine. Now you can exit the terminal. I also recommend installing Wine tricks while we're at it to manage our Windows settings. To be clear, you don't need any of this to run games through Steam, which launches Windows games through its own included Proton layer. 

![](https://res.cloudinary.com/brightsoftwares/image/upload/v1672678577/brightsoftwares.com.blog/p59ecqpjel95aqneuktd.png)


After all your installs are done, open the applications drawer and you'll see that they're ready to rock. No extra steps required. Steam opens right up and you can log in as normal before you go wild. You can get your favorite [[2020-09-01-how-to-take-a-screenshot-in-windows.md|screenshot application]] ready to go. Installing games though you should enable Proton for all titles under Steam. Play and Steam Settings Menu Click. Ok. Steam will restart and you're good to go. Cool, right? 
Like I can just straight up install Cyberpunk for example and it'll work. In fact, it works really well for a game with a silver rating like must have been like a recent update or something I don't know. You can check how well a game is expected to run as well as how it ran in the past, and whether anything special needs to be done to get it working. On Proton Db. 


The vast majority of games work out of the box, although with some caveats we'll get to shortly. 

But first, if you have an Nvidia Gpu, Shadow Play doesn't exist in Linux and that's a problem. But what if I told you there's a way to get something even better? It's a couple extra steps and we're going to have to use the terminal to do it. but trust me, it's very worth it. 

First download the code from the Nvidia patch repository and extract the zip file. Then go to the folder you just extracted right, click the empty space, and click open in terminal. Next, type this command and hit enter. 

![](https://res.cloudinary.com/brightsoftwares/image/upload/v1672678714/brightsoftwares.com.blog/r2ijbfpfdcdtnbyfbfld.png)


This will enable Nvfbc or Framebuffer capture the extremely fast method that Shadowplay uses to capture the screen and something Nvidia normally has disabled for Geforce cards by default. That wasn't so hard, but we still had to install the plugin for Obs to use. 

Unfortunately, there's no package for it in Popos or Ubuntu right now, so we'll have to download it ourselves. To be clear, this is one of the last options you want to use as far as installing software. Download the code from this repository, then extract it, go to the folder, and open it into the terminal. Like before now, we need to install some things before we can actually continue. So type this command. Hit, enter, enter your password. 

Now type these commands, hitting enter after each one, and once that's done, you can go back to the files window, go to the build folder, and copy this file. go to your home folder, show hidden files, then go here, make a new folder called plugins, then in there, make new folders that look like this, and paste the file you copied before and you're done. 

![](https://res.cloudinary.com/brightsoftwares/image/upload/v1672678766/brightsoftwares.com.blog/jnfqud7itdlnlx8isvmv.png)


Linux veterans will point out that we could have done a lot of this more quickly if we'd done more of it in the terminal. And that's true. The terminal is really handy for a lot of things, especially for tutorials, where it's the only truly common factor between Linux distributions. But contrary to popular belief, it's not necessary. 

Most of the time it's just faster or easier if you know what you're doing. If you aren't familiar with it, using it in short bursts like this can help you get acclimated and learn what can be done just by typing a few words. Now we can go to Obs and add the Mvfbc source to our scene and look at that. high resolution, high frame rate screen capture with very little overhead just like shadow play. If you open up system monitor, which is kind of like the Windows Task manager, you'll see very little cpu usage. 

You can combine this with Nveng for high performance gameplay, streaming, and recording too. Oh, and did I mention that most game controllers just work out of the box? 

![](https://res.cloudinary.com/brightsoftwares/image/upload/v1672678870/brightsoftwares.com.blog/sxlmppum9r24a2yoixzo.png)


The list of devices that Linux supports is much larger than the list. it doesn't, and the majority of those are a result of a company not releasing the driver, or at least not releasing the information relevant for making one from scratch. Nvidia's much maligned proprietary driver, on the other hand, works pretty well and has been getting some serious attention from Team Green recently. with Dlss and ray tracing support and more. 

The Popos comes with the latest drivers and updates for them come down through the pop shop like everything else. 

## Why people are not massively using Linux?


So if installing linux isn't that big of a hassle, why haven't more people jumped on board? Well, the main problem at least in the past, is that for all the freedom and control you're getting from Linux, you had to give up performance or functionality or both, especially in gaming. 


But since the release of Valve's wine based proton compatibility Layer in 2018, things have been exploding to the point where the vast majority of steam games run flawlessly on Linux with no configuration necessary. 

The biggest issue for Linux gamers is the fact that many anti-cheat programs still don't work properly at all, meaning that games like Pubg, Apex, Legends, Destiny 2, and Rainbow Six Siege are just presently unplayable despite working in offline mode. This spills over into productivity apps like Microsoft Office and Creative Cloud, where their anti-piracy implementations fail to authenticate thanks to reliance on an integrated Internet Explorer. Yeah, disgusting. 


## Compatibility is rapidly advancing

But compatibility is rapidly advancing. 

My personal advice is to use the tools that fit you best, whether that's Windows, Mac, Os, Linux, or even something else entirely. And if these compatibility issues are show stoppers for you, I'm not going to wag my finger at you and expect you to find an alternative. 

What I am going to do though, is ask you to give it a try and see if the alternatives work for you. 

I find immense joy in trying new things and finding better ways of doing what I like to do. And with Linux, the sheer number of different ways of doing things means you're extremely likely to find something Anything at all that works better for you than what you're doing right now. you have only to look for it. 

Do you need to use fax to send documents? Our blog post on [[2020-09-01-how-to-send-and-receive-faxes-online-without-a-fax-machine-or-phone-line.md|How to Send and Receive Faxes Online Without a Fax Machine or Phone Line]] explains why How to Send and Receive Faxes Online Without a Fax Machine or Phone Line.

If you're interested in learning more about How Do I Fix My Cracked iPhone Screen During the Shutdown?, our blog post on [[2020-08-11-how-do-i-fix-my-cracked-iphone-screen-during-the-shutdown.md|fix cracked iphone screen nyc]] How Do I Fix My Cracked iPhone Screen During the Shutdown.

Our blog post on [[2020-08-04-do-i-need-a-new-cable-modem-if-im-stuck-working-from-home.md|using your cable modem]] explores how Do I Need a New Cable Modem If I'm Stuck Working From Home.



