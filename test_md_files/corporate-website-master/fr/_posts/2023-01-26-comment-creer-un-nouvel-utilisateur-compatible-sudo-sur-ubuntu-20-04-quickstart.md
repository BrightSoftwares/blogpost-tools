---
Tags:
- ubuntu
- linux
- server
- security
ToReview: true
author: full
categories:
- ubuntu
date: 2023-01-26
description: "Lors de la gestion d'un serveur, vous souhaiterez parfois autoriser les utilisateurs à exécuter des commandes en tant que 'root', l'utilisateur de niveau administrateur. La commande `sudo` fournit aux administrateurs système un moyen d'accorder des privilèges d'administrateur - généralement disponibles uniquement pour l'utilisateur root - aux utilisateurs normaux."
image: https://res.cloudinary.com/brightsoftwares/image/upload/t_BSBlogImage/v1656243722/pexels-franklin-david-10670164_uqf4i1.jpg
lang: fr
layout: flexstart-blog-single
pretified: true
ref: sudoenabled_202007051236
title: Comment créer un nouvel utilisateur compatible Sudo sur Ubuntu 20.04 [Quickstart]
seo:
  links: [ "https://www.wikidata.org/wiki/Q381" ]
---

<h3 id="introduction">Introduction</h3>

<p>Lors de la gestion d'un serveur, vous souhaiterez parfois autoriser les utilisateurs à exécuter des commandes en tant que "root", l'utilisateur de niveau administrateur. La commande <code>sudo</code> fournit aux administrateurs système un moyen d'accorder des privilèges d'administrateur - généralement disponibles uniquement pour l'utilisateur <strong>root</strong> - aux utilisateurs normaux. </p>

<p>Dans ce didacticiel, vous apprendrez à créer un nouvel utilisateur avec un accès <code>sudo</code> sur Ubuntu 20.04 sans avoir à modifier le fichier <code>/etc/sudoers</code> de votre serveur. </p>

<p><span class='note'><strong>Remarque :</strong> Si vous souhaitez configurer <code>sudo</code> pour un utilisateur existant, passez à l'étape 3.<br></span> </p>

<h2 id="step-1-—-logging-into-your-server">Étape 1 - Connexion à votre serveur</h2>

<p>SSH sur votre serveur en tant qu'utilisateur <strong>root</strong> :</p>
<pre class="code-pre command prefixed local-environment"><code><ul class="prefixed"><li class="line" prefix="$">ssh root@<span class="highlight"> votre_adresse_ip_serveur</span>
</li></ul></code></pre>
<h2 id="step-2-—-adding-a-new-user-to-the-system">Étape 2 - Ajouter un nouvel utilisateur au système</h2>

<p>Utilisez la commande <code>adduser</code> pour ajouter un nouvel utilisateur à votre système :</p>
<pre class="code-pre super_user prefixed"><code><ul class="prefixed"><li class="line" prefix="#">adduser <span class="highlight">sammy</span>
</li></ul></code></pre>
<p>Assurez-vous de remplacer <code><span class="highlight">sammy</span></code> par le nom d'utilisateur que vous souhaitez créer. Vous serez invité à créer et à vérifier un mot de passe pour l'utilisateur :</p>
<pre class="code-pre "><code><div class="secondary-code-label " title="Output">Output</div>Entrez le nouveau mot de passe UNIX :
Retapez le nouveau mot de passe UNIX :
passwd : mot de passe mis à jour avec succès
</code></pre>
<p>Ensuite, il vous sera demandé de fournir des informations sur le nouvel utilisateur. Vous pouvez accepter les valeurs par défaut et laisser ces informations vides :</p>
<pre class="code-pre "><code><div class="secondary-code-label " title="Output">Sortie</div>Modification des informations utilisateur pour <span class="highlight">sammy< /span>
Entrez la nouvelle valeur ou appuyez sur ENTER pour la valeur par défaut
    Nom et prénom []:
    Numéro de chambre []:
    Téléphone de travail []:
    Téléphone fixe []:
    Autre []:
