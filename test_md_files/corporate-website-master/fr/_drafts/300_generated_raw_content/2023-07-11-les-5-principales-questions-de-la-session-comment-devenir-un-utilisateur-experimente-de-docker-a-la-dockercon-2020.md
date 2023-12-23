---
ToReview: true
author: full
categories:
- docker
date: 2023-07-11
description: It was a fantastic experience hosting my first ever virtual conference
  session. The commute to my home office was great, and I even picked up a coffee
  on the way before my session started. No more waiting in lines, queueing for food,
  or sitting on the conference floor somewhere in a corner to check emails.
image: https://sergio.afanou.com/assets/images/image-midres-28.jpg
lang: fr
layout: flexstart-blog-single
post_date: 2023-07-11
pretified: true
ref: top5_questions_howtobecome_a_dockerpoweruser
seo:
  links:
  - https://m.wikidata.org/wiki/Q15206305
tags:
- docker
- productivity
- poweruser
title: Les 5 principales questions de la session "Comment devenir un utilisateur expérimenté
  de Docker" à la DockerCon 2020
transcribed: true
youtube_video: http://www.youtube.com/watch?v=gD7KPXA8jPQ
youtube_video_description: Les webinars de notre programme de peer learning Malt Academy
  sont maintenant dispo en replay ! Retrouvez toutes les ...
youtube_video_id: gD7KPXA8jPQ
youtube_video_title: Dockerfile - Les bonnes pratiques
---

# 

