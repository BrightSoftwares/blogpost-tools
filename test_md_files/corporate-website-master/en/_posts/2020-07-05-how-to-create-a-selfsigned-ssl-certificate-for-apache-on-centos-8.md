---
ToReview: true
author: full
categories:
- ubuntu
description: TLS, or “transport layer security” — and its predecessor SSL — are protocols
  used to wrap normal traffic in a protected, encrypted wrapper. Using this technology,
  servers can safely send information to their clients without their messages being
  intercepted or read by an outside party. In this guide, we will show you how to
  create and use a self-signed SSL certificate with the Apache web server on a CentOS
  8 machine.
image: https://sergio.afanou.com/assets/images/image-midres-46.jpg
lang: en
layout: flexstart-blog-single
ref: selfsigned_ssl_1237
seo:
  links:
  - https://www.wikidata.org/wiki/Q381
silot_terms: server dev and admin
title: How To Create a Self-Signed SSL Certificate for Apache on CentOS 8
toc: true
---

The **TLS** protocol, or “transport layer security” — and its predecessor **SSL** — are protocols used to wrap normal traffic in a protected, encrypted wrapper. Using this technology, servers can safely send information to their clients without their messages being intercepted or read by an outside party.

In this [[2023-11-29-port-forward-pia-a-comprehensive-guide|guide]], we will show you how to create and use a self-signed SSL certificate with the Apache [[2023-11-27-hp-web-services-not-working-troubleshooting-tips|web]] server on a CentOS 8 machine.

**Note:** A self-signed certificate will encrypt communication between your server and its clients. However, because it is not signed by any of the trusted certificate authorities included with web browsers and operating systems, users cannot use the certificate to automatically validate the identity of your server. As a result, your users will see a security error when visiting your site.

Because of this limitation, self-signed certificates are not appropriate for a production environment serving the public. They are typically used for testing, or for securing non-critical services used by a single [[2023-05-04-current-user-what-it-is-and-how-it-can-help-your-business|user]] or a small group of users that can establish trust in the certificate’s validity through alternate communication channels.