Les informations sont-elles correctes ? [O/n]
</code></pre>
<h2 id="step-3-—-adding-the-user-to-the-sudo-group">Étape 3 - Ajouter l'utilisateur au groupe <strong>sudo</strong></h2>

<p>Utilisez la commande <code>usermod</code> pour ajouter l'utilisateur au groupe <strong>sudo</strong> :</p>
<pre class="code-pre super_user prefixed"><code><ul class="prefixed"><li class="line" prefix="#">usermod -aG sudo <span class="highlight">sammy< /span>
</li></ul></code></pre>
<p>Encore une fois, assurez-vous de remplacer <code><span class="highlight">sammy</span></code> par le nom d'utilisateur que vous venez d'ajouter. Par défaut sur Ubuntu, tous les membres du groupe <strong>sudo</strong> ont tous les privilèges <code>sudo</code>.</p>

<h2 id="step-4-—-testing-sudo-access">Étape 4 - Tester l'accès <code>sudo</code></h2>

<p>Pour tester que les nouvelles autorisations <code>sudo</code> fonctionnent, utilisez d'abord la commande <code>su</code> pour basculer vers le nouveau compte utilisateur :</p>
<pre class="code-pre super_user prefixed"><code><ul class="prefixed"><li class="line" prefix="#">su - <span class="highlight">sammy</span >
</li></ul></code></pre>
<p>En tant que nouvel utilisateur, vérifiez que vous pouvez utiliser <code>sudo</code> en ajoutant <code>sudo</code> à la commande que vous souhaitez exécuter avec les privilèges de superutilisateur :</p>
<pre class="code-pre command prefixed"><code><ul class="prefixed"><li class="line" prefix="$">sudo <span class="highlight">command_to_run</span>
</li></ul></code></pre>
<p>Par exemple, vous pouvez lister le contenu du répertoire <code>/root</code>, qui n'est normalement accessible qu'à l'utilisateur root :</p>
<pre class="code-pre command prefixed"><code><ul class="prefixed"><li class="line" prefix="$">sudo ls -la /root
</li></ul></code></pre>
<p>La première fois que vous utilisez <code>sudo</code> dans une session, vous serez invité à entrer le mot de passe du compte de cet utilisateur. Saisissez le mot de passe pour continuer :</p>
<pre class="code-pre "><code><div class="secondary-code-label " title="Sortie :">Sortie :</div>[sudo] mot de passe pour <span class="highlight"> samy</span> :
</code></pre>
<p><span class='note'><strong>Remarque :</strong> il ne s'agit <em>pas</em> de demander le mot de passe <strong>root</strong> ! Entrez le mot de passe de l'utilisateur sudo que vous venez de créer.<br></span></p>

<p>Si votre utilisateur est dans le bon groupe et que vous avez correctement saisi le mot de passe, la commande que vous avez émise avec <code>sudo</code> s'exécutera avec les privilèges <strong>root</strong>.</p>

<h2 id="conclusion">Conclusion</h2>

<p>Dans ce tutoriel de démarrage rapide, nous avons créé un nouveau compte utilisateur et l'avons ajouté au groupe <strong>sudo</strong> pour activer l'accès <code>sudo</code>. </p>

<p>Pour que votre nouvel utilisateur bénéficie d'un accès externe, veuillez suivre notre section sur <a href="https://www.digitalocean.com/community/tutorials/initial-server-setup-with-ubuntu-20-04 #step-5-%E2%80%94-enabling-external-access-for-your-regular-user">Activation de l'accès externe pour votre utilisateur régulier</a>.</p>

<p>Si vous avez besoin d'informations plus détaillées sur la configuration d'un serveur Ubuntu 20.04, veuillez lire notre <a href="https://www.digitalocean.com/community/tutorials/initial-server-setup-with-ubuntu-20 -04">Tutoriel de configuration initiale du serveur avec Ubuntu 20.04</a>.</p>