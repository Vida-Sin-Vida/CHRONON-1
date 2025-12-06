# CHRONON - Guide Fonctionnel

## 1. Vue d'ensemble
CHRONON est une application scientifique conçue pour la simulation, l'acquisition et l'analyse de données chronométriques (Phi).
L'architecture est modulaire, séparant l'interface graphique (GUI) de la logique métier (Core/Experiment).

## 2. Modules Principaux

### `app/gui` (Interface Utilisateur)
-   **Application (`application.py`)** : Fenêtre principale, thème, navigation.
-   **Frames** :
    -   `setup_frame.py` : Configuration des paramètres (Alpha, Beta, Gamma, etc.).
    -   `acquisition_frame.py` : Contrôle de l'expérience, logs temps réel et animation.
    -   `visualization_frame.py` : Graphiques dynamiques (Trace, Histogramme, Heatmap).
    -   `analysis_frame.py` : Statistiques post-run et génération de rapports PDF.

### `app/experiment` (Gestion Expérience)
-   **Manager (`manager.py`)** : Le "Cerveau". Orchestre la boucle d'acquisition, gère les threads, et stocke l'historique. Contient désormais une logique optimisée pour les modes "Batch".

### `chronon_core` (Logiciel Scientifique)
-   **Stats (`stats.py`)** : Librairie de calcul statistique (Moyennes, WLS, Newey-West Errors).
-   **Simulator (`simulator.py`)** : Moteur physique pour les simulations avancées (bruit coloré, modèles de marées).

## 3. Paramètres Scientifiques
Ces paramètres sont ajustables dans l'onglet **SETUP**.

| Paramètre | Symbole | Description | Impact |
| :--- | :--- | :--- | :--- |
| **Alpha** | $\alpha$ | Sensibilité altimétrique | Amplifie l'effet de `Delta_h`. |
| **Beta** | $\beta$ | Biais systématique | Ajoute un offset constant au signal. |
| **Gamma** | $\gamma$ | Facteur de Récursivité | Lisse le signal ($0.0$ = Brut, $0.99$ = Très Lissé). |
| **Delta_h** | $\Delta h$ | Variation hauteur (m) | Amplitude de la perturbation simulée. |
| **Nu_sq** | $\nu^2$ | Facteur de bruit | Intensité du bruit aléatoire injecté. |

## 4. Optimisation & Performance
-   **Calculs** : Les formules critiques utilisent `numpy` pour la vectorisation.
-   **Affichage** : En "Mode Batch", l'interface réduit la fréquence de rafraîchissement pour maximiser la vitesse de calcul.
-   **Logs** : Système robuste avec gestion d'erreurs automatique (le programme ne crashe pas en cas d'anomalie sur un point).

## 5. Extensions (Pour Développeurs)
-   **Ajouter un Graphique** : Modifier `visualization_frame.py` -> `update_plot()`.
-   **Nouveau Scénario** : Ajouter une condition dans `manager.py` -> `_calculate_physics_step`.
-   **Tests** : Utiliser le dossier `notebooks/` pour valider les algorithmes avant intégration.

---

~ ~ ~ Φ(x) ~ ~ ~
Benjamin Brécheteau | Chronon Field 2025
~ ~ ~ ~ ~ ~ ~ ~ ~
