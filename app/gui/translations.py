# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~
# Project : CHRONON
# Version : 1.0
# Dev     : Brécheteau.B
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~

TRANSLATIONS = {
    "fr": {
        "SIDEBAR": {
            "SETUP": "SETUP",
            "ACQUISITION": "ACQUISITION",
            "VISUALIZATION": "VISUALISATION",
            "ANALYSIS": "ANALYSE",
            "HISTORY": "HISTORIQUE",
            "HELP": "AIDE / THÉORIE"
        },
        "SETUP": {
            "TITLE": "Paramètres de l'Expérience",
            "LBL_PORT": "Port COM:",
            "LBL_BAUD": "Baud Rate:",
            "BTN_CONNECT": "Connecter",
            "BTN_DISCONNECT": "Déconnecter",
            "STATUS_CONNECTED": "Connecté",
            "STATUS_DISCONNECTED": "Déconnecté",
            "LBL_PHYS": "PARAMÈTRES PHYSIQUES",
            "LBL_THEORY": "THÉORIE CHRONON (Ω)",
            "LBL_ITER": "Itérations (Run)",
            "LBL_DUR": "Durée (s)",
            "LBL_DH": "Delta H (m)",
            "LBL_RAD": "Rayon (km)",
            "LBL_ALPHA": "Alpha (Couplage)",
            "LBL_BETA": "Beta (Phase)",
            "LBL_NU": "Nu² (Fréquence)",
            "LBL_GAMMA": "Gamma (Récursivité)",
            "LBL_LINK": "Lien:",
            "LBL_SCENARIO": "Scénario:",
            "CHK_BATCH": "Mode Batch",
            "BTN_START": "LANCER LA SIMULATION",
            "BTN_SAVE": "Sauvegarder",
            "BTN_LOAD": "Charger",
            "LINK_OPTIONS": ["Fibre Optique", "Espace Libre", "Cryogénique"],
            "SCENARIO_OPTIONS": ["Standard", "Anomalie S3", "Collapsus", "Demo: Négatif", "Demo: Positif (3σ)", "Demo: Positif (>5σ)"]
        },
        "ACQUISITION": {
            "TITLE": "Contrôle d'Acquisition",
            "BTN_START": "Démarrer",
            "BTN_STOP": "ARRÊT D'URGENCE",
            "LBL_SAMPLES": "Échantillons:",
            "STATUS_RUNNING": "EN COURS",
            "STATUS_IDLE": "PRÊT"
        },
        "VISUALIZATION": {
            "TITLE": "Contrôles Graphiques (V1.0)",
            "LBL_X_AXIS": "Temps (s) / Delta h (m)",
            "LBL_Y_AXIS": "Amplitude / Delta ln(Phi)",
            "LBL_QC": "QC: VALIDE",
            "LBL_BLIND": "Blind: ON",
            "LBL_FALLBACK": "Fallback: OFF",
            "BTN_HELP": "Aide / Guide",
            "BTN_REFRESH": "Actualiser",
            "BTN_EXPORT": "Export Sélection",
            "BTN_SAVE": "Sauvegarder Graphique",
            "BTN_APPLY": "Appliquer",
            "CHK_OVERLAY": "Overlay Multi-runs",
            "CHK_ERRORBARS": "Barres d'erreur",
            "LBL_FILTER": "Filtre (Run ID)",
            "PLOT_TYPES": ["Régression Centrale (εΦ)", "Série Temporelle", "Résidus Δy", "Corrélation T2/Φ", "Heatmap", "Histogramme"]
        },
        "ANALYSIS": {
            "METRICS_EPSILON": "εΦ (pente)",
            "METRICS_BETA": "β (T2)",
            "STATUS_PENDING": "Stats: EN ATTENTE",
            "STATUS_NO_DATA": "Stats: PAS DE DONNÉES",
            "BTN_DIAGNOSTICS": "Diagnostics / Drift",
            "BTN_QUBITS": "Analyse Qubits (T2)",
            "BTN_SIMULATION": "Simulateur Power",
            "BTN_CORRELATION": "Matrice de Corrélation",
            "BTN_INTERPRETATION": "Interprétation / CCI",
            "BTN_LIMIT": "Limite Détection",
            "BTN_WHATIF": "Simulateur What-If",
            "LBL_INSIGHT": "Insight & Analyse Automatisée",
            "TXT_WAITING": ">>> En attente d'exécution QC...",
            "CHK_TRACE": "Trace Temporel",
            "CHK_HIST": "Histogramme",
            "CHK_CORR": "Corrélation",
            "BTN_REPORT": "Générer Rapport PDF (Rapide)",
            "MSG_REPORT_SUCCESS": "Rapport PDF généré!",
            "MSG_REPORT_FAIL": "Echec génération rapport",
            "LBL_BLIND_ON": "Blinding (ON) 🔒",
            "LBL_BLIND_OFF": "Blinding (OFF)"
        },
        "HISTORY": {
            "TITLE": "Historique des Sessions",
            "BTN_LOAD": "Charger la sélection",
            "BTN_DELETE": "Supprimer",
            "BTN_REFRESH": "Actualiser",
            "COL_DATE": "Date/Heure",
            "COL_SAMPLES": "N Points"
        },
        "HELP": {
            "TITLE": "Documentation & Théorie",
            "TXT_DOC": """=== GUIDE FONCTIONNALITÉS CHRONON ===

🔍 1. Exécuter QC (Quality Control)
Validation scientifique du run.
Critères :
- Witness Δh = 0 nul.
- Conditions environnementales ok.
- Stabilité Δh (jitter).
Résultat : PASS / FAIL.

📉 2. Diagnostics
Fiabilité de εΦ (résidus).
- Autocorrélation (Ljung-Box).
- Normalité / Hétéroscédasticité.

⏱️ 3. Calcul Qubits (T2)
Analyse T₂ vs Δln Φ => slope β.

💥 4. Simulateur Power
Courbe ROC, sensibilité S1/S2/S3.

🔗 5. Corrélation
Heatmap des biais potentiels.

🕶️ 6. Blinding
Masquage des résultats pour intégrité.

=== RÉSUMÉ EXPRESS ===
QC: Valide | Diag: Fiabilise | T2: Qubits | Power: Sensibilité | Blind: Intégrité.
"""
        },
        "INTERPRETATION": {
            "STRONG": "DÉTECTION FORTE",
            "WEAK": "DÉTECTION VALIDÉE",
            "TRACE": "AMBIGU / TRACE",
            "NULL": "NON-DÉTECTION",
            "EVAL_STRONG": "Signal hautement significatif (p < 0.001).",
            "EVAL_WEAK": "Signal significatif (p < 0.05).",
            "EVAL_TRACE": "Indice de signal non-concluant (0.05 < p < 0.10).",
            "EVAL_NULL": "Dominance du bruit. Aucune corrélation significative.",
            "NOTE_QC_FAIL": " NOTE: Données potentiellement corrompues (voir QC).",
            "DIAG_OK": "Diagnostics OK.",
            "DIAG_WARN": "ATTENTION: ",
            "QC_STATUS": "Statut QC",
            "SLOPE_OBS": "Pente observée",
            "INTENSITY": "Intensité",
            "MODEL_RELIABILITY": "Fiabilité Modèle",
            "RECOMMENDATION": "Recommandation",
            "REC_PUBLISH": "Publier",
            "REC_CHECK": "Augmenter N ou vérifier Setup",
            "PUB_TEMPLATE": (
                "Analyse de régression pondérée (N={n}). "
                "Contrôle qualité: {qc_res} (Statut: {qc_status}). "
                "Résultat: corrélation {sig_word} (pente εΦ = {slope:.2e} ± {stderr:.2e}, p = {pval:.4g}). "
                "Diagnostics: {diag_res}."
            ),
            "PUB_TERMS": {
                "passed": "validés",
                "failed": "échoués",
                "significant": "significative",
                "non-significant": "non-significative",
                "confirmed": "confirmé",
                "issues": "problèmes potentiels"
            },
            "CONCLUSION_LABEL": "CONCLUSION",
            "EVALUATION_LABEL": "EVALUATION",
            "PUBLICATION_LABEL": "PUBLICATION"
        },
        "REPORT": {
            "TITLE": "RAPPORT D'ANALYSE SCIENTIFIQUE",
            "GENERATED_ON": "Généré le",
            "MAIN_RESULT": "RÉSULTAT PRINCIPAL (εΦ)",
            "DETAILED_STATS": "STATISTIQUES DÉTAILLÉES",
            "METADATA": "MÉTADONNÉES",
            "AUTO_DESC_TITLE": "RAPPORT AUTOMATISÉ DÉTAILLÉ",
            "DISCLAIMER": "Généré automatiquement par CHRONON System V1.0 - Certification interne.",
            "Visualisation": "VISUALISATION",
            "DIAGNOSTICS": "DIAGNOSTICS & QUALITÉ",
            "RESIDUALS_TESTS": "Tests Statistiques sur Résidus",
            "HIST_TITLE": "Distribution des Résidus",
            "QQ_HINT": "Distribution normale centrée sur 0 = Modèle sain.",
            "TABLE_METRIC": "Métrique",
            "TABLE_VALUE": "Valeur",
            "TABLE_DESC": "Description",
            "TABLE_TEST": "Test",
            "TABLE_STAT": "Statistique",
            "TABLE_RESULT": "Résultat"
        },
        "COMMON": {
            "ERROR": "Erreur",
            "SUCCESS": "Succès",
            "INFO": "Information"
        }
    },
    "en": {
        "SIDEBAR": {
            "SETUP": "SETUP",
            "ACQUISITION": "ACQUISITION",
            "VISUALIZATION": "VISUALIZATION",
            "ANALYSIS": "ANALYSIS",
            "HISTORY": "HISTORY",
            "HELP": "HELP / THEORY"
        },
        "SETUP": {
            "TITLE": "Experiment Setup",
            "LBL_PORT": "COM Port:",
            "LBL_BAUD": "Baud Rate:",
            "BTN_CONNECT": "Connect",
            "BTN_DISCONNECT": "Disconnect",
            "STATUS_CONNECTED": "Connected",
            "STATUS_DISCONNECTED": "Disconnected",
            "LBL_PHYS": "PHYSICAL PARAMETERS",
            "LBL_THEORY": "CHRONON THEORY (Ω)",
            "LBL_ITER": "Iterations (Run)",
            "LBL_DUR": "Duration (s)",
            "LBL_DH": "Delta H (m)",
            "LBL_RAD": "Radius (km)",
            "LBL_ALPHA": "Alpha (Coupling)",
            "LBL_BETA": "Beta (Phase)",
            "LBL_NU": "Nu² (Frequency)",
            "LBL_GAMMA": "Gamma (Recursion)",
            "LBL_LINK": "Link Type:",
            "LBL_SCENARIO": "Scenario:",
            "CHK_BATCH": "Batch Mode",
            "BTN_START": "START SIMULATION",
            "BTN_SAVE": "Save",
            "BTN_LOAD": "Load",
            "LINK_OPTIONS": ["Fiber Optic", "Free Space", "Cryogenic"],
            "SCENARIO_OPTIONS": ["Standard", "S3 Anomaly", "Collapse", "Demo: Negative", "Demo: Positive (3σ)", "Demo: Positive (>5σ)"]
        },
        "ACQUISITION": {
            "TITLE": "Acquisition Control",
            "BTN_START": "Start",
            "BTN_STOP": "EMERGENCY STOP",
            "LBL_SAMPLES": "Samples:",
            "STATUS_RUNNING": "RUNNING",
            "STATUS_IDLE": "READY"
        },
        "VISUALIZATION": {
            "TITLE": "Graphical Controls (V1.0)",
            "LBL_X_AXIS": "Time (s) / Delta h (m)",
            "LBL_Y_AXIS": "Amplitude / Delta ln(Phi)",
            "LBL_QC": "QC: VALID",
            "LBL_BLIND": "Blind: ON",
            "LBL_FALLBACK": "Fallback: OFF",
            "BTN_HELP": "Help / Guide",
            "BTN_REFRESH": "Refresh",
            "BTN_EXPORT": "Export Selection",
            "BTN_SAVE": "Save Plot",
            "BTN_APPLY": "Apply",
            "CHK_OVERLAY": "Multi-run Overlay",
            "CHK_ERRORBARS": "Error Bars",
            "LBL_FILTER": "Filter (Run ID)",
            "PLOT_TYPES": ["Central Regression (εΦ)", "Time Series", "Residuals Δy", "Correlation T2/Φ", "Heatmap", "Histogram"]
        },
        "ANALYSIS": {
            "METRICS_EPSILON": "εΦ (Slope)",
            "METRICS_BETA": "β (T2)",
            "STATUS_PENDING": "Stats: PENDING",
            "STATUS_NO_DATA": "Stats: NO DATA",
            "BTN_DIAGNOSTICS": "Diagnostics / Drift",
            "BTN_QUBITS": "Qubit Analysis (T2)",
            "BTN_SIMULATION": "Power Simulator",
            "BTN_CORRELATION": "Correlation Matrix",
            "BTN_INTERPRETATION": "Interpretation / CCI",
            "BTN_LIMIT": "Detection Limit",
            "BTN_WHATIF": "What-If Simulator",
            "LBL_INSIGHT": "Insight & Automated Analysis",
            "TXT_WAITING": ">>> Waiting for QC execution...",
            "CHK_TRACE": "Time Trace",
            "CHK_HIST": "Histogram",
            "CHK_CORR": "Correlation",
            "BTN_REPORT": "Generate PDF Report (Fast)",
            "MSG_REPORT_SUCCESS": "PDF Report Generated!",
            "MSG_REPORT_FAIL": "Failed to generate report",
            "LBL_BLIND_ON": "Blinding (ON) 🔒",
            "LBL_BLIND_OFF": "Blinding (OFF)"
        },
        "HISTORY": {
            "TITLE": "Session History",
            "BTN_LOAD": "Load Selection",
            "BTN_DELETE": "Delete",
            "BTN_REFRESH": "Refresh",
            "COL_DATE": "Date/Time",
            "COL_SAMPLES": "N Points"
        },
        "HELP": {
            "TITLE": "Documentation & Theory",
            "TXT_DOC": """=== CHRONON FEATURES GUIDE ===

🔍 1. Run QC (Quality Control)
Scientific validation.
Checks:
- Witness Δh = 0.
- Environmental tolerances.
- Δh stability.
Result: PASS / FAIL.

📉 2. Diagnostics
Residual check (εΦ reliability).
- Autocorrelation (Ljung-Box).
- Normality / Homoscedasticity.

⏱️ 3. Qubit Calculation (T2)
Slope β analysis (T₂ vs Δln Φ).

💥 4. Power Simulator
Protocol sensitivity test (ROC, S1-S3).

🔗 5. Correlation
Bias heatmap.

🕶️ 6. Blinding
Integrity protection.

=== EXPRESS SUMMARY ===
QC: Validate | Diag: Secure | T2: Analyze | Power: Justify | Blind: Integrity.
"""
        },
        "INTERPRETATION": {
            "STRONG": "STRONG DETECTION",
            "WEAK": "VALIDATED DETECTION",
            "TRACE": "AMBIGUOUS / TRACE",
            "NULL": "NON-DETECTION",
            "EVAL_STRONG": "Highly significant signal (p < 0.001).",
            "EVAL_WEAK": "Significant signal (p < 0.05).",
            "EVAL_TRACE": "Inconclusive (0.05 < p < 0.10).",
            "EVAL_NULL": "Noise dominance. No correlation.",
            "NOTE_QC_FAIL": " NOTE: Potentially corrupted (see QC).",
            "DIAG_OK": "Diagnostics OK.",
            "DIAG_WARN": "WARNING: ",
            "QC_STATUS": "QC Status",
            "SLOPE_OBS": "Observed Slope",
            "INTENSITY": "Intensity",
            "MODEL_RELIABILITY": "Model Reliability",
            "RECOMMENDATION": "Recommendation",
            "REC_PUBLISH": "Publish",
            "REC_CHECK": "Increase N or check Setup",
            "PUB_TEMPLATE": (
                "Weighted regression (N={n}). "
                "QC: {qc_res} (Status: {qc_status}). "
                "Result: {sig_word} correlation (εΦ = {slope:.2e} ± {stderr:.2e}, p = {pval:.4g}). "
                "Diagnostics: {diag_res}."
            ),
            "PUB_TERMS": {
                "passed": "passed",
                "failed": "failed",
                "significant": "significant",
                "non-significant": "non-significant",
                "confirmed": "confirmed",
                "issues": "potential issues"
            },
            "CONCLUSION_LABEL": "CONCLUSION",
            "EVALUATION_LABEL": "EVALUATION",
            "PUBLICATION_LABEL": "PUBLICATION"
        },
        "REPORT": {
            "TITLE": "SCIENTIFIC ANALYSIS REPORT",
            "GENERATED_ON": "Generated on",
            "MAIN_RESULT": "MAIN RESULT (εΦ)",
            "DETAILED_STATS": "DETAILED STATISTICS",
            "METADATA": "METADATA",
            "AUTO_DESC_TITLE": "DETAILED AUTOMATED REPORT",
            "DISCLAIMER": "Generated by CHRONON System V1.0 - Internal Certification.",
            "Visualisation": "VISUALIZATION",
            "DIAGNOSTICS": "DIAGNOSTICS & QUALITY",
            "RESIDUALS_TESTS": "Residual Statistical Tests",
            "HIST_TITLE": "Residuals Distribution",
            "QQ_HINT": "Normal dist centered on 0 = Healthy model.",
            "TABLE_METRIC": "Metric",
            "TABLE_VALUE": "Value",
            "TABLE_DESC": "Description",
            "TABLE_TEST": "Test",
            "TABLE_STAT": "Statistic",
            "TABLE_RESULT": "Result"
        },
        "COMMON": {
            "ERROR": "Error",
            "SUCCESS": "Success",
            "INFO": "Information"
        }
    }
}

# (~ ~ ~ Φ(x) ~ ~ ~
#  Benjamin Brécheteau | Chronon Field 2025
#  ~ ~ ~ ~ ~)
