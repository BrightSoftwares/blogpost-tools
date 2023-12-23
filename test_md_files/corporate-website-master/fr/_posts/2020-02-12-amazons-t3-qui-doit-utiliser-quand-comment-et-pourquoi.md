---
layout: flexstart-blog-single
title: "Amazon’s T3 – Qui peut l'utiliser, quand, comment et pourquoi?"
author: full
lang: fr
ref: aws_t3_usage
categories: [aws]
description: "T2 n'est plus à la mode, à cause de son CPU throttling au dessus de la baseline. Amazon l'a mis en version unlimited – avec une option pour faire du CPU throtling avec du crédit."
image: "https://sergio.afanou.com/assets/images/image-midres-6.jpg"
seo:
  links: [ "https://www.wikidata.org/wiki/Q456157" ]
---

Amazon vient d'annoncer le 21 août [la troisième génération de la série T - T3](https://aws.amazon.com/blogs/aws/new-t3-instances-burstable-cost-effective-performance/). Cet article examinera :

* Comment fonctionnent les T3 ?
* La classe T3 est-elle un type d'instance à utiliser dans votre liste d'arsenal EC2 ?
* Si oui, quand est-il judicieux d'activer T3 ?

La norme T2 a été très mal comprise en raison de la limitation de son processeur par rapport à la ligne de base, à laquelle Amazon a introduit [T2 illimité](https://www.cloudsqueeze.ai/amazons-t2-unlimited-who-should-use-it-when-how- and-the-why/index.html) - avec un moyen de surmonter la limitation du processeur avec un mécanisme de paiement pour le crédit pendant la période où l'EC2 a dépassé la ligne de base. La nouvelle introduction - [T3, est un T2 illimité](https://aws.amazon.com/ec2/instance-types/t3/) avec quelques variations subtiles et a des cas d'utilisation dans votre arsenal EC2.

Chaque instance T3 dispose d'un ensemble fixe de mémoire et d'un seuil de référence spécifié par AWS. Comparons certains des attributs des classes T3 avec ceux de T2. Remarquez comment le nombre de vCPU indiqués aux extrémités inférieures a doublé pour t3.nano, t3.micro, t3.small par rapport à t2.nano, t2.micro et t2.small. Le prix une fois que vous dépassez le seuil de base est de 0,05 $ / heure CPU en cas d'explosion au-dessus de la ligne de base. Ainsi, alors qu'AWS peut faire une réclamation sans précédent pour le t3.nano peut fonctionner aussi bas que 3,796 $ / mois, inhérent à l'éclatement au-dessus de la ligne de base, il y a des surprises de prix inattendues pour l'utilisateur naïf, qui n'a pas compris comment fonctionne la classe T3.


![Comparaison des types T3 et T2](https://www.cloudsqueeze.ai/wp-content/uploads/2018/08/t31.png)

Les caractéristiques de base du T3 sont similaires à celles du T2 illimité à bien des égards. L'utilisation du processeur est mesurée au niveau de la milliseconde par AWS pour ce type d'instance. Lorsque votre système de classe T3 fonctionne à des niveaux inférieurs à la ligne de base pour cet EC2, il gagne des crédits à un taux établi ; au départ, aucun crédit n'est gagné ni épuisé ; à des seuils supérieurs à la ligne de base, vous payez les crédits en fonction du nombre de vCPU pour ce type d'instance.



![Comment fonctionnent les crédits T3](https://www.cloudsqueeze.ai/wp-content/uploads/2018/08/t32.png)

T3.nano peut être une alternative proposée au bas du marché de l'hébergement où les sites WordPress sont hébergés sur des plateformes partagées pour 5 à 10 $ / mois. Si l'utilisation est d'une poignée de visiteurs par jour, cela peut être suffisant. Si vous avez un processus par lots ou un processus incontrôlable et que vous dépassez les crédits de base sur 2 vCPU, c'est là que les crédits empruntés et le paiement entrent en jeu.

Un crédit CPU équivaut à un vCPU fonctionnant à 100 % d'utilisation pendant une minute. Par exemple, un crédit CPU équivaut à un vCPU fonctionnant à 50 % d'utilisation pendant deux minutes, ou à deux vCPU fonctionnant à 25 % d'utilisation pendant deux minutes. La classe T3 gagne des crédits lorsqu'elle fonctionne en dessous de la ligne de base avec un niveau de crédit maximum qui s'accumule jusqu'à 7 jours, contrairement à T2 illimité qui semble avoir une limite quotidienne.

![Graphique de référence T3](https://www.cloudsqueeze.ai/wp-content/uploads/2018/08/t33.png)

Les crédits CPU sont facturés à 0,05 $ par heure vCPU pour Linux et à 0,096 $ par heure vCPU pour Windows. C'est là que le nouveau client T3.nano plus petit peut trouver une surprise dans sa facture.

Oui, le t3.nano ne coûte que 3,796 $ / mois (sans stockage EBS ni coût IP), mais si l'on parvenait à exécuter cette instance à 100 % d'utilisation pendant un mois, la facture pourrait atteindre 3,976 $ + (0,05 $ \* 2 \* 24 \* 30) = 75,976 $ / mois. Si vous n'êtes pas en mesure de surveiller les crédits gagnés, la classe T3 inférieure fonctionnant en mode illimité attirera forcément quelques personnes avec des factures imprévues sur les attentes fixées à 4 $ / mois. À ces prix surprise de 75 $ / mois, il existe de bien meilleurs types d'instances comme le C5.large qui a 2 vCPU et 4 Gio (8 fois plus de mémoire que le T3.nano) à 61 $ / mois (Linux, US-East-1 Région).

> Un coût de 4 $/mois pour T3.nano peut atteindre 76 $/mois, alors que le C5.large a 8 fois plus de mémoire que T3.nano peut fonctionner à 61 $/mois.

La norme T2, d'autre part, a la restriction similaire à si un serveur Web est hébergé avec des milliers d'autres, que les performances sont simplement limitées. L'activation de T2 illimité dans de telles situations présente l'avantage de savoir que votre application n'est pas limitée si vous obtenez une rafale soudaine et inattendue.

En supprimant le facteur de surprise pour le T3 aux plus petites extrémités du spectre, aux seuils de mémoire de 4, 8, 16, 32 Gio, il y a de bonnes performances de prix pour cette classe T3 en général. La grande majorité de l'analyse des déploiements de cloud public que nous avons vu, ce qu'Amazon aurait probablement fait aussi, ils sauraient que la plupart des instances EC2 fonctionnent bien en dessous de ces seuils de base de 30 à 40 %. Il existe des modèles d'utilisation quotidiens typiques (type 9-5) et des modèles d'utilisation du week-end (faibles par rapport aux jours de semaine) pour les déploiements de cloud public et de cloud général pour une myriade de raisons pour lesquelles T3 a une meilleure proposition de valeur dans de nombreux cas d'utilisation.

Pour comprendre la proposition de valeur, examinons le coût/vCPU de la mémoire pour Linux et Microsoft. Pour ces prix, j'utilise les prix à cette date pour la région US-East-1, et pour la plupart, les ratios de prix relatifs sont valables dans toutes les régions :


![Comparaison des prix T3](https://www.cloudsqueeze.ai/wp-content/uploads/2018/08/t34.png)

Notez d'abord le prix du crédit en rafale - il s'agit du prix des crédits CPU empruntés à Amazon lorsque les crédits gagnés sont épuisés. À l'extrémité inférieure du spectre des Go (moins de 4 Go), les choix dans les autres classes sont limités. Les options disponibles sont un ancien système de classe M (m1.small) et une classe C5 qui ont des prix plus élevés. Si vos besoins en mémoire sont de 0,5, 1, 2 Go et que votre charge de travail peut rester en grande partie dans la plage de référence, T2 ou T3 sont de bons choix. Si la prévisibilité des prix est plus importante que la performance, envisagez la norme T2. Si les performances sont plus importantes que le prix T2 illimité et T3 peuvent être bons à court terme. Si vous épuisez constamment les crédits gagnés et empruntez des crédits pour maintenir les performances de votre système, alors M1.small (1 vCPU, 1,7 Go) et C5.large (2 vCPU, 4 Go) deviennent des systèmes à considérer sur le T3 ou le T2 illimité.


> Si la prévisibilité des prix est plus importante que les performances pour une application nécessitant 0,5, 1, 2 Go de mémoire, envisagez la norme T2. Si les performances sont importantes par rapport au prix et que vous êtes relativement certain que l'utilisation est bien inférieure à la ligne de base de 20 %, envisagez T3 ou T2 illimité. Si les performances sont importantes par rapport à la variabilité des prix, envisagez m1.small ou c5.large.



Le prix des crédits en rafale Microsoft est de 0,096 $/heure vCPU. Il a des modèles similaires à Unix dans la mesure où la classe T3 de moins de 4 Go de mémoire est un excellent choix.

![Comparaison des prix T3 ](https://www.cloudsqueeze.ai/wp-content/uploads/2018/08/t35.png)

Dans les deux, les graphiques ci-dessus notent les clusters autour de 4 Go, 8 Go, 16 Go et 32 ​​​​Go. Les offres de clusters proches proviennent des systèmes C5 et M5 de nouvelle génération. Examinons ces prix les uns par rapport aux autres et incluons une option convertible sans paiement initial d'un an. La raison d'envisager le type de réservation convertible est qu'il vous donne plus de choix - par exemple, si pendant la durée de l'accord, le type T4 apparaît, ce qui est probablement à un coût bien inférieur avec une amélioration des performances - cela a à voir avec la nature de la technologie ! Si vous regardez les classes de première génération ou même de deuxième génération de C, M et si vous avez acheté la réservation standard de 3 ans, par rapport aux économies de coûts sur C5, M5 - vous serez probablement mieux loti sur les types de systèmes de classe plus récents grâce aux améliorations de performances et les économies de coûts inhérentes à ces systèmes de nouvelle génération.

> Le type de réservation convertible vous donne plus de choix que la réservation standard pour changer à mesure que les changements technologiques se produisent dans le cloud.

![Comparaison des prix C, M et T3](https://www.cloudsqueeze.ai/wp-content/uploads/2018/08/t36.png)

Au seuil de 4 Go, si votre utilisation de base se situe dans la plage de 20 %, alors T3 est un excellent choix. Dans la classe C, le C5.large est peut-être le seul choix car dans la classe M5, l'extrémité la plus basse commence à 8 Go de mémoire. Si votre instance T3 commence à emprunter fréquemment des crédits, les performances de la classe C5 s'avèrent être presque le double de l'augmentation de prix (103%).

> Au niveau de la mémoire de 4 Go, les économies de coûts que vous obtenez de T3.medium sont importantes même si vous explosez occasionnellement par rapport à un type d'instance C5, qui est la combinaison de valeur de performance la plus proche.


À 8,16, 32 Go de mémoire, si vous êtes relativement certain que vos performances de base se situent dans la plage 30-40% T3, c'est un bon pari. Mais avec C5 et M5 fonctionnant à 1,6% de plus que le prix T3 lorsque vous obtenez des fractions de CPU, ce n'est pas si attrayant! La plupart des systèmes déployés dans le cloud AWS maintiennent rarement une utilisation constante de 30 à 40 % sur une période de 24 heures. Cependant, si vous n'avez pas surveillé activement les modèles d'utilisation du processeur et que les performances sont importantes, le risque avec T3 et illimité activé par défaut est la possibilité d'un élément de coût surprise par rapport à un type d'instance C5 ou M5 qui a de bonnes performances globales et valeur.

> Avec des niveaux d'utilisation de la mémoire de 8, 16 et 32 ​​Go, la famille T3 n'est pas un choix attrayant si la référence d'utilisation de votre application dépasse les niveaux de 30 à 40 %. La plupart des applications maintiennent rarement ces seuils de manière constante sur une période de 24 heures. Si les performances sont importantes à ces seuils de mémoire, les systèmes C5 et M5 offrent une bonne proposition de valeur globale par rapport à la famille T3.


Sur les lecteurs ont posté une réponse à l'enquête sur les moyens de surmonter ce paramètre par défaut et sur la façon d'exécuter T3 en mode standard antérieur que je voudrais aborder en tant qu'addendum à ce message initial. Oui, l'exécution d'un T3 en mode standard surmonte ce problème potentiel d'une facture inattendue lorsque les crédits nécessaires sont facturés. L'inconvénient de ceci est la surprise des coûts si vous ne regardez pas les journaux CloudWatch sur les crédits CPU gagnés, consommés spécifiques à la classe T2/T3.

Dans la console EC2, vous devriez trouver un paramètre de modification T2/T3 illimité.
![Où changer T3 en standard](https://www.cloudsqueeze.ai/wp-content/uploads/2018/08/T3a1.png)
La valeur par défaut sur T3 est l'état activé qui peut être basculé facilement :

![basculer les paramètres T3](https://www.cloudsqueeze.ai/wp-content/uploads/2018/08/T3A2.png)

![où changer T3](https://www.cloudsqueeze.ai/wp-content/uploads/2018/08/T3A3.png)
Si vous changez une instance T2 en T3, assurez-vous que l'exigence ENA est satisfaite sur le T3. Ceci est référencé plus en détail dans les [tutoriels AWS](https://www.cloudsqueeze.ai/aws-tutorials/index.html) sur [comment modifier un type d'instance EC2](https://www.cloudsqueeze. ai/how-to-change-an-aws-ec2-instance-type-a-step-by-step-guide/index.html). Vous pouvez changer la plupart des types d'instance en classe T, et plus précisément [comment changer un type d'instance en T2](https://www.cloudsqueeze.ai/how-to-change-to-t2-unlimited-for-an- aws-ec2-instance-type/index.html) est décrit et les étapes sont presque les mêmes, il suffit de sélectionner T3. Si vous essayez de modifier le type d'instance sans que cette exigence ENA soit remplie, vous verrez une erreur comme celle-ci ci-dessous (ne paniquez pas) :
![erreur avec T3](https://www.cloudsqueeze.ai/wp-content/uploads/2018/08/T3A4.png)


# Conclusion

En résumé, la famille d'instances T3 avec son comportement par défaut similaire à celui de T2 illimité est susceptible de surprendre ceux qui n'ont pas examiné les caractéristiques d'utilisation de la mémoire et du processeur par les applications. Si vous utilisez T3, assurez-vous de surveiller activement l'utilisation du processeur, les crédits gagnés et les crédits empruntés auprès de CloudWatch. Le type de norme T2 peut être quelque chose à considérer lorsque la limitation du processeur est un moyen acceptable de limiter les anomalies d'application - par exemple, les boucles de code rouge run away qui consomment le processeur de manière inattendue ou certaines installations de logiciels malveillants modifient la façon dont le processeur est consommé. Si les performances sont relativement importantes, les familles C5 et M5 peuvent être de meilleurs choix par rapport à la nouvelle classe T3. La classe T3, bien qu'elle ait un prix bas, le comportement par défaut des crédits en rafale illimités avec plus de vCPU sur T2 a le potentiel de surprendre quelqu'un qui s'attend à ce qu'une facture de 4 $/mois se transforme en 76 $/mois (le système Windows coûte plus cher que Linux ).

