# CHRONON Project

## Description
CHRONON est une application de simulation scientifique basée sur le protocole expérimental CHRONON-1. Elle permet d'étudier les effets de modulation du champ de Chronon sur des systèmes quantiques et optiques.

Le projet comprend :
- Un **cœur scientifique** (`chronon_core`) pour les calculs et simulations.
- Une **interface graphique** (`app/gui`) pour interagir facilement avec le modèle.

## Installation

1. Assurez-vous d'avoir **Python 3.10+** installé.
2. Installez les dépendances via le terminal :
   ```bash
   pip install -r app/requirements.txt
   ```

## Utilisation

### Lancement Rapide
Un raccourci **"Lancer CHRONON"** a été créé sur votre bureau. Double-cliquez simplement dessus pour démarrer.

### Modes de Fonctionnement
L'interface propose deux modes principaux :

1. **Démonstration (Pas à pas)** :
   - Idéal pour découvrir le fonctionnement.
   - Vous guide à travers une simulation pré-configurée étape par étape.

2. **Mode Réel** :
   - Pour les utilisateurs avancés.
   - Permet de lancer des simulations complètes avec vos propres paramètres.

### Lancement Manuel
Vous pouvez aussi lancer le programme via le script batch :
```cmd
c:\Users\Brécheteau\Desktop\CHRONON\run_gui.bat
```

## Structure du Projet

- `chronon_core/` : Bibliothèque scientifique (Protocol, Field, Analyzer).
- `app/gui/` : Interface utilisateur (basée sur CustomTkinter).
- `app/backend/` : Logique serveur (si applicable).
- `run_gui.bat` : Script de lancement pour Windows.