bonjour bonjour tout le monde
merci merci d'être là pour cette note
academy enchanté moi je m'appelle cloud
et du coup je travaille avec l'équipe
community chez baltes et j'ai de la
coordination des maths academy est-ce
que vous dans un premier temps vous
m'entendez tous bien et est ce que vous
voyez tous bien mon écran salaire mais
super super vous êtes tous réactif
parfait bah du coup ce que je vais faire
en attendant que la dernière personne se
connecte je vais vous présenter un petit
peu la session comment ça va se passer
du coup on accueille aujourd'hui
guillaume et julien jérémy voilà là
autant pour moi désolé gérer mais j'ai
vraiment un problème avec avec mon
prénom je m'excuse guillaume et jérémy
donc ils nous font l'honneur d'animer
ces malte académie pour nous autres
parler davantage de docker et et des
bonnes pratiques
du coup pour vous expliquer un peu ce
que c'est que les maths académie ce sont
des formations qui ont été proposées en
commençant avec la situation qu vide
pendant le confinement des formations en
fait qui sont faites par des freelances
de la plateforme d'e bénévolement pour
d'autres il ans pour monter en
compétences sur des sujets tout
simplement
ou alors pour rappel pour ceux qui
seraient là aujourd'hui et qui ne sont
pas encore membres de la plateforme mal
c'est une plateforme de mise en relation
freelance client en fait donc on
collabore avec une grosse communauté de
free lance sa plus grosse de france plus
de 200000 freelance en france en
allemagne et en espagne 1 et avec plus
de cent cinquante mille clients donc
voilà pour la présentation
je vais bientôt du coup laissé la parole
à guillaume et à jérémy voilà si vous
avez des questions n'hésitez pas à les
poser dans l'onglet question pour que ce
soit plus pas plus pratique après pour
les peaux les speakers pour qu'ils
puissent retrouver vos questions et y
répondre et puis et puis voilà sans plus
tarder
et si vous voulez discuter aussi dans
l'onglet chat n'y a pas de souci pour
échanger sur le sujet sans plus tarder
je vous laisse la parole guillaume et
jérémy et bonne bouffe attaque admis à
tout le monde
je laisse l'écran très bien je le prends
hop là voilà et voilà c'est parti
alors bye bonjour à tous merci donc à
tous d'être présent si nombreux
aujourd'hui on va vous parler avec
jérémy des bonnes pratiques pour les
docteurs file donc alors si voilà si ça
veut bien fonctionné donc qui sommes
nous donc je vais commencer par moi même
comme ça sera fait c'est super super pop
lit mais ça sera on avancera je
m'appelle guillaume je suis développeur
chez de coeur depuis un an et demi et
donc moi donc j'ai envie de rouler je
suis anciennement développeur chez
docker maintenant je travaille chez les
dogues
et donc je suis vidé je suis toujours
senior software engineer
on va commencer
al rai allez c'est parti
alors déjà on va commencer par vous
expliquer les bases donc qu'est-ce que
c'est un joker fine alors un docker fail
c'est un peu comme une recette de
cuisine dans lequel vous expliquer tout
ce que vous allez faire pour préparer
votre application bild et votre
application bull dès votre image pour
pour pouvoir la voir après la publier ou
l'utiliser voilà donc quand vous prenez
votre docteur faye vous le passez à
l'esn jean il va le bild et vous allez
obtenir une image une image ces composés
de quoi ces composés de d'une image de
base donc à partir de quoi vous allez
partir donc si par exemple vous voulez
partir d'une image de bien dit que
l'image de base c'est de bien et ensuite
à chaque fois que vous ajoutez une robe
une commande comme ron adou copie vous
allez créer un nouveau
layher alors qu'est ce que c'est un
leurre à un meilleur c'est un tard qui
va être ensuite compressés au moment de
l'exécution
ils vont être tout ce qu'on caténaire
les uns avec les autres et vous allez
pouvoir avoir votre fs comme ça donc les
meilleurs généralement ils sont
organisés par ordre de changement de
fréquence de changement vous allez
mettre ce qui semble changer le moins
souvent en haut et ceux qui sont changés
le plus souvent en basse parce que dans
les meilleurs vous avez un mécanisme de
cache et se cache vous allez pouvoir
vous en servir pour bild et le moins de
chine - de layher possible donc si par
exemple vous avez une meilleure tout
début qui changent pas souvent je vous
ai souvent le site fin au moment du bild
il va être ce type et en utilisant cash
et vous allez gagner du temps sur votre
bulle une fois que votre image à les
build est pareil vous ne pouvez
l'exécuter et ça va vous créez un
container où il faut bien dissocier le
dr faye l'image et le conteneur qui sont
trois étapes différentes du cycle de vie
de votre application
ok on parle de quoi on va partir sur un
bon exemple du famille on part sur un
gros joker fall qui contient engine x
pour servir de réserve proxy une
application frottant react un backend
hans spring août et une base de données
mon goût tout ça ça va être dans le même
doctor flake donc dans la même image et
dans le même conteneur tout ça va
fonctionner ensemble donc l'image
actuellement à fait à peu près 1 giga
set et a fait presque 500 secondes pour
la bild or au total donc c'est énorme et
c'est parce qu'on veut au film ses cours
et donc c'est courant par contre c'est
courant mais c'est parce qu'on donc on
va commencer donc par regarder à quoi ça
ressemble à sion excusez moi je suis
passé
là je veux juste m'assurer que voilà ça
marche pas ici donc cette application
c'est une application qui recense
l'ensemble des brasseries en belgique
voilà ce que ce taux qu'on avait
présenté la première fois des vans
belgium et donc il fallait quelque chose
de pour la belgique
et donc si on regarde le code on va
pouvoir regarder un petit peu comment ça
se passe voilà on l'a on a en fait avant
que tu commences avec le docteur file un
client qui est stocké ici
donc comme on le disait qui est en react
donc on va pas rentrer dans le code des
à proprement parler du client du serveur
sait pas ce qui nous intéresse
aujourd'hui qu'un client react le proxy
donc la configuration dj mix et le
serveur donc un serveur en springwood
coating voilà je te laisse sa marque
voilà alors je vais faire ça pour que tu
restes focus ion mon curseur voilà donc
ce dock gros joker fine il est nos
comparses que je disais au début d'une
image de base qui s'appelle ubuntu
bionique donc c'est la version bio ning
tout le temps et on commence par
installer plein de choses donc on va
faire une synchro du père époux apt-get
elle répond répéter avec son art en
local on va ensuite installé l'openjdk
pour pouvoir faire tourner des
applications en java
on va installer wget et des outils pour
faire de la ville une signature gpg pour
pouvoir installer après nod aimons go et
enfin on installe engine x donc à la
suite de ça on fait un gros copie de la
config engine x ont créé un répertoire
dans lequel mungo il va stocker tout ça
data est ce que ça se collent tout seul
oui ça ce qu'on me touche c'est
merveilleux ensuite on va installer le
serveur donc le copier à l'intérieur
d'eux
de l'image faire le build est pareil
pour le client on copie le client dans
le mode dans l'image
on la build et on déplace enfin ça dans
un répertoire que n janyk va servir et
ensuite on va copier un script qui va
nous permettre de démarrer tout notre
petit bordel là au démarrage de
l'application via la commande cm
démarrage de l'image du conteneur bon
voilà donc à quoi ça ressemble à tripoli
j'ai pas la bonne version
si non ce que tu peut sauvegarder mais
c'est sauvegarder tu as la bonne version
qu'est ce qui te manque j'ai pas le
start mon goût mais ses paroles voilà
ces banques risquent donc sa part est
gelée port donc notre application
donc il ya trois fonctions beh si les
terroristes c'est pas grave c'est pas un
peu avec continue voilà sont ensuite
appelés donc on appelle mon godet on ne
démarre en mode fort que pour pas qu'ils
soient bloquant donc on va le faire
tourner dans le background dans notre
image ont ensuite on prend le serveur on
pareil même chose on va le faire
démarrer en mode en mode non bloquant
avec un stern hu est à la fin et ensuite
à la fin on va démarrer engine x lui qui
sera en bloquant parce que si jamais il
n'y a rien qui est bloquant notre
containers va démarrer s'éteindre
aussitôt donc une génie qui va être le
point bloquant sur notre application
voilà donc c'est le moment de démarrer
comment on peut attaquer le nettoyage de
cette grosse image alors première règle
sûrement
la principale haut niveau au niveau des
docteurs file à la une très très bonne
pratique c'est de n'avoir qu'un seul
service par conteneurs donc ça veut dire
un seul service par part de coeur file
on va donc créer un docker file au congo
1 pour le serveur un pôle front-end est
également un autre pour le pour le proxy
engine x donc je vais commencer par
copier le docker file créer un
répertoire pour hautmont go on va
commencer par le plus simple coller des
dockers file ici donc je vais dans le
docker ça c'est le docteur faye
d'origine
je vais retirer tout ce qui fait
référence à mon goût plus clair et qu'on
met un petit peu mois plus de visibilité
tout à l'heure quand on va continuer à
partir de ce docteur file voilà j'ai
retiré l'installation j'ai laissé wget
parce qu'on en a besoin pour récupérer
note également et j'ai retiré la partie
de configuration du lieu du du storage
pour mango donc la lamal fichier tel
qu'il était je vais donc là par contre
faire l' inverse c'est à dire retirer
tout ce qui ne correspond pas à mon goût
donc ça j'en ai plus besoin ça j'en ai
plus besoin a pesé plus aujourd'hui une
tribune que j'ai rien de spécial à
exposer et il ya une chose que je vais
changer c'est
je vais démarrer je vais reprendre tout
simplement ce que j'avais dans dans
notre fichier de 10 mythes je vais
rappeler exactement la même commande
alors c'est un petit peu voyez ça peut
être plus d'intérêt il faut placer
chacun des paramètres de la commande
dans une eau string donc là on se
retrouve avec une installation alors je
vais je vais faire le ménage aussi si
alors jérémy c'est parce qu'il m'a fait
mon ami partout donc le scot ce domaine
je vais retirer sa voix là c'est bon et
donc voilà donc pour en revenir à notre
à notre docteur faye pour mango on a
quelque chose de simple apt-get day
t'installes de wget et tout ça bon le
truc qui est germi vous à part les
délégués apt-get update la commande elle
va jamais changer donc ce qui va se
passer c'est qu'on risque d' utile enfin
on va toujours utilisé le même layher
une fois qu'il aurait été vue d une fois
pour cette image
et si on venait je sais pas pour une
raison x ou y à changer notre version
ici de de mungo qu'on voulait installer
et ben on pourrait se retrouver en
décalage entre les versions qu'on a
récupéré avec l'update la toute première
fois on a créé l'image est ce qu'on
essaie d'installer on risque d'avoir des
problèmes à la création de mobiles de
notre image d'antan donc on va en fait
tout simplement tout simplement faire un
seul et même layher de tout ça va venir
j'y vais j'y vais voilà et donc là on
fait un seul d'ailleurs ça veut dire que
l'installation si jamais je change la
version de mongolie jeux spécifiques par
exemple une version
particulière pour mango serveurs et bah
on va retour offert on va faire le bate
à 2d des paquets à péter l'installer on
va tout jouer on est obligé de faire un
deuxième break parce que vous avez vu
qu'on passait par hypo spécifiques
voilà ça c'est pas mal un petit truc
qu'on peut faire on oublie la plupart du
temps c'est c'est de faire ça à la fin
voilà merci jérémy c'est de supprimer ce
qu'on a récupéré il y en a à la liste
les index a pété la récupère à peu près
20 mégas c'est un méga de plus dans
votre dans votre dans notre image au
final et dans votre conteneur donc ainsi
si vous tournez sur ses pas votre claude
provider préféré que et qui vous facture
la bande passante comme ça arrive
souvent et ben c'est un méga chaque fois
donc n'hésitez pas à nettoyer un peu
bon c'est pas mal tout ça on est un peu
mieux
mais en vrai on pourrait faire quelque
chose d'un peu plus un peu plus
intelligent c'est à dire que moi c'est
pas mon boulot d'installer de maintenir
mango est de savoir comment est-ce
qu'ils s'installent et tout donc je
pourrais simplifier mon voilà mon
install de mango voilà c'est fini
c'est mon docteur faye de mungo c'est à
dire qu'il ya une image officielle qui
est fourni par la communauté et des gens
dont c'est le métier de savoir installer
mango et de le faire proprement et de
gérer toutes les feuilles de sécu et
tout ça et tout ça et comme on n'a rien
fait spécifique dans notre config de
mango et ben je peux l'utiliser tel quel
donc je vais utiliser l'image officielle
mungo en version 4 0 de signal et ce
n'est pas la dernière
on pourrait prendre une 4,4 je croire
les dernières céder 4,4
donc voilà donc c'est pas mal pour pour
la extrait on like on l'extrait on a on
a je pense le docteur faye le plus
simple qui puisse exister c'est à dire
la récupération d'une image officielle
et l'utilisation directe de cette image
officielle permet aux serveurs bon on va
faire la même chose je vais le copier
jusqu'au pis le docteur faye dans le
serveur je vais continuer à nettoyer
celui-ci donc je n'ai plus besoin
d'installer java pareil j'ai pas besoin
de faire le bild
et puis donc sur sur cette partie là
j'ai dans le nord le dr fall be single
we dans le docteur faye du serveur
excusez moi je vais je vais garder que
ce qui m'intéresse c'est à dire que tout
ça ça m'intéresse pas je vais exposer un
port quand même mon serveur il tourne
sur le port 80 80 voilà et
il faut changer la donne en fait ouais
c'est un petit pas où je vais fermer le
docteur file pour paquin gêne
ok donc pareil que tout à l'heure il
faut repasser toutes les commandes
voilà merci jérémy ados ça va plus vite
voilà donc quelque chose de plus de plus
simple petit ghetto boy tu installes
d'openjdk copie du répertoire serveurs
alors ça c'était valable quand notre
docteur faye se trouvait la racine du
projet maintenant qu'on a qu'un docteur
faye spécifique pour le serveur on va
lui demander de copier le répertoire
courant puisqu'il se trouve ici donc ce
qui va m'intéresser c'est de récupérer
les sources
le pommeau tout ce qui se trouve dans le
répertoire courant et on va et puis
après on va tout simplement demandé à
mes veines de packagée l'application
donc donc c'est pas mal mais on peut
faire comme comme tout à l'heure à
savoir ne faire qu'un seul meilleur ici
faire un arm de tout ça et et on est
déjà un peu un peu plus plus propre bon
vous imaginez bien qu'en en vrai on a
quelque chose qui existe des aussi et on
peut tout simplement utiliser une image
openjdk officielle qui va s'occuper
d'installer proprement le le jdk et tout
ça donc là on se retrouve avec
uniquement ben copier
code source puis et puis vidé notre
package est et le run et voilà rené
nadja à la fin ça donne ça donnerait
quoi côté caen affronte jeremy alors
côté frondeur envers l'appareil on va
copier le gros gros gros docker failli
s'y mêlent ce qu'un disque dur et puis
on va le mettre dans le dans le dossier
client un donc je sais pas si ça se voit
avec de ton côté
je viens d'ouvrir un docteur faye qui se
trouve dans le dossier client
donc on va partir à refaire la même
chose sauf que deux pour le client c'est
un peu compliqué parce qu'on va avoir
besoin de notes pour bull dès notre
client de prendre a besoin des knicks
pour le servir et donc du coup je ne
sais pas trop enfin le sec mais qu'est
ce qu'il faut faire
est-ce que tu as je prends l'image de
montrouge installa une des knicks par
dessus où je prends une image dungeon x
et d'un installeur note par note plus
engine x men technique plus noble bah en
fait il ya quelques années
do kalenjin ils ont ajouté un truc qui
permet d'avoir plusieurs étapes dans le
docteur fall qui permet de dissocier
d'avoir par exemple de dr fall dans un
même docteur fait ça s'appelle le multi
stakes but donc c'est ce qu'on va faire
aujourd'hui on va faire deux styles
différents
un stage qui va permettre de guider
notre application et on va prendre le
résultat et le copier dans le state
d'après pour roman du rhône est donc ce
que ça ça permet ça permet de d'avoir
dans le stade final seulement les roses
les copies l'eren et tout ça les lakers
dont on a besoin
donc on va voir tout de suite comme ça
se passe donc au lieu de partir de
ubuntu est d'installer notes à la main
comme un cochon on va partir de l'image
officielle de nos dons à partir en lts
on va falloir besoin de copier la conf
engine x parce que pas besoin on va vite
notre client donc on encore dire clients
voire dire clients ont fait une termine
stable npn mobile copier ça dans le
répertoire va rejeter mais l'on n'en a
pas besoin parce qu'on n'a pas engine x
ici parler de tout ça on va être
intéressant c'est de travailler à partir
du répertoire courant exactement donc le
client ici on est plus valide parce
qu'on
travail dans le répertoire on va faire
notre commande docker de bild notre
image directement depuis le répertoire
cuir donc on va faire copie le
répertoire courant dont on va retenir
clients à partir de là on a notre note
fraude qui est bild est donc ici il faut
rajouter quelque chose pour définir le
sketch de dire halte bild
on va appeler ce stade la bile beurre et
on va le réutiliser après donc si on dit
from on va créer un nouveau stage donc
qui va être from engine x en crise et
d'image allemagne parce que pourquoi pas
et dans l'image
le bnd janyk star défaut sincère un
répertoire précis donc ce répertoire il
se trouve dans le var vvv htm
donc ce qu'on va faire c'est qu'on va
dire ok copie from donc là on va définir
quels stage à partir de castelli va
copier
donc c'était d'en vouloir dire clients'
et je vais même préparé le snippet et
voilà donc on fait qu pyfrom de culte
heures donc où est ce que ça se trouve
dans l'image blitzer ce qu'on veut
copier donc par défaut notre application
a généré un dossier bean et sans lemay
denrées user cheikh ndiaye mixage thème
est automatiquement engine x quand on
voit l'image
cette image là va démarrer and john
hicks et elle va servir ce dossier là et
donc c'est tout donc ça c'est bien mais
on peut encore faire mais pas au niveau
du biel parce que là au final quand vous
avez démarré votre image ou poulets
votre image
vous allez poulet toutes les touts les
layher de l'image
nd janyk et ensuite pour les un seul
layher qui contient votre pulled donc
vous avez une réduction énorme de ce que
vous aviez avant qu'yves copier tout net
copier tout les layher de notes ensuite
copier les sources et copier le résultat
donc comment on peut améliorer encore au
niveau au moment du bild on va passer
par
ce procès cela je vous ai expliqué tout
à l'heure de ce qu'on avait un mécanisme
de cacher le cacher ça valide si jamais
il ya des modifications dans ce que vous
avez copié ici dans un projet mode en
général on change moins souvent les
dépendances que le code source
donc si jamais un jour vous modifiez
votre code source en ajouter de
dépendance et que vont relancer bild
vous avez toujours repasser par le
endgame install ce qui est gourmand en
tennis de la planète quoi bon à
télécharger tous les modules à chaque
fois si vous n'êtes pas ce que ce don
savez peut-être pas besoin donc ce qu'on
va faire c'est qu'on va commencer dans
une première étape à faire le mpm ce
talent au début en copiant notre package
isen et le package
loc jason directement dans voir pu dire
lâche donc là on va copier ces deux
fichiers là les mecs dans leur
répertoire le bon club on va faire notre
frère npm install et ensuite on va
copier nos ressources dans le projet et
fernande bill donc ce que ça ça te
permet de faire c'est si jamais un jour
vous changez vos sources sans changer le
paquet de clopes
vous allez passer jusque là ça va être
tout le tout va être en cash et à partir
de ce moment là le cas je vais être
invalidés et donc vous avez juste faire
le npr ron beal donc ça va vous faire un
gain en temps de bill qui va être et non
donc ça on peut peut-être déjà commencé
par le guide est donc comment on va
faire ça
la perte war on va se mettre dans le
répertoire clair voilà et on va faire un
docker
puis il des montagnes docker death
practice du bipper classe g q si on
avait fait de la question
la plaie de lit on à bild ça oui j'ai
oublié le point parce qu'on est longue
et j'ai perdu le focus à faut lui donner
le
le contexte qui voit la courbe on dit
qu'on est dans le répertoire court donc
là ça on va commencer à du type tout ça
ça valait super vite
hop donc là on va télécharger l'image de
nonnes et donc ça va prendre comme un
petit peu de temps deux pendant ce temps
là je pense que guillaume tu peux
attaquer à la même chose pour lui
ouais parce que parce que mine de rien
comment dire c'est faisable
ouais ouais mais vannes va fonctionner
un peu de la même manière et puis et
puis parce que tu es ce que tu as fais
là en ayant une image qui contient
seulement engine x avec le code le code
wild est plutôt que d'avoir tout tout le
code source et tout ça dans ton image
finale on peut commencer par faire ça
c'est à dire qu'au lieu de faire tourner
de tourner notre conteneurs sur une
image openjdk avec tout le jdk et où
vous pourrez très bien tourné uniquement
avec avec j heureux donc faire ça comme
ceux ci et puis et puis voilà
se retrouver avec quelque chose qui est
à peu près du même genre c'est à dire
que là je vais me retrouver avec mon nom
je me suis trompé
voilà je me retrouve avec une giraud
uniquement donc une image beaucoup plus
petit qui va exposer le port 80 80 je
vais copier le résultat de mon but de
meeuwen à savoir donc aller chercher le
jard qui a été générée dans dans la
partie target de mon serveur la world xi
an
excusez moi j'ai l'habitude justice très
j'utilise lidge et du coup mais
raccourcie font pas la même chose sous
cette île voilà donc je copie se
chargent l'appel destructice et puis du
coup bah je lance je lance le jard
directement donc là on va se retrouver
avec une image qui je pense avec le jdk
et tout fait à peu près 500 meg images
heureuses time avec la giraud qui va
plus en faire que deux sens mais
quelques donc ouais on va diviser
facilement par deux le la taille du
conteneur qui va tourner sur vous sur
vos serveurs derrière donc c'est pas
mais au-delà de ça quand vous allez
démarrer sa sur votre serveur si jamais
dans votre cache de votre serveur
disposer déjà de l'image openjdk eleven
généraux slim et les parois télécharger
l'image où les électeurs seulement de
télécharger la différence ouais et donc
vous allez juste télécharger un ou deux
mais god liés à votre application
après ça dépend de la taille de rogers
évidemment donc voilà mais eux mais on
peut appliquer le même principe sur le
build comme toi mais venons en paix le
même mécanisme de fonctionnement c'est à
dire si si je vous dis pas fall alors
dans une image si je copie comme toi
tous dès le moindre changement je vais
invalidé le cache ici
et du coup je vais retélécharger la
planète aussi à chaque fois donc donc on
peut faire la même à savoir qu'on va on
va on va faire des choses un petit peu
plus intelligent donc définir not work
dire çà çà çà çà change pas on va copier
ce qui bouge le mois en premier donc là
on pourrait même faire un seul et même
annoncer un répertoire ça va être un peu
plus de layher 1 pour copier tout ce qui
se trouve dans le dans le répertoire nvn
plus la copie du binaire qu'on va
utiliser pour pour est en stand alone
pour pouvoir fermer appelé mes veines on
va copier le pommeau donc qui bouge
beaucoup moins que le comment dire le
source le source
et on va appeler en fait la récupération
des dépendances elle en faisant un bmw
dépendantes sing off line et donc là on
va voir arriver à ce niveau là tout un
cache de layher avec les dépendances
donc si vous modifiez le pommeau
forcément valait 1 re rappelé le fin de
la tde les téléchargements des
dépendances quoi mais mais si par contre
on modifie cole source
parce que là on peut copier nous que
enfin copier directement le source
tout ce qui se trouve dans les séries c
est ben on va uniquement arrivé ici
copier faire l'install forcément puisque
il faut il pour but d'aider les classes
à partir des des points java est là mais
voilà on peut aller encore un petit peu
plus loin c'est ce que vous allez voir
avec ces choses là c'est à dire que à ce
niveau là je fais j'exécute le jardon
dans la partie commentaires dans la
partie runtime mais hazard c'est ni plus
ni moins qu'une archives avec des choses
qui bougent plus ou moins donc dans la
partie puisque on va s'amuser à faire
c'est qu'au pied à créer un répertoire
dépendantes si dans target le définir
comme étant notre répertoire de travail
et on va demander à
à des zips et le jard en fait dans ce
répertoire des tendances et qu'est ce
qu'on va en faire tout ça eh ben on va
en faire un bon j'ai pas pressé de
choses excusez moi
voilà
et donc ce qu'on va en faire dans la
partie jr eux c'est qu'on va
ajouté une dépense alors j'avais oublié
fait sa petite blague 1,6 m 2
snippets fonctionne pas jérémy ne couche
pas si le peuple est en même temps que
moi donc je vais créer une
un argument qui va juste sauvé m'éviter
de retaper à chaque fois ou ordinaire
serveurs target dépendent aussi d'accord
et je vais faire des copies donc je vais
faire en fait un meilleur parent type de
choses que je vais copier donc les
choses qui bougent le moins ça va être
les libres que j'ai récupéré donc les
jarres de mes dépendances
donc je vais commencer par copier les
jarres de mes dépendances dans appli ben
je vais ensuite à les copier toutes mes
ressources fichiers de config et ou qui
vont se trouver dans nos méthodes et
ensuite je vais à les copier mon source
mes classes qui a qui ont changé ce qui
veut dire qu'en fait si je change que du
code source que je fais juste évoluer
mon application
eh bien je vais je vais passer tout ça
donc forcément ici je vais quand même
faire loin ce talent mais s'ils voient
qu'il ya pas de changement sur sur la
partie libé sur la partie mais tu as un
fait je vais aller jusqu'aux pieds et
uniquement ma partie ma partie mais mais
mais point classe est derrière au lieu
d'appeler le charge peut appeler comme
classiquement le juste le point d'entrée
magma la classe qui contient montmagny
pour démarrer mon serveur donc si on
bill de ça a forcément la première fois
comme pour jérémy il valait télécharger
toutes les dépendances avec meeuwen mai
donc là il récupère les deux images il
s'est aperçu qu'il y avait des images je
peux le l'agir eu plus le jdk et il va
télécharger tout ça est
et puis et puis on devrait pouvoir
utiliser tout ça mais du coup ça me fait
me poser une question jérémy c'est que
c'est super on a
un docker file pour la base de données
hors de coeur file pour le front tu un
docteur faye bon serveur mois avant
c'était tout dans le même truc ça
marchait ça parler tout seul
comment est-ce que ça va causer oui donc
avant c'était simple on démarrait juste
une image en avait un conteneur c'était
bon maintenant on va être obligé
d'orchestrés tout ça donc c'est là qu'on
va ajouter là une autre fonctionnalité
c'est 2,4 compose donc de keur contre
compose on ne définit via en définissant
un fichier qui s'appelle le dogger
composent prend il ya même dans lequel
vous définissez tous vos services
donc là on va définir un service pour le
proxy un service pour le client un
service pour j'ai encore un poil de
synchro entre l'instructeur et ce que
j'ai dit à graver à tout est bon là
c'est parti
pas grave c'était reparti sur le dakar
fait du sport tas fait d'accord voilà
bon moi ce que j'aime c'est pas grave on
va se dire et tout ça donc on va avoir
voir partir de là où ça devait être up
et hop donc on part avec des finissantes
tous nos services dont un client serveur
mango et donc pour pour pouvoir
orchestrer tout ça et dire ok quand mon
maroc et tarifs faut que six séances
lâché pierre sur le serveur et 6 ans
lâche faut que ces élections un client
on va rajouter un reverse proxy en
frontal qui va nous faire de tout c'est
trop direction donc ce rêveur ce proxy
on va l'appeler le service proxy on va
dire que l'image savez ce docker dastrac
tirait proxy moi j'aimerais déjà que tu
l'as but vide
en fait ce qu'on peut faire aussi c'est
à dire ok des matches de cette image là
elle se trouve dans le répertoire proxy
et quand vous allez faire docker
composent bild automatiquement ça va
vous bill 17 immeubles
donc cette image là on va la faire tout
de suite donc on va dans le répertoire
proxy qui n'est pas ouvert chez toi mais
que moi je devrais donc on avait avant
un rêveur proxy qui existait déjà
donc on avait déjà un fichier engines
points quand donc on va le garder pour
plus tard
on va faire on va créer un autre docteur
fait on va partir d'une base qui
s'appelle dungeon x et on va copier donc
notre fichier de config
on va le copier dans le bon endroit
parce que sinon c'est d'être chiant
indjai nyx.com on va le coffee dans le
tc engine x cela je trouve point des
soucis comme ça que ça donc ça cette
configuration là vous faire cet endroit
vous le trouverez sur le dos qu'ubs dans
la configuration des n'y a donc là
automatiquement on va créer notre image
avait en copiant le phishing confie donc
ça c'est cool
maintenant faut qu'on explique à notre
engine x comment rediriger les choses
donc il ya un truc magique dans docker
composent qui est que avec ces noms là
les noms des services automatiquement ça
intègre une résolution de dns ce qui
fait que dans notre engine x.com si on
veut que tout ce qui est en cela elle
paye soit redirigée vers notre serveur
je sais quoi j'ai encore un problème de
synchro c'est pas grave hot comme ça non
s'asseoir
voilà voilà voilà donc voilà ce qu'on va
avoir à la fin donc on a tous 15h il
paye ça va être redirigée vers explique
appui de principe des serveurs parce que
c'est non à une résolution dns en
interne sur le port 80 80 parce que le
serveur et des explosions pour 90 et on
va faire un autre raid direction un
autre os xi passe pour notre client qui
va rediriger vers klein sur le port 80
parce que je ne l'aï mixé pour 80 voilà
donc juste avec ça on va avoir notre
résolution de dernis
mais ça juste comme ça de but en blanc
ça va pas marcher parce que nos services
ne sont pas interconnectés pour qu'ils
puissent communiquer entre eux il faut
qu'on les lit via un système de network
donc on va dire que tout ce qui est de
accessible depuis l'internet accessible
depuis notre reverso xi on va le lier à
un auditoire qui s'appelle front thème
parce que c'est les frontaux de notre
application
donc ce qu'on fait c'est qu'on va bien
on va définir les nestois faisait notre
propre si on va dire qu'il fait partie
d'un réseau français pareil pour le
client
pareil pour le serbe et ensuite on va
faire un nouveau network pour le backend
pour que le bac est depuis ce connecter
le puissent communiquer avec le que
notre serveur puisse connectés
communiquer avec le la base longo ont
fait ça et donc là on voit qu'on a donné
trois bien bien dissocier on a celui ces
deux là qui peuvent communiquer entre
eux est ce que tu peux et ces trois là
qui peuvent communiquer entre on
pourrait encore découpé et dire que le
client il peut pas communiquer avec les
serveurs et même deux réseaux différents
mais c'est un peu aux verts qui est
ensuite de ensuite on a besoin de dire
ok il faut monter le proxy les ports du
proxy sur le post
donc pour ça on a un mot clé qui
s'appelle porte et qui va le dire ok on
va monter le port 80 90 postes donc de
notre machine sur le port 80 du
conteneur et voit ça suffit donc
maintenant ce qu'on va faire c'est qu'on
va essayer bild et
notre proxy sa marche donc on va faire
deux coeurs composent bild proxy là tout
seul ça va aller chercher de file donc
ça c'est bon ça marche maintenant on
peut démarrer tout mettre non attends là
il faut te le serveur tu prennes l'est
par contre c'est pas la bonne version
c'est bon alors donc donc et recompose
up est longue donc ça ça va démarrer
tous nos conteneurs ça ça va être
magique qui on va avoir du plaisir
est ce que tu peux pas croire dire si je
peux le faire voilà donc on voit que
tout démarre comme il faut rien mais
nous en voulaient pas si on n'utilise
pas les dernières versions ne pas
toujours fait ça n'ont pas réussi à se
connecter à la base de données alors est
ce que tu sais pourquoi
ouais ouais ouais parce que tu viens de
l'expliquer en fait comme on a de la
résolution dns
avant on avait tout dans un seul et même
conteneur donc pour se connecter à la
base de données on utilisait le cas lost
mais maintenant ils sont plus dans le
même conteneur donc je peux pas le faire
beaucoup normalement si j'ai bien suivi
tout ce que tu me racontes et si
j'appelle ça mungo et que là j'arrête et
que je redémarre devrait être capable
communiqué ah non non et non non excusez
moi un peu morbide va un peu vite en
besogne
voilà exactement alors tu heureux ce
qu'on pourrait faire vous avez vu j'ai
modifié uniquement un fichier de config
j'ai pas donc normalement je devrais pas
avoir à
retélécharger la planète et où quand je
vais refaire mon image là hop et ben
voilà ça a été super vite
il a vu que le matif sur up que tout a
été caché ce qu'il m'a bien sauvegarder
mon image d'en gach peut être donc en
gros ils auraient dû faire quand même le
installe et anne ou recopié la partie
mais tu as un fait les classes peu
importe les relations du ca refaisons un
composant à mungo le proxy qui a démarré
mon goût en train de démarrer ce prix
n'y tombe de son côté ouais mon goût à
des tec
action c'est là donc on va le porter à
20 4 euros donc alors attendez ce que je
vais faire c'est que vous m'accusiez de
tricher je vais ouvrir un deuxième
moi ce que je peux voir là le petit
cliché le coeur ps vous allez voir que
j'ai plusieurs conteneurs qui tourna il
en est un qui s'appelle devoxx foule de
que je vais arrêter qui est celui qui
tourne sur le port 80 80 c'est
l'ancienne version le groupe blue bulls
je vais l'arrêter je vais vous montrer
qu'il tente plus à l'est on me dit donc
ouais elle partage d'écran et souhaité
toulouse voilà pour ne plus avoir besoin
de retourner sur celui ci
hop et l'a donc lui il est plus présent
lui qui était pas présent et et et quand
elle est fraîche un plat on a bien tout
paraît donc si on utilise bien notre
application notre nouvelle application
avec nos quatre conteneurs qui toi super
donc voilà on est passé d'une image qui
faisait d'eux d'une seule image qui
faisait un giga cette idée en 5 secondes
à quatre petites images qui sont
essentiellement basées sur des images
originelles
enfin deux de profondeur officielle est
officiel la totalité des images fait 7
100 mégas le 2 1 gigahertz le bill times
en séquentiel donc fait la moitié du
temps qu'on avait à agent et en plus de
ça on a rajouté un niveau de sécurité
qui fait que avant si jamais il y avait
un attaquant qui voulez vous à quai il
est rentré dans votre conteneur fia le
engine x et c'était les prêts il était
déjà il avait déjà accès à votre base de
données
maintenant si l'attaquant essaye de
rentrer sur le pendjab x il faut encore
qu'ils attaquent votre springboard et
ensuite votre nom godet b pourront
accéder à votre vote data donc il y a
beaucoup plu
deux niveaux de sécurité quand on fait
un découpage puis ok juste juste pour
regarder un peu ce que ce que ça donne
en terme de taille
voilà on se retrouve avec un proxy qui
fait 21 méga on a un serveur 230 pour la
partie serveur le client fait 23 médias
et et l'image officielle mungo fait 425
mec donc en fait quand vous dis qu'on a
cinq cents et quelques mecs qui tourne
c'est parce qu'on a à mon goût l'image
officielle mango qui est extrêmement
lourde parce qu'en fait sinon on a on a
réduit de 1 giga 1 giga 3 l'a indiqué
kata qui a quasi 20,4 à 300-400 meg
or mon goût quoi donc voilà on a fait à
peu près de toi si si j'ai un petit truc
que j'ai oublié parce que je sais de
quoi je veux avoir vous parlez là bas je
vais le faire au moment où je vous en
parlerai donc ce qu'il faut retenir un
seul process par conteneurs ça a été
imaginé pour fonctionner comme ça même
si ça vous permet de faire tourner une
district du coup vous pouvez faire ce
que vous voulez essayer de garder bien
ça en tête
un conteneur c'est fait pour faire
tourner un service à la fois et pourrait
éviter il doit pas faire leur kerstrat
sion et contenir l'intégralité de votre
application utiliser les images
officielles
elles sont à jour elles sont maintenues
dès qu'il ya des failles de sécurité il
ya des mises à jour qui sont fournis il
ya tout un système de tags assez
puissant et du coup ça on vient au point
suivant il faut pas utiliser le tag à
latest en production pensez à la santé
mentale de vos apps
utiliser des tags bien nommé notamment
sur les images officielles quand vous
les poulets n'hésitez pas à prendre le
tag le plus précis possible parce que
ces tags
ils sont ils sont accessibles et vos up
sont généralement les outils qui vont
bien pour faire des recherches
imaginez vous avez un cluster cube qui
fait tourner je ne sais pas combien de
conteneurs ils ont besoin de retrouver
ceux qui tournent avec une alpine je
sais pas quoi parce qu'il ya une feuille
de sécu et bien ils vont pouvoir faire
des recherches par tag plus facilement
que si l'essai tout tourné avec avec
latest ils n'ont pas savoir quelle voie
est obligé d'aller creuser deux
peut-être même se connecter aux
conteneurs pour vérifier ce qui tourne
réellement quoi donc user et abuser des
tags et des labels parce qu'on en a pas
parlé mais on aussi possibilité de
rajouter des labels dans les temps les
deux choeurs file pour pour enrichir et
donné de ma formation en termes de
documentation donc n'hésitez pas à jouer
avec tout ça pour pour faciliter
l'exploitation derrière bien sûr le
multitouch guilde là la bonne pratique
c'est vraiment un stage pour buhl idée
construire votre application et un stage
qui va s'occuper uniquement durant times
a minima et je demande que veut en avoir
plein pouvait aller regarder dans dans
les ripoux docker sur les sur les
derniers projets les dernières sied
l'oeil et sur lesquels on a bossé tout
on a beaucoup beaucoup de multi cette
huile vous où on crée des stages pour
faire du biel du multi arche où ce genre
de choses
donc n'hésitez pas à les voir on peut
faire plein de choses intéressantes
pensez à nettoyer volleyeurs parce que
s'il voulait nettoyer pas et bat c c'est
de la taille d'image et de conteneurs
qui augmente ça veut donc dire que vous
allez vous retrouver avec
avec de la facturation de bande passante
si vous êtes si vous faites tourner et
vous appuyez sur le club
inutile donc de penser à travailler la
taille de vos images notamment en
nettoyant ce qui a nettoyé donc multi
cette build pour avoir un runtime le
plus fin possible et inclinable de ski
et le dernier point on a oublié de
parler ne pas tourner vos conteneurs ans
donc je vais revenir vite fait c'est
c'est en fait un si petit que ça c'est
même plutôt très simple le lait hier que
les hier de plus de stendhal les
balayeurs véhiculant c'est pas ça qui va
qui va faire augmenter la taille de
votre image ajoutez des groupes définir
le nom de votre groupe a ajouté un user
leurs ajouté le groupe
dire que ce que vous allez faire après
ce fait avec cet utilisateur là et
notamment l'exécution de l'hymne tripolt
et votre votre compte ne retournera avec
l'utilisateur que vous avez définies
quoi ok si on veut aller un peu plus
loin il y à une intro sur le blog de
docker sur les sur les sur les best
practice honda dans la doc un truc est
vraiment très très très très bien
pousser vous allez retrouver par ces
choses là ça semble le poste assez
récents qui est tiré de cette
présentation que vous allez retrouver la
même chose
peut-être si vous avez besoin
d'explications vous vous rappelez plus
des trucs vous allez retrouver les infos
dans ce blog post
et sinon à une vidéo de nous de nos
collègues américains hollandais qui ont
été faits landas de coeur comme 2019 et
une approche un peu différente de même
pratique avec peut-être une ou deux ans
plus un goût différent voilà on a
quelques petites questions à
alors si vous avez des questions mettez
les dans l'onglet question on va essayer
d'y répondre
donc j'ai répondu déjà à certaines
peut-être tu peux les relire et puis
alors est ce qu'on peut
on vous a mis le lien vers leur est
profitable où il ya toutes ces données
sur dans leurs réponses aux questions
alors il ya une question c'est mais du
coup le docteur faye pour mon gars est
il vraiment utile car on ruine une image
existante à l'identique donc ont repris
le pas on va juste faire une référence
parce qu'il n'y a pas de nouveaux layher
ya rien d'autre mais c'est vrai qu'on
pourrait juste utilisé dans notre ici
dans notre composent find it in y aller
exactement où 4.0 directionnelle parce
qu'il faut spécifier la version alors
autre question c'est si l'on précise la
version exacte d'une image de base on
risque de ne plus bénéficier des images
à jour de sécurité
alors le truc sic pour bénéficier des
mises à jour de toute façon il va
falloir vous rebellez vous n'allez pas
pouvoir swaps et l'image au dessus de
l'image de base comme ça on va devoir
remobiliser votre application
alors votre vote d'eau car fait il est
écrit à un instant t si vous voulez leur
bile des à l'instant t plus de moi si
jamais vous utilisez le tag les tests il
se peut que dans le late est athée plus
de moi ce soit pas la même version de
note par exemple passiez de l'échangé de
8 à l'image 1016 et donc du coup j'avais
plein de choses qui vont péter donc pour
ça si jamais vous voulez revivre des
aliments achetés plus de moi il faut que
vous spécifiez vos versions sinon ça
risque de péter ensuite via enfin il ya
certaines boîtes qui entre le dev et le
prod est la prod vous l'environnement de
beijing et l'environnement de prod ils
préfèrent remis le daily mail pour ce
qui est des mises à jour de sécurité il
sait mieux de spécifier à la main quelle
version vous voulez vous qu'ils petrak
aux fraudes qui traque de quelle version
vous voulez si par exemple vous avez
mungo 4,0 points quelque chose vous
pouvez utiliser la version 4.0 comme ça
des mises à jour de sécurité vous avez
toujours les décombres les avoir quand
vous allez au rebut le début de match et
ça va faire tout cela
autre question quelle différence entre
les commandes à des copies la halle est
celle là alors à death et commande un
peu magique qui est un peu
il faut éviter d'utiliser dans l'univers
d'eau car ils disent d'éviter d'utiliser
je sais pas trop plus pourquoi as tu
savais vous permet de dire ok 2 add tel
fichier qui se trouve à thé l'url dans
mon image ça ça peut être un problème
parce que le coeur je pense qu'il est
fait pas dans le contexte de bild mais à
l'extérieur je suis pas certain de ça
mais la chose dit qu' il faut éviter
d'utiliser ad'autant faire un multi
styles du bide de faire un run avec un
coeur le devant et c'était bien plus
propre
y at-il une limite au niveau de nombre
de couches layher a ajouté 5 et 6 sont
énormes je crois qu'il en a il y en a
une mais je serai plus dire de combien
faut regarder dans la doc
mais fin avant que vous l'atteignez bon
ben voilà c'est ça c'est pas dur à les
regarder et on utilisait l'image mango
aller voir combien il ya de meilleur sur
l'image bongo enfin voilà quoi
si vous commencez à être obligé d'avoir
autant de l'est hier que sur l'image
mango ça veut dire que vous faites
sûrement des choses qui sont pas liées
directement votre application et que
vous allez avoir plus que un service
dans votre conteneur la plupart du temps
on a une seule question ensuite qui et
quid des modes des fraudes sur le dans
le multi stakes alors que je réponde à
sa brève asie alors là par exemple on
est sur le docteur fall du serveur
disons que je peux rajouter un fichier 1
cm d ici qui s'appelle zij aval au
lendemain ces jarres enfin exécute mon
genre je sais plus comment fait je fais
pas déjà pardon et donc comment au
moment du build vous allez pouvoir faire
deux coeurs build acier pas dessus je
suis pas dedans c'est pas les krills en
dessous voilà allez pouvoir faire deux
cartes bild et dire moi - target et là
vous allez dire builder
et ça ça va vous guider votre image
jusqu'ici
et donc quand vous allez faire un docker
ron vous à les exécuter cette commande
là en mode dave
enfin vous allez exécuter cette commande
là ça vous permet de ne pas avoir toute
la phase d'optimisation avec le gir et
si jamais vous voulez faire un docteur
ron - - unité pour avec un badge
derrière pour pouvoir monter dans le
conteneur bas vous allez être dans le
conteneur de bild et du coup faire que
ça réponde vraiment méchante et j'espère
que ça répond à ta vision que vous
pouvez rajouter vos volumes
enfin voilà quoi comme d'habitude quoi
et pareil je vous pouvez utiliser un
système d'arguments dire arguments argue
target ici et dire dave et ensuite dire
from je sais pas mon image ici vous
utilisez la variable que vous venez de
définir et donc vous pouvez injecté au
moment du bild quelle est l'image dans
laquelle vous voulez aller au final
enfin il ya tout un système comme ça de
d'orientation de 2002 votre image qui
vous permet d'avoir des bébés des
mécanismes bien trop alors et
pouvez-vous nous attentons me pardonne
moi vous montrer encore une fois la suze
une route donc aller surligner l'a donc
l'idée c'est de faire un run qui veut
donc ni plus ni moins qu'une commande
shell où on va ajouter le groupe java et
on va faire 1 à 12 heures derrière 12
heures qui s'appelle j'avais user qu'on
va associer au groupe java qu'on aura
défini juste avant et en commande et
explicite docteur faye l'on va faire
user et on va appeler cela va user qu'on
a créés donc voilà c'est ni plus ni moi
ça c'est créer la bonne pratique vous
n'êtes pas obligé de créer du groupe
vous pouvez créer juste un user ivoire
groupe par défaut tous les bonnes
pratiques qui veulent que il est mieux
de créer le groupe
et de rajouter votre user à un groupe
et ensuite voulu définissez en faisant
usage java user et les commandes qui
vont s'exécuter derrière sont faites
dans le contexte de cet utilisateur à la
galigaï qui demandent je remarque que
vous utilisez deux coeurs composent 3
avez vous des solutions conseils
destructif pour remplacer la fonction ex
de docker composent 2 alors non pas paul
a directement par contre ce que je peux
vous dire c'est que ça maintenant ça
fonctionne vous n'êtes plus obligé de
spécifier la version alors il faut
savoir que docker composent s'il ya deux
choses il ya le la command line fait
part de coeur en python et de l'autre
côté il ya le format de fichier
le compost qui recompose paille et toute
la partie fichiers formate format et
spécifications a été sorti dans un cpe
une fondation et était complètement
sorti du projet est accessible depuis
depuis quito ben c'est en train
d'évoluer énormément avec d'autres
d'autres sociétés cadeaux coeur amazon
microsoft qui sont pas mal avancé il ya
là le mainteneur de compose avec un cac
qui travaille aussi sur le sujet donc la
spécification en train d'évoluer
énormément et donc si c'est des choses
que dont vous avez besoin
il faut pas hésiter à ouvrir des if you
directement là dessus pour pouvoir
rajouter ces demandes je sais pas là je
vais pas vous dire c'est pris en compte
c'est pas pris en compte mais j'irai à
pile ou face quoi que je préfère vous
dire allez regarder dans donc ça
s'appelle compo spec dans les rivaux de
compos spec il ya tout l'aspect qu et et
vous allez voir est donc évidemment
docker composent évolue donc le la
partie pitt ont évolué en même temps que
l'aspect qui évolue on est généralement
l'implémentation de référence du truc
donc on essaye d'être le plus à jour
possible vis-à-vis de la spec est un
petit peu au plus haut niveau du extends
pour en avoir discuté avec des hawks
c'est un peu mauvaise pratique parce que
ça va essayer de démarrer tous les trucs
dans le bon ordre
sauf que en production vous avez jamais
avoir tous vos services qui vont tout va
jamais bien se passer
il faut toujours partir du cas où
peut-être vous n'allez pas avoir accès à
votre bébé donc votre application et
réagissent comme il faut donc le mieux
c'est de ne pas l'utiliser tout va être
démarrés en vrac en même temps votre
application va devoir se doit
potentiellement attendre un timeout
jusqu'à ce qu'ils aient la connexion
c'est ainsi la pas la connexion
redémarre elle ci a besoin
donc ça c'est un peu au niveau de
l'application de le prendre en compte et
pas au niveau de leurs fins de ce mini
orchestrateur qui est au coeur compose
donc de ça il ya une autre question qui
est qu est la différence entre deux
coeurs composer les orchestrateurs de
coeur composent à l'origine c'est fait
pour une machine c'est votre poste par
votre poste nouveau la machine en prod
une seule machine un orchestrateur c'est
un n machine c'est vous démarrez tout ça
dans sur le cloud sur le réseau sur
plusieurs machines
mais il ya des choses alors il ya des
choses qui évoluent c'est entre autres
pour ça que l'aspect qui est sorti on a
bien c'est pas la spec de
l'implémentation c'est que on a on a
maintenant une
c'est un petit peu perturbant jeu je
vais je voudrais pas vous permet le
coeur composent c'est avec un lâche
comme vous avez peut-être remarqué on
appelle les recompose le billard python
c'est avec un dash et maintenant on a on
à docker composent kiki amené à
remplacer à terme composent qui lui va
permettre de faire la même chose mais en
utilisant les alors ce qu'on appelle les
contextes docker et on peut commencer à
définir des compteurs des contextes
essiane donc azur containers instance
est ici s
ces détails lors le les instances de
conteneurs de chez amazon et donc vous
est maintenant capable de faire tourner
sa donc votre composent file sur le
cloud et les ailes et les conteneurs
sont répartis sur différentes instances
évidemment la cible c'est d'arriver vers
d'utiliser des compos strasbourg pour
des positions du cube pour éviter en
fait pour vous puissiez utiliser votre
version composent file local
jusqu en production voilà la question
warcq work in progress voilà si vous
avez d'autres questions n'hésitez pas à
nous contacter sur twitter par exemple
ne dispos et et à ouvrir des fichiers ou
sur les aires hypo en fonction des
problèmes et où vous pouvez rencontrer
tous voila voila merci beaucoup
guillot merci beaucoup jérémy c'était
très intéressant est ce que est ce que 2
de ceux qui sont qui sont là vous avez
encore d'autres questions ou deux points
éventuellement non ça a l'air bon ça a
l'air bon je partageais mon écran
là et bien écoutez merci à tous d'avoir
participé à ce mal d'académie mais a
surtout à jérémy et guillaume d'avoir
d'avoir donné de leur temps pour cette
mode académie c'était super intéressant
et très complet j'ai vu qu'il y avait eu
beaucoup de questions et beaucoup de
personnes qui avaient réagi donc c'est
vraiment top
si vous voulez voir d'autres malte
academy sur des sujets sur d'autres
sujets n'hésitez pas allez jeter un coup
d'oeil sur nos titres matt academy.com
comme est affiché à l'écran puis si vous
souhaitez faire comme jérémy et comme
guillaume est animée de matt academy
n'hésitez pas non plus à cliquer sur le
bouton devenir speaker pour nous envoyer
vos idées de vos idées de sujets de
maths academy et ne vous inquiétez pas
si vous n'avez pas vu le début cette
matt academy vous pourrez tout à fait la
revoir en replay elle sera disponible
sur le site malte academy voilà mes
écoutes et merci encore à jérémy et à
guillaume adjutor à bientôt pour une
prochaine date academy et merci au
revoir