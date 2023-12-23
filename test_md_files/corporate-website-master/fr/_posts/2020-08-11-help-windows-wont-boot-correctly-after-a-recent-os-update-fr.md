---
layout: flexstart-blog-single
title:  "Help! Windows Won't Boot Correctly After a Recent OS Update"
author: full
lang: fr
ref: recentosupdate_1247
categories: [ productivity ]
description: "What happens when Windows starts tossing up annoying error messages each and every time you try to launch the operating system? If you’re trying to log in for the day and actually do work for the critical deadlines you have, and you don’t really have an IT department to help out, this is probably the worst spot to be in.

Since we’re all stuck—or will soon be stuck—in our homes and apartments for the foreseeable future, 


 The question:


 I have a Windows 10 desktop. Several weeks ago windows "
image: "https://sergio.afanou.com/assets/images/image-midres-55.jpg"
---

What happens when Windows starts tossing up annoying error messages each and every time you try to launch the operating system? If you’re trying to log in for the day and actually do work for the critical deadlines you have, and you don’t really have an IT department to help out, this is probably the worst spot to be in.

Since we’re all stuck—or will soon be stuck—in our homes and apartments for the foreseeable future,

### The question:

> _I have a Windows 10 desktop. Several weeks ago windows did an update and several days later when I powered on, I got the message “windows didn’t load properly” blue screen with several options. The ones I tried didn’t work well, until I found the “Revert to a previous date” option. That worked well. Computer went back on and functioned normally. Unfortunately I still receive the windows did not load properly screen every several days. Im running Windows 10 on a Mac. I was thinking of completely wiping out windows and then reloading it. Maybe I have a virus or bug ? Thanks !!_

### The humble answer:

For what it’s worth, you’re not alone on this one. Microsoft has been having issues with Windows 10 updates lately, which can sometimes introduce more problems for users than they can fix. It’s possible that you’re in this camp, but the good news is that it’s very, _very_ unlikely that you’ve been hit with a virus or some piece of sketchy malware. It’s just a Windows issue—not very soothing to hear when you’re experiencing it, I’m sure, but at least slight more comforting than, “Your system is infected” (I hope).

Generally speaking, I like to abandon ship at the first sign of trouble that would likely take me longer to troubleshoot—with mixed results—than it would take me to reinstall Windows and all of my applications. I suspect that might be the case here. And since you’re Boot Camping into Windows on your Mac, I’m less bothered by putting you out of commission for a bit, since you’ll always have macOS to use if you absolutely need to do something on your computer.

Before we go nuclear, though, let’s try a few things. First off, if you can boot _into_ Windows—and it sounds like you can—I’m not sure there’s anything you can uninstall that will help you. The last major Windows 10 update that would have probably affected you was the big 1909 update from [November](https://support.microsoft.com/en-us/help/4529964/windows-10-update-history). There have been a number of piecemeal updates since then, but I can’t think of one that’s been especially problematic. Oh, except for KB4535996, which even Microsoft suggested users uninstall.

So, let’s start there. Pull up **Windows Update**, click on **View Update History**, click on **Uninstall Updates**, and look to see if you can uninstall KB4535996. If you can, great! If not, there goes that troubleshooting technique.

While you’re here, maybe check to see if there are any additional Windows updates you can install. It’s a long shot, but perhaps something has arrived that could fix whatever issues your Windows installation is struggling to deal with. And since you’re using Boot Camp to run Windows on your Mac, pull up Apple Software Update and make sure there aren’t any new drivers or updates to install.

###### How Can I Keep an Old All-In-One PC Running Quickly and Efficiently?

I’m always thrilled to get “help me out with a tech problem” letters in my inbox, and I’ve had…

Finally, try reinstalling Boot Camp’s [Windows Support Drivers](https://support.apple.com/en-us/HT204923), which might magically cure whatever is causing your system to blue screen upon launch. There’s no guarantee this will fix things, but it’s worth exploring before you take more drastic measures.

While you’re in Windows, you can also open up an elevated command prompt (search for “Command Prompt” in the Start Menu, right click on it, and select “Run as administrator”). From there, try running a simple “chkdsk /f” to conform there aren’t any issues with your file system. You can also try “chkdsk /r /f” for a much more thorough analysis and fixing process, but it’ll take a lot longer. If your hard drive is failing and that’s the reason behind your Windows issues, it’s also possible you might not get any additional information from chkdsk. You’ll want to use [some other techniques](https://lifehacker.com/how-to-check-if-your-hard-drive-is-failing-1835065626) to confirm you’re ok (or headed toward disaster).

You can also run “sfc /verifyonly” followed by “sfc /scannow” in the same elevated command prompt. If the first command found any corruption in your Windows system files, the second command should fix them.

Once you’ve finished this, consider pulling up the Windows Troubleshooter. Pull up the old-school Control Panel (via the Start Menu) and select Troubleshooting. Then, click on “Fix problems with Windows Update,” and see what the utility finds (if anything!)

Finally, click on your Start Menu, click on the Power icon, hold down the Shift key on your keyboard, and click on Restart. This should boot you into Windows 10's [Advanced Startup](https://www.dell.com/support/article/en-us/sln317102/booting-to-the-advanced-startup-options-menu-in-windows-10?lang=en) options menu. Click on Troubleshoot, click on Advanced options, and try using the Startup Repair option to see if that can solve your Windows problem.

###### How Can You Keep Your Old Desktop PC Running Well?

When your desktop PC is aging, but you don’t have the heart (or the budget) to replace it, there’s…

If all else fails, then a wipe and restore might be your best option. Save all your critical Windows 10 files to a flash drive or [cloud storage](https://lifehacker.com/google-one-is-now-open-for-everyone-but-is-it-a-good-d-1826049257), then launch macOS and use Boot Camp Assistant to [remove your Windows OS](https://support.apple.com/guide/bootcamp-assistant/remove-windows-from-your-mac-using-boot-camp-bcmp59c41c31/mac). Use Microsoft’s [Media Creation Tool](https://www.microsoft.com/en-us/software-download/windows10) to download a new, fresh .ISO of Windows 10, and then use [Boot Camp](https://support.apple.com/guide/bootcamp-assistant/get-started-with-boot-camp-on-mac-bcmp712cfeb8/6.1/mac/10.15) to reinstall that on your Mac. Once Windows is up and running, make sure you’ve installed any updates from Apple (the aforementioned Windows Support Drivers and Apple Software Update) first, then install all the WIndows Updates Microsoft offers, _then_ start putting your files and apps [back on your system](https://lifehacker.com/the-best-way-to-quickly-install-apps-on-a-new-windows-p-1836244140) once you’ve verified that everything feels right.

Don’t worry; it takes a lot less time than it sounds like.
