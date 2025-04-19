# FP&A Dashboard

**Financial Planning & Analysis Interactive App**

Ce projet est une application **Streamlit** destinée à la planification financière, au reporting et à l'analyse de variances (Budget vs Forecast vs Actual). Vous y trouverez des pages dédiées à la synthèse de ventes, aux tendances, aux analyses par catégorie, aux écarts budgétaires et aux prévisions de fin d'année.

---

## 📋 Prérequis

- Python 3.8+
- pip (ou conda)

---

## ⚙️ Installation

1. **Cloner le dépôt**
   ```bash
   git clone <votre-repo-url>
   cd <votre-projet>
   ```
2. **Créer un environnement virtuel** (recommandé)
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # macOS/Linux
   .venv\Scripts\activate     # Windows
   ```
3. **Installer les dépendances**
   ```bash
   pip install -r requirements.txt
   ```

---

## 🗂️ Structure du projet

```text
├── Data/
│   ├── client_dimension.csv
│   ├── df_fact.xlsx
│   ├── final_client_dimension.xlsx
│   ├── fpa_actual.xlsx
│   ├── fpa_budget.xlsx
│   └── fpa_forecast.xlsx
│
├── images/
│   └── logo.webp
│
├── pages/
│   ├── 1_Group_summary.py
│   ├── 2_Trends.py
│   ├── 3_Analysis_By_Category.py
│   ├── 4_Budget_Variances.py
│   └── 5_Forecast_End_Of_Year.py
│
├── Home.py
├── config.toml            # Thème Streamlit
├── utils.py               # Fonctions utilitaires (logo, etc.)
├── visuals.py             # Template Plotly personnalisé
├── requirements.txt       # Dépendances Python
└── README.md              # (ce fichier)
```

---

## 📑 Description des pages

| Page                                    | Contenu                                                                 |
|-----------------------------------------|-------------------------------------------------------------------------|
| **Home.py**                             | Page d'accueil avec menu et présentation générale.                      |
| **1_Group_summary.py**                  | Synthèse mensuelle des ventes (Actual vs Budget/Forecast), marges.     |
| **2_Trends.py**                         | Analyse des tendances de ventes par pays, pays, etc.                   |
| **3_Analysis_By_Category.py**           | Analyse détaillée des performances par catégorie de produit.           |
| **4_Budget_Variances.py**               | Visualisation des écarts budgétaires et bridges (Budget → Forecast).   |
| **5_Forecast_End_Of_Year.py**           | Prévisions de fin d'année avec scénarios (Central, Optimistic...).     |

---

## 🔧 Configuration

- **Thème Streamlit** : réglé dans `config.toml` pour une palette verte/bleue, arrière-plans clairs.
- **Template Plotly** : défini dans `visuals.py` (`finance_gb_blend`).
- **Logo cliquable** : géré par `utils.py`, affiché sur toutes les pages.

---

## 🚀 Lancer l'application

```bash
streamlit run Home.py
```

Puis naviguez via la sidebar ou les pages (l'application s'appuie sur le routing de Streamlit >= 1.11).

---

## 📜 Licence

Ce projet est fourni « as is » pour usage interne. Adaptez et partagez selon vos besoins.
