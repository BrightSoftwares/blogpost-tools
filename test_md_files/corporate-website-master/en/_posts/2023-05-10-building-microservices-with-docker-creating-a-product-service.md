---
author: full
date: 2023-05-10
description: In the first video, we learned that an image is a template for the environment
  that you want to run, and when you run an image, you get a container. We tried this
  out by running a PHP image. This was okay for our very simple application, but imagine,
  if you have something more complicated, let's work through an example. Traditionally,
  a big website like an online store would be one big application, but a newer trend
  is to split these big applications up into smaller micro-services The website can
  then be quite minimal and it just makes calls to other services to get information
  or to ask them to do some piece of work. We're going to build a really simple ecommerce
  website, but we're going to put the codes that provides the product and the product
  information in its own microservice. The website will then use an api on the product
  service to request the list of
image: https://res.cloudinary.com/brightsoftwares/image/upload/t_BSBlogImage/v1655551310/pexels-elevate-1267338_viff5b.jpg
image_search_query: container transportation
lang: en
layout: flexstart-blog-single
post_date: 2023-05-10
pretified: true
ref: building-microservices-with-docker-creating-a-product-service
seo:
  links:
  - https://m.wikidata.org/wiki/Q15206305
silot_terms: container docker kubernetes
tags: []
title: 'Building Microservices with Docker: Creating a Product Service'
transcribed: true
youtube_video: https://www.youtube.com/watch?v=Qw9zlE3t8Ko&ab_channel=JakeWright
youtube_video_id: Qw9zlE3t8Ko
---

Microservices are becoming increasingly popular in web development due to their flexibility and scalability. In this article, we'll [[2021-12-10-kubernetes-helm-how-to-show-multi-line-properties|show]] you how to create a product [[2022-01-11-how-to-fix-cannot-tcp-connect-from-outside-virtual-machine-network-traffic-not-forwarded-to-service-port|service]] using Python and [[2023-04-04-should-a-docker-container-run-as-root-or-user|Docker]], two essential tools in the microservices architecture.

### Understanding Microservices and Docker

In the first video of our series, we learned that an image is a template for the environment that you want to [[2021-12-29-how-to-run-minikube-in-a-virtual-machine-ubuntu-vm_vt-x-amd-v|run]], and when you [[2023-04-04-should-a-docker-container-run-as-root-or-user|run]] an image, you get a [[2022-06-15-how-do-i-connect-a-docker-bridged-container-to-the-outside-of-the-host|container]]. We used a PHP image to [[2021-12-29-how-to-run-minikube-in-a-virtual-machine-ubuntu-vm_vt-x-amd-v|run]] a simple application, but for a more complicated one, we need to [[2021-12-14-how-to-use-local-docker-images-with-minikube|use]] microservices.

Traditionally, a big website like an online store would be one big application, but a newer trend is to split these big [[2023-12-04-can-you-run-gui-applications-in-a-linux-docker-container|applications]] up into smaller microservices. A microservice architecture allows for more flexibility and scalability, making it [[2023-12-18-understanding-helm-chart-structure-for-easier-deployment|easier]] to add new features and improve performance.

### Creating a Product Service

In this tutorial, we'll build a simple ecommerce website, but we'll put the codes that provide the product and product information in their own microservice. The website will then [[2021-12-14-how-to-use-local-docker-images-with-minikube|use]] an API on the product [[2022-01-11-how-to-fix-cannot-tcp-connect-from-outside-virtual-machine-network-traffic-not-forwarded-to-service-port|service]] to request the list of products to [[2021-12-10-kubernetes-helm-how-to-show-multi-line-properties|show]] to the customer.

To begin, we'll create a new directory for the product service called `product`. We'll write a simple Python script that will serve as the API for the service. We'll call it `api.py`.



```python
from flask import Flask
from flask_restful import Resource, Api

app = Flask(__name__)
api = Api(app)

class Product(Resource):
    def get(self):
        return {
            'products': [
                'ice cream',
                'chocolates',
                'fruit'
            ]
        }

api.add_resource(Product, '/')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=80)
```

We want this to be a simple RESTful API, so we imported Flask and Flask-RESTful and instantiated these objects. We created a `Product` class which extends `Resource` and has a `get` method that returns some JSON data. In this case, we're returning a list of products - ice cream, chocolates, and fruit.

### Running the Product Service in Docker

Now that we've created the product service, we can [[2023-10-29-docker-run-stopped-container|run]] it in [[2022-05-08-can-docker-connect-to-database|Docker]]. First, we'll create a `[[2023-08-30-docker-compose-vs-dockerfile|Dockerfile]]`:



