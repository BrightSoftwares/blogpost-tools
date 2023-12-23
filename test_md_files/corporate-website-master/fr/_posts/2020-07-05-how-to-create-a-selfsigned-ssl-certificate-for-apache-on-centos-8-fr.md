---
layout: flexstart-blog-single
title:  "How To Create a Self-Signed SSL Certificate for Apache on CentOS 8"
author: full
lang: fr
ref: selfsigned_ssl_1237
categories: [ ubuntu ]
description: "TLS, or “transport layer security” — and its predecessor SSL — are protocols used to wrap normal traffic in a protected, encrypted wrapper. Using this technology, servers can safely send information to their clients without their messages being intercepted or read by an outside party.
In this guide, we will show you how to create and use a self-signed SSL certificate with the Apache web server on a CentOS 8 machine."
image: "https://sergio.afanou.com/assets/images/image-midres-46.jpg"
seo:
  links: [ "https://www.wikidata.org/wiki/Q381" ]
---

<h3 id="introduction">Introduction</h3>

<p><strong>TLS</strong>, or &ldquo;transport layer security&rdquo; — and its predecessor <strong>SSL</strong> — are protocols used to wrap normal traffic in a protected, encrypted wrapper. Using this technology, servers can safely send information to their clients without their messages being intercepted or read by an outside party.</p>

<p>In this guide, we will show you how to create and use a self-signed SSL certificate with the Apache web server on a CentOS 8 machine.</p>

<span class='note'><p>
<strong>Note:</strong> A self-signed certificate will encrypt communication between your server and its clients. However, because it is not signed by any of the trusted certificate authorities included with web browsers and operating systems, users cannot use the certificate to automatically validate the identity of your server. As a result, your users will see a security error when visiting your site.</p>

<p>Because of this limitation, self-signed certificates are not appropriate for a production environment serving the public. They are typically used for testing, or for securing non-critical services used by a single user or a small group of users that can establish trust in the certificate&rsquo;s validity through alternate communication channels.</p>

<p>For a more production-ready certificate solution, check out <a href="https://letsencrypt.org/">Let&rsquo;s Encrypt</a>, a free certificate authority. You can learn how to download and configure a Let&rsquo;s Encrypt certificate in our <a href="https://www.digitalocean.com/community/tutorials/how-to-secure-apache-with-let-s-encrypt-on-centos-8">How To Secure Apache with Let&rsquo;s Encrypt on CentOS 8</a> tutorial.<br></p></span>

<h2 id="prerequisites">Prerequisites</h2>

<p>Before starting this tutorial, you&rsquo;ll need the following: </p>

<ul>
<li>Access to a CentOS 8 server with a non-<strong>root</strong>, sudo-enabled user. Our <a href="https://www.digitalocean.com/community/tutorials/initial-server-setup-with-centos-8">Initial Server Setup with CentOS 8</a> guide can show you how to create this account.</li>
<li><p>You will also need to have Apache installed. You can install Apache using <code>dnf</code>:</p>
<pre class="code-pre command prefixed"><code><ul class="prefixed"><li class="line" prefix="$">sudo dnf install httpd
</li></ul></code></pre>
<p>Enable Apache and start it using <code>systemctl</code>:</p>
<pre class="code-pre command prefixed"><code><ul class="prefixed"><li class="line" prefix="$">sudo systemctl enable httpd
</li><li class="line" prefix="$">sudo systemctl start httpd
</li></ul></code></pre>
<p>And finally, if you have a <code>firewalld</code> firewall set up, open up the <code>http</code> and <code>https</code> ports:</p>
<pre class="code-pre command prefixed"><code><ul class="prefixed"><li class="line" prefix="$">sudo firewall-cmd --permanent --add-service=http
</li><li class="line" prefix="$">sudo firewall-cmd --permanent --add-service=https
</li><li class="line" prefix="$">sudo firewall-cmd --reload
</li></ul></code></pre></li>
</ul>

<p>After these steps are complete, be sure you are logged in as your non-<strong>root</strong> user and continue with the tutorial.</p>