For a more production-ready certificate solution, check out [Let’s Encrypt](https://letsencrypt.org/), a free certificate authority. You can learn how to download and configure a Let’s Encrypt certificate in our [How To Secure Apache with Let’s Encrypt on CentOS 8](https://www.digitalocean.com/community/tutorials/how-to-secure-apache-with-let-s-encrypt-on-centos-8) tutorial.  

## Prerequisites


Before starting this tutorial, you’ll need the following:

*   Access to a CentOS 8 server with a non-**root**, sudo-enabled user. Our [Initial Server Setup with CentOS 8](https://www.digitalocean.com/community/tutorials/initial-server-setup-with-centos-8) guide can show you how to create this account.
*   You will also need to have Apache installed. You can install Apache using `dnf`:

```
sudo dnf install httpd
```


Enable Apache and start it using `systemctl`:

```
sudo systemctl enable httpd
sudo systemctl start httpd
```


And finally, if you have a `firewalld` firewall set up, open up the `http` and `https` ports:

```
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --reload
```


Note: For more information on how to create a new Sudo-enabled User on Ubuntu 20.04, check out our comprehensive guide on [[2020-07-05-how-to-create-a-new-sudoenabled-user-on-ubuntu-2004-quickstart.md|ubuntu create new sudo user]].


After these steps are complete, be sure you are logged in as your non-**root** user and continue with the tutorial.

## Step 1 — Installing `mod_ssl`


We first need to install `mod_ssl`, an Apache module that provides support for SSL encryption.

Install `mod_ssl` with the `dnf` command:

```
sudo dnf install mod_ssl
```


Because of a packaging bug, we need to restart Apache once to properly generate the default SSL certificate and key, otherwise we’ll get an error reading `'/etc/pki/tls/certs/localhost.crt' does not exist or is empty`.

```
sudo systemctl restart httpd
```


The `mod_ssl` module is now enabled and ready for use.


## Step 2 — Creating the SSL Certificate


Now that Apache is ready to use encryption, we can move on to generating a new SSL certificate. The certificate will store some basic information about your site, and will be accompanied by a key file that allows the server to securely handle encrypted data.

We can create the SSL key and certificate files with the `openssl` command:

```
sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout /etc/pki/tls/private/apache-selfsigned.key -out /etc/pki/tls/certs/apache-selfsigned.crt
```


After you enter the command, you will be taken to a prompt where you can enter information about your website. Before we go over that, let’s take a look at what is happening in the command we are issuing:

*   `openssl`: This is the command line tool for creating and managing OpenSSL certificates, keys, and other files.
*   `req -x509`: This specifies that we want to use X.509 certificate signing request (CSR) management. X.509 is a public key infrastructure standard that SSL and TLS adhere to for key and certificate management.
*   `-nodes`: This tells OpenSSL to skip the option to secure our certificate with a passphrase. We need Apache to be able to read the file, without user intervention, when the server starts up. A passphrase would prevent this from happening, since we would have to enter it after every restart.
*   `-days 365`: This option sets the length of time that the certificate will be considered valid. We set it for one year here. Many modern browsers will reject any certificates that are valid for longer than one year.
*   `-newkey rsa:2048`: This specifies that we want to generate a new certificate and a new key at the same time. We did not create the key that is required to sign the certificate in a previous step, so we need to create it along with the certificate. The `rsa:2048` portion tells it to make an RSA key that is 2048 bits long.
*   `-keyout`: This line tells OpenSSL where to place the generated private key file that we are creating.
*   `-out`: This tells OpenSSL where to place the certificate that we are creating.

Fill out the prompts appropriately. The most important line is the one that requests the `Common Name`. You need to enter either the hostname you’ll use to access the server by, or the public IP of the server. It’s important that this field matches whatever you’ll put into your browser’s address bar to access the site, as a mismatch will cause more security errors.

The full list of prompts will look something like this:

```
Country Name (2 letter code) [XX]:US
State or Province Name (full name) []:Example
Locality Name (eg, city) [Default City]:Example 
Organization Name (eg, company) [Default Company Ltd]:Example Inc
Organizational Unit Name (eg, section) []:Example Dept
Common Name (eg, your name or your server's hostname) []:your_domain_or_ip
Email Address []:webmaster@example.com
```

    

Both of the files you created will be placed in the appropriate subdirectories of the `/etc/pki/tls` directory. This is a standard directory provided by CentOS for this purpose.

Next we will update our Apache configuration to use the new certificate and key.


## Step 3 — Configuring Apache to Use SSL

Now that we have our self-signed certificate and key available, we need to update our Apache configuration to use them. On CentOS, you can place new Apache configuration files (they must end in `.conf`) into `/etc/httpd/conf.d` and they will be loaded the next time the Apache process is reloaded or restarted.

For this tutorial we will create a new minimal configuration file. If you already have an Apache `<Virtualhost>` set up and just need to add SSL to it, you will likely need to copy over the configuration lines that start with `SSL`, and switch the `VirtualHost` port from `80` to `443`. We will take care of port `80` in the next step.

Open a new file in the `/etc/httpd/conf.d` directory:

```
sudo vi /etc/httpd/conf.d/your_domain_or_ip.conf
```

    

Paste in the following minimal VirtualHost configuration:

/etc/httpd/conf.d/your\_domain\_or\_ip.conf

```
<VirtualHost *:443>
        ServerName your_domain_or_ip
        DocumentRoot /var/www/ssl-test
        SSLEngine on
        SSLCertificateFile /etc/pki/tls/certs/apache-selfsigned.crt
        SSLCertificateKeyFile /etc/pki/tls/private/apache-selfsigned.key
</VirtualHost>
```
    

Be sure to update the `ServerName` line to however you intend to address your server. This can be a hostname, full domain name, or an IP address. Make sure whatever you choose matches the `Common Name` you chose when making the certificate.

The remaining lines specify a `DocumentRoot` directory to serve files from, and the SSL options needed to point Apache to our newly-created certificate and key.

Now let’s create our `DocumentRoot` and put an HTML file in it just for testing purposes:

```
sudo mkdir /var/www/ssl-test
```


Note: If you're interested in learning more about What is the LAMP stack, our blog post on [[2022-09-14-what-is-the-lamp-stack.md|lamp stack full form]] offers practical tips and advice. Also, our blog post on [[2020-04-04-how-to-install-wordpress-with-lamp-on-ubuntu-1604.md|install lamp ubuntu 16.04]] explains why How To Install WordPress with LAMP on Ubuntu 16.04.




Open a new `index.html` file with your text editor:

```
sudo vi /var/www/ssl-test/index.html
```

    

Paste the following into the blank file:

/var/www/ssl-test/index.html

```
<h1>it worked!</h1>
```
    

This is not a full HTML file, of course, but browsers are lenient and it will be enough to verify our configuration.

Save and close the file, then check your Apache configuration for syntax errors by typing:

```
sudo apachectl configtest
```
    

You may see some warnings, but as long as the output ends with `Syntax OK`, you are safe to continue. If this is not part of your output, check the syntax of your files and try again.

When all is well, reload Apache to pick up the configuration changes:

```
sudo systemctl reload httpd
```

    

Now load your site in a browser, being sure to use `https://` at the beginning.

You should see an error. This is normal for a self-signed certificate! The browser is warning you that it can’t verify the identity of the server, because our certificate is not signed by any of the browser’s known certificate authorities. For testing purposes and personal use this can be fine. You should be able to click through to **advanced** or **more information** and choose to proceed.

After you do so, your browser will load the `it worked!` message.

**Note:** if your browser doesn’t connect at all to the server, make sure your connection isn’t being blocked by a firewall. If you are using `firewalld`, the following commands will open ports `80` and `443`:

```
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --reload 
```


Next we will add another `VirtualHost` section to our configuration to serve plain HTTP requests and redirect them to HTTPS.

## Step 4 — Redirecting HTTP to HTTPS

Currently, our configuration will only respond to HTTPS requests on port `443`. It is good practice to also respond on port `80`, even if you want to force all traffic to be encrypted. Let’s set up a `VirtualHost` to respond to these unencrypted requests and redirect them to HTTPS.

Open the same Apache configuration file we started in previous steps:

```
sudo vi /etc/httpd/conf.d/your_domain_or_ip.conf
```
    

At the bottom, create another `VirtualHost` block to match requests on port `80`. Use the `ServerName` directive to again match your domain name or IP address. Then, use `Redirect` to match any requests and send them to the SSL `VirtualHost`. Make sure to include the trailing slash:

/etc/httpd/conf.d/your\_domain\_or\_ip.conf

```
<VirtualHost *:80>
        ServerName your_domain_or_ip
        Redirect / https://your_domain_or_ip/
</VirtualHost>
```

    

Save and close this file when you are finished, then test your configuration syntax again, and reload Apache:

```
sudo apachectl configtest
sudo systemctl reload httpd
```
    

You can test the new redirect functionality by visiting your site with plain `http://` in front of the address. You should be redirected to `https://` automatically.

# Conclusion

You have now configured Apache to serve encrypted requests using a self-signed SSL certificate, and to redirect unecrypted HTTP requests to HTTPS.

If you are planning on using SSL for a public website, you should look into purchasing a domain name and using a widely supported certificate authority such as [Let’s Encrypt](https://letsencrypt.org/).

For more information on using Let’s Encrypt with Apache, please read our [How To Secure Apache with Let’s Encrypt on CentOS 8](https://www.digitalocean.com/community/tutorials/how-to-secure-apache-with-let-s-encrypt-on-centos-8) tutorial.