---
author: full
categories:
- aws
date: 2022-08-10
description: null
image: https://res.cloudinary.com/brightsoftwares/image/upload/t_BSBlogImage/v1655551334/pexels-sora-shimazaki-5668838_cefpaw.jpg
lang: en
layout: flexstart-blog-single
post_date: 2022-08-10
pretified: true
ref: aws_t3_usage
silot_terms: cloud aws
tags:
- aws
- ec2
- finops
title: Regex email validation
toc: true
transcribed: true
youtube_video: https://www.youtube.com/watch?v=QxjAOSUQjP0&ab_channel=TheNetNinja
youtube_video_id: QxjAOSUQjP0
---

Email validation is a very debatted question. The one we are going to see in this post will
probably not catch every single email. There's a lot of debate for what is the best regular expression for an email and I've done a fairly simple one here it captures a most of them to be honest in my opinion but it's maybe not the perfect one.

A lot of people believe it or not argue like mad over what is the best regular expression for
an email.

If you do your research you'll come across different ways of doing this this is just one way out of very many. 

But there you have it . We have all of our different fields accounted for and we're testing them against different regular expressions.


# The structure of an email address

Here they are ! You can see we have four different parts here.
![](https://res.cloudinary.com/brightsoftwares/image/upload/v1658852177/brightsoftwares.com.blog/xz4ol7tl3atztfgbfgou.png)


## Part 1 : the user id

The first part is your domain so the bit before the at symbol for example theboss. 

Next we have the at symbol then the second main part is the domain. 

The first part right here your name this can be any letters numbers dots and all hyphens


So it could be something like donna.peters@something.com. 
Right! So we can have dots in there or donna-peters@something.com


## Part 2: The domain

For example thenetninja or Gmail or whatever email you [[2020-02-12-amazons-t3-who-should-use-it-when-how-and-the-why|use]]. It will be theboss@thenetninja then we have the dot after the domain. 

This second part of the extension (here number four) that is going to be optional.
The second part this domain could be any letter number and or hyphens so it could be at the net ninja or at the net - ninja.


This is going to be compulsory because they all have at least one extension like com or something like that but this second one is going to be optional, dot something else.

## Part 3: the extension

Then the third main part is the extension. So for example, **ca** or **ogg** or in our case **co**.

Number three this third main part of the extension can be any letters but that's it.

We don't have numbers in the extension or symbols it's just lettuce calm dog net
co@uk.

## Part 4: the additional extension

We also have a fourth optional part which is another dot and then the extension. Again so .uk. So sometimes the extension is one word like comma dog and sometimes is two words like co.uk.

And the fourth part over here is always going to begin with a dot then any letters so dots then UK or dot then something else.


# Apply this check on the html form

Let's try creating these four different parts plus the apps and the dot in our regular
expression.


![](https://res.cloudinary.com/brightsoftwares/image/upload/v1658858478/brightsoftwares.com.blog/ed23wj8q2quufslqp5v0.png)



Then so let's start to put together this email regular expression so let's place a comma after the last one the final one is called email.

We'll just do our forward slashes first of all then we'll do the caret and we'll do the dollar sign for the end as well. 


The first part over here your name is any letter numbers dots and or hyphens. First of all what, we will do is enclose this in a set of parentheses just so we know what each section is and they're going to be evaluated separately. But it's not going to have any effect on the overall evaluation of the string.


Any letter first of all so we'll do A to Z and by the way these are all going to be lowercase I'm not doing case insensitive stuff right here. Lower case letters then any digits as well zero to nine so for that we can do buck /d for the digit metacharacter.


We can also allow dots now we can't just do a dot because remember a dot has a special meaning in regex. It means any character whatsoever. We're not seeing any character  we're saying the literal dots. So we have to escape the default special behavior by doing a
backslash before it now you can see its own read meaning we've escaped that
meaning.

Now we've said we're allowed lowercase letters any digit dots we also wanted to allow - so it can place - there as well. 

What about the length? You might have the longest name in the world right so what we could do is just place the plus sign here and that means it needs to be one let alone but as many as you like.


We'll keep it simple and do something like that. So there we go that is the first part of the regular expression done. 

Now we've sorted this bit, next up is the @ symbol so let's place that in that has to come next.


The second part we're going to enclose in brackets as well and the
second part is the domain. We have set here it can be any letters numbers and or hyphens . This isn't going to be too dissimilar to the first part so again a character set any lowercase.


Also will use the digit meta characters or backslash D that's any number from 0 to 9. 
Who knows how long this domain is so I'll do a plus sign right. Here which says this must be at least one character long but as many characters long as need be.


So, we have the first two sections of this email regular expression don't we have your name and the domain as well as this @ symbol in between them. 


![](https://res.cloudinary.com/brightsoftwares/image/upload/v1658859330/brightsoftwares.com.blog/nql9licvans7uvnchszi.png)



The next part remember is the dot for example shawn at the net ninja dot and then we've got the extension to come after this. So let's open up our brackets for the next section and this extension right here number 3 can only be letters.


All right so nothing else just letters. By the way this dot I've done it wrong I fell into the trap it needs to be escaped. Remember the dot has a special meaning so we need to escape that special meaning because we want the literal dot so backslash before the dot.


This next one character set just lowercase letters so A to Z and that's it. What about the length well this time I'm not going to say as long as you want because of no no extensions are 20 characters long instead we'll say between 2 and 8 characters.

I think the least is 2 and the most might be more than a I'm not so sure but we'll
just put in 8. So calm would work - all good work net co and then that is the third part done.


Finally, we have the second part of the extension and remember this second part is
optional. So if we take a look at this again this second part begins with a dot and then it can be any letters again.

Let us open up our parentheses and then inside first of all the first character has to be a dot so back slash dot to escape the normal behavior. That will match a dot then any letters so A - Z for any lowercase letter then the length of this is going to be again between 2 and 8 characters long.


I don't think any of the second part of the extension a more than a or even a in length. That will get us .uk or whatever. Remember this second part is optional so it doesn't have to actually be in the string that we're testing.


To make all of this optional in parentheses you've seen this before we can add a question mark on the end so this question mark makes the character before it optional but since it's all enclosed in brackets it's making this whole thing in brackets before it optional.


So we could have a .co.uk or we could just have a co or com.  

So just to quickly go through this again we have got the your name bit so something like shaun at then the domain so the net ninja then a dot and then the extension which could be co or com.

Then finally the added bit which is optional, .uk or something similar.


![](https://res.cloudinary.com/brightsoftwares/image/upload/v1658852736/brightsoftwares.com.blog/drodkshzx4r7hruv6lgh.png)


So then let's give this a whirl over, here and refresh I'm going to just inspect this element. So we can see there's a class added to it at any point. 

To begin with no class but I'm just gonna say is invalid already so if we start to type out now an email it will only become valid once a valid email address is entered into this field.


The match to the regular expression is true okay so Shawn the net ninja dots co.uk.

We get a valid class here or it could be calm that's absolutely fine as well it's still valid. But we can't end it in a dot that's invalid. We can't end it in something that's ridiculous like that that's invalid or even numbers. This is invalid.

But we can do com we could also add in a - right here and this is still valid any other symbol and it's not valid we can't do that here only hyphens and letters.


Likewise we could add in a Shawn dot something else right here and this would still be funny. Because we're allowing dots and also hyphens here but if we add in something like plus then it's gonna become invalid.


All right so there we go this is a basic regular expression for an email.

![](https://res.cloudinary.com/brightsoftwares/image/upload/v1658852801/brightsoftwares.com.blog/vruhnp3btvgloa7nrmvw.png)

# A disclamer about the best email regex


Just a disclaimer! 

This will probably not catch every single email there's a lot of debate for what is the best regular expression for an email. I have done a fairly simple one here it captures a most of them to be honest. In my opinion but it's maybe not the perfect one.


A lot of people believe it or not argue like mad over what is the best regular expression for
an email.


So if you do your research you'll come across different ways of doing this this is just one way out of very very very many. But there you have it now we have all of our different fields accounted for and we're testing them against different regular expressions.


We've done all that I want to do one more thing in the next video and that's kind of make this look a little bit better and give the user some feedback as to whether their value is valid or invalid.


# Conclusion

That is all.
What is your preferred email validation regex?  How do you build your regular expressions?

Let us know in the comments.