<h2 id="step-1-—-installing-mod_ssl">Step 1 — Installing <code>mod_ssl</code></h2>

<p>We first need to install <code>mod_ssl</code>, an Apache module that provides support for SSL encryption.</p>

<p>Install <code>mod_ssl</code> with the <code>dnf</code> command:</p>
<pre class="code-pre command prefixed"><code><ul class="prefixed"><li class="line" prefix="$">sudo dnf install mod_ssl
</li></ul></code></pre>
<p>Because of a packaging bug, we need to restart Apache once to properly generate the default SSL certificate and key, otherwise we&rsquo;ll get an error reading <code>'/etc/pki/tls/certs/localhost.crt' does not exist or is empty</code>.</p>
<pre class="code-pre command prefixed"><code><ul class="prefixed"><li class="line" prefix="$">sudo systemctl restart httpd
</li></ul></code></pre>
<p>The <code>mod_ssl</code> module is now enabled and ready for use.</p>

<h2 id="step-2-—-creating-the-ssl-certificate">Step 2 — Creating the SSL Certificate</h2>

<p>Now that Apache is ready to use encryption, we can move on to generating a new SSL certificate. The certificate will store some basic information about your site, and will be accompanied by a key file that allows the server to securely handle encrypted data.</p>

<p>We can create the SSL key and certificate files with the <code>openssl</code> command:</p>
<pre class="code-pre command prefixed"><code><ul class="prefixed"><li class="line" prefix="$">sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout /etc/pki/tls/private/apache-selfsigned.key -out /etc/pki/tls/certs/apache-selfsigned.crt
</li></ul></code></pre>
<p>After you enter the command, you will be taken to a prompt where you can enter information about your website. Before we go over that, let&rsquo;s take a look at what is happening in the command we are issuing:</p>

<ul>
<li><code>openssl</code>: This is the command line tool for creating and managing OpenSSL certificates, keys, and other files.</li>
<li><code>req -x509</code>: This specifies that we want to use X.509 certificate signing request (CSR) management. X.509 is a public key infrastructure standard that SSL and TLS adhere to for key and certificate management.</li>
<li><code>-nodes</code>: This tells OpenSSL to skip the option to secure our certificate with a passphrase. We need Apache to be able to read the file, without user intervention, when the server starts up. A passphrase would prevent this from happening, since we would have to enter it after every restart.</li>
<li><code>-days 365</code>: This option sets the length of time that the certificate will be considered valid. We set it for one year here. Many modern browsers will reject any certificates that are valid for longer than one year.</li>
<li><code>-newkey rsa:2048</code>: This specifies that we want to generate a new certificate and a new key at the same time. We did not create the key that is required to sign the certificate in a previous step, so we need to create it along with the certificate. The <code>rsa:2048</code> portion tells it to make an RSA key that is 2048 bits long.</li>
<li><code>-keyout</code>: This line tells OpenSSL where to place the generated private key file that we are creating.</li>
<li><code>-out</code>: This tells OpenSSL where to place the certificate that we are creating.</li>
</ul>

<p>Fill out the prompts appropriately. The most important line is the one that requests the <code>Common Name</code>. You need to enter either the hostname you&rsquo;ll use to access the server by, or the public IP of the server. It&rsquo;s important that this field matches whatever you&rsquo;ll put into your browser&rsquo;s address bar to access the site, as a mismatch will cause more security errors.</p>

