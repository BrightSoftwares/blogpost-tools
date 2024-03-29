---
categories:
- kubernetes
date: 2023-05-17
description: in this video we're going to talk about a git ops tool that is gaining
  popularity in the devops world which is called argo cd if you don't know what git
  ops is you can check out my other video about git ups after which this video will
  make much more sense to you first i'm going to explain what argo city is and what
  are the common use cases or why we need argo cd we will then see how argo city actually
  works and how it does its job and in the final part we will do a hands-on demo project
  where we deploy argo cd and set up a fully automated cd pipeline for kubernetes
  configuration changes to get some practical experience with argo cd right away     argo
  city is as the name already tells you a continuous delivery tool and to understand
  argo cd as a cd tool or continuous
image: null
lang: en
post_date: 2023-05-17
pretified: true
tags: []
title: Introduction to ArgoCD for DevOps
transcribed: true
youtube_video: https://www.youtube.com/watch?v=MeU5_k9ssrs&ab_channel=TechWorldwithNana
youtube_video_id: MeU5_k9ssrs
---

#  Intro and Overview

in this video we're going to talk about
a git ops tool that is gaining
popularity in the devops world which is
called argo cd if you don't know what
git ops is you can check out my other
video about git ups after which this
video will make much more sense to you
first i'm going to explain what argo
city is and what are the common use
cases or why we need argo cd we will
then see how argo city actually works
and how it does its job and in the final
part we will do a hands-on demo project
where we deploy argo cd and set up a
fully automated cd pipeline for
kubernetes configuration changes to get
some practical experience with argo cd
right away



#  What is ArgoCD

argo city is as the name already tells
you a continuous delivery tool and to
understand argo cd as a cd tool or
continuous delivery tool let's first
understand how continuous delivery is
implemented in most projects using
common tools like jenkins or gitlab cicd
and then see how argo city compares to
them and in that context we will answer
the questions such as is argo city just
another cd tool or what is so special
about it and if it's so special does it
actually replace any of these other
established tools like jenkins or
gitlabci icd so let's say we have a



#   CD workflow without ArgoCD

microservices application and we're
running it in a kubernetes cluster when
things change in the application code
like new feature or a bug fix gets added
the ci pipeline on jenkins for example
will be automatically triggered and will
test the changes build a new docker
image and push it to a docker repository
now how does this new image get deployed
to kubernetes
we update applications deployment yaml
file for kubernetes with the new image
tag and this yaml file then should be
applied in kubernetes in most projects
these steps are the continuation of the
ci pipeline so after the image gets
pushed to the repository
jenkins
will update the deployment yaml file for
the application and using cubectl tool
for example will apply the updated
deployment file to kubernetes and this
is how many projects are set up however
there are a couple of challenges with
this approach first of all you need to
install and set up tools like cubectl or
helm etc to access kubernetes cluster
and execute changes
on those
build automation tools right so you
would need to install and configure them
on jenkins
you also need to configure access to
kubernetes for these tools because
kubectl is just the kubernetes client
and in order for it to connect to
kubernetes it needs to provide some
credentials so you will need to
configure credentials for kubernetes
cluster in jenkins if you're using eks
cluster which is a kubernetes managed
cluster on aws for example in addition
you would also need access to aws so
you'd have to add aws credentials in
addition to the kubernetes credentials
also to jenkins and this is not only a
configuration effort but also a security
challenge because you need to give your
cluster credentials to external services
and tools especially we have 50 projects
that deploy applications to the cluster
each project application will need its
own kubernetes credentials so that it
can only access
that specific application resources in
the cluster same way if we have 50
clusters where things get deployed we
would have to configure it for each and
every cluster and the third challenge
and probably the most important one is
that
once jenkins deploys the application to
kubernetes or it applies any changes to
kubernetes configuration it has no
further visibility in the deployment
status so once cube ctl apply was
executed
jenkins doesn't actually know the status
of that execution did the application
actually get created is it in a healthy
status or is it actually failing to
start and so on you can only find that
out with following test steps
so the city part of the pipeline
when working with kubernetes
specifically can be improved and made
more efficient



#  CD workflow with ArgoCD

and argo city was built for this
specific use case to make continuous
delivery to kubernetes clusters
specifically more efficient argo city
was actually purpose built for
kubernetes with github's principles and
we will see why this is a good thing
throughout this video so how does argo
city make the cd process more efficient
and address the challenges with the
common city flow that i mentioned
we basically just reverse the flow
instead of externally accessing cluster
from the cicd tool like jenkins the tool
is itself part of the cluster and
instead of pushing the changes to the
cluster
we use a pull workflow where an agent in
the cluster which is argo cd pulls those
changes and applies them there so now
let's see how does the workflow look
like when we replace the common cd setup
with argo city first we deploy arcgis
city in the cluster and then we
configure argo city and tell it hey
connect to this git repository and start
watching for any changes and if
something changes there automatically
pull those changes and apply in the
cluster so now when developers commit
the application changes to the
application source code repository sci
pipeline on jenkins since we're using
jenkins as an example will automatically
start a build process it will test the
changes build the image push it to the
repository and finally update kubernetes
manifest file like deployment.yml with a
new image version now a very important
note here about repositories is that it
has been established as a best practice
to have separate repositories for
application source code and application
configuration code so kubernetes
manifest files for the application would
be hosted in its own git repository and
one of the main reasons for that is
because the application configuration
code is not only the deployment file but
it could be config map secret service
ingress and so on and basically
everything that the application may need
to run in the cluster and these files
can all change completely independent of
the source code right and when you
update a service yemo file for the
application which is just application
configuration and not part of the code
you don't want to run the whole ci
pipeline for the application because the
code itself has not changed and you also
don't want to have a complex logic in
your build pipeline that has to decide
and check what actually changed so again
the jenkins ci pipeline will update the
deployment.yaml file in a separate git
repository where the kubernetes manifest
files are for the application and as
soon as the configuration file changes
in the git repository argo cd in the
cluster will immediately know about it
because we configured it at the
beginning to constantly monitor the
repository for changes and it will pull
and apply those changes in the cluster
automatically argo cd supports
kubernetes manifests defined as plain
yml files helm charts customize files or
other template files which eventually
all get generated into plain kubernetes
yaml files so you can use all of these
with argo cd and the repository for
configuration files which is tracked and
synced by argo cd which is a git ops
tool is sometimes also called a git
githubs repository so now whether the
application configuration repository
gets updated by jenkins in case of an
image version update in the deployment
yaml file or by devops engineers where
they change other manifest files the
changes will get automatically pulled
and applied
in the cluster by argo cd and as a
result
we end up having separate ci and cd
pipelines where the ci pipeline is owned
mostly by developers
and configured on jenkins for example
and cd pipeline is owned by operations
or devops teams and configured using
argo cd in this way we can still have an
automated ci cd pipeline but with a
separation of concerns where different
teams are responsible for different
parts of that full pipeline now let's



