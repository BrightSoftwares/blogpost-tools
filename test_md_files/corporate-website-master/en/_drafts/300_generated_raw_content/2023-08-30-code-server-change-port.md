---
author: full
categories:
- code-server
date: 2023-08-30
description: '``` Exported with AIPRM https://www.aiprm.com by Full Bright on 21/03/2023
  23:42:03 ```  ---   **User:** code-server change port   ---  **ChatGPT:** Code-server
  is a powerful tool that allows you to run a fully-fledged code editor in your web
  browser. One of the benefits of code-server is that it can be customized to suit
  your specific needs. One of the ways you can customize your code-server experience
  is by changing the port that it runs on. By default, code-server runs on port 8080,
  but you can change it to any port that you like. In this article, we''ll show you
  how to change the port of code-server. Before we can change the port of code-server,
  we need to stop it. To stop code-server, run the following command in your terminal:
  ```css css Copy code systemctl stop code-server ``` This command will stop code-server
  from running. Next, we need to edit the code-server configuration file. The configuration'
image: https://res.cloudinary.com/brightsoftwares/image/upload/t_BSBlogImage/v1/brightsoftwares.com.blog/B3l0g6HLxr8
image_search_query: code server
lang: en
layout: flexstart-blog-single
links:
- https://www.wikidata.org/wiki/Q19841877
post_date: 2023-08-30
pretified: true
ref: code-server-change-port
silot_terms: code server
tags: []
title: Code server change port
---

```
Exported with AIPRM https://www.aiprm.com by Full Bright on 21/03/2023 23:42:03
```

---


**User:**
code-server change port


---

**ChatGPT:**
Code-server is a powerful tool that allows you to run a fully-fledged code editor in your web browser. One of the benefits of code-server is that it can be customized to suit your specific needs. One of the ways you can customize your code-server experience is by changing the port that it runs on. By default, code-server runs on port 8080, but you can change it to any port that you like. In this article, we'll show you how to change the port of code-server.
Before we can change the port of code-server, we need to stop it. To stop code-server, run the following command in your terminal:
```css
css
Copy code
systemctl stop code-server
```
This command will stop code-server from running.
Next, we need to edit the code-server configuration file. The configuration file is located at <code>~/.config/code-server/config.yaml</code>. You can edit this file using any text editor of your choice. To edit the file using nano, run the following command in your terminal:
```javascript
javascript
Copy code
nano ~/.config/code-server/config.yaml
```
Once you have the file open, look for the following line:
```makefile
makefile
Copy code
bind-addr: localhost:8080
```
This line tells code-server to bind to the localhost address on port 8080. To change the port, simply replace <code>8080</code> with the port of your choice. For example, if you want code-server to run on port 3000, change the line to:
```makefile
makefile
Copy code
bind-addr: localhost:3000
```
Once you have made your changes to the config file, save it and exit the text editor. If you are using nano, you can save the file by pressing <code>Ctrl + X</code>, then <code>Y</code>, and finally <code>Enter</code>.
Now that you have made your changes to the config file, you can start code-server again. To start code-server, run the following command in your terminal:
```css
css
Copy code
systemctl start code-server
```
Code-server will now start and bind to the port that you specified in the config file.
Yes, you can change the port of code-server to any port that is available on your system.
No, you do not need to restart your server after changing the port of code-server. You only need to stop and start code-server.
If you can't access code-server after changing the port, make sure that you are using the correct port number. If you are still unable to access code-server, try stopping and starting it again.
Changing the port of code-server is a simple process that can help you customize your code-server experience. By following the steps outlined in this article, you can change the port of code-server to any port that you like. Whether you're running