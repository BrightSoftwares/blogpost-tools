---
author: full
categories:
- laravel
date: 2023-08-21
description: 'How to to send mail using gmail in Laravel?   Sending emails is an essential
  feature in modern web applications. Laravel, being one of the most popular PHP frameworks,
  has a built-in email system that makes it easy to send emails. In this article,
  we will explore how to send mail using Gmail in Laravel. We will cover everything
  from setting up your Gmail account to sending your first email.   Email is a powerful
  tool for communication, and Laravel makes it easy to send emails from your web application.
  In this article, we will show you how to use Gmail as your email provider for sending
  emails from your Laravel application.   Before we dive into the steps to send email
  using Gmail in Laravel, you need to have the following:  -   A Gmail account -   A
  Laravel application set up on your local machine or server   If'
image: https://res.cloudinary.com/brightsoftwares/image/upload/t_BSBlogImage/v1/brightsoftwares.com.blog/npxXWgQ33ZQ
image_search_query: email web application
lang: en
layout: flexstart-blog-single
links:
- https://m.wikidata.org/wiki/Q15206305
post_date: 2023-08-21
pretified: true
ref: how-to-send-mail-using-gmail-in-laravel
silot_terms: laravel devops
tags: []
title: How to Send Mail Using Gmail in Laravel?
---

How to to send mail using gmail in Laravel?

# How to Send Mail Using Gmail in Laravel?

Sending emails is an essential feature in modern web applications. Laravel, being one of the most popular PHP frameworks, has a built-in email system that makes it easy to send emails. In this article, we will explore how to send mail using Gmail in Laravel. We will cover everything from setting up your Gmail account to sending your first email.

## Introduction

Email is a powerful tool for communication, and Laravel makes it easy to send emails from your web application. In this article, we will show you how to use Gmail as your email provider for sending emails from your Laravel application.

## Prerequisites

Before we dive into the steps to send email using Gmail in Laravel, you need to have the following:

-   A Gmail account
-   A Laravel application set up on your local machine or server

## Step 1: Create a Gmail Account

If you don't already have a Gmail account, you need to create one. Go to [https://mail.google.com](https://mail.google.com/) and sign up for a new account. Once you have created your account, sign in to your account.

## Step 2: Enable Less Secure Apps

By default, Gmail does not allow less secure apps to access your account. To enable access, you need to turn on the "Less secure app access" setting in your Google account. Follow the below steps to enable it:

-   Go to your Google Account settings ([https://myaccount.google.com/security](https://myaccount.google.com/security))
-   Click on the "Less secure app access" option
-   Toggle the button to turn it on

## Step 3: Install and Configure SMTP

Laravel uses SMTP to send email, and you need to configure it to use your Gmail account. Follow the below steps to install and configure SMTP in your Laravel application:

-   Install the "swiftmailer/swiftmailer" package using composer by running the below command:



`composer require swiftmailer/swiftmailer`

-   Open the ".env" file in your Laravel application root directory and add the following SMTP settings:



`MAIL_DRIVER=smtp MAIL_HOST=smtp.gmail.com MAIL_PORT=587 MAIL_USERNAME=your-gmail-email-address MAIL_PASSWORD=your-gmail-password MAIL_ENCRYPTION=tls`

-   Save the file and run the below command to clear the cache:



`php artisan config:cache`

## Step 4: Create a Route and Controller

Create a new route and controller method to send the email from your Laravel application. Here is an example code snippet for the route and controller method:



`Route::get('/send-email', 'MailController@sendEmail');  public function sendEmail() {     $data = array('name'=>"John Doe");       Mail::send('emails.mail', $data, function($message) {         $message->to('recipient@gmail.com', 'Recipient Name')                 ->subject('Welcome to my Laravel Application');         $message->from('your-gmail-email-address','Your Name');     });       return "Email sent successfully!"; }`

In this code, we are sending an email to "[recipient@gmail.com](mailto:recipient@gmail.com)" with the subject "Welcome to my Laravel Application". We are using a view "emails.mail" to render the email body, and passing the data variable to the view.

## Step 5: Create an Email View

Create an email view to render the email body. Here is an example email view:



`<!DOCTYPE html> <html> <head>     <title>Welcome to my Laravel Application</title> </head> <body>     <h2>Hello {{ $name }},</h2>     <p>Thanks for signing up for my Laravel application. We are excited to have you on board.</p>     <p>Regards,</`

![](data:image/svg+xml,%3csvg%20xmlns=%27http://www.w3.org/2000/svg%27%20version=%271.1%27%20width=%2730%27%20height=%2730%27/%3e)![Full Bright](https://chat.openai.com/_next/image?url=https%3A%2F%2Flh3.googleusercontent.com%2Fa%2FAGNmyxZW1bm17GGxeKnZvNIeq9WloDUSy05B9sX8lC4X6Q%3Ds96-c&w=64&q=75)

Continue writing please

## Step 6: Test Your Email

After setting up your Gmail account and Laravel application, you can now test your email sending feature. Access the URL of the route you created in Step 4 and you should receive an email in your recipient email address.

Sending emails with Laravel and Gmail is simple and effective. With these steps, you can now start sending emails to your users and customers with ease. It is an emotional and exciting moment to see your emails being delivered successfully and connecting with your audience.

## Conclusion

In this article, we explored how to send mail using Gmail in Laravel. We showed you how to set up your Gmail account, enable less secure apps, install and configure SMTP in your Laravel application, create a route and controller, and create an email view. Sending emails is an essential feature in modern web applications, and Laravel makes it easy to implement. With these steps, you can start sending emails to your users and customers and connect with them emotionally.

## FAQs

1.  What should I do if my Gmail account is not sending emails from my Laravel application? You may need to check the SMTP settings in your Laravel application's ".env" file and ensure that the correct settings are configured.
    
2.  Can I use a different email provider other than Gmail to send emails in Laravel? Yes, you can use other email providers such as Yahoo, Outlook, or your own custom email server.
    
3.  How can I ensure that my email does not end up in the recipient's spam folder? Ensure that you follow the best practices for email deliverability such as having a valid sender email address, providing valuable content, and avoiding spam trigger words.
    
4.  Is it possible to send attachments with the email in Laravel? Yes, you can attach files to your email using the "attach" method in the "Mail" facade.
    
5.  How can I customize the email template in Laravel? You can customize the email template by creating a new view file and passing the necessary data to the view when sending the email.