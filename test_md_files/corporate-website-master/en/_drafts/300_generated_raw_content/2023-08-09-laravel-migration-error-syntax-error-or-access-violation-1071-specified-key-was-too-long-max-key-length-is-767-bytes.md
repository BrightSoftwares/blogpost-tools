---
author: full
categories:
- laravel
date: 2023-08-09
description: 'Laravel Migration Error: Syntax error or access violation: 1071 Specified
  key was too long; max key length is 767 bytes   Are you trying to migrate your Laravel
  database but getting an error message that says "Syntax error or access violation:
  1071 Specified key was too long; max key length is 767 bytes"? If so, you''re not
  alone. This is a common issue that many Laravel developers face when trying to create
  a new migration.   This error occurs when you try to create a database index with
  a key length that exceeds the maximum allowed length of 767 bytes. This limitation
  is due to the fact that MySQL''s InnoDB storage engine only supports indexes with
  a maximum key length of 767 bytes.   There are a few ways to solve this error, but
  the easiest and most common way is to set the default string length to a lower value
  in your AppServiceProvider.php file. Simply'
image: null
image_search_query: screen web application
lang: en
layout: flexstart-blog-single
links:
- https://www.wikidata.org/wiki/Q15206305
- https://www.wikidata.org/wiki/Q13634357
post_date: 2023-08-09
pretified: true
ref: laravel-migration-error-syntax-error-or-access-violation-1071-specified-key-was-too-long-max-key-length-is-767-bytes
silot_terms: laravel debug
tags: []
title: 'Laravel Migration Error: Syntax error or access violation: 1071 Specified
  key was too long; max key length is 767 bytes'
---

Laravel Migration Error: Syntax error or access violation: 1071 Specified key was too long; max key length is 767 bytes

# Laravel Migration Error: Syntax error or access violation: 1071 Specified key was too long; max key length is 767 bytes

Are you trying to migrate your Laravel database but getting an error message that says "Syntax error or access violation: 1071 Specified key was too long; max key length is 767 bytes"? If so, you're not alone. This is a common issue that many Laravel developers face when trying to create a new migration.

## What causes this error?

This error occurs when you try to create a database index with a key length that exceeds the maximum allowed length of 767 bytes. This limitation is due to the fact that MySQL's InnoDB storage engine only supports indexes with a maximum key length of 767 bytes.

## How to solve this error?

There are a few ways to solve this error, but the easiest and most common way is to set the default string length to a lower value in your AppServiceProvider.php file. Simply add the following line to the boot() method:



`use Illuminate\Support\Facades\Schema;  public function boot() {     Schema::defaultStringLength(191); }`

This will set the default string length to 191, which is the maximum length allowed by MySQL's InnoDB storage engine.

## Other solutions

If setting the default string length doesn't solve the issue, you can try the following solutions:

### Solution 1: Use a different database engine

If you don't want to change the default string length, you can switch to a different database engine that supports longer key lengths. For example, you can switch to the MyISAM storage engine, which supports key lengths up to 1000 bytes.

### Solution 2: Use a shorter index name

Another solution is to use a shorter index name. The longer the index name, the more bytes it will take up. Try using a shorter name for your index and see if that solves the issue.

### Solution 3: Manually specify the index length

You can also manually specify the index length when creating the migration. For example, instead of using the following code:



`$table->string('name')->unique();`

You can use the following code to specify the index length:



`$table->string('name', 191)->unique();`

This will create an index with a length of 191 bytes, which is the maximum length allowed by MySQL's InnoDB storage engine.

## Conclusion

In conclusion, the "Syntax error or access violation: 1071 Specified key was too long; max key length is 767 bytes" error is a common issue that many Laravel developers face when trying to create a new migration. However, by following the solutions outlined above, you can easily solve this error and continue with your Laravel project.

## FAQs

1.  What is the maximum key length allowed by MySQL's InnoDB storage engine?

-   The maximum key length allowed by MySQL's InnoDB storage engine is 767 bytes.

2.  What causes the "Syntax error or access violation: 1071 Specified key was too long" error in Laravel?

-   This error occurs when you try to create a database index with a key length that exceeds the maximum allowed length of 767 bytes.

3.  How can I solve the "Syntax error or access violation: 1071 Specified key was too long" error in Laravel?

-   You can solve this error by setting the default string length to a lower value in your AppServiceProvider.php file, using a different database engine, using a shorter index name, or manually specifying the index length.

4.  Is it safe to change the default string length in Laravel?

-   Yes, it is safe to change the default string length in Laravel as long as you don't exceed the maximum key