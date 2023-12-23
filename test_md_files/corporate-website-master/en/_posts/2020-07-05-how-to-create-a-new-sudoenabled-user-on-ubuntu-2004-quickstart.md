---
Tags:
- ubuntu
- linux
- server
- security
ToReview: true
author: full
categories:
- ubuntu
description: When managing a server, you’ll sometimes want to allow users to execute
  commands as “root,” the administrator-level user. The sudo command provides system
  administrators with a way to grant administrator privileges — ordinarily only available
  to the root user — to normal users. In this tutorial, you’ll learn how to create
  a new user with sudo access on Ubuntu 20.04 without having to modify your server’s
  /etc/sudoers file.
image: https://sergio.afanou.com/assets/images/image-midres-47.jpg
lang: en
layout: flexstart-blog-single
ref: sudoenabled_202007051236
seo:
  links:
  - https://www.wikidata.org/wiki/Q381
silot_terms: server dev and admin
title: How To Create a New Sudo-enabled User on Ubuntu 20.04 [Quickstart]
toc: true
---

<h3 id="introduction">Introduction</h3>

<p>When managing a server, you’ll sometimes want to allow users to execute commands as “root,” the administrator-level [[2023-05-04-current-user-what-it-is-and-how-it-can-help-your-business|user]]. The <code>sudo</code> command provides system administrators with a way to grant administrator privileges — ordinarily only available to the <strong>root</strong> user — to normal users. </p>

<p>In this tutorial, you’ll learn how to create a new user with <code>sudo</code> access on Ubuntu 20.04 without having to modify your server&rsquo;s <code>/etc/sudoers</code> file. </p>

<p><span class='note'><strong>Note:</strong> If you want to configure <code>sudo</code> for an existing user, skip to step 3.<br></span></p>

<h2 id="step-1-—-logging-into-your-server">Step 1 — Logging Into Your Server</h2>

<p>SSH in to your server as the <strong>root</strong> user:</p>
<pre class="code-pre command prefixed local-environment"><code><ul class="prefixed"><li class="line" prefix="$">ssh root@<span class="highlight">your_server_ip_address</span>
</li></ul></code></pre>
<h2 id="step-2-—-adding-a-new-user-to-the-system">Step 2 — Adding a New User to the System</h2>

<p>Use the <code>adduser</code> command to add a new user to your system:</p>
<pre class="code-pre super_user prefixed"><code><ul class="prefixed"><li class="line" prefix="#">adduser <span class="highlight">sammy</span>
</li></ul></code></pre>
<p>Be sure to replace <code><span class="highlight">sammy</span></code> with the username that you want to create. You will be prompted to create and verify a password for the user:</p>
<pre class="code-pre "><code><div class="secondary-code-label " title="Output">Output</div>Enter new UNIX password:
Retype new UNIX password:
passwd: password updated successfully
</code></pre>
<p>Next, you&rsquo;ll be asked to fill in some information about the new user. It is fine to accept the defaults and leave this information blank:</p>



<pre class="code-pre "><code><div class="secondary-code-label " title="Output">Output</div>Changing the user information for <span class="highlight">sammy</span>
Enter the new value, or press ENTER for the default
    Full Name []:
    Room Number []:
    Work Phone []:
    Home Phone []:
    Other []:
Is the information correct? [Y/n]
</code></pre>
<h2 id="step-3-—-adding-the-user-to-the-sudo-group">Step 3 — Adding the User to the <strong>sudo</strong> Group</h2>

<p>Use the <code>usermod</code> command to add the user to the <strong>sudo</strong> group:</p>
<pre class="code-pre super_user prefixed"><code><ul class="prefixed"><li class="line" prefix="#">usermod -aG sudo <span class="highlight">sammy</span>
</li></ul></code></pre>
<p>Again, be sure to replace <code><span class="highlight">sammy</span></code> with the username you just added. By default on Ubuntu, all members of the <strong>sudo</strong> group have full <code>sudo</code> privileges.</p>

<h2 id="step-4-—-testing-sudo-access">Step 4 — Testing <code>sudo</code> Access</h2>

<p>To test that the new <code>sudo</code> permissions are [[2023-11-27-hp-web-services-not-working-troubleshooting-tips|working]], first use the <code>su</code> command to switch to the new user account:</p>
<pre class="code-pre super_user prefixed"><code><ul class="prefixed"><li class="line" prefix="#">su - <span class="highlight">sammy</span>
</li></ul></code></pre>
<p>As the new user, verify that you can use <code>sudo</code> by prepending <code>sudo</code> to the command that you want to run with superuser privileges:</p>
<pre class="code-pre command prefixed"><code><ul class="prefixed"><li class="line" prefix="$">sudo <span class="highlight">command_to_run</span>
</li></ul></code></pre>
<p>For example, you can list the contents of the <code>/root</code> directory, which is normally only accessible to the root user:</p>
<pre class="code-pre command prefixed"><code><ul class="prefixed"><li class="line" prefix="$">sudo ls -la /root
</li></ul></code></pre>
<p>The first time you use <code>sudo</code> in a session, you will be prompted for the password of that user’s account. Enter the password to proceed:</p>
<pre class="code-pre "><code><div class="secondary-code-label " title="Output:">Output:</div>[sudo] password for <span class="highlight">sammy</span>:
</code></pre>
<p><span class='note'><strong>Note:</strong> This is <em>not</em> asking for the <strong>root</strong> password! Enter the password of the sudo-enabled user you just created.<br></span></p>

<p>If your user is in the proper group and you entered the password correctly, the command that you issued with <code>sudo</code> will run with <strong>root</strong> privileges.</p>

<h2 id="conclusion">Conclusion</h2>

<p>In this quickstart tutorial, we created a new user account and added it to the <strong>sudo</strong> group to enable <code>sudo</code> access. </p>

<p>For your new user to be granted external access, please follow our section on <a href="https://www.digitalocean.com/community/tutorials/initial-server-setup-with-ubuntu-20-04#step-5-%E2%80%94-enabling-external-access-for-your-regular-user">Enabling External Access for Your Regular User</a>.</p>

We checked one ubuntu server in this tutorial. You can have a set of tools to achieve your development targets. One of the most interesting stacks is the LAMP stack. Our blog post on [[2020-04-04-how-to-install-wordpress-with-lamp-on-ubuntu-1604.md|install lamp ubuntu 16.04]] explains how to install WordPress with LAMP on Ubuntu 16.04.

You might want also to secure your installation with SSL. Our blog post on [[2020-07-05-how-to-create-a-selfsigned-ssl-certificate-for-apache-on-centos-8.md|generate ssl certificate apache]] explains why how to create a self-signed SSL certificate for Apache on CentOS 8.



<p>If you need more detailed information on setting up an Ubuntu 20.04 server, please read our <a href="https://www.digitalocean.com/community/tutorials/initial-server-setup-with-ubuntu-20-04">Initial Server Setup with Ubuntu 20.04</a> tutorial.</p>