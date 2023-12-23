---
date: 2023-05-10
description: Laravel - Eloquent "Has", "With", "WhereHas" - What do they mean?   Are
  you looking for a powerful and efficient way to work with your database in Laravel?
  Look no further than Eloquent, Laravel's built-in ORM (Object-Relational Mapping)
  tool. One of the most useful features of Eloquent is its ability to work with related
  models through the use of "Has", "With", and "WhereHas" methods. In this article,
  we'll explore what these methods do and how you can use them to make your database
  queries more efficient and effective.   Before we dive into the specifics of "Has",
  "With", and "WhereHas", let's first take a moment to understand what Eloquent is
  and how it works. Eloquent is Laravel's implementation of the ActiveRecord pattern,
  which allows you to work with your database in an object-oriented manner. This means
  that instead of writing raw SQL queries, you can work with your database tables
  as if they were objects, making it
image: null
image_search_query: screen web application
post_date: 2023-11-12
pretified: true
ref: laravel-eloquent-has-with-wherehas-what-do-they-mean
silot_terms: laravel devops
tags: []
title: Laravel - Eloquent "Has", "With", "WhereHas" - What do they mean?
---

[[2023-07-31-laravel-eloquent-groupby-and-also-return-count-of-each-group|Laravel]] - [[2023-11-15-how-to-create-multiple-where-clause-query-using-laravel-eloquent|Eloquent]] "Has", "With", "WhereHas" - What do they mean?

# Laravel - Eloquent "Has", "With", "WhereHas" - What do they mean?

Are you looking for a powerful and efficient way to work with your database in [[2022-05-26-7-easy-steps-to-deploy-a-laravel-application-in-a-docker-container|Laravel]]? Look no further than [[2023-11-26-laravel-eloquent-artisan-the-ultimate-guide-to-building-stunning-web-applications|Eloquent]], [[2023-12-03-laravel-5-remove-public-from-url|Laravel]]'s built-in ORM (Object-Relational Mapping) tool. One of the most useful features of Eloquent is its ability to work with related models through the use of "Has", "With", and "WhereHas" methods. In this article, we'll explore what these methods do and how you can use them to make your database queries more efficient and effective.

## What is Eloquent?

Before we dive into the specifics of "Has", "With", and "WhereHas", let's first take a moment to understand what Eloquent is and how it works. Eloquent is [[2023-10-27-how-to-create-custom-helper-functions-in-laravel|Laravel]]'s implementation of the ActiveRecord pattern, which allows you to work with your database in an object-oriented manner. This means that instead of writing [[2023-08-29-how-to-get-the-query-builder-to-output-its-raw-sql-query-as-a-string|raw SQL]] queries, you can work with your database tables as if they were objects, making it easier to write and maintain code.

## "Has" Method

The "Has" method is used to retrieve all records from a model that have at least one related record in another model. For example, let's say we have a "User" model and a "Post" model, where each post belongs to a user. We can use the "Has" method to retrieve all users who have at least one post:



```php
$users = User::has('posts')->get();
```

This will return a collection of all users who have at least one post. The "Has" method is incredibly useful when working with related models, as it allows you to filter your results based on the existence of related records.

## "With" Method

The "With" method is used to eager load related models when retrieving records. By default, when you retrieve a model with related models, Eloquent will perform a separate query for each related model. This can quickly become inefficient when working with large datasets. The "With" method solves this problem by allowing you to specify which related models to load in a single query.

Continuing with our "User" and "Post" example, let's say we want to retrieve all users and their posts. We can use the "With" method to eager load the posts:



```php
$users = User::with('posts')->get();
```

This will retrieve all users and their posts in a single query, making our code much more efficient. The "With" method is particularly useful when working with large datasets or when you need to perform operations on related models.

## "WhereHas" Method

The "WhereHas" method is used to retrieve all records from a model that have at least one related record that meets certain conditions. For example, let's say we want to retrieve all users who have posted at least one post with the title "Hello World". We can use the "WhereHas" method to achieve this:



```php

$users = User::whereHas('posts', function ($query) {     $query->where('title', 'like', '%Hello World%'); })->get();

```

This will retrieve all users who have posted at least one post with the title "Hello World". The "WhereHas" method is incredibly powerful when working with related models, as it allows you to filter your results based on conditions in the related model.

## Conclusion

In conclusion, the "Has", "With", and "WhereHas" methods are powerful tools that can greatly simplify your database queries when working with related models in [[2023-11-13-apache-and-laravel-5-remove-public-from-url|Laravel]]. The "Has" method allows you to retrieve records based on the existence of related records, while the "With" method allows you to eager load related