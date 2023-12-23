---
author: full
categories:
- laravel
date: 2023-12-03
description: Laravel 5 is a powerful PHP framework that is widely used for web development.
  It comes with many advanced features that make it a preferred choice for developers.
  However, one issue that many developers face is the "public" folder in the URL.
  In this article, we will discuss how to remove "public" from the URL in Laravel
  5, and make your website more user-friendly.   When you install Laravel 5, it comes
  with a "public" folder that contains all the assets, such as images, CSS, and JavaScript
  files. This folder is the root directory of your website, which means that you need
  to include it in the URL every time you want to access a page on your website. For
  example, if your website's domain name is "example.com", and you want to access
  the home page, you need to type "example.com/public" in the URL. This can be confusing
  for users,
image: https://res.cloudinary.com/brightsoftwares/image/upload/t_BSBlogImage/v1/brightsoftwares.com.blog/OqtafYT5kTw
image_search_query: screen web application
lang: en
layout: flexstart-blog-single
links:
- https://m.wikidata.org/wiki/Q15206305
post_date: 2023-12-03
pretified: true
ref: laravel-5-remove-public-from-url
silot_terms: laravel devops
tags: []
title: Laravel 5 Remove Public from URL
---

[[2023-07-31-laravel-eloquent-groupby-and-also-return-count-of-each-group|Laravel]] 5 is a powerful PHP framework that is widely used for [[2023-11-26-laravel-eloquent-artisan-the-ultimate-guide-to-building-stunning-web-applications|web]] development. It comes with many advanced features that make it a preferred choice for developers. However, one issue that many developers face is the "[[2023-11-13-apache-and-laravel-5-remove-public-from-url|public]]" folder in the URL. In this article, we will discuss how to remove "public" from the URL in [[2023-05-10-laravel-eloquent-has-with-wherehas-what-do-they-mean|Laravel]] 5, and make your website more user-friendly.

## The Issue with the Public Folder

When you install [[2023-11-15-how-to-create-multiple-where-clause-query-using-laravel-eloquent|Laravel]] 5, it comes with a "public" folder that contains all the assets, such as images, CSS, and JavaScript files. This folder is the root directory of your website, which means that you need to include it in the URL every time you want to access a page on your website. For example, if your website's domain name is "example.com", and you want to access the home page, you need to type "example.com/public" in the URL. This can be confusing for users, and also affects the SEO of your website.

### Why You Need to Remove "Public" from URL

Having "public" in the URL can negatively impact the user experience of your website. It can make the URL look longer and less professional, which can discourage users from visiting your website. Moreover, it can also affect the SEO of your website, as search engines prefer short and clean URLs. By removing "public" from the URL, you can improve the user experience and SEO of your website.

### How to Remove "Public" from URL

To remove "public" from the URL in [[2022-05-26-7-easy-steps-to-deploy-a-laravel-application-in-a-docker-container|Laravel]] 5, follow the steps below:

#### Step 1: Rename the Server.php File

The first step is to rename the "server.php" file in the root directory of your [[2023-10-27-how-to-create-custom-helper-functions-in-laravel|Laravel]] 5 installation. Rename it to "index.php".

#### Step 2: Move the .htaccess File

The next step is to move the ".htaccess" file from the "public" folder to the root directory of your Laravel 5 installation. If you don't have the ".htaccess" file in the "public" folder, create a new one in the root directory, and paste the following code:



`<IfModule mod_rewrite.c>     RewriteEngine On     RewriteRule ^(.*)$ public/$1 [L] </IfModule>`


#### Step 3: Modify the index.php File

The final step is to modify the "index.php" file in the root directory of your Laravel 5 installation. Open the file in a text editor, and find the following line:


`require __DIR__.'/../bootstrap/autoload.php';`

Replace it with the following line:



`require __DIR__.'/bootstrap/autoload.php';`


Next, find the following line:



`$app = require_once __DIR__.'/../bootstrap/app.php';`

Replace it with the following line:



`$app = require_once __DIR__.'/bootstrap/app.php';`

Save the file, and your website is now accessible without "public" in the URL.

## Conclusion

In conclusion, having "public" in the URL can negatively impact the user experience and SEO of your Laravel 5 website. However, by following the steps mentioned above, you can easily remove "public" from the URL, and make your website more user-friendly. So, go ahead and implement these steps, and give your users a seamless browsing experience.

## FAQs

1.  Why is "public" in the URL in Laravel 5?

-   Laravel 5 has a "public" folder that contains all the assets, such as images, CSS, and JavaScript files. This folder is the root directory of your website, which means that you need to include it in the URL every time you want to access

2.  How does having "public" in the URL affect the user experience?

-   Having "public" in the URL can make the URL look longer and less professional, which can discourage users from visiting your website.

3.  Can removing "public" from the URL affect the functionality of the website?

-   No, removing "public" from the URL will not affect the functionality of the website. The website will work the same way as it did before.

4.  Does removing "public" from the URL affect the SEO of the website?

-   Yes, removing "public" from the URL can improve the SEO of the website, as search engines prefer short and clean URLs.

5.  Are there any other benefits of removing "public" from the URL?

-   Yes, removing "public" from the URL can improve the overall user experience of your website, and make it look more professional and trustworthy.

As a Laravel 5 developer, you know that the framework is powerful, efficient, and user-friendly. However, one issue that many developers face is the "public" folder in the URL. It can make the URL look longer, less professional, and negatively impact the SEO of your website. But, by following the steps mentioned above, you can easily remove "public" from the URL, and give your users a seamless browsing experience.

So, don't wait, take action today, and give your Laravel 5 website the professional look it deserves. Remove "public" from the URL, and take your website to the next level.