```dockerfile
FROM python:3-onbuild
COPY . /usr/src/app
CMD ["python", "api.py"]
```


The first line specifies the base image that we'll build on top of. We're using the official Python image and the `onbuild` tag, which will automatically install any dependencies listed in the `requirements.txt` file. The next line copies our source code into the image, and the last line specifies the command to run when the [[2022-07-28-how-to-copy-files-from-host-to-docker-container|container]] starts.

To build the [[2022-05-08-can-docker-connect-to-database|Docker]] image, we'll run the following command:


```bash
docker build -t product-service .
```

This will create an image with the tag `product-service`.

To run the [[2022-07-28-how-to-copy-files-from-host-to-docker-container|container]], we'll [[2023-10-25-using-helm-practical-use-cases|use]] the following command:


```bash
docker run -d -p 80:80 product-service
```

This will start a [[2022-06-15-how-do-i-connect-a-docker-bridged-container-to-the-outside-of-the-host|container]] and map [[2021-12-26-how-to-expose-a-port-on-minikube|port]] 80 in the [[2023-05-14-understanding-kubernetes-the-container-orchestrator|container]] to [[2021-12-26-how-to-expose-a-port-on-minikube|port]] 80 on our [[2023-05-12-running-mysql-server-in-docker-container-and-connecting-to-it-from-host-machine|machine]].

### Using Docker Compose

As we add more services, building and running each one separately can become tedious. This is where [[2023-12-22-convert-docker-compose-to-kubernetes|Docker Compose]] comes in. [[2023-11-17-what-is-docker-compose|Docker]] Compose lets us define all of our services in a configuration file, and with one command, it'll spin up all the containers that we need.

We'll create a `[[2023-05-08-restart-docker-daemon-a-comprehensive-guide|docker]]-compose.yml` file in the parent directory:



```yaml
version: '3'

services:
  product:
    build:
```


ChatGPT

### Defining the Website Service

Now, let's define the `website` service in our `[[2023-08-25-docker-exec-bash-example|docker]]-compose.yml` file.



```yaml
services:
  product:
    build: ./product
    ports:
      - "5001:80"

  website:
    build: ./website
    ports:
      - "5000:80"
    depends_on:
      - product
```


Similar to the `product` service, we first specify the build context for the `website` service. In this case, it's the `./website` directory.

Next, we specify the ports to expose. We want to expose port `80` inside the [[2023-11-22-monit-docker-container-a-comprehensive-guide|container]], so we map it to port `5000` on the host machine.

Finally, we specify that the `website` service depends on the `product` service. This means that `docker-compose` will start the `product` service before starting the `website` service.

### Writing the Website Code

Let's create a new directory called `website` and create a file called `app.py` inside it. Here's the code for the `app.py` file:



```python
from flask import Flask, jsonify
import requests

app = Flask(__name__)

@app.route('/')
def index():
    products = requests.get('http://product:80/products').json()
    return jsonify(products)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
```


This code is very similar to the `product` service code. We create a Flask app and define a route for the root URL. When a user visits the root URL, the `index()` function is called.

Inside the `index()` function, we make a request to the `product` service using the `requests` library. We then return the JSON response from the `product` service.

### Building and Running the Website Service

Now that we have written the code for the `website` service, let's build and run the service.

First, let's create a `Dockerfile` for the `website` service. Here's what the `Dockerfile` should look like:


```dockerfile
FROM python:3

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD [ "python", "app.py" ]
```


This `Dockerfile` is very similar to the `product` service `Dockerfile`. We start with the official Python 3 image, set the working directory to `/app`, and copy the `requirements.txt` file into the [[2023-05-15-understanding-container-networking|container]]. We then install the Python dependencies using `pip`.

Next, we copy the entire `website` directory into the container and set the command to run `python app.py`.

To build the `website` service, run the following command in the root directory of the project:


```bash
docker-compose build website
```

This will build the `website` service and create a Docker image.

To run the `website` service, run the following command:



```bash
docker-compose up
```

This will start both the `product` and `website` services. You should now be able to visit [http://localhost:5000/](http://localhost:5000/) in your web browser and see a JSON response with the list of products.

## Conclusion

In this tutorial, we learned how to build a simple e-commerce website using microservices and Docker. We split our application into two services: a `product` service and a `website` service. We then used `docker-compose` to define and run both services.

Microservices can help make your applications more scalable and easier to maintain. By splitting your application into smaller services, you can make changes to one service