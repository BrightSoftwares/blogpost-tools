---
ToReview: true
author: full
categories:
- aws
description: "T2 standard got vastly misunderstood due to its CPU throttling over
  baseline, to which Amazon introduced T2 unlimited – with a way to overcome the CPU
  throttling with a pay for credit mechanism for the period the EC2 ran over the baseline.
  Should you from from\taws T2 vs T3"
image: https://sergio.afanou.com/assets/images/image-midres-6.jpg
lang: en
layout: flexstart-blog-single
ref: aws_t3_usage
seo:
  links:
  - https://www.wikidata.org/wiki/Q456157
silot_terms: cloud aws
tags:
- aws
- ec2
- finops
title: Amazon’s T3 – Who should use it, when, how and the why?
toc: true
---

![Amazons T3 instance type](https://www.cloudsqueeze.ai/wp-content/uploads/2018/08/Amazon-T3-780.jpg)

Amazon just announced on August 21st [a the third generation of the T series – T3](https://aws.amazon.com/blogs/aws/new-t3-instances-burstable-cost-effective-performance/). This article will look at:

*   How does the T3 class works?
*   Is T3 class an instance type to use in your [[2022-01-20-migrate-your-current-vps-linode-rackspace-aws-ec2-to-digitalocean-reviewed|EC2]] arsenal list?
*   If so, when does it make sense to enable T3?

T2 standard got vastly misunderstood due to its CPU throttling over baseline, to which Amazon introduced [T2 unlimited](https://www.cloudsqueeze.ai/amazons-t2-unlimited-who-should-use-it-when-how-and-the-why/index.html) – with a way to overcome the CPU throttling with a pay for credit mechanism for the period the EC2 ran over the baseline. The new introduction – [T3, is a T2 unlimited](https://aws.amazon.com/ec2/instance-types/t3/) with some subtle variations and has use cases in your EC2 arsenal.

Each T3 instances has a fixed set of memory and a baseline threshold specified by AWS. Let’s compare some of the attributes of T3 classes with that of T2.  Notice how the number of vCPUs given at the lower ends has doubled for t3.nano, t3.micro, t3.small as compared to t2.nano, t2.micro, and t2.small. The pricing once you exceed the baseline threshold is at $0.05 / CPU hour when bursting above baseline. So while AWS can make an unprecedented claim for the t3.nano can operate as low as $3.796 / month, inherent in bursting above the baseline lies some unexpected price surprises for the naive user, who hasn’t understood how the T3 class works.

![Comparison of T3 and T2 types](https://www.cloudsqueeze.ai/wp-content/uploads/2018/08/t31.png)

## The comparison AWS t2 vs t3. 

The baseline characteristics of T3 are similar to that of T2 unlimited in many ways. CPU utilization is measured at the millisecond level by AWS for this instance type. When your T3 class system is operating at levels below the baseline for that EC2, it is earning credits at an established rate; at baseline, neither credits are earned nor depleted; at thresholds over baseline, you are paying for the credits based on the number of vCPUs for that instance type.

### The CPU credit

![How T3 credits work](https://www.cloudsqueeze.ai/wp-content/uploads/2018/08/t32.png)

T3.nano may be an alternative pitched at the low end of the hosting market where WordPress sites are hosted on shared platforms for $5-10 / month. If the usage is a handful of visitors a day, this may be sufficient. If you have some batch or a runaway process and exceed the baseline credits across 2 vCPUs, this is where the borrowed credits and payment kicks in.

One CPU credit is equal to one vCPU running at 100% utilization for one minute. For example, one CPU credit is equal to one vCPU running at 50% utilization for two minutes, or two vCPUs running at 25% utilization for two minutes. T3 class earns credits when operating below baseline with a maximum credit level which is accrued for up to 7 days, unlike T2 unlimited which appears to have a daily limit. ![T3 baseline chart](https://www.cloudsqueeze.ai/wp-content/uploads/2018/08/t33.png)

CPU credits have a charge at $0.05 per vCPU-Hour for Linux and at $0.096 per vCPU-Hour for Windows. This is where the new smaller end T3.nano customer can find a surprise in their bill.

Yes the t3.nano is only $3.796 / month (without EBS storage and IP cost), but if one managed to run this instance at 100% utilization for a month the bill could be as high as $3.976 + ($0.05 \* 2 \* 24 \* 30) = $75.976 / month. If you aren’t able to monitor credits earned the lower end T3 class operating in the unlimited mode is bound to get a few people with bill shocks on expectation set at $4/month. At these surprise price points of $75 / month, there are far better instance types like the C5.large that has 2 vCPUs and 4GiBs (8 times more memory than the T3.nano) at $61 / month (Linux, US-East-1 region).

> A $4/month cost for T3.nano can turn as high as $76/month, whereas the C5.large has 8 times the memory T3.nano can run at $61/month.

[Tweet this](https://twitter.com/intent/tweet?text=A $4/month cost for T3.nano can turn as high as $76/month, whereas the C5.large has 8 times the memory T3.nano can run at $61/month.&url=https://www.cloudsqueeze.ai/amazons-t3-who-should-use-it-when-how-and-the-why/index.html&via=cloudsqueeze)

T2 standard, on the other hand, has the restriction similar to if a web server is hosted along with thousands of others, that the performance just gets throttled. Turning on T2 unlimited in such situations has the benefit in that you know your application isn’t getting throttled if you get a sudden unexpected burst.

Taking out the surprise factor for the T3 at the smaller ends of the spectrum, at the 4, 8, 16, 32 GiB memory thresholds there is good price performance for this T3 class in general. The vast majority of the analysis the public cloud deployments we have seen, which Amazon would likely have done as well they would know that most EC2 instances are operating well under these baseline thresholds of 30-40% range. There are typical daily usage patterns (9-5 type) and weekend usage patterns (low relative to weekdays) for public cloud and general cloud deployments for a myriad of reasons where T3 has a better value proposition in many use cases.

To understand the value proposition let’s look at the cost/vCPU for memory for Linux and Microsoft. For these prices, I am using pricing as of this date for the US-East-1 region, and for the most part, the relative price ratios hold across regions:

![T3 price comparison](https://www.cloudsqueeze.ai/wp-content/uploads/2018/08/t34.png)

## AWS T2 vs T3 Pricing comparison

Notice first the burst price point credit price – this is the price for borrowed CPU credits from Amazon when earned credits are exhausted. At the lower end of the GB spectrum (under 4GB) the choices in other classes are limited. The options available are is an older M class (m1.small) system and C5 class that have higher price points. If your memory requirements are at 0.5, 1, 2 GB range and your workload can stay for the most part inside the baseline range T2 or T3 are good choices. If price predictability is more important than performance consider T2 standard. If performance is more important than price T2 unlimited and T3 may be good in the short term. If you are consistently exhausting credits earned and borrowing credits to maintain your system performance then M1.small (1vCPU, 1.7GB) and C5.large(2vCPU, 4GB) become systems to consider over the T3 or T2 unlimited.

> If price predictability is more important than performance for an application needing 0.5, 1, 2 GB of memory consider the T2 standard. If performance is important over price and you are relatively certain the utilization is well under the 20% baseline then consider T3 or T2 unlimited. If performance is important relative to price variability then consider m1.small or c5.large.

[Tweet this](https://twitter.com/intent/tweet?text=If price predictability is more important than performance for an application needing 0.5, 1, 2 GB of memory consider the T2 standard. If performance is important over price and you are relatively certain the utilization is well under the 20% baseline then consider T3 or T2 unlimited. If performance is important relative to price variability then consider m1.small or c5.large.&url=https://www.cloudsqueeze.ai/amazons-t3-who-should-use-it-when-how-and-the-why/index.html&via=cloudsqueeze)

The price for Microsoft burst credits is at $0.096/vCPU hour. It has similar patterns to Unix in that under 4GB memory T3 class is an excellent choice.  
![T3 price compare ](https://www.cloudsqueeze.ai/wp-content/uploads/2018/08/t35.png)

In both, the above graphs note the clusters around 4GB, 8GB, 16GB, and 32GB. The close cluster offerings come from newer generation C5 and M5 systems. Let’s look at these prices relative to each other and include a 1-year convertible no cash upfront option. The reason to consider convertible reservation type is it gives you more choices – example if during the term of the agreement T4 type comes up which is likely at a far lower cost with a performance enhancement – it has to do with the nature of technology! If you look at the first generation or even second generation classes of C, M and if you purchased the standard 3-year reservation, vs. cost savings on C5, M5 – you will likely be better off on newer class system types from performance enhancements and cost savings inherent in these newer generation systems.

> The convertible reservation type gives you more choices than the standard reservation to change as technology changes occur in the cloud.

[Tweet this](https://twitter.com/intent/tweet?text=The convertible reservation type gives you more choices than the standard reservation to change as technology changes occur in the cloud.&url=https://www.cloudsqueeze.ai/amazons-t3-who-should-use-it-when-how-and-the-why/index.html&via=cloudsqueeze)

![C, M and T3 price comparison](https://www.cloudsqueeze.ai/wp-content/uploads/2018/08/t36.png)

At the 4GB threshold, if your baseline usage is in the 20% range then T3 is a great choice. In the C class, the C5.large is perhaps the only choice as in the M5 class the lowest end starts at 8GB of memory. If your T3 instance starts borrowing credits frequently the performance of C5 class turns out to be almost double the price (103%) increase.

> At the 4GB memory level, the cost savings you get from T3.medium is significant even if you are bursting ocassionally compared to a C5 instance type, that is the closest in performance value combination.

[Tweet this](https://twitter.com/intent/tweet?text=At the 4GB memory level, the cost savings you get from T3.medium is significant even if you are bursting ocassionally compared to a C5 instance type, that is the closest in performance value combination.&url=https://www.cloudsqueeze.ai/amazons-t3-who-should-use-it-when-how-and-the-why/index.html&via=cloudsqueeze)

At 8,16, 32 GB of memory, if you are relatively certain that your baseline performance is in the 30-40% range T3, is a good bet. But with C5 and M5 operating at 1.6% higher than the T3 price point when you get fractions of CPU isn’t all that attractive! Most systems deployed in the AWS cloud rarely sustain 30-40% utilization consistently over a 24 hour period. However, if you haven’t actively monitored CPU utilization patterns and performance is important, the risk with T3 and unlimited turned on as default is the possibility of a surprise element of cost relative to a C5 or M5 instance type that has overall good performance and value.

> At 8,16, 32GB memory usage levels, T3 family isnt an attractive choice if your application utilization baseline is over the 30-40% levels. Most applications rarely sustain these thresholds consistently over a 24 hour period. If performance is important at these memory thresholds the C5 and M5 systems provide a good overall value proposition relative to the T3 family.

[Tweet this](https://twitter.com/intent/tweet?text=At 8,16, 32GB memory usage levels, T3 family isnt an attractive choice if your application utilization baseline is over the 30-40% levels. Most applications rarely sustain these thresholds consistently over a 24 hour period. If performance is important at these memory thresholds the C5 and M5 systems provide a good overall value proposition relative to the T3 family.&url=https://www.cloudsqueeze.ai/amazons-t3-who-should-use-it-when-how-and-the-why/index.html&via=cloudsqueeze)

On the readers posted a survey response on the ways to overcome this default setting and how to run T3 in prior standard mode that I would like to address as an addendum to this initial post. Yes, running a T3 in standard mode overcomes this potential issue of an unexpected bill when credits needed are charged. The downside of this is the cost surprise if you are not looking at CloudWatch logs on CPU credits earned, consumed specific to the T2/T3 class.

In the EC2 console you should find a change T2/T3 unlimited setting.  
![Where to change T3 to standard](https://www.cloudsqueeze.ai/wp-content/uploads/2018/08/T3a1.png)  
The default on T3 is enabled state that can be toggled easily:

![toggle T3 settings](https://www.cloudsqueeze.ai/wp-content/uploads/2018/08/T3A2.png)  
![where to change T3](https://www.cloudsqueeze.ai/wp-content/uploads/2018/08/T3A3.png)  
If you are changing a T2 instance to T3 ensure the ENA requirement is met on the T3. This is referenced in greater detail under the [AWS tutorials](https://www.cloudsqueeze.ai/aws-tutorials/index.html) on [how to change an EC2 instance type](https://www.cloudsqueeze.ai/how-to-change-an-aws-ec2-instance-type-a-step-by-step-guide/index.html).  You can change most instance types to the T class, and specifically [how to change an instance type to T2](https://www.cloudsqueeze.ai/how-to-change-to-t2-unlimited-for-an-aws-ec2-instance-type/index.html) is described, and the steps are nearly the same, just select T3.  If you attempt to change the instance type without this ENA requirement met, you will see an error like this below (do not panic):  


![error with T3](https://www.cloudsqueeze.ai/wp-content/uploads/2018/08/T3A4.png)


In summary, T3 instance family with its default behavior similar to that of T2 unlimited is likely to surprise some who haven’t looked at application utilization characteristics of memory and CPU. If you use T3, ensure you are actively monitoring CPU utilization, earned credits and borrowed credits from CloudWatch. The T2 standard type may be something to consider when CPU throttling is an acceptable way to limit application anomalies – example rouge run away code loops that consume CPU unexpectedly or some malware installs change the way CPU is consumed. If performance is relatively important the C5 and M5 families can be better choices over the newly introduced T3 class. The T3 class while it has a low price point, the default behavior of unlimited burst credits along with more vCPUs over T2 has the potential to surprise someone expecting a $4/month bill to turn to $76/month (Windows system to cost additional over Linux).

/\*\* \* RECOMMENDED CONFIGURATION VARIABLES: EDIT AND UNCOMMENT THE SECTION BELOW TO INSERT DYNAMIC VALUES FROM YOUR PLATFORM OR CMS. \* LEARN WHY DEFINING THESE VARIABLES IS IMPORTANT: https://disqus.com/admin/universalcode/#configuration-variables\*/ /\* var disqus\_config = function () { this.page.url = PAGE\_URL; // Replace PAGE\_URL with your page's canonical URL variable this.page.identifier = PAGE\_IDENTIFIER; // Replace PAGE\_IDENTIFIER with your page's unique identifier variable }; \*/ (function() { // DON'T EDIT BELOW THIS LINE var d = document, s = d.createElement('script'); s.src = 'https://https-www-softwareworx-com.disqus.com/embed.js'; s.setAttribute('data-timestamp', +new Date()); (d.head || d.body).appendChild(s); })();

Please enable JavaScript to view the [comments powered by Disqus.](https://disqus.com/?ref_noscript)