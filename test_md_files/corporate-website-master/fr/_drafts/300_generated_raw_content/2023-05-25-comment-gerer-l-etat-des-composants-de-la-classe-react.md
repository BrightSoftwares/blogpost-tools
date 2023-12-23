---
ToReview: true
author: full
categories:
- javascript
date: 2023-05-25
description: In React, state refers to a structure that keeps track of how data changes
  over time in your application. Managing state is a crucial skill in React because
  it allows you to make interactive components and dynamic web applications. State
  is used for everything from tracking form inputs to capturing dynamic data from
  an API. In this tutorial, you’ll run through an example of managing state on class-based
  components.
image: https://sergio.afanou.com/assets/images/image-midres-43.jpg
lang: fr
layout: flexstart-blog-single
post_date: 2023-05-25
pretified: true
ref: reactclass_components_1238
tags: []
title: Comment gérer l'état des composants de la classe React
transcribed: true
youtube_video: http://www.youtube.com/watch?v=fBC9jk30BCg
youtube_video_description: Abonne-toi pour me soutenir ▷ https://www.youtube.com/nordcoders?sub_confirmation=1
  Suis-moi sur Twitter ...
youtube_video_id: fBC9jk30BCg
youtube_video_title: Apprendre ReactJS | État et cycle de vie d&#39;une classe
---

# 

