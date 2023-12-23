---
layout: flexstart-blog-single
title:  "How To Configure Jenkins with SSL Using an Nginx Reverse Proxy on Ubuntu 20.04"
author: full
lang: fr
ref: configure_jenkins_202007051235
categories: [ docker ]
description: "By default, Jenkins comes with its own built-in Winstone web server listening on port 8080, which is convenient for getting started. It’s also a good idea, however, to secure Jenkins with SSL to protect passwords and sensitive data transmitted through the web interface.

In this tutorial, you will configure Nginx as a reverse proxy to direct client requests to Jenkins."
image: "https://sergio.afanou.com/assets/images/image-midres-32.jpg"
seo:
  links: [ "https://m.wikidata.org/wiki/Q15206305", "https://www.wikidata.org/wiki/Q7491312" ]
---

<h3 id="introduction">Introduction</h3>

<p>By default, <a href="https://jenkins.io/">Jenkins</a> comes with its own built-in Winstone web server listening on port <code>8080</code>, which is convenient for getting started. It&rsquo;s also a good idea, however, to secure Jenkins with SSL to protect passwords and sensitive data transmitted through the web interface. </p>

<p>In this tutorial, you will configure Nginx as a reverse proxy to direct client requests to Jenkins. </p>

<h2 id="prerequisites">Prerequisites</h2>

<p>To begin, you&rsquo;ll need the following:</p>

<ul>
<li>One Ubuntu 20.04 server configured with a non-root sudo-enabled user and firewall, following the <a href="https://www.digitalocean.com/community/tutorials/initial-server-setup-with-ubuntu-20-04">Ubuntu 20.04 initial server setup guide</a>.</li>
<li>Jenkins installed, following the steps in <a href="https://www.digitalocean.com/community/tutorials/how-to-install-jenkins-on-ubuntu-20-04">How to Install Jenkins on Ubuntu 20.04</a></li>
<li>Nginx installed, following the steps in <a href="https://www.digitalocean.com/community/tutorials/how-to-install-nginx-on-ubuntu-20-04">How to Install Nginx on Ubuntu 20.04</a></li>
<li>An SSL certificate for a domain provided by <a href="https://letsencrypt.org/">Let&rsquo;s Encrypt</a>. Follow <a href="https://www.digitalocean.com/community/tutorials/how-to-secure-nginx-with-let-s-encrypt-on-ubuntu-20-04">How to Secure Nginx with Let&rsquo;s Encrypt on Ubuntu 20.04</a> to obtain this certificate. Note that you will need a <a href="https://www.digitalocean.com/docs/networking/dns/">registered domain name</a> that you own or control. This tutorial will use the domain name <strong>example.com</strong> throughout.</li>
</ul>

<h2 id="step-1-—-configuring-nginx">Step 1 — Configuring Nginx</h2>

<p>In the prerequisite tutorial <a href="https://www.digitalocean.com/community/tutorials/how-to-secure-nginx-with-let-s-encrypt-on-ubuntu-20-04">How to Secure Nginx with Let&rsquo;s Encrypt on Ubuntu 20.04</a>, you configured Nginx to use SSL in the <code>/etc/nginx/sites-available/<span class="highlight">example.com</span></code> file. Open this file to add your reverse proxy settings:</p>
<pre class="code-pre command prefixed"><code><ul class="prefixed"><li class="line" prefix="$">sudo nano /etc/nginx/sites-available/<span class="highlight">example.com</span>
</li></ul></code></pre>
<p>In the <code>server</code> block with the SSL configuration settings, add Jenkins-specific access and error logs: </p>
<div class="code-label " title="/etc/nginx/sites-available/example.com">/etc/nginx/sites-available/example.com</div><pre class="code-pre "><code>. . . 
server {
        . . .
        # SSL Configuration
        #
        listen [::]:443 ssl ipv6only=on; # managed by Certbot
        listen 443 ssl; # managed by Certbot
        <span class="highlight">access_log            /var/log/nginx/jenkins.access.log;</span>
        <span class="highlight">error_log             /var/log/nginx/jenkins.error.log;</span>
        . . .
        }