<p>The full list of prompts will look something like this:</p>
<pre class="code-pre "><code>Country Name (2 letter code) [XX]:<span class="highlight">US</span>
State or Province Name (full name) []:<span class="highlight">Example</span>
Locality Name (eg, city) [Default City]:<span class="highlight">Example </span>
Organization Name (eg, company) [Default Company Ltd]:<span class="highlight">Example Inc</span>
Organizational Unit Name (eg, section) []:<span class="highlight">Example Dept</span>
Common Name (eg, your name or your server's hostname) []:<span class="highlight">your_domain_or_ip</span>
Email Address []:<span class="highlight">webmaster@example.com</span>
</code></pre>
<p>Both of the files you created will be placed in the appropriate subdirectories of the <code>/etc/pki/tls</code> directory. This is a standard directory provided by CentOS for this purpose.</p>

<p>Next we will update our Apache configuration to use the new certificate and key.</p>

<h2 id="step-3-—-configuring-apache-to-use-ssl">Step 3 — Configuring Apache to Use SSL</h2>

<p>Now that we have our self-signed certificate and key available, we need to update our Apache configuration to use them. On CentOS, you can place new Apache configuration files (they must end in <code>.conf</code>) into <code>/etc/httpd/conf.d</code> and they will be loaded the next time the Apache process is reloaded or restarted.</p>

<p>For this tutorial we will create a new minimal configuration file. If you already have an Apache <code>&lt;Virtualhost&gt;</code> set up and just need to add SSL to it, you will likely need to copy over the configuration lines that start with <code>SSL</code>, and switch the <code>VirtualHost</code> port from <code>80</code> to <code>443</code>. We will take care of port <code>80</code> in the next step.</p>

<p>Open a new file in the <code>/etc/httpd/conf.d</code> directory:</p>
<pre class="code-pre command prefixed"><code><ul class="prefixed"><li class="line" prefix="$">sudo vi /etc/httpd/conf.d/<span class="highlight">your_domain_or_ip</span>.conf
</li></ul></code></pre>
<p>Paste in the following minimal VirtualHost configuration:</p>
<div class="code-label " title="/etc/httpd/conf.d/your_domain_or_ip.conf">/etc/httpd/conf.d/your_domain_or_ip.conf</div><pre class="code-pre "><code>&lt;VirtualHost *:443&gt;
    ServerName <span class="highlight">your_domain_or_ip</span>
    DocumentRoot /var/www/ssl-test
    SSLEngine on
    SSLCertificateFile /etc/pki/tls/certs/apache-selfsigned.crt
    SSLCertificateKeyFile /etc/pki/tls/private/apache-selfsigned.key
&lt;/VirtualHost&gt;
</code></pre>
<p>Be sure to update the <code>ServerName</code> line to however you intend to address your server. This can be a hostname, full domain name, or an IP address. Make sure whatever you choose matches the <code>Common Name</code> you chose when making the certificate.</p>

<p>The remaining lines specify a <code>DocumentRoot</code> directory to serve files from, and the SSL options needed to point Apache to our newly-created certificate and key.</p>

<p>Now let&rsquo;s create our <code>DocumentRoot</code> and put an HTML file in it just for testing purposes:</p>
<pre class="code-pre command prefixed"><code><ul class="prefixed"><li class="line" prefix="$">sudo mkdir /var/www/ssl-test
</li></ul></code></pre>
<p>Open a new <code>index.html</code> file with your text editor:</p>
<pre class="code-pre command prefixed"><code><ul class="prefixed"><li class="line" prefix="$">sudo vi /var/www/ssl-test/index.html
</li></ul></code></pre>
<p>Paste the following into the blank file:</p>
<div class="code-label " title="/var/www/ssl-test/index.html">/var/www/ssl-test/index.html</div><pre class="code-pre "><code>&lt;h1&gt;it worked!&lt;/h1&gt;
</code></pre>
<p>This is not a full HTML file, of course, but browsers are lenient and it will be enough to verify our configuration.</p>

<p>Save and close the file, then check your Apache configuration for syntax errors by typing:</p>
<pre class="code-pre command prefixed"><code><ul class="prefixed"><li class="line" prefix="$">sudo apachectl configtest
</li></ul></code></pre>
<p>You may see some warnings, but as long as the output ends with <code>Syntax OK</code>, you are safe to continue. If this is not part of your output, check the syntax of your files and try again.</p>

<p>When all is well, reload Apache to pick up the configuration changes:</p>
<pre class="code-pre command prefixed"><code><ul class="prefixed"><li class="line" prefix="$">sudo systemctl reload httpd
</li></ul></code></pre>
<p>Now load your site in a browser, being sure to use <code>https://</code> at the beginning. </p>

<p>You should see an error. This is normal for a self-signed certificate! The browser is warning you that it can&rsquo;t verify the identity of the server, because our certificate is not signed by any of the browser&rsquo;s known certificate authorities. For testing purposes and personal use this can be fine. You should be able to click through to <strong>advanced</strong> or <strong>more information</strong> and choose to proceed.</p>

<p>After you do so, your browser will load the <code>it worked!</code> message.</p>

<span class='note'><p>
<strong>Note:</strong> if your browser doesn&rsquo;t connect at all to the server, make sure your connection isn&rsquo;t being blocked by a firewall. If you are using <code>firewalld</code>, the following commands will open ports <code>80</code> and <code>443</code>:</p>

<pre class="code-pre command prefixed"><code><ul class="prefixed"><li class="line" prefix="$">sudo firewall-cmd --permanent --add-service=http
</li><li class="line" prefix="$">sudo firewall-cmd --permanent --add-service=https
</li><li class="line" prefix="$">sudo firewall-cmd --reload
</li></ul></code></pre>
<p></p></span>

<p>Next we will add another <code>VirtualHost</code> section to our configuration to serve plain HTTP requests and redirect them to HTTPS.</p>

<h2 id="step-4-—-redirecting-http-to-https">Step 4 — Redirecting HTTP to HTTPS</h2>

<p>Currently, our configuration will only respond to HTTPS requests on port <code>443</code>. It is good practice to also respond on port <code>80</code>, even if you want to force all traffic to be encrypted. Let&rsquo;s set up a <code>VirtualHost</code> to respond to these unencrypted requests and redirect them to HTTPS.</p>

<p>Open the same Apache configuration file we started in previous steps:</p>
<pre class="code-pre command prefixed"><code><ul class="prefixed"><li class="line" prefix="$">sudo vi /etc/httpd/conf.d/<span class="highlight">your_domain_or_ip</span>.conf
</li></ul></code></pre>
<p>At the bottom, create another <code>VirtualHost</code> block to match requests on port <code>80</code>. Use the <code>ServerName</code> directive to again match your domain name or IP address. Then, use <code>Redirect</code> to match any requests and send them to the SSL <code>VirtualHost</code>. Make sure to include the trailing slash:</p>
<div class="code-label " title="/etc/httpd/conf.d/your_domain_or_ip.conf">/etc/httpd/conf.d/your_domain_or_ip.conf</div><pre class="code-pre "><code>&lt;VirtualHost *:80&gt;
    ServerName <span class="highlight">your_domain_or_ip</span>
    Redirect / https://<span class="highlight">your_domain_or_ip</span>/
&lt;/VirtualHost&gt;
</code></pre>
<p>Save and close this file when you are finished, then test your configuration syntax again, and reload Apache:</p>
<pre class="code-pre command prefixed"><code><ul class="prefixed"><li class="line" prefix="$">sudo apachectl configtest
</li><li class="line" prefix="$">sudo systemctl reload httpd
</li></ul></code></pre>
<p>You can test the new redirect functionality by visiting your site with plain <code>http://</code> in front of the address. You should be redirected to <code>https://</code> automatically.</p>

<h2 id="conclusion">Conclusion</h2>

<p>You have now configured Apache to serve encrypted requests using a self-signed SSL certificate, and to redirect unecrypted HTTP requests to HTTPS.</p>

<p>If you are planning on using SSL for a public website, you should look into purchasing a domain name and using a widely supported certificate authority such as <a href="https://letsencrypt.org/">Let&rsquo;s Encrypt</a>.</p>

<p>For more information on using Let&rsquo;s Encrypt with Apache, please read our <a href="https://www.digitalocean.com/community/tutorials/how-to-secure-apache-with-let-s-encrypt-on-centos-8">How To Secure Apache with Let&rsquo;s Encrypt on CentOS 8</a> tutorial.</p>
