---
author: full
categories:
- laravel
date: 2023-06-23
description: Get Specific Columns Using “With()” Function in Laravel Eloquent   Are
  you tired of fetching unnecessary data from your Laravel Eloquent queries? Do you
  want to optimize your queries and reduce the load on your database? If so, then
  you're in luck! Laravel's "with()" function can help you fetch only the specific
  columns you need, and in this article, we'll explore how to use it effectively.   Before
  diving into how to use "with()" to fetch specific columns, let's first understand
  what the function does. The "with()" function is a powerful tool in Laravel's Eloquent
  ORM that allows you to eager load related models and their respective columns. By
  default, Eloquent fetches all columns from the related table, which can sometimes
  result in unnecessary data being loaded.   To fetch specific columns using "with()",
  you simply need to pass an array of columns as the second argument to the function.
  For example, let's say we have
image: null
image_search_query: screen web application
lang: en
layout: flexstart-blog-single
links:
- https://m.wikidata.org/wiki/Q15206305
post_date: 2023-06-23
pretified: true
ref: get-specific-columns-using-with-function-in-laravel-eloquent
silot_terms: laravel devops
tags: []
title: Get Specific Columns Using “With()” Function in Laravel Eloquent
---

Get Specific Columns Using “With()” Function in Laravel Eloquent

# Get Specific Columns Using “With()” Function in Laravel Eloquent

Are you tired of fetching unnecessary data from your Laravel Eloquent queries? Do you want to optimize your queries and reduce the load on your database? If so, then you're in luck! Laravel's "with()" function can help you fetch only the specific columns you need, and in this article, we'll explore how to use it effectively.

## Introduction

Before diving into how to use "with()" to fetch specific columns, let's first understand what the function does. The "with()" function is a powerful tool in Laravel's Eloquent ORM that allows you to eager load related models and their respective columns. By default, Eloquent fetches all columns from the related table, which can sometimes result in unnecessary data being loaded.

## Using “with()” Function to Fetch Specific Columns

To fetch specific columns using "with()", you simply need to pass an array of columns as the second argument to the function. For example, let's say we have a "User" model with a "hasMany" relationship with a "Post" model. We want to fetch only the "title" and "created_at" columns from the "posts" table. Here's how we can do it:



`$users = User::with(['posts' => function ($query) {     $query->select('title', 'created_at'); }])->get();`

In the above example, we're passing an array to the "with()" function, with the key being the name of the relationship ("posts") and the value being an anonymous function that defines the columns we want to fetch from the "posts" table.

## Fetching Columns from Multiple Relationships

Sometimes, you may need to fetch columns from multiple related models. In this case, you can simply add additional keys to the array passed to the "with()" function. Let's say we have a "Comment" model with a "belongsTo" relationship with both the "User" and "Post" models. We want to fetch the "name" column from the "users" table and the "title" column from the "posts" table. Here's how we can do it:



`$comments = Comment::with(['user' => function ($query) {     $query->select('name'); }, 'post' => function ($query) {     $query->select('title'); }])->get();`

In the above example, we're passing an array with two keys ("user" and "post"), each with its own anonymous function that defines the columns we want to fetch from the respective tables.

## Conclusion

By using Laravel's "with()" function to fetch only the specific columns you need, you can optimize your queries and reduce the load on your database. With the ability to fetch columns from multiple relationships, "with()" provides a flexible and powerful tool for managing your data. So next time you're working with Eloquent models in Laravel, remember to use "with()" to fetch only the data you need!

## FAQs

Q1. Can I use "with()" to fetch columns from a pivot table? A1. Yes, you can use "with()" to fetch columns from a pivot table by defining the relationship between the models in your Eloquent model classes.

Q2. How can I fetch all columns from a related table using "with()"? A2. By default, Eloquent fetches all columns from a related table when using "with()". If you want to fetch all columns, you don't need to pass a second argument to the function.

Q3. Can I use "with()" to fetch columns from a related model that has a "hasOne" relationship? A3. Yes, you can

![](data:image/svg+xml,%3csvg%20xmlns=%27http://www.w3.org/2000/svg%27%20version=%271.1%27%20width=%2730%27%20height=%2730%27/%3e)![Full Bright](https://chat.openai.com/_next/image?url=https%3A%2F%2Flh3.googleusercontent.com%2Fa%2FAGNmyxZW1bm17GGxeKnZvNIeq9WloDUSy05B9sX8lC4X6Q%3Ds96-c&w=64&q=75)

Continue writing please

A3. Yes, you can use "with()" to fetch columns from a related model that has a "hasOne" relationship. Just pass the name of the relationship as the key in the array passed to the function, and define the columns you want to fetch in the anonymous function.

Q4. Can using "with()" impact the performance of my application? A4. Using "with()" can actually improve the performance of your application by reducing the number of queries that need to be executed. By fetching only the specific columns you need, you can also reduce the amount of data that needs to be transferred between your application and the database.

Q5. Is it possible to chain multiple "with()" functions together? A5. Yes, you can chain multiple "with()" functions together to fetch data from multiple related models. Just make sure to define the columns you want to fetch in each anonymous function.

In conclusion, using Laravel's "with()" function can make a huge difference in the performance of your application. By fetching only the specific columns you need, you can optimize your queries and reduce the load on your database. So go ahead and try it out, and see the difference it makes in your application's performance. Happy coding!