#  Benefits of using GitOps with ArgoCD

see some benefits that using git ops in
your project has with an example of argo
cd the first benefit is that we have the



#  Git as Single Source of Truth

whole kubernetes configuration defined
as code in a git repository so instead
of everyone doing stuff from their
laptops and executing scripts and doing
cube ctl apply or helm install commands
they all use the same interface to make
any changes in the cluster
and that could be the first
big benefit of using this model
now a very interesting use case arises
here when someone in the team decides
you know what let me just quickly update
something in a cluster it's much quicker
to just do a cube ctl apply
than to write the code changes commit
that push that and get a review from
colleagues and then eventually merge it
in the repository so now what happens
when people update the cluster manually
in addition to having the configuration
code defined in the git repository well
arcgis cd does not only watch the
changes in the git repository but it
also watches the changes in the cluster
and anytime a change happens either in
the git repository or the cluster it
compares those two states and if it sees
that something has changed in any of the
two places and they don't match anymore
so the desired state defined in the git
repository does not match
the actual life state in the cluster it
knows that it has to do something and
that something is always to sync
whatever is defined in the git
repository to the cluster
so in that case if someone goes and
makes manual changes in the cluster argo
city will detect that and it will
see that the states have diverged so the
cluster state is different than the git
repository state and it will sync the
changes and basically overwrite whatever
was done manually and this is really
useful because
this actually guarantees that git
repository and whatever is defined there
remains at any time the only source of
truth for your cluster state and it also
gives you a full transparency of the
cluster because you know that whatever
is defined in that git repository as a
configuration code is exactly the state
which you have in the cluster now it
could be that many projects need time to
adjust to these workflows and sometimes
team members or engineers absolutely
need a quick way to update things in the
cluster before changing that in the code
and you can actually configure argo cd
to not automatically override and undo
those manual cluster changes but instead
send out an alert that something has
changed in the cluster manually and that
it needs to be updated in the code as
well so you have that option to
configure argo cd in this way and
finally as a result of using
git as a single interface for making
changes in the cluster instead of
untrackable cube ctl apply commands we
have each change documented in a version
controlled way which gives us history of
changes as well as an audit trail of who
changed what in the cluster but also
this gives teams a way to collaborate on
any changes in the cluster like
proposing a change in kubernetes which
others can discuss and work on and when
done just merge those changes in the
main branch another benefit of using git



#  Easy Rollback

for config files is an easy rollback
arcacity pulls any changes and applies
them in the cluster if something breaks
with these changes or let's say a new
application version fails to start we
can revert to the previous working state
in the git history
basically just by moving back to the
last working version
especially we have thousands of clusters
that all get updated by the same git
repository this is going to be very
efficient because you don't have to
manually revert
each and every component doing cube ctl
delete or helm uninstall and basically
clean up all the things you simply
declare the previous working state and
cluster will be synced to that state
again another advantage is



#  Cluster Disaster Recovery

cluster disaster recovery
which becomes
super easy with this setup so if i have
an eks cluster in a region 1a and that
cluster completely crashes i can create
a new cluster point it to the git
repository where the complete cluster
configuration is defined and it will
recreate the same exact state as the
previous one without any intervention
from our side because again i have
described my whole cluster in code in a
declarative way and i want to mention
here that these are all actually
github's principles and benefits that
you get when implementing these
principles
using whatever githubs tool you want so
these are not specific benefits of argo
city itself but argos city just helps
implement those principles
however there are some benefits that
using argo city specifically has



#  K8s Access Control with Git & ArgoCD

now of course you don't want every team
member to be able to make changes to
cluster especially in a production
environment so again using it you can
actually configure access rules easily
you can say every member of the devops
team
or operations team even junior engineers
can initiate or propose any change to
the cluster and make pull requests and
only a handful of senior engineers can
then approve and merge those requests
and this gives you a clean way of
managing cluster permissions indirectly
through git without having to create
cluster roles and users for each team
member with different access permissions
so basically we have a benefit of easy
cluster access management
and because of the pull model you only
need to give engineers access to the git
repository and not cluster directly now
in addition to human user access with
this workflow we also have a benefit of
easier cluster access management for
non-human users like cicd tools such as
jenkins so in this case you don't need
to give external cluster access to
jenkins or other external tools because
argo city is already
running in the cluster and is the only
one that actually applies those changes
so basically cluster credentials don't
have to be outside the cluster anymore
because the agent runs inside the
cluster and this makes managing security
in all your kubernetes clusters
way easier



#  ArgoCD as Kubernetes Extension