</code></pre>
<p>Next let&rsquo;s configure the proxy settings. Since we&rsquo;re sending all requests to Jenkins, we&rsquo;ll comment out the default <code>try_files</code> line, which would otherwise return a 404 error before the request reaches Jenkins:</p>
<div class="code-label " title="/etc/nginx/sites-available/example.com">/etc/nginx/sites-available/example.com</div><pre class="code-pre "><code>. . .
           location / {
                # First attempt to serve request as file, then
                # as directory, then fall back to displaying a 404.
                <span class="highlight">#</span> try_files $uri $uri/ =404;        }
. . . 
</code></pre>
<p>Let&rsquo;s now add the proxy settings, which include:</p>

<ul>
<li><code>proxy_params</code>: The <code>/etc/nginx/proxy_params</code> file is supplied by Nginx and ensures that important information, including the hostname, the protocol of the client request, and the client IP address, is retained and available in the log files.</li>
<li><code>proxy_pass</code>: This sets the protocol and address of the proxied server, which in this case will be the Jenkins server accessed via <code>localhost</code> on port <code>8080</code>. </li>
<li><code>proxy_read_timeout</code>: This enables an increase from Nginx&rsquo;s 60 second default to the Jenkins-recommended 90 second value. </li>
<li><code>proxy_redirect</code>: This ensures that <a href="https://wiki.jenkins-ci.org/display/JENKINS/Jenkins+says+my+reverse+proxy+setup+is+broken">responses are correctly rewritten</a> to include the proper host name.</li>
</ul>

<p>Be sure to substitute your SSL-secured domain name for <code><span class="highlight">example.com</span></code> in the <code>proxy_redirect</code> line below:</p>
<div class="code-label " title="/etc/nginx/sites-available/example.com">/etc/nginx/sites-available/example.com</div><pre class="code-pre "><code>Location /  
. . .
           location / {
                # First attempt to serve request as file, then
                # as directory, then fall back to displaying a 404.
                <span class="highlight">#</span> try_files $uri $uri/ =404;
                <span class="highlight">include /etc/nginx/proxy_params;</span>
                <span class="highlight">proxy_pass          http://localhost:8080;</span>
                <span class="highlight">proxy_read_timeout  90s;</span>
                <span class="highlight"># Fix potential "It appears that your reverse proxy setup is broken" error.</span>
                <span class="highlight">proxy_redirect      http://localhost:8080 https://example.com;</span>
</code></pre>
<p>Once you&rsquo;ve made these changes, save the file and exit the editor. We&rsquo;ll hold off on restarting Nginx until after we’ve configured Jenkins, but we can test our configuration now:</p>
<pre class="code-pre command prefixed"><code><ul class="prefixed"><li class="line" prefix="$">sudo nginx -t
</li></ul></code></pre>
<p>If all is well, the command will return:</p>
<pre class="code-pre "><code><div class="secondary-code-label " title="Output">Output</div>nginx: the configuration file /etc/nginx/nginx.conf syntax is ok
nginx: configuration file /etc/nginx/nginx.conf test is successful
</code></pre>
<p>If not, fix any reported errors until the test passes.</p>

<span class='note'><p>
<strong>Note:</strong> <br>
If you misconfigure the <code>proxy_pass</code> (by adding a trailing slash, for example), you will get something similar to the following in your Jenkins <strong>Configuration</strong> page.</p>

<p><img src="https://assets.digitalocean.com/articles/nginx_jenkins/1.jpg" alt="Jenkins error: Reverse proxy set up is broken"></p>

<p>If you see this error, double-check your <code>proxy_pass</code> and <code>proxy_redirect</code> settings in the Nginx configuration.<br></p></span>

<h2 id="step-2-—-configuring-jenkins">Step 2 — Configuring Jenkins</h2>

<p>For Jenkins to work with Nginx, you will need to update the Jenkins configuration so that the Jenkins server listens only on the <code>localhost</code> interface rather than on all interfaces (<code>0.0.0.0</code>). If Jenkins listens on all interfaces, it&rsquo;s potentially accessible on its original, unencrypted port (<code>8080</code>).  </p>

<p>Let&rsquo;s modify the <code>/etc/default/jenkins</code> configuration file to make these adjustments:</p>
<pre class="code-pre command prefixed"><code><ul class="prefixed"><li class="line" prefix="$">sudo nano /etc/default/jenkins
</li></ul></code></pre>
<p>Locate the <code>JENKINS_ARGS</code> line and add <code>--httpListenAddress=127.0.0.1</code> to the existing arguments:</p>
<div class="code-label " title="/etc/default/jenkins">/etc/default/jenkins</div><pre class="code-pre "><code>. . .
JENKINS_ARGS="--webroot=/var/cache/$NAME/war --httpPort=$HTTP_PORT <span class="highlight">--httpListenAddress=127.0.0.1</span>"
</code></pre>
<p>Save and exit the file.</p>

<p>To use the new configuration settings, restart Jenkins:</p>
<pre class="code-pre command prefixed"><code><ul class="prefixed"><li class="line" prefix="$">sudo systemctl restart jenkins
</li></ul></code></pre>
<p>Since <code>systemctl</code> doesn&rsquo;t display output, check the status:</p>
<pre class="code-pre command prefixed"><code><ul class="prefixed"><li class="line" prefix="$">sudo systemctl status jenkins
</li></ul></code></pre>
<p>You should see the <code>active (exited)</code> status in the <code>Active</code> line:</p>
<pre class="code-pre "><code><div class="secondary-code-label " title="Output">Output</div>● jenkins.service - LSB: Start Jenkins at boot time
   Loaded: loaded (/etc/init.d/jenkins; generated)
   Active: <span class="highlight">active (exited)</span> since Mon 2018-07-09 20:26:25 UTC; 11s ago
     Docs: man:systemd-sysv-generator(8)
  Process: 29766 ExecStop=/etc/init.d/jenkins stop (code=exited, status=0/SUCCESS)
  Process: 29812 ExecStart=/etc/init.d/jenkins start (code=exited, status=0/SUCCESS)
</code></pre>
<p>Restart Nginx:</p>
<pre class="code-pre command prefixed"><code><ul class="prefixed"><li class="line" prefix="$">sudo systemctl restart nginx
</li></ul></code></pre>
<p>Check the status:</p>
<pre class="code-pre command prefixed"><code><ul class="prefixed"><li class="line" prefix="$">sudo systemctl status nginx
</li></ul></code></pre><pre class="code-pre "><code><div class="secondary-code-label " title="Output">Output</div>● nginx.service - A high performance web server and a reverse proxy server
   Loaded: loaded (/lib/systemd/system/nginx.service; enabled; vendor preset: enabled)
   Active: <span class="highlight">active (running)</span> since Mon 2018-07-09 20:27:23 UTC; 31s ago
     Docs: man:nginx(8)
  Process: 29951 ExecStop=/sbin/start-stop-daemon --quiet --stop --retry QUIT/5 --pidfile /run/nginx.pid (code=exited, status=0/SUCCESS)
  Process: 29963 ExecStart=/usr/sbin/nginx -g daemon on; master_process on; (code=exited, status=0/SUCCESS)
  Process: 29952 ExecStartPre=/usr/sbin/nginx -t -q -g daemon on; master_process on; (code=exited, status=0/SUCCESS)
 Main PID: 29967 (nginx)
</code></pre>
<p>With both servers restarted, you should be able to visit the domain using either HTTP or HTTPS. HTTP requests will be redirected automatically to HTTPS, and the Jenkins site will be served securely.</p>

<h2 id="step-3-—-testing-the-configuration">Step 3 — Testing the Configuration</h2>

<p>Now that you have enabled encryption, you can test the configuration by resetting the administrative password. Let&rsquo;s start by visiting the site via HTTP to verify that you can reach Jenkins and are redirected to HTTPS.</p>

<p>In your web browser, enter <code>http://<span class="highlight">example.com</span></code>, substituting your domain for <code><span class="highlight">example.com</span></code>. After you press <code>ENTER</code>, the URL should start with <code>https</code> and the location bar should indicate that the connection is secure. </p>

<p>You can enter the administrative username you created in <a href="https://www.digitalocean.com/community/tutorials/how-to-install-jenkins-on-ubuntu-20-04">How To Install Jenkins on Ubuntu 20.04</a> in the <strong>User</strong> field, and the password that you selected in the <strong>Password</strong> field.</p>

<p>Once logged in, you can change the password to be sure it&rsquo;s secure. </p>

<p>Click on your username in the upper-right-hand corner of the screen. On the main profile page, select <strong>Configure</strong> from the list on the left side of the page:</p>

<p><img src="https://assets.digitalocean.com/articles/jenkins-nginx-ubuntu-1804/configure_password.png" alt="Navigate to Jenkins password page"></p>

<p>This will take you to a new page, where you can enter and confirm a new password:</p>

<p><img src="https://assets.digitalocean.com/articles/jenkins-nginx-ubuntu-1804/password_page.png" alt="Jenkins create password page"></p>

<p>Confirm the new password by clicking <strong>Save</strong>. You can now use the Jenkins web interface securely.</p>

<h3 id="conclusion">Conclusion</h3>

<p>In this tutorial, you configured Nginx as a reverse proxy to Jenkins&rsquo; built-in web server to secure your credentials and other information transmitted via the web interface. Now that Jenkins is secure, you can learn <a href="https://www.digitalocean.com/community/tutorials/how-to-set-up-continuous-integration-pipelines-in-jenkins-on-ubuntu-16-04">how to set up a continuous integration pipeline</a> to automatically test code changes.  Other resources to consider if you are new to Jenkins are <a href="https://jenkins.io/doc/pipeline/tour/hello-world/">the Jenkins project&rsquo;s &ldquo;Creating your first Pipeline&rdquo;</a> tutorial or <a href="https://plugins.jenkins.io/">the library of community-contributed plugins</a>.</p>