bonjour à tous et bienvenue dans cette
vidéo durant laquelle on va voir un peu
les différents états durant le cycle de
vie des composants
on a des fonctions qui sont appelés
durant la vie du composant suivant s'il
vient d'être créé et s'il vient d'être
supprimée ou mises à jour et tout ça
c'est très intéressant on va mettre un
petit peu des consoles log un peu
partout voir quand est ce que les
fleuves sont appelés et qui est vraiment
appeler et à quel moment
une façon à bien comprendre ce qui se
passe derrière et la logique donc là je
suis sur la documentation va pas prendre
l'exemple pour l'instant la du timer
qu'ils ont pris mais on va s'intéresser
déjà à la première fonction qui est le
composite 10 min alors si vous comprenez
un petit peu l'anglais vous allez vite
compris ça veut dire quoi se dire quand
est ce que le composant était monté
alors et quand est ce que le composant
était monté on va voir ça de suite
moi je reviens sur mon application avec
mon appétit point js donc d'en exercer
abb point j s étant donné que c'est une
classe forcément la première chose qui
va être rappelé être le constructeur
donc ce qu'on va faire c'est déjà mettre
un petit console log en mettant
constructeur constructeur appelez donc
ça ça va être déjà d'une première chose
ensuite on a le render alors attention
le rhin dont on va également lui m
console à boire quand est ce qu'il est
appelé avant le return parce que après 2
return
il y aura pas de quoi d'exécuter ce
qu'on renvoie directement notre gsx et
s'est terminée donc constructeur un peu
les on va mettre la rend renders appelé
très bien donc déjà on va voir quand est
ce que ces fonctions là sont appelés à
quel moment on va examiner l'élément et
donc je vais reprendre ma page on voit
constructeur appelé dans un premier
temps et le render appel dans un second
temps très bien maintenant si je clique
sur le bouton et je fais apparaître une
image on voit que le render est appelé
une seconde fois comme il ya une
modification de state c'est bien le cas
parce que lorsque je clique qu'est ce
que je fais je fais un set state et je
change l'état de chaud et bien mon
composants raid us va ré appelé le
render var et appelé le g16 les bases du
genre cliquer dessus
j'ai quand même changé le state quand
bien même je fais disparaître l'image
il va ré appelé le render donc très bien
on sait maintenant que le render est
appelée à chaque fois que un état state
a été modifié il rappelle le g16
maintenant qu'est-ce qu'on va faire on
va appeler cette fameuse fonction
complète dit bolt donc on est parti
avant mon vendeur je vais appeler
comprenette 10 min et je vais mettre un
petit console loeb pour le mouvement de
composants montés tout simplement et on
va rendre notre page alors on va qu'on a
le constructeur qui a appelé dans un
premier temps le render qui est appelé
dans un second temps ça ça ne change pas
et enfin quand le g16 est rendu on
appelle cette fonction composantes
comprenant dix demandes le composant est
bel et bien monté c'est ok donc on voit
l'ordre dans lequel est appelé les
différentes sont appelés différentes
fonctions donc c'est important d'avoir
ça en tête
alors maintenant qu'est ce qui se passe
si je modifie state ce qu' a priori
lorsqu'on appelle cette fonction là
c'est pour pas faire quelque chose c'est
pour dire bombay le composent ont été
créés maintenant je vais faire quelque
chose je vais vérifier en state par
exemple on va se rajouter dans
trop tableau de state un title pourquoi
pas ce title ce sera coucou les amis
comme d'habitude
et qu'est ce qu'on va faire on va
simplement il s'est rajoutée dans notre
div
un petit h 1 voilà on va très très
rapidement utiliser ça en rajoutant un
texte 4xl on va lui donner une bombe de
couleur du texte
purple 900 voilà peut-être un peu qu'on
peut plus clair 700 et on va mettre
margin ouailles pour donner un petit peu
plus d espace 2 3 ou même de 2,5 et à
l'intérieur de sacha qu'est ce que je
fais mais je vais appeler is state title
donc là je vais appeler mon title id ici
j'appelle le zii state et comme la clé à
ce niveau là au niveau de mon de mon
objet c'est title j'appelle cette clé là
ça va me rendre
l'élément la valeur coucou les amis
j'enregistre et j'ai mon super titre
parfait donc jusque là rien qui a été et
est modifié ainsi j'appelle mon image le
render est appelée à chaque fois très
bien maintenant au niveau de ce
composant d'une banque
eh ben je vais modifier ce title et je
vais faire this
et là attention comme la propriété est
immuable on est obligé de passer par
cette secte donc ça on l'avait déjà vu
j'ouvre un objet et gillet title et là
je vais m
le composant a bien été monté par
exemple et je vais enregistrer
on voit là que ça a été autre élodée
donc mon title a été modifié on va
reprendre l'image pour voir ce qui se
passe donc qu'est ce qui se passe on est
le constructeur le render le composerait
bien monté très bien donc on a bien se
console l'add on se console le glas qui
a été appelé et ensuite le rwanda a été
ré appelé encore une fois pourquoi parce
que il ya encore eu une modification du
state j'ai modifié mon title donc
modification du state donc renders du
g16 il rend une nouvelle fois le g16
donc on a cet ordre là qui a été qui a
été appelé si je fais un coup de clic je
modifie encore une fois le state donc le
render a été rappelé
donc voilà vous avez maintenant une
petite idée de l'ordre dans lequel sont
appelés les fonctions donc on va
continuer avec les autres états du cycle
de vie notre composants donc on continue
avec la deuxième fonction complète will
hunt donc si vous comprenez cette
fonction est appelée lorsque le
composant a été détruit d'où ce qu'on va
faire on va copier cette fonction là et
alors je la mettrais bien de notre à
pépé point de gesse seulement ce
composant la à pépé à aucun moment il
n'est détruit donc ce qu'on va faire
c'est qu'on va se créer un petit dossier
dans src qui s'appellera components on
va y glisser la partie images d'accord
donc simplement cette image là on va en
faire un composant est ensuite suivant
si on appelle bas après c'est la logique
de notre composants initial suivant si
on appelle notre state ou pas ça sera
monté ou détruits ou démonter et là on
pourra sur ce composant la appeler
d'autres
notre fonction hunt première chose à
faire dans notre dossier src on se crée
un de ses composés très bien à
l'intérieur de ce qu'on connaît
on va se créer ce qui sera notre
prochain composant notre prochain compo
net on l'appelait pictures ou images
comme vous voulez pictures points gs
très bien alors pour pas vous casser la
tête à chaque fois que vous recréez un
composant il faut importer réacteur
classique stand tout ça vous pouvez
installer une extension qui s'appelle
laisse seven react voilà réduits aux
actuels répète ce qui va vous permettre
d'avoir accès à des raccourcis un petit
peu comme sur et même pour ceux qui sont
le fanatique de html qui va permettre de
mettre en place un boiler plight très
facilement par exemple si je tape rcc ça
va me permettre de faire react classe
composantes et là j'ai déjà mon ma
classe pictures qui étant déjà deux
compos net avec les différents import et
ça c'est super déjà une fonction renders
qu'il est prête à rendre lui gsx voilà
donc c'est ce qu'on va faire on va
simplement ici récupérer notre image
voilà up de cette façon dont j'ai coupé
je vais coller ça je le remplaçais par
mon pare d'un div et je mets mon et mg
très bien maintenant mais c'est un peu
plus simple
je vais ici rendent si le zii state est
égal à choquer ce que je rends je rends
pictures voilà
alors après il faut pas oublier
d'importer on va le faire plus
simplement si je commence à écrire à
écrire pictures il me propose ici mon
composants donc de cette façon là voilà
ils m'apportent directement pictures
deux compagnons pictures c'était juste
pour éviter de le taper à la main mais
vous pouvez très bien le café à la main
lamont visual studio kohn est assez
intelligent pour même porté le bon
composants donc pour l'instant ce qu'on
a fait c'est qu'on a exporté tout ça
dans un nouveau composant et au lieu
d'appeler directement notre html belges
appellent ce composant la qui lui va
rentrer en images dans son gilet 6 dans
la fonction renders très bien
normalement tout fonctionne à merveille
donc je vais revenir à réactualiser
carrément l'actualiser si je clique le
render est rappelée normal le state est
inchangée sur au clic l'image disparaît
pour l'instant impeccable mais
maintenant le gros avantage c'est que
cette ce composant la pictures il les
détruit au moment où je change sont
state en nul donc c'est là qu'on va
pouvoir utiliser la fonction propos neil
twente on va la mettre dans notre classe
pictures composantes will hunt et on va
faire un console blog et on va marquer
composants pictures
démonté ou détruits comme vous voulez et
on clique donc le render est appelée
très bien le g6 a été modifiée le style
a été modifié je re clic lohan n'aurait
rien à pelé est le composant pictures
des mondes et qu'on voit que le console
up fonctionne très bien
donc maintenant on voit comment utiliser
ce cette fonction là on voit que les
biens appelé après cas que le composant
était retiré détruits maintenant on va
mettre un petit peu de logique et je
vais vous montrer comment faire les
choses parce qu'il va falloir bien faire
les choses
à certains moments parce que notamment
ça peut inclure des memory leak des
fuites de mémoire on va se dire qu'on va
prendre l'exemple de la documentation
on va se dire que quand le composant est
monté donc là je rappelle aux koponen
d'etoudi nantes alors là je l'appelle
sur ma classe pictures je l'appelle sur
mon composants de classe pictures pas
sur mon apb quand le composant est monté
qu'est ce qu'on va faire mais on peut
faire un petit cet intervalle alors on
va mettre 1000 1000 secondes ça fera une
seconde
voilà très bien et toutes les secondes
qu'est-ce qu'on peut faire on va juste
mettre un petit console log et on va
marquer ben timer timer appelé tout
simplement
voilà donc
qu'est ce qui se passe on appelle notre
timer toutes les secondes dès que ce
composant la est monté vous pourrez voir
un tout petit peu plus clair je vais
retirer les consoloc du composant abb
parce que là ça fait beaucoup de
consoles ogg et on a compris à ce niveau
là commence à fonctionner les l'ordre
dans lequel tout été appelé donc j'ai
mon comprenant des demandes qui lance un
timer très bien et qui fera inconscient
le timer appelé toutes les secondes
quand le composant est montée quand le
composant n'est plus monté qui les
détruit qu'il est démontée on fait notre
petit con soldats très bien on
réactualise tout ça tout va bien je
clique g montagnards qui appelait donc
on voit qu'ils appelaient toutes les
secondes on voit ici ça s'incrémente 8 9
10 tout est souvent le timer est appelée
très bien je re cliquer sur le bouton ça
va aider monter mon image et là qu'est
ce qui se passe on a le consoloc
pictures démonter impeccable on s'y
attendait par contre le timer appelé là
il est reparti ça veut dire que à ce
niveau là montrent timer a été encore
une fois appelé et là c'est une grosse
fuite de mémoire parce que vous avez à
ce niveau là un timer cet intervalle qui
est appelée et qui va renault pour
toujours là il est parti à aucun moment
ce timer va s'arrêter et pourtant dans
ma logique moi je le veux qu'ils soient
appelés que lorsque le composant est
monté et lorsqu'il est démonté je veux
que ça cesse je ne veux plus que ce
timer soirée appelée je veux juste
qu'ils s'arrêtent donc il va falloir
être un petit peu astucieux et stocker
un peu son état dans dans le lait state
donc qui dit state dix constructeurs on
est parti on appelle la petite fonction
constructeur donc attention hein on
utilise toujours le super propre comme
on avait l'habitude de faire pour
hériter de les propriétés du
pas-de-la-case parente super propre
ok pas de souci à ce niveau-là c'est
bien et là je peux mettre monzie state
is state
et là bas qu'est ce que je vais faire
bon là j'avais stocker chaud et abala je
vais stocker l'état de mon timer donc je
vais l'appeler tyler et je veux dire que
c'est nul
tout simplement voilà donc mon timer
nuls
ensuite qu'est ce que je fais quand je
monte mon pictures ben je vais faire une
modification de mon état donc 6,7 state
on sait faire maintenant timer ckoi
bétail meurt maintenant c'est ça on
appelle notre set tiner à ce niveau là
pas de point virgule on va le mettre ici
impeccable donc quand je monte ça
pictures là je change le state demande
timer qui était initialement nul initial
ni initialement nul en sept timer enfin
voilà la valeur c'est vraiment son timer
donc le timer démarre et la valeur est
stocké dans notre objet dans notre state
timer quand le compound est détruit
qu'est ce que je fais je fais un cuir
intervalle this state tiger et je vais
aller attraper mon timer au travers de
du state google faisait cela était
j'appelle la clé moi je l'avais appelé
timer donc faut être accord avec le code
à vous si vous l'avez appelé intervalle
vous faites c'est cet intervalle vous
appeler cette valeur là et vous allez
claire l'intervalle et normalement à ce
niveau là
si je réactualise tout va fonctionner on
aura plus de fuite de mémoire donc je
clique mon image et appelaient donc on
n'a plus les consoles log d'avant parce
que j'ai des rotules mais on a le timer
qui appelait impeccable on voit que ça
s'incrémente d'accord c'est répéter
chaque seconde
je re clic composants pictures démonter
et là on n'a plus cette fuite de mémoire
on n'a plus le timer qui se relance
parce qu'on a effectivement clear cet
intervalle donc c'est très important
d'utiliser les bonnes pratiques donc là
je n'invente rien tout ce que je vous
donne c'est plus ou moins dans la
documentation
voilà donc on se souvient des qu'on
décide pas de rajouter de la logique
dans notre composants au montage
montage d'autres composants on n'oublie
pas de faire les choses bien et de
stocker les états dans notre state et
d'utiliser les fonctions qu'ils vont
bien pour appeler belle les bonnes
choses au moment où le composant et
détruit en l'occurrence notre notre
intervalles on l'a clear au travers de
l'état lorsqu'on a appelé un autre
composante oui la demande et on n'a pas
juste des c'est le l'intervalle
s'appelait dans le composant dit membres
et ensuite on s'est dit voilà dès que le
composant et détruit ben ça s'arrêtera
non ça s'arrêtera pas il ya une fuite de
mémoire il faut traiter ça avec les
bonnes pratiques donc enfin on va voir
maintenant un autre état dont le cycle
de vie de ce composant qui est le
comprenez did update alors vous l'avez
vu vous l'avez compris en réalité au
travers des deux précédents état on va
dire les deux précédents mouvements qui
se déroulent pendant son cycle de vie
il y a eu à des à certains moments le
render qui a été rendu parce qu'une
modification du state et du coup sa
force et le composant art rendre le j ai
6 et ça
si vous désirez le capturer ce moment eh
bien je reviens sur mon appétit point g
est ce vous avez un complot net camp
poney guide
gates comme son nom l'indiqué on va
mettre un console point l'homme de
composants mis à jour dès que le
composent a mis à jour des cas une
modification du states have a vécu ça va
attraper ce moment là donc ça va appeler
composants dit abdel est donc là j'ai
pas forcément de logique à rajouter en
plus si ceux des bains revendre notre
composants et là on voit composants mise
a mis à jour donc j'ai retiré
précédemment les différents autres
consoles homme bon vous savez dans quel
ordre ça se fait ça fait d'abord le
constructeur ensuite ça rend le j ai 6
très bien et quand le composant a été
monté il a modifié le titre vous
souvenez on avait défini dans
le constructeur initialement un titre
qui était coucou les amis et ensuite il
ya eu une modification du state
donc c'est une modification du state il
y a eu renders qui a été qui a rendu une
nouvelle fois le g16 et donc il ya eu
une mise à jour donc on appelle ce qu'il
ya dans cette fonction-là composants dit
être fier le composant consoloc de
composants des agents en revanche si je
commente cette modification du title on
a plus de 7 state
donc on a plus de modifications d'état
donc surrender n'est plus rendu une
seconde fois il est rendu juste après le
constructeur comme on l'a vu et cette
fonction complète des tablettes n'est
pas appelé si j'aurai un qu'allez vous
voyez elle n'est plus appelé de la même
manière si je clique sur le bouton et
que je modifie l'état de chaud et bien
on va on va forcément modifier un état
ici l'état de chaud et donc sa
modification du state il va y avoir
quand paul ended dette qui sera appelée
donc au bord pour en avoir le coeur net
on va le faire de suite je clique et on
voit composants mis à jour bon le timer
est appelée très bien mais on voit que
le composant et émile journault
comprenez dit d' abject a été appelé
avant le tiger d'accord séjour au clic
on a d'abord le composant pictures qui a
été démontée et ensuite quand tout s'est
déroulé à la fin composants remis à jour
donc voilà maintenant pour les
différents états du cycle de vie des
composants