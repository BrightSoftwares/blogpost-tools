---
ToReview: true
author: full
categories:
  - productivity
date: 2022-06-28
description: "Que se passe-t-il lorsque Windows commence à lancer des messages d'erreur ennuyeux à chaque fois que vous essayez de lancer le système d'exploitation ? Si vous essayez de vous connecter pour la journée et que vous travaillez réellement dans les délais critiques que vous avez, et que vous n'avez pas vraiment de service informatique pour vous aider, c'est probablement le pire endroit où se trouver."
image: https://res.cloudinary.com/brightsoftwares/image/upload/t_BSBlogImage/v1656238010/pexels-engin-akyurt-2952661_qseeuf.jpg
lang: fr
layout: flexstart-blog-single
pretified: false
ref: recentosupdate_1247
title: "Windows ne démarre pas correctement après une mise à jour récente du système d'exploitation"
---

Que se passe-t-il lorsque Windows commence à lancer des messages d'erreur ennuyeux à chaque fois que vous essayez de lancer le système d'exploitation ? Si vous essayez de vous connecter pour la journée et que vous travaillez réellement dans les délais critiques que vous avez, et que vous n'avez pas vraiment de service informatique pour vous aider, c'est probablement le pire endroit où se trouver.

Puisque nous sommes tous coincés - ou serons bientôt coincés - dans nos maisons et nos appartements dans un avenir prévisible,

### La question:

> _J'ai un bureau Windows 10. Il y a plusieurs semaines, Windows a fait une mise à jour et plusieurs jours plus tard, lorsque j'ai allumé, j'ai reçu le message "Windows ne s'est pas chargé correctement" sur un écran bleu avec plusieurs options. Ceux que j'ai essayés ne fonctionnaient pas bien, jusqu'à ce que je trouve l'option "Revenir à une date précédente". Cela a bien fonctionné. L'ordinateur s'est rallumé et a fonctionné normalement. Malheureusement, je reçois toujours l'écran Windows qui ne se chargeait pas correctement tous les plusieurs jours. J'utilise Windows 10 sur un Mac. Je pensais effacer complètement les fenêtres puis les recharger. Peut-être ai-je un virus ou un bug ? Merci !!_

### L'humble réponse :

Pour ce que ça vaut, vous n'êtes pas seul sur celui-ci. Microsoft a récemment rencontré des problèmes avec les mises à jour de Windows 10, ce qui peut parfois poser plus de problèmes aux utilisateurs qu'ils ne peuvent en résoudre. Il est possible que vous soyez dans ce camp, mais la bonne nouvelle est qu'il est très, très peu probable que vous ayez été touché par un virus ou un logiciel malveillant sommaire. C'est juste un problème Windows - pas très apaisant à entendre lorsque vous le rencontrez, j'en suis sûr, mais au moins un peu plus réconfortant que "Votre système est infecté" (j'espère).

De manière générale, j'aime abandonner le navire au premier signe de problème qui me prendrait probablement plus de temps à résoudre - avec des résultats mitigés - qu'il ne me faudrait pour réinstaller Windows et toutes mes applications. Je soupçonne que ce pourrait être le cas ici. Et puisque vous êtes Boot Camping dans Windows sur votre Mac, je suis moins gêné de vous mettre un peu hors service, car vous aurez toujours macOS à utiliser si vous devez absolument faire quelque chose sur votre ordinateur.