as i mentioned an advantage of using
argo city is that it's deployed directly
in the kubernetes cluster but it's not
just deployed in the cluster because you
can actually deploy jenkins in the
cluster too but it's really an extension
to the kubernetes api so argo city
actually leverages the kubernetes
resources itself and instead of building
all the functionality itself
it uses some of the existing kubernetes
functionalities for doing its job like
using its id for storing the data and
using kubernetes controllers for
monitoring and comparing this actual and
desired state and what is the benefit of
that the main benefit is the visibility
in the cluster
that jenkins for example does not have
that allows argo city to give us
real-time updates of the application
state so argo city can monitor
deployment state after the application
was deployed or after the changes in the
cluster configuration have been made so
for example when you deploy a new
application version you can actually see
in real time in argo city ui
that configuration files were applied
pods were created application is running
and in a healthy status or if it's in a
failing status and a rollback is needed
so if we zoom out and look at a big
picture we have git repository on one
side and kubernetes cluster on another
and argo city in the middle of these two
and git is the desired state of our
cluster at any time and kubernetes
cluster is the actual state and argo
city is
an agent in the middle that makes sure
these two are always in sync
updating the actual state with the
desired state as soon as they diverge



#  How to configure ArgoCD?

now how do we actually configure argo
city to do all this
basically we deploy argo city in
kubernetes just like we deploy
prometheus istio or any other tool
and since it was purpose built for
kubernetes it extends kubernetes api
with crds or custom resource definitions
which allows configuring argo cd using
kubernetes native yaml files and the
main
component of argo cd is
an application and we can define this
application crd in a kubernetes native
yaml file and it looks like this
and the main part of the configuration
of application is we define which git
repository should be synced with which
kubernetes cluster
and this could be any git repository in
any kubernetes cluster in terms of
kubernetes cluster this could be the
cluster where argo city itself is
running in
but it could also be an external cluster
that argo cd manages and you can
configure multiple such applications for
different microservices for example for
your cluster and if some applications
belong together you can group them in
another crd called app project



#  Multiple Clusters with ArgoCD

now there is one more thing we need to
address which is working with multiple
clusters and how we apply these
processes in a multi-cluster environment
let's say we have three cluster replicas
for a dev environment
in three different regions and in one of
the clusters we have argo cd
running and configured to deploy any
changes
to all three cluster replicas at the
same time and the benefit here is that
that kubernetes administrators will only
have to basically configure and manage
one argo cd instance and the same
instance will be able to configure a
fleet of clusters whether these are
three clusters in three different
regions or thousand cluster replicas
distributed all over the world now what
about multiple cluster environments
let's say we have development staging
and production environments and maybe
each environment with their own cluster
replicas
and in this case in each environment we
may deploy and run own argo city
instance but we still have
one repository where the cluster
configuration is defined and we don't
want to deploy the same configuration to
all environments at once instead if
something changes we need to test the
changes first on each environment and
then promote it to the next one right so
the changes will be applied to the
development environment and only if
these changes are successful
then they will be promoted on a staging
environment and so on
so how do we achieve that in this
workflow for that we have two options
the first one is using multiple branches
in our git repository for each
environment so you would have
development staging and production
branches which is probably not the best
option even though it is commonly used
another and a better option would be to
use overlays with customize where you
have your own context for each
environment so with overlays you can
reuse the same base yaml files and then
selectively change specific parts in
them for different environments so now
the development ci pipeline can update
the template in development overlay the
staging ci pi plan can update the
template in a staging overlay and so on
so using these options you can actually
also automate and streamline applying
changes to different environments
before moving on i want to give a shout
out to castin who made this video
possible
kessen's k10 is the data management
platform for kubernetes
k10 basically takes off most of the load
of doing backup and restore in
kubernetes from the cluster
administrators it has a very simple ui
so it's super easy to work with and has
an intelligent logic which does all the
heavy lifting for you and with my link
you can download k10 for free and get 10
nodes free forever to do your kubernetes
backups so make sure to check out the
link in the video description and now



#  Replacement for other CI/CD tools?

let's continue
now seeing some of the benefits that
github's workflow and argo cd tool
specifically provides many people may
ask does that mean argo cd will replace
jenkins or gitlab ci cd and such tools
well not really because we still need
the ci pipeline right we still need to
configure pipelines to actually
test and build application code changes
and argo cd as a name also implies is a
replacement for cd pipeline but
specifically for kubernetes so for other
platforms you will still need a
different tool
also argo cd is not the only gear ops cd
tool for kubernetes there are many
alternatives already out there and as
the trend emerges and becomes even more
popular probably some more alternatives
will be created and one of the most
popular ones right now is flux cd which
works with and implements the same git
ops principles
so now that you understand all the
concepts around argo city and not only
what it is but also why we should care
about using it it's time to see argo
city in action and for that we're going
to use a simple but realistic demo



#  Demo Setup & Overview

