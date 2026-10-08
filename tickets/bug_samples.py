# tickets/bug_samples.py
"""Jeu de tickets réalistes pour la commande seed_data.

Faker produit du texte sans signification, ce qui convient pour
remplir une base mais pas pour tester les fonctionnalités d'IA :
un modèle ne peut pas résumer un texte qui n'a pas de sens.
"""

BUGS = [
    (
        "Erreur 500 à l'ouverture d'un ticket sans développeur",
        "Quand j'ouvre un ticket qui n'a pas encore de développeur "
        "assigné, j'obtiens une page d'erreur 500. Ça n'arrive que "
        "sur les projets où aucun membre n'a le rôle développeur. "
        "La console affiche un MultiValueDictKeyError.",
    ),
    (
        "Le filtre par statut ne retient pas la sélection",
        "Je filtre les tickets sur « En cours », je clique sur un "
        "ticket, je reviens en arrière, et le filtre est revenu à "
        "« Tous ». Je dois refiltrer à chaque fois.",
    ),
    (
        "Les notifications ne sont pas envoyées après une assignation",
        "Quand j'assigne un ticket à un développeur, aucune notification "
        "n'est envoyée. Le ticket apparaît bien dans sa liste, mais il "
        "ne reçoit ni notification dans l'application ni e-mail.",
    ),
    (
        "Le compteur de tickets ouverts affiche une valeur incorrecte",
        "Le tableau de bord affiche 24 tickets ouverts alors que la "
        "liste des tickets n'en contient que 21. Les trois tickets "
        "supprimés semblent toujours être pris en compte dans le compteur.",
    ),
    (
        "Impossible de modifier un ticket après son changement de statut",
        "Après avoir passé un ticket de « Nouveau » à « Résolu », le "
        "bouton Modifier disparaît. Pourtant, les utilisateurs ayant "
        "les permissions nécessaires devraient toujours pouvoir modifier "
        "la description ou ajouter des informations.",
    ),
    (
        "Les caractères accentués disparaissent dans les commentaires",
        "Lorsque j'ajoute un commentaire contenant des caractères comme "
        "é, è, à, ç ou œ, certains caractères sont remplacés par des "
        "symboles incorrects après l'enregistrement. Le problème apparaît "
        "également dans les e-mails de notification.",
    ),
    (
        "La recherche ne trouve pas les tickets contenant plusieurs mots",
        "Une recherche sur « problème connexion » ne retourne aucun "
        "résultat alors qu'un ticket contient exactement ces deux mots "
        "dans sa description. Une recherche sur un seul mot fonctionne.",
    ),
    (
        "Un utilisateur peut voir les tickets d'une autre entreprise",
        "Un utilisateur connecté à l'entreprise A peut accéder directement "
        "à un ticket appartenant à l'entreprise B en modifiant son "
        "identifiant dans l'URL. Le ticket ne devrait jamais être visible "
        "en dehors de son entreprise.",
    ),
    (
        "La pagination revient à la première page après une modification",
        "Je suis sur la page 4 de la liste des tickets et je modifie un "
        "ticket. Après avoir enregistré mes changements, je suis renvoyé "
        "à la première page au lieu de rester sur la page 4.",
    ),
    (
        "Le formulaire accepte une date d'échéance antérieure à la création",
        "Il est possible de créer un ticket aujourd'hui avec une date "
        "d'échéance située plusieurs semaines dans le passé. Le formulaire "
        "ne signale aucune erreur et le ticket est enregistré normalement.",
    ),
    (
        "Le statut affiché dans l'API ne correspond pas à l'interface",
        "L'interface affiche « En cours », mais l'API retourne la valeur "
        "\"in_progress_old\". Certains clients de l'API ne reconnaissent "
        "plus cette ancienne valeur et échouent lors du traitement.",
    ),
    (
        "Les pièces jointes disparaissent après modification du ticket",
        "J'ajoute une capture d'écran à un ticket puis je modifie uniquement "
        "son titre. Après l'enregistrement, la pièce jointe n'est plus "
        "visible et semble avoir été supprimée.",
    ),
    (
        "Le bouton de suppression reste visible sans permission",
        "Un utilisateur qui possède uniquement la permission de consulter "
        "les tickets voit quand même le bouton Supprimer. Lorsqu'il clique "
        "dessus, une erreur 403 apparaît. Le bouton devrait être masqué.",
    ),
    (
        "Les tickets récemment créés n'apparaissent pas dans le tableau de bord",
        "Je crée un nouveau ticket et il apparaît immédiatement dans la "
        "liste des tickets, mais le tableau de bord continue d'afficher "
        "les anciennes statistiques pendant plusieurs minutes.",
    ),
    (
        "L'export CSV mélange les tickets de plusieurs entreprises",
        "Lorsque je lance l'export CSV depuis mon entreprise, le fichier "
        "contient certains tickets appartenant à d'autres entreprises. "
        "Le problème semble uniquement concerner l'export et pas la liste "
        "normale des tickets.",
    ),
    (
        "Une erreur CSRF apparaît lors de la création d'un ticket",
        "De manière aléatoire, la création d'un ticket échoue avec une "
        "erreur CSRF. Recharger la page puis soumettre à nouveau le "
        "formulaire permet généralement de créer le ticket.",
    ),
    (
        "Le tri par priorité fonctionne dans le mauvais ordre",
        "Lorsque je sélectionne le tri par priorité décroissante, les "
        "tickets avec la priorité « Faible » apparaissent avant ceux "
        "marqués « Critique ». Le tri semble fonctionner dans l'ordre "
        "alphabétique au lieu de respecter le niveau de priorité.",
    ),
    (
        "Les commentaires sont visibles après suppression du ticket",
        "Après avoir supprimé un ticket, certains de ses commentaires "
        "restent accessibles via une ancienne URL. Ils ne devraient plus "
        "être accessibles une fois le ticket supprimé.",
    ),
    (
        "Le bouton Enregistrer peut être soumis plusieurs fois",
        "Si je clique rapidement plusieurs fois sur le bouton Enregistrer "
        "du formulaire, plusieurs tickets identiques sont créés. Le "
        "bouton devrait être désactivé après la première soumission ou "
        "le serveur devrait empêcher les doublons.",
    ),
    (
        "L'avatar du développeur ne se charge pas dans la liste des tickets",
        "Les avatars des développeurs apparaissent correctement sur leur "
        "profil, mais restent vides dans la liste des tickets. Le problème "
        "se produit uniquement pour les utilisateurs ayant téléchargé "
        "une nouvelle photo récemment.",
    ),
    (
        "Le changement de projet ne met pas à jour les développeurs disponibles",
        "Lorsque je change le projet sélectionné dans le formulaire de "
        "création d'un ticket, la liste des développeurs conserve les "
        "membres du projet précédent. Il est donc possible d'assigner "
        "un ticket à un développeur qui ne fait pas partie du nouveau projet.",
    ),
]