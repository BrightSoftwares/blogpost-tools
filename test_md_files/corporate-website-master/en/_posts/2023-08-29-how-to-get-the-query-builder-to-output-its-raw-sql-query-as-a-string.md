---
author: full
categories:
- laravel
date: 2023-08-29
description: Have you ever found yourself in a situation where you need to know the
  exact SQL query being executed by Laravel's query builder? Maybe you're trying to
  optimize a slow-running query or you just want to see what's going on under the
  hood. In this article, I'll show you how to get the query builder to output its
  raw SQL query as a string.   Before we dive into how to get the raw SQL query, let's
  take a moment to understand what the query builder is and how it works. Laravel's
  query builder provides a convenient, fluent interface for building and executing
  database queries. It allows you to construct complex queries using a set of intuitive
  methods and supports a variety of database systems.  The query builder is built
  on top of PDO, which is a PHP extension
image: https://res.cloudinary.com/brightsoftwares/image/upload/t_BSBlogImage/v1/brightsoftwares.com.blog/EhTcC9sYXsw
image_search_query: screen web application
lang: en
layout: flexstart-blog-single
links:
- https://m.wikidata.org/wiki/Q15206305
post_date: 2023-08-29
pretified: true
ref: how-to-get-the-query-builder-to-output-its-raw-sql-query-as-a-string
silot_terms: laravel devops
tags: []
title: How to Get the Query Builder to Output Its Raw SQL Query as a String
---

Have you ever found yourself in a situation where you need to know the exact SQL [[2023-11-15-how-to-create-multiple-where-clause-query-using-laravel-eloquent|query]] being executed by [[2023-07-31-laravel-eloquent-groupby-and-also-return-count-of-each-group|Laravel]]'s query builder? Maybe you're trying to optimize a slow-running query or you just want to see what's going on under the hood. In this article, I'll show you how to get the query builder to output its raw SQL query as a string.

## Understanding Laravel's Query Builder

Before we dive into how to get the raw SQL query, let's take a moment to understand what the query builder is and how it works. [[2023-05-10-laravel-eloquent-has-with-wherehas-what-do-they-mean|Laravel]]'s query builder provides a convenient, fluent interface for [[2023-11-26-laravel-eloquent-artisan-the-ultimate-guide-to-building-stunning-web-applications|building]] and executing database queries. It allows you to construct complex queries using a set of intuitive methods and supports a variety of database systems.

The query builder is built on top of PDO, which is a PHP extension for interacting with databases. When you execute a query using the query builder, it generates a prepared statement that is sent to the database server. The prepared statement is compiled by the database server and executed with the parameters you provide. This approach provides several benefits, including improved performance and protection against SQL injection attacks.

## Getting the Raw SQL Query

Now that we have a basic understanding of how the query builder works, let's move on to getting the raw SQL query. There are several ways to do this, but I'll show you the easiest and most straightforward method.

To get the raw SQL query, we'll use the `toSql` method provided by the query builder. This method returns the SQL query that will be executed by the query builder. Here's an example:



`$query = DB::table('users')->where('name', 'John')->toSql();  echo $query;`


In this example, we're selecting all users with the name "John" from the "users" table. We're then calling the `toSql` method on the query builder object and storing the result in the `$query` variable. Finally, we're echoing the raw SQL query to the screen.

## Using the Raw SQL Query

Now that we have the raw SQL query, we can use it in several ways. For example, we can copy and paste it into a database client such as phpMyAdmin or MySQL Workbench to execute the query directly on the database. This can be useful for debugging or testing purposes.

We can also use the raw SQL query in the query builder itself. This can be done by passing the query as a string to the `DB::raw` method. For example:


`$query = DB::table('users')->select(DB::raw('COUNT(*) as user_count'))->toSql();  echo $query;`


In this example, we're using the `DB::raw` method to pass the raw SQL query to the query builder. We're then selecting the count of all users and aliasing the result as "user_count". Finally, we're calling the `toSql` method to get the raw SQL query and echoing it to the screen.

## Conclusion

In conclusion, getting the query builder to output its raw SQL query as a string is a simple and straightforward process. By using the `toSql` method provided by the query builder, we can quickly and easily get the raw SQL query and use it in a variety of ways. Whether we're debugging a slow-running query or testing a new feature, having access to the raw SQL query can be a valuable tool in our development toolbox.

## FAQs

1.  What is the query builder in [[2022-05-26-7-easy-steps-to-deploy-a-laravel-application-in-a-docker-container|Laravel]]? The query builder is a fluent interface provided by [[2023-12-03-laravel-5-remove-public-from-url|Laravel]] for building and executing database queries.
    
2.  How does the query builder work? The query builder generates a prepared statement that is sent to the database server.