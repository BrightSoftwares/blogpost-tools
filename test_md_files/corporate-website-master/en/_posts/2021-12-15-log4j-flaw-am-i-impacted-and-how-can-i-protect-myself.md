---
layout: flexstart-blog-single
title: "Log4j flaw: Am I impacted and how can I protect myself"
author: full
lang: en
ref: log4jflow<zeroday_impacted_and_protection
categories:
  - security
date: 2021-12-15T13:36:11.440Z
image: https://res.cloudinary.com/brightsoftwares/image/upload/v1639575508/photo-1639140651961-41392a332bfc_njfgu8.jpg
silot_terms: security zero day
toc: true
---
A flaw in Log4j, a Java library developed by the open-source Apache Software Foundation for logging error messages in applications, is the most high-profile security vulnerability on the internet right now and comes with a severity score of 10 out of 10. 


The library is developed by the open-source Apache Software Foundation and is a key Java-logging framework. The [CERT New Zealand triggered an alert last week ](https://www.zdnet.com/article/security-warning-new-zero-day-in-the-log4j-java-library-is-already-being-exploited/) that [CVE-2021-44228](https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2021-44228), a remote code execution flaw in Log4j, was already being exploited by attackers. Several national cybersecurity agencies also issed the alert, including the Cybersecurity and Infrastructure Security Agency (CISA) and the UK's National Cyber Security Centre (NCSC). 

Read more at [Internet infrastructure provider Cloudflare said Log4j exploits started on December 1](https://www.zdnet.com/article/log4j-rce-activity-began-on-december-1-as-botnets-start-using-vulnerability/).  

# What devices and applications are at risk? 

![Are my devices impacted by the Log4j flaw](https://res.cloudinary.com/brightsoftwares/image/upload/v1639579714/log4j_detection_nkqvl4.png)

Here are the criteria:

1. Your device must be exposed to the internet.
2. Your device must be running Apache Log4j
3. Apache Log4j version must be between 2.0 and 2.14.1

If you have **IOT devices** connected to the internet, with the conditions above, you are at risk. Probably, Mirai, a botnet that targets all manner of internet-connected (IoT) devices, might be trying to locate your device.

# Where is Log4j most used?

NCSC [notes](https://www.ncsc.gov.uk/news/apache-log4j-vulnerability) that Log4j version 2 (Log4j2), the affected version, is included in :

* Apache Struts2 framework
* Solr framework
* Druid framework
* Flink framework
* Swift framework. 

For IBM products, there is  Websphere 8.5 and 9.0.

# Big players response

## AWS

AWS is [working on patching its services](https://aws.amazon.com/security/security-bulletins/AWS-2021-005/) that use Log4j and has released mitigations for services like CloudFront. It has also detailed how the flaw impacts its services.


AWS has updated its **WAF rule set** – AWSManagedRulesKnownBadInputsRuleSet AMR – to detect and mitigate Log4j attack attempts and scanning. It also has mitigation options that can be enabled for **CloudFront**, **Application Load Balancer (ALB)**, **API Gateway**, and **AppSync**. It's also currently updating all **Amazon OpenSearch Service** to the patched version of Log4j. 


## IBM

Same for IBM [shared](https://www.ibm.com/blogs/psirt/an-update-on-the-apache-log4j-cve-2021-44228-vulnerability/) that it is ****"actively responding"**** to the Log4j vulnerability across IBM's own infrastructure and its products. IBM has confirmed **Websphere [8.5 and 9.0 are vulnerable](https://www.ibm.com/support/pages/node/6525706/)**. 

Oracle has [issued a patch for the flaw, too](https://www.oracle.com/security-alerts/alert-cve-2021-44228.html). 

> "Due to the severity of this vulnerability and the publication of exploit code on various  sites, Oracle strongly recommends that customers apply the updates provided by this  Security Alert as soon as possible," it said. 

# Other players


Vendors with popular products known to be still vulnerable include 

- Atlassian, 
- Amazon, 
- Microsoft Azure, 
- Cisco, 
- Commvault, 
- ESRI, 
- Exact, 
- Fortinet, 
- JetBrains, 
- Nelson, 
- Nutanix, 
- OpenMRS, 
- Oracle, 
- Red Hat,
- Splunk, 
-Soft, and 
- VMware. 

The list is even longer when adding products where a patch has been released.  


# What you should do: Discover your devices and patch them

![Steps to the solution](https://res.cloudinary.com/brightsoftwares/image/upload/v1639579711/log4j_solution_zbuf59.png)


Part of the challenge will be **identifying software harboring the Log4j vulnerability**. 

The Netherland's Nationaal Cyber Security Centrum (NCSC) has posted a [comprehensive and sourced A-Z list on GitHub](https://github.com/NCSC-NL/log4shell/tree/main/software) of all affected products it is aware are either vulnerable, not vulnerable, are under investigation, or where a fix is available. 

The list of products illustrates how widespread the vulnerability is, spanning cloud services, developer services, security devices, mapping services, and more.    


CISA's main advice is to identify internet-facing devices running Log4j and upgrade them to version 2.15.0, or to apply the mitigations provided by vendors "immediately". But it also recommends setting up alerts for probes or attacks on devices running Log4j.  

> "To be clear, this vulnerability poses a severe risk," [CISA director Jen Easterly said Sunday](https://www.cisa.gov/news/2021/12/11/statement-cisa-director-easterly-log4j-vulnerability). 
> "We will only minimize potential impacts through collaborative efforts between government and the private sector. 
> We urge all organizations to join us in this essential effort and take action."  

Additional steps recommended by CISA include: **enumerating any external facing devices with Log4j installed**; ensuring the **security operations center actions** every alert with Log4j installed; and **installing a web application firewall (WAF)** with rules to focus on Log4j. 


# What if I cannot patch or upgrade?

It is recommended to upgrade to version 2.15.0 of Log4j. There might be situations where upgrading is not immediately possible.

## Update Log4j's configuration

NCSC [recommends](https://www.ncsc.gov.uk/news/apache-log4j-vulnerability) updating to version 2.15.0 or later, and – where not possible – mitigating the flaw in Log4j 2.10 and later by setting system property **```"log4j2.formatMsgNoLookups"``` to ```"true"```** or removing the **```JndiLookup```** class from the classpath. 
  

## Setup network rules to detect exploit attempts

NCCGroup has posted [several network-detection rules](https://research.nccgroup.com/2021/12/12/log4shell-reconnaissance-and-post-exploitation-network-detection/) to detect exploitation attempts and indicators of successful exploitation.

# Is my system compromised?

Finally, Microsoft has released its set of indicators of compromise and [guidance for preventing attacks on Log4j vulnerability](https://www.microsoft.com/security/blog/2021/12/11/guidance-for-preventing-detecting-and-hunting-for-cve-2021-44228-log4j-2-exploitation/). Examples of the post-exploitation of the flaw that Microsoft has seen include installing **coin miners**, **Cobalt Strike** to enable credential theft and lateral movement, and exfiltrating data from compromised systems.  

What is Log4j?
--------------

Log4J is a widely used Java library for logging error messages in applications. It is used in enterprise software applications, including those custom applications developed in-house by businesses, and forms part of many cloud computing services.

Where is Log4j used?
--------------------

The Log4j 2 library is used in enterprise Java software and according to the UK's NCSC is included in Apache frameworks such as Apache Struts2, Apache Solr, Apache Druid, Apache Flink, and Apache Swift.

Which applications are affected by the Log4j flaw?
--------------------------------------------------

Because Log4j is so widely used, the vulnerability may impact a very wide range of software and services from many major vendors. According to NCSC an application is vulnerable "if it consumes untrusted user input and passes this to a vulnerable version of the Log4j logging library."

How widely is the Log4j flaw being exploited?
---------------------------------------------

Security experts have warned that there are hundreds of thousands of attempts by hackers to find vulnerable devices; over 40 percent of corporate networks have been targeted according to one security company.

# Conclusion

The primary objective you need to have is first the assesment of your devices.
Split your team in 3 groups:

1. **Assesment group** : will list all the devices of your infrastructure and check if they are impacted. If they found corrupted devices, take them offline. For the other ones, route them to the tow remaining teams.
2. **Upgrade group** : They perform the upgrade of the devices.
3. **Reconfigure group**: they process the devices that are not immediately upgradable.