in the demo part we will set up a fully
automated cd pipeline for kubernetes
configuration changes with argo cd i
have a git repository with deployment
and service yaml files
where the deployment file references my
own applications image version 1.0
i have three image versions that i've
already created for this app in my
docker public repository
which means you can also access them and
use that in your demo
so here we can just imagine that some
kind of ci pipeline ran and built these
images but it doesn't matter for us we
just have them available and we also
have an empty
mini cube cluster but again this could
be any kubernetes cluster you want so
with this setup we will first install
argo city in kubernetes cluster and then
configure argo cd with an application
crd component where we tell argo cd hey
this is the git repository you need to
start tracking and syncing with this
mini cube cluster and that's it from
then on we basically don't have to do
anything in kubernetes directly we're
just going to be updating
config files in git repository and argo
cd will pull and apply these changes
automatically so let's get started and
as i said i have an empty mini minikube
cluster
there is nothing running or installed on
it yet
plus i have
an application configuration repository
where only the kubernetes manifest files
for that application are hosted and
inside that i have one
dev folder basically and i have my
deployment and service.yml files here
they're super simple examples of an
internal service and a deployment
like this
with two replicas and an image
that basically points to
my own application image with version
1.0 and this is a public image that i'm
hosting on a docker hub which you can
also push and use in your demo
which is this one right here and inside
that i have these three image tags we're
using 1.0
in our deployment
and we're going to basically update it
to one of the later versions so that's
the whole setup and you're going to find
the links to all the repositories in the
video description so you can use them as
well and of course since this is only
the configuration repository there is
also an application source code
repository that i used to build this
image which is a separate repository i
will also link that in the video if you
want to see exactly what's in the image
but the source code itself is not very
relevant for us we just want to see how
the deployment in kubernetes works



#  Beginning of Hands-On Demo




#  compact and easy-to-read ebook bundle      👉🏼   https://bit.ly/3mPIaiU