Avant de passer au nucléaire, essayons quelques trucs. Tout d'abord, si vous pouvez démarrer _into_ Windows - et il semble que vous le puissiez - je ne suis pas sûr qu'il y ait quoi que ce soit que vous puissiez désinstaller qui vous aidera. La dernière mise à jour majeure de Windows 10 qui vous aurait probablement affecté était la grande mise à jour de 1909 de [novembre](https://support.microsoft.com/en-us/help/4529964/windows-10-update-history). Il y a eu un certain nombre de mises à jour au coup par coup depuis lors, mais je ne peux pas penser à une qui a été particulièrement problématique. Oh, sauf pour KB4535996, que même Microsoft a suggéré aux utilisateurs de désinstaller.

Alors, commençons par là. Lancez **Windows Update**, cliquez sur **Afficher l'historique des mises à jour**, cliquez sur **Désinstaller les mises à jour** et regardez si vous pouvez désinstaller KB4535996. Si vous le pouvez, super ! Sinon, il y a cette technique de dépannage.

Pendant que vous êtes ici, vérifiez peut-être s'il existe des mises à jour Windows supplémentaires que vous pouvez installer. C'est long, mais peut-être que quelque chose est arrivé qui pourrait résoudre les problèmes que votre installation Windows a du mal à gérer. Et puisque vous utilisez Boot Camp pour exécuter Windows sur votre Mac, lancez Apple Software Update et assurez-vous qu'il n'y a pas de nouveaux pilotes ou mises à jour à installer.

###### Comment faire fonctionner rapidement et efficacement un ancien PC tout-en-un ?

Je suis toujours ravi de recevoir des lettres "aidez-moi avec un problème technique" dans ma boîte de réception, et j'ai eu…

Enfin, essayez de réinstaller les [pilotes de support Windows](https://support.apple.com/en-us/HT204923) de Boot Camp, qui pourraient résoudre comme par magie tout ce qui provoque l'écran bleu de votre système au lancement. Il n'y a aucune garantie que cela résoudra les choses, mais cela vaut la peine d'explorer avant de prendre des mesures plus drastiques.

Lorsque vous êtes sous Windows, vous pouvez également ouvrir une invite de commande élevée (recherchez "Invite de commandes" dans le menu Démarrer, cliquez dessus avec le bouton droit de la souris et sélectionnez "Exécuter en tant qu'administrateur"). À partir de là, essayez d'exécuter un simple "chkdsk / f" pour vous conformer, il n'y a aucun problème avec votre système de fichiers. Vous pouvez également essayer "chkdsk /r /f" pour une analyse beaucoup plus approfondie et un processus de correction, mais cela prendra beaucoup plus de temps. Si votre disque dur tombe en panne et que c'est la raison de vos problèmes Windows, il est également possible que vous n'obteniez aucune information supplémentaire de chkdsk. Vous voudrez utiliser [d'autres techniques](https://lifehacker.com/how-to-check-if-your-hard-drive-is-failing-1835065626) pour confirmer que tout va bien (ou que vous vous dirigez vers un sinistre).

Vous pouvez également exécuter « sfc /verifyonly » suivi de « sfc /scannow » dans la même invite de commande élevée. Si la première commande a trouvé une corruption dans vos fichiers système Windows, la deuxième commande devrait les réparer.

Une fois que vous avez terminé, envisagez de lancer l'utilitaire de résolution des problèmes de Windows. Ouvrez le panneau de configuration de la vieille école (via le menu Démarrer) et sélectionnez Dépannage. Ensuite, cliquez sur "Résoudre les problèmes avec Windows Update" et voyez ce que l'utilitaire trouve (le cas échéant !)

Enfin, cliquez sur votre menu Démarrer, cliquez sur l'icône d'alimentation, maintenez la touche Maj enfoncée de votre clavier et cliquez sur Redémarrer. Cela devrait vous démarrer dans le [démarrage avancé] de Windows 10 (https://www.dell.com/support/article/en-us/sln317102/booting-to-the-advanced-startup-options-menu-in-windows- 10?lang=fr) menu des options. Cliquez sur Dépannage, cliquez sur Options avancées et essayez d'utiliser l'option de réparation du démarrage pour voir si cela peut résoudre votre problème Windows.

###### Comment assurer le bon fonctionnement de votre ancien ordinateur de bureau ?

Quand votre PC de bureau vieillit, mais que vous n’avez pas le cœur (ni le budget) pour le remplacer, il y a…

Si tout le reste échoue, un effacement et une restauration pourraient être votre meilleure option. Enregistrez tous vos fichiers critiques de Windows 10 sur un lecteur flash ou [stockage cloud] (https://lifehacker.com/google-one-is-now-open-for-everyone-but-is-it-a-good-d -1826049257), puis lancez macOS et utilisez Boot Camp Assistant pour [supprimer votre système d'exploitation Windows](https://support.apple.com/guide/bootcamp-assistant/remove-windows-from-your-mac-using-boot- camp-bcmp59c41c31/mac). Utilisez [Media Creation Tool](https://www.microsoft.com/en-us/software-download/windows10) de Microsoft pour télécharger un nouveau fichier .ISO de Windows 10, puis utilisez [Boot Camp](https: //support.apple.com/guide/bootcamp-assistant/get-started-with-boot-camp-on-mac-bcmp712cfeb8/6.1/mac/10.15) pour le réinstaller sur votre Mac. Une fois que Windows est opérationnel, assurez-vous d'abord d'avoir installé toutes les mises à jour d'Apple (les pilotes de support Windows susmentionnés et la mise à jour du logiciel Apple), puis installez toutes les mises à jour Windows proposées par Microsoft, _puis_ commencez à remettre vos fichiers et applications [sur votre système] (https://lifehacker.com/the-best-way-to-quickly-install-apps-on-a-new-windows-p-1836244140) une fois que vous avez vérifié que tout se passe bien.

Ne vous inquiétez pas; cela prend beaucoup moins de temps qu'il n'y paraît.
