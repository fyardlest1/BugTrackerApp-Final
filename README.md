# BugTracker

Un traqueur de bugs multi-entreprises, sécurisé, avec une API REST.

## Démo en ligne

https://bugtrackerapp.up.railway.app/

Comptes de démonstration : des boutons sur la page de connexion permettent d'essayer chaque rôle (Admin, Chef de projet, Développeur, Rapporteur) sans créer de compte.

## Captures d'écran

### Liste des tickets, avec recherche et filtres

![Liste des tickets](/readme-img/apercu-tickets.png)

### Documentation interactive de l'API

![Documentation de l'API](/readme-img/app40.png)

### Page de profil utilisateur

![Profil utilisateur](/readme-img/app45.png)

### Interface d'administration

![Administration Django](/readme-img/admin-dash.png)

## Fonctionnalités

- Isolation stricte des données par entreprise (multi-tenant)
- Rôles et permissions : Admin, Chef de projet, Développeur, Rapporteur
- CRUD projets et tickets, commentaires, pièces jointes
- Notifications internes et invitations par email
- Tableau de bord avec graphiques
- API REST documentée, avec authentification JWT

## Stack technique

Django 6, Django REST Framework, PostgreSQL, Tailwind CSS, Docker, déployé sur Railway.

## Installation locale

```bash
# 1. Cloner le dépôt
git clone https://github.com/fyardlest1/BugTrackerApp-Final.git
cd bugtracker

# 2. Créer et activer un environnement virtuel
python -m venv .venv
source .venv/bin/activate        # Windows : .venv\Scripts\activate

# 3. Installer les dépendances
pip install -r requirements.txt

# 4. Configurer les variables d'environnement
cp .env.example .env             # puis renseigner SECRET_KEY, DATABASE_URL, etc.

# 5. Appliquer les migrations et générer des données de démonstration
python manage.py migrate
python manage.py seed_demo

# 6. Lancer le serveur de développement
python manage.py tailwind runserver
```

L'application est alors accessible en locale sur http://127.0.0.1:8000.