in this video we're going to talk about
a git ops tool that is gaining
popularity in the devops world which is
called argo cd if you don't know what
git ops is you can check out my other
video about git ups after which this
video will make much more sense to you
first i'm going to explain what argo
city is and what are the common use
cases or why we need argo cd we will
then see how argo city actually works
and how it does its job and in the final
part we will do a hands-on demo project
where we deploy argo cd and set up a
fully automated cd pipeline for
kubernetes configuration changes to get
some practical experience with argo cd
right away
argo city is as the name already tells
you a continuous delivery tool and to
understand argo cd as a cd tool or
continuous delivery tool let's first
understand how continuous delivery is
implemented in most projects using
common tools like jenkins or gitlab cicd
and then see how argo city compares to
them and in that context we will answer
the questions such as is argo city just
another cd tool or what is so special
about it and if it's so special does it
actually replace any of these other
established tools like jenkins or
gitlabci icd so let's say we have a
microservices application and we're
running it in a kubernetes cluster when
things change in the application code
like new feature or a bug fix gets added
the ci pipeline on jenkins for example
will be automatically triggered and will
test the changes build a new docker
image and push it to a docker repository
now how does this new image get deployed
to kubernetes
we update applications deployment yaml
file for kubernetes with the new image
tag and this yaml file then should be
applied in kubernetes in most projects
these steps are the continuation of the
ci pipeline so after the image gets
pushed to the repository
jenkins
will update the deployment yaml file for
the application and using cubectl tool
for example will apply the updated
deployment file to kubernetes and this
is how many projects are set up however
there are a couple of challenges with
this approach first of all you need to
install and set up tools like cubectl or
helm etc to access kubernetes cluster
and execute changes
on those
build automation tools right so you
would need to install and configure them
on jenkins
you also need to configure access to
kubernetes for these tools because
kubectl is just the kubernetes client
and in order for it to connect to
kubernetes it needs to provide some
credentials so you will need to
configure credentials for kubernetes
cluster in jenkins if you're using eks
cluster which is a kubernetes managed
cluster on aws for example in addition
you would also need access to aws so
you'd have to add aws credentials in
addition to the kubernetes credentials
also to jenkins and this is not only a
configuration effort but also a security
challenge because you need to give your
cluster credentials to external services
and tools especially we have 50 projects
that deploy applications to the cluster
each project application will need its
own kubernetes credentials so that it
can only access
that specific application resources in
the cluster same way if we have 50
clusters where things get deployed we
would have to configure it for each and
every cluster and the third challenge
and probably the most important one is
that
once jenkins deploys the application to
kubernetes or it applies any changes to
kubernetes configuration it has no
further visibility in the deployment
status so once cube ctl apply was
executed
jenkins doesn't actually know the status
of that execution did the application
actually get created is it in a healthy
status or is it actually failing to
start and so on you can only find that
out with following test steps
so the city part of the pipeline
when working with kubernetes
specifically can be improved and made
more efficient
and argo city was built for this
specific use case to make continuous
delivery to kubernetes clusters
specifically more efficient argo city
was actually purpose built for
kubernetes with github's principles and
we will see why this is a good thing
throughout this video so how does argo
city make the cd process more efficient
and address the challenges with the
common city flow that i mentioned
we basically just reverse the flow
instead of externally accessing cluster
from the cicd tool like jenkins the tool
is itself part of the cluster and
instead of pushing the changes to the
cluster
we use a pull workflow where an agent in
the cluster which is argo cd pulls those
changes and applies them there so now
let's see how does the workflow look
like when we replace the common cd setup
with argo city first we deploy arcgis
city in the cluster and then we
configure argo city and tell it hey
connect to this git repository and start
watching for any changes and if
something changes there automatically
pull those changes and apply in the
cluster so now when developers commit
the application changes to the
application source code repository sci
pipeline on jenkins since we're using
jenkins as an example will automatically
start a build process it will test the
changes build the image push it to the
repository and finally update kubernetes
manifest file like deployment.yml with a
new image version now a very important
note here about repositories is that it
has been established as a best practice
to have separate repositories for
application source code and application
configuration code so kubernetes
manifest files for the application would
be hosted in its own git repository and
one of the main reasons for that is
because the application configuration
code is not only the deployment file but
it could be config map secret service
ingress and so on and basically
everything that the application may need
to run in the cluster and these files
can all change completely independent of
the source code right and when you
update a service yemo file for the
application which is just application
configuration and not part of the code
you don't want to run the whole ci
pipeline for the application because the
code itself has not changed and you also
don't want to have a complex logic in
your build pipeline that has to decide
and check what actually changed so again
the jenkins ci pipeline will update the
deployment.yaml file in a separate git
repository where the kubernetes manifest
files are for the application and as
soon as the configuration file changes
in the git repository argo cd in the
cluster will immediately know about it
because we configured it at the
beginning to constantly monitor the
repository for changes and it will pull
and apply those changes in the cluster
automatically argo cd supports
kubernetes manifests defined as plain
yml files helm charts customize files or
other template files which eventually
all get generated into plain kubernetes
yaml files so you can use all of these
with argo cd and the repository for
configuration files which is tracked and
synced by argo cd which is a git ops
tool is sometimes also called a git
githubs repository so now whether the
application configuration repository
gets updated by jenkins in case of an
image version update in the deployment
yaml file or by devops engineers where
they change other manifest files the
changes will get automatically pulled
and applied
in the cluster by argo cd and as a
result
we end up having separate ci and cd
pipelines where the ci pipeline is owned
mostly by developers
and configured on jenkins for example
and cd pipeline is owned by operations
or devops teams and configured using
argo cd in this way we can still have an
automated ci cd pipeline but with a
separation of concerns where different
teams are responsible for different
parts of that full pipeline now let's
see some benefits that using git ops in
your project has with an example of argo
cd the first benefit is that we have the
whole kubernetes configuration defined
as code in a git repository so instead
of everyone doing stuff from their
laptops and executing scripts and doing
cube ctl apply or helm install commands
they all use the same interface to make
any changes in the cluster
and that could be the first
big benefit of using this model
now a very interesting use case arises
here when someone in the team decides
you know what let me just quickly update
something in a cluster it's much quicker
to just do a cube ctl apply
than to write the code changes commit
that push that and get a review from
colleagues and then eventually merge it
in the repository so now what happens
when people update the cluster manually
in addition to having the configuration
code defined in the git repository well
arcgis cd does not only watch the
changes in the git repository but it
also watches the changes in the cluster
and anytime a change happens either in
the git repository or the cluster it
compares those two states and if it sees
that something has changed in any of the
two places and they don't match anymore
so the desired state defined in the git
repository does not match
the actual life state in the cluster it
knows that it has to do something and
that something is always to sync
whatever is defined in the git
repository to the cluster
so in that case if someone goes and
makes manual changes in the cluster argo
city will detect that and it will
see that the states have diverged so the
cluster state is different than the git
repository state and it will sync the
changes and basically overwrite whatever
was done manually and this is really
useful because
this actually guarantees that git
repository and whatever is defined there
remains at any time the only source of
truth for your cluster state and it also
gives you a full transparency of the
cluster because you know that whatever
is defined in that git repository as a
configuration code is exactly the state
which you have in the cluster now it
could be that many projects need time to
adjust to these workflows and sometimes
team members or engineers absolutely
need a quick way to update things in the
cluster before changing that in the code
and you can actually configure argo cd
to not automatically override and undo
those manual cluster changes but instead
send out an alert that something has
changed in the cluster manually and that
it needs to be updated in the code as
well so you have that option to
configure argo cd in this way and
finally as a result of using
git as a single interface for making
changes in the cluster instead of
untrackable cube ctl apply commands we
have each change documented in a version
controlled way which gives us history of
changes as well as an audit trail of who
changed what in the cluster but also
this gives teams a way to collaborate on
any changes in the cluster like
proposing a change in kubernetes which
others can discuss and work on and when
done just merge those changes in the
main branch another benefit of using git
for config files is an easy rollback
arcacity pulls any changes and applies
them in the cluster if something breaks
with these changes or let's say a new
application version fails to start we
can revert to the previous working state
in the git history
basically just by moving back to the
last working version
especially we have thousands of clusters
that all get updated by the same git
repository this is going to be very
efficient because you don't have to
manually revert
each and every component doing cube ctl
delete or helm uninstall and basically
clean up all the things you simply
declare the previous working state and
cluster will be synced to that state
again another advantage is
cluster disaster recovery
which becomes
super easy with this setup so if i have
an eks cluster in a region 1a and that
cluster completely crashes i can create
a new cluster point it to the git
repository where the complete cluster
configuration is defined and it will
recreate the same exact state as the
previous one without any intervention
from our side because again i have
described my whole cluster in code in a
declarative way and i want to mention
here that these are all actually
github's principles and benefits that
you get when implementing these
principles
using whatever githubs tool you want so
these are not specific benefits of argo
city itself but argos city just helps
implement those principles
however there are some benefits that
using argo city specifically has
now of course you don't want every team
member to be able to make changes to
cluster especially in a production
environment so again using it you can
actually configure access rules easily
you can say every member of the devops
team
or operations team even junior engineers
can initiate or propose any change to
the cluster and make pull requests and
only a handful of senior engineers can
then approve and merge those requests
and this gives you a clean way of
managing cluster permissions indirectly
through git without having to create
cluster roles and users for each team
member with different access permissions
so basically we have a benefit of easy
cluster access management
and because of the pull model you only
need to give engineers access to the git
repository and not cluster directly now
in addition to human user access with
this workflow we also have a benefit of
easier cluster access management for
non-human users like cicd tools such as
jenkins so in this case you don't need
to give external cluster access to
jenkins or other external tools because
argo city is already
running in the cluster and is the only
one that actually applies those changes
so basically cluster credentials don't
have to be outside the cluster anymore
because the agent runs inside the
cluster and this makes managing security
in all your kubernetes clusters
way easier
as i mentioned an advantage of using
argo city is that it's deployed directly
in the kubernetes cluster but it's not
just deployed in the cluster because you
can actually deploy jenkins in the
cluster too but it's really an extension
to the kubernetes api so argo city
actually leverages the kubernetes
resources itself and instead of building
all the functionality itself
it uses some of the existing kubernetes
functionalities for doing its job like
using its id for storing the data and
using kubernetes controllers for
monitoring and comparing this actual and
desired state and what is the benefit of
that the main benefit is the visibility
in the cluster
that jenkins for example does not have
that allows argo city to give us
real-time updates of the application
state so argo city can monitor
deployment state after the application
was deployed or after the changes in the
cluster configuration have been made so
for example when you deploy a new
application version you can actually see
in real time in argo city ui
that configuration files were applied
pods were created application is running
and in a healthy status or if it's in a
failing status and a rollback is needed
so if we zoom out and look at a big
picture we have git repository on one
side and kubernetes cluster on another
and argo city in the middle of these two
and git is the desired state of our
cluster at any time and kubernetes
cluster is the actual state and argo
city is
an agent in the middle that makes sure
these two are always in sync
updating the actual state with the
desired state as soon as they diverge
now how do we actually configure argo
city to do all this
basically we deploy argo city in
kubernetes just like we deploy
prometheus istio or any other tool
and since it was purpose built for
kubernetes it extends kubernetes api
with crds or custom resource definitions
which allows configuring argo cd using
kubernetes native yaml files and the
main
component of argo cd is
an application and we can define this
application crd in a kubernetes native
yaml file and it looks like this
and the main part of the configuration
of application is we define which git
repository should be synced with which
kubernetes cluster
and this could be any git repository in
any kubernetes cluster in terms of
kubernetes cluster this could be the
cluster where argo city itself is
running in
but it could also be an external cluster
that argo cd manages and you can
configure multiple such applications for
different microservices for example for
your cluster and if some applications
belong together you can group them in
another crd called app project
now there is one more thing we need to
address which is working with multiple
clusters and how we apply these
processes in a multi-cluster environment
let's say we have three cluster replicas
for a dev environment
in three different regions and in one of
the clusters we have argo cd
running and configured to deploy any
changes
to all three cluster replicas at the
same time and the benefit here is that
that kubernetes administrators will only
have to basically configure and manage
one argo cd instance and the same
instance will be able to configure a
fleet of clusters whether these are
three clusters in three different
regions or thousand cluster replicas
distributed all over the world now what
about multiple cluster environments
let's say we have development staging
and production environments and maybe
each environment with their own cluster
replicas
and in this case in each environment we
may deploy and run own argo city
instance but we still have
one repository where the cluster
configuration is defined and we don't
want to deploy the same configuration to
all environments at once instead if
something changes we need to test the
changes first on each environment and
then promote it to the next one right so
the changes will be applied to the
development environment and only if
these changes are successful
then they will be promoted on a staging
environment and so on
so how do we achieve that in this
workflow for that we have two options
the first one is using multiple branches
in our git repository for each
environment so you would have
development staging and production
branches which is probably not the best
option even though it is commonly used
another and a better option would be to
use overlays with customize where you
have your own context for each
environment so with overlays you can
reuse the same base yaml files and then
selectively change specific parts in
them for different environments so now
the development ci pipeline can update
the template in development overlay the
staging ci pi plan can update the
template in a staging overlay and so on
so using these options you can actually
also automate and streamline applying
changes to different environments
before moving on i want to give a shout
out to castin who made this video
possible
kessen's k10 is the data management
platform for kubernetes
k10 basically takes off most of the load
of doing backup and restore in
kubernetes from the cluster
administrators it has a very simple ui
so it's super easy to work with and has
an intelligent logic which does all the
heavy lifting for you and with my link
you can download k10 for free and get 10
nodes free forever to do your kubernetes
backups so make sure to check out the
link in the video description and now
let's continue
now seeing some of the benefits that
github's workflow and argo cd tool
specifically provides many people may
ask does that mean argo cd will replace
jenkins or gitlab ci cd and such tools
well not really because we still need
the ci pipeline right we still need to
configure pipelines to actually
test and build application code changes
and argo cd as a name also implies is a
replacement for cd pipeline but
specifically for kubernetes so for other
platforms you will still need a
different tool
also argo cd is not the only gear ops cd
tool for kubernetes there are many
alternatives already out there and as
the trend emerges and becomes even more
popular probably some more alternatives
will be created and one of the most
popular ones right now is flux cd which
works with and implements the same git
ops principles
so now that you understand all the
concepts around argo city and not only
what it is but also why we should care
about using it it's time to see argo
city in action and for that we're going
to use a simple but realistic demo
in the demo part we will set up a fully
automated cd pipeline for kubernetes
configuration changes with argo cd i
have a git repository with deployment
and service yaml files
where the deployment file references my
own applications image version 1.0
i have three image versions that i've
already created for this app in my
docker public repository
which means you can also access them and
use that in your demo
so here we can just imagine that some
kind of ci pipeline ran and built these
images but it doesn't matter for us we
just have them available and we also
have an empty
mini cube cluster but again this could
be any kubernetes cluster you want so
with this setup we will first install
argo city in kubernetes cluster and then
configure argo cd with an application
crd component where we tell argo cd hey
this is the git repository you need to
start tracking and syncing with this
mini cube cluster and that's it from
then on we basically don't have to do
anything in kubernetes directly we're
just going to be updating
config files in git repository and argo
cd will pull and apply these changes
automatically so let's get started and
as i said i have an empty mini minikube
cluster
there is nothing running or installed on
it yet
plus i have
an application configuration repository
where only the kubernetes manifest files
for that application are hosted and
inside that i have one
dev folder basically and i have my
deployment and service.yml files here
they're super simple examples of an
internal service and a deployment
like this
with two replicas and an image
that basically points to
my own application image with version
1.0 and this is a public image that i'm
hosting on a docker hub which you can
also push and use in your demo
which is this one right here and inside
that i have these three image tags we're
using 1.0
in our deployment
and we're going to basically update it
to one of the later versions so that's
the whole setup and you're going to find
the links to all the repositories in the
video description so you can use them as
well and of course since this is only
the configuration repository there is
also an application source code
repository that i used to build this
image which is a separate repository i
will also link that in the video if you
want to see exactly what's in the image
but the source code itself is not very
relevant for us we just want to see how
the deployment in kubernetes works
so the first step is we want argo cd
deployed in our cluster so let's go
ahead and do that
and you can reference the getting
started guide of argo cd for that and
installing argo city in kubernetes
cluster is super easy it's just the one
liner basically and you can also find
the instructions for getting started on
the official documentation page so we
can also reference that in this video so
first of all we're going to create a
namespace argo cd and argo cd and all
these components will be running in that
specific namespace
so these are the two commands that we
need so switching back to my command
line
first i'm going to create an argo cd
namespace in my cluster
and then we're going to basically apply
a yaml file
that installs everything that argo cd
needs now as an alternative you can
first download this yaml file and
basically see what's inside and maybe
save it to know exactly what will be
deployed here i'm just going to apply
directly so
all of these will be installed in an
argo cd namespace so let's execute
and there you go you see that bunch of
components have been created and now if
i do get pod in an argo cd namespace i
should see a bunch of parts being
created
so we're going to wait for all the parts
to get in a running state and then we're
going to access argo cd ui
great so the pods are all running now
how do we access the argo cd ui
if we check
the services that were created we have
one of them which is argo cd server
which is accessible on http and https
ports so we are just going to use cube
ctl port forward to access this service
port forward let's not forget the argo
cd
namespace
and we're going to port forward a
service argo city server
and
make it available locally on port 8080.
so forward the service requests on this
port to localhost port 8080. let's
execute
like this
and
now if i grab that url
we're going gonna get a warning of the
connection because it's https but not
secure
we're gonna proceed anyway and here
we're gonna need to log in to argo city
ui and again going back to getting
started guide we can see how to log in
to the service first of all the username
is admin and the password gets
auto-generated and saved in a secret
called argo cd initial admin secret
so if i get that secret
in an argo cd namespace
let's do
yaml output
here we have a password attribute with a
base64 encoded value so that's basically
the password we're gonna decode it
and there you go so that's the password
you can ignore the percentage sign here
and just copy the string
and use it as a password
paste it in sign in and there you go
and as you see arca city is currently
empty we have no applications because we
first need to configure it so right now
it doesn't do anything
so that's going to be our next step
let's write a configuration file for
argo cd to connect it to the git
repository where the configuration files
are hosted and we're going to put that
argcity configuration file also in this
configuration repository so i have
checked out the project which you can
also go ahead and do so just clone it
and we're gonna work on this project
locally
so i'm gonna switch to that project and
where we have this dev folder with the
configuration files and i'm gonna open
this whole thing in a visual studio code
and there you go
so now let's create an argo cd
configuration and let's call it
application.yaml
the configuration is actually very
simple first of all we have our already
familiar fields from kubernetes which
are api version
and for custom components or custom
resource definitions the api version
is from the project itself so this is
going to be argo
project
io
and that's the version which is still
alpha
then we have the kind which is
application
metadata
where we have the name and the namespace
so let's call this my app argo
application
and the namespace will be argo city so
this application component will be
created in the same name space where
argo city is running and then we have
the specification which is specific to
this application kite now very important
note about the api version this of
course changes so as they move it from
alpha to better and then just basically
release it this will change so when
creating this application kind please
always refer
the documentation to make sure you have
the correct values here and you can see
the example in the documentation right
here the application section you have
this example application definition and
i'm going to link this also in the
description
so moving back to the specification we
have a couple of attributes first of all
we have the project
which as i said you can group multiple
applications into a project if we don't
care about that we just use the default
project that's where everything goes by
default and leave it at that and then we
have two things that we want to
configure in every application the first
one is the git repository that argo cd
will connect to and sync it and the
second one is the destination or the
cluster where argosy will
apply the definitions it found in the
git repository so the source of the
configuration and the target or
destination cluster for that
configuration
so we have source
for the git repository and for this we
have repo
url and that's going to be our git
repository
so just copy this url right here
we also have target
revision
and we're going to point it to head so
that's basically always the last commit
in that git repository
and we also have path attribute
that
lets us specify whether we want to
sync or track a specific
path in that repository and since we
have dev path we're going to
use that one so that's the configuration
for repository as a source and then we
have destination
and that's gonna be the address of the
kubernetes cluster itself which is the
api server and because we're running
argo cd inside the destination cluster
itself we can put a dns name here for
kubernetes api server which is
kubernetes
dot default dot service so that's
basically
an internal service name of kubernetes
api server and
if we check that
if we do a quick ctl get service in the
default namespace you see that we have
this kubernetes service which basically
is the internal service for api server
and because again argo city is running
inside the cluster it can access the
internal services directly we don't have
to provide an external cluster endpoint
but as i said argo city can also connect
to clusters externally or can manage
multiple clusters and synchronize the
definitions to multiple clusters at once
and for that you would then use an
external address of your cluster so
that's going to be the server address
and finally we can also specify a
namespace so basically when argo city
finds those configuration files in which
namespace it should apply them and if
it's not default then we would have to
specify a namespace here
and let's say we want all this
configuration to be created in my app
namespace now
we actually don't have my at namespace
currently
in the cluster so when argo cd tries to
deploy this
we want argo city to
automatically create this namespace if
it doesn't exist already in the cluster
and we need to configure that as well
and to configure that we have another
attribute called
sync
policy
and inside that we have sync options
and one of the sync options or
synchronize options is create
namespace
equals true so by default it's false
it's not going to create a namespace
automatically if it doesn't find it but
we're going to set it to true
using this configuration now there are a
couple more things we want to configure
here the first one is as we said we want
argo city to basically automatically
sync
any changes in the git repository but
default
that is turned off so if you change and
push something to the git repository
argo cd doesn't automatically fetch that
but we can enable it simply
by using automated
attribute
and inside that automated attribute we
have
two more options the first one is as i
mentioned we can configure argo cd to
undo or overwrite any manual changes to
the cluster so if i did cuba city apply
manually in the cluster argo city will
basically override it and sync it with
the git repository state instead and we
can enable it using a self-heal
attribute
set to true and finally if we rename a
component for example or if we deleted
the whole service.yaml file we want
argosy to also delete that component or
that old component in the cluster as
well and that's going to be an attribute
called prune and we're going to set it
to true
now note that
the automated attribute will configure
argo cd to pull the changes in git
repository in three minute intervals so
argo cd will not pull the changes as
soon as they happen in the git
repository but rather it will basically
check every three minutes whether
something has changed and then pull and
apply those changes in the cluster
that's how it's going to work
alternatively if you absolutely needed
to configure your workflow to always
basically apply and synchronize with
cluster as soon as something changes in
the git repository you can actually
configure a web hook
integration between git repository and
argo cd so you have that option as well
but we're gonna just go with the default
where argo city checks for any changes
in the repository regularly now you'll
probably be wondering
why are these things turned off by
defaults so why do i have to enable
automatic sync or
undoing the manual changes and deleting
the applications when their
configuration gets removed and so on and
my assumption is that it's a protection
mechanism that something doesn't get
accidentally deleted so you have to
actually explicitly enable it or that
you don't want automatic syncs in the
cluster or self-healing because your
team needs some time to transition to
this workflow and maybe that's why you
have to explicitly enable them but as
you see enabling them and configuring
that is not very difficult and with this
configuration we're gonna fully automate
all these actions and that's basically
our application configuration for this
specific repository and this specific
path and as you already see from this
configuration
in the same cluster you may have
multiple such applications for different
name spaces um or different environments
that you can create in argo city now we
need to actually apply this
configuration to configure argacity with
this logic so let's go ahead and do that
using cube ctl apply so this is going to
be ideally the only cube ctl apply that
i have to do in this project because
after that everything should be auto
synchronized so first i'm going to add
this to the repository to the remote
repository basically
because again argo cd will connect to
the remote repository so we want the
argo cd
configuration to also be available there
and if i refresh i will see my
application.yemel now argo city doesn't
know anything about this repository or
this configuration yet
for that we need to apply
this
application.yemo in the cluster so let's
go ahead and do that and see application
component was created
and now if we go back to argo city ui
you see that we have my app argo
application
that's the name that we gave the
application component and it seems like
it has successfully synced
everything from this repository and we
can click inside to see more details
details about successful sync but also
a pretty cool feature in the ui is this
overview here of different components
that
the my app argo application triggered to
create so this is the argo city
application
component itself
and
this one actually triggered creation of
the service as you see with the service
icon here and you also see all the
components that have been created in the
background from these top level
components so we have the deployment
here we have the replica set behind that
deployment and we have
the two pod replicas
because we have
two replicas defined here
of this specific image
as you see
in those pots and again you click on one
of these components for even more
details so if i click in the pod you see
the main data including the image
as well as
the actual state manifest
you see the events
for that pod as well as the logs
which are some pretty neat additional
features here and the same way you can
also click into the application and here
you have the details of the application
that we provided like repository url
create namespace automatically enabled
the sync policy prune self-heal and so
on you can edit them here as well and
you also have the manifest view or the
yaml view that we configured right here
awesome so now let's actually test the
automatic sync
by updating something
in the configuration
so what we're going to do is go into the
deployment.yml file
and update
the image
to a later tag
i'm going to do it directly in the
gitlab user interface so we don't have
to commit and push etc and let's change
the tag to 1.2
and commit the changes
and now at a certain interval when argo
cd checks the git repository for any
changes it will see that the desired
state has changed and it's 1.2
and not 1.0 that we have running in the
cluster
and it will automatically sync those
changes
and as you saw argo cd showed the
application stayed out of sync very
briefly and then the deployment got
updated so
a new replica set was created in the
background which then started two pods
and if we check the pods you see that
the image tag is now 1.2
and the deployment desired state
is also image with version 1.2
now let's make one more change in our
configuration repository to test that
pruning the applications
also works which again means if i rename
a resource which means
the resource with the old name doesn't
exist anymore or if i deleted this whole
configuration file then i want argo city
to also delete that component in the
cluster and let's test that
and i'm going to rename my deployment to
just my app
and commit the change
and again after some interval argo city
will sync those changes
and as you see it removed the old
deployment with my app deployment
name and it basically created a new one
with its own replica set and started
those two parts so it means the pruning
works as well and finally let's now try
changing something in the cluster
directly using cubectl command
so let's say i edit the deployment
in
my app namespace with the deployment
name my app
and i want to configure
four replicas instead i'm going to make
my window a little smaller so we can see
that
in life
and as soon as i try to
save these changes
you saw that two pods were added but
argo cd immediately reverted that back
to two replicas because we have
self-heal configured which undoes any
manual changes in the cluster
and if i do cube ctl edit deployment
again you see that it again says two
replicas here
so my change was basically reverted and
finally if you're testing around with
argo cd and you don't want to wait for
the time interval to basically update
your cluster you can also trigger the
synchronization with the git repository
manually so first you basically refresh
which
tells argo city to compare the state in
the cluster with the state in the
repository and then you can do sync
which will then actually synchronize
those states
now if you learned a lot in this video
then please like it and share it with
your colleagues so that they can learn
about these concepts as well and with
that thank you for watching and see you
in the next video