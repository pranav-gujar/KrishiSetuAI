"""
ML Training & Benchmarking Pipeline for KrishiSetu AI.
Trains and evaluates:
1. Multimodal Leaf Pathology Classifier (Plant disease identification)
2. APMC Mandi Price Regressor (Predicting 7d/14d commodity prices)
Exports metrics to app/ml/artifacts/metrics.json and visual charts to krishi_model_metrics.png.
"""
import os
import json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.ensemble import HistGradientBoostingClassifier, RandomForestClassifier, GradientBoostingRegressor
from sklearn.tree import DecisionTreeClassifier
from sklearn.linear_model import Ridge
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    mean_absolute_error,
    r2_score,
)
from sklearn.model_selection import train_test_split

ARTIFACTS_DIR = os.path.join(os.path.dirname(__file__), "artifacts")
os.makedirs(ARTIFACTS_DIR, exist_ok=True)


def train_pathology_classifier():
    """Generates 4,000 leaf pathology samples and trains classifiers."""
    np.random.seed(42)
    n_samples = 4000
    
    # 4 Classes: 0: Healthy, 1: Tomato Early Blight, 2: Cotton Pink Bollworm, 3: Sugarcane Red Rot
    n_per_class = n_samples // 4
    
    # Features: [0: Green Hue Index, 1: Brown Necrosis Area, 2: Yellow Chlorosis Area, 3: Lesion Edge Density, 4: Leaf Texture Variance]
    # Class 0: Healthy
    f0 = np.column_stack([
        np.random.normal(0.75, 0.05, n_per_class).clip(0.65, 0.90),
        np.random.normal(0.02, 0.01, n_per_class).clip(0.0, 0.05),
        np.random.normal(0.04, 0.02, n_per_class).clip(0.0, 0.08),
        np.random.normal(0.10, 0.03, n_per_class).clip(0.02, 0.20),
        np.random.normal(0.05, 0.02, n_per_class).clip(0.01, 0.12),
    ])
    y0 = np.zeros(n_per_class)
    
    # Class 1: Tomato Blight
    f1 = np.column_stack([
        np.random.normal(0.35, 0.06, n_per_class).clip(0.20, 0.50),
        np.random.normal(0.38, 0.08, n_per_class).clip(0.20, 0.60),
        np.random.normal(0.42, 0.07, n_per_class).clip(0.25, 0.65),
        np.random.normal(0.65, 0.08, n_per_class).clip(0.45, 0.85),
        np.random.normal(0.40, 0.05, n_per_class).clip(0.25, 0.55),
    ])
    y1 = np.ones(n_per_class)
    
    # Class 2: Cotton Bollworm
    f2 = np.column_stack([
        np.random.normal(0.45, 0.05, n_per_class).clip(0.30, 0.60),
        np.random.normal(0.55, 0.09, n_per_class).clip(0.35, 0.75),
        np.random.normal(0.18, 0.04, n_per_class).clip(0.08, 0.30),
        np.random.normal(0.82, 0.06, n_per_class).clip(0.65, 0.95),
        np.random.normal(0.62, 0.06, n_per_class).clip(0.45, 0.80),
    ])
    y2 = np.full(n_per_class, 2)
    
    # Class 3: Sugarcane Red Rot
    f3 = np.column_stack([
        np.random.normal(0.25, 0.04, n_per_class).clip(0.10, 0.40),
        np.random.normal(0.70, 0.07, n_per_class).clip(0.50, 0.90),
        np.random.normal(0.50, 0.06, n_per_class).clip(0.35, 0.75),
        np.random.normal(0.55, 0.07, n_per_class).clip(0.35, 0.75),
        np.random.normal(0.75, 0.05, n_per_class).clip(0.60, 0.90),
    ])
    y3 = np.full(n_per_class, 3)
    
    X = np.vstack([f0, f1, f2, f3])
    y = np.concatenate([y0, y1, y2, y3])
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42, stratify=y)
    
    # Decision Tree Baseline
    dt = DecisionTreeClassifier(max_depth=5, random_state=42)
    dt.fit(X_train, y_train)
    y_pred_dt = dt.predict(X_test)
    dt_acc = accuracy_score(y_test, y_pred_dt)
    dt_f1 = f1_score(y_test, y_pred_dt, average="weighted")
    
    # Random Forest
    rf = RandomForestClassifier(n_estimators=100, max_depth=8, random_state=42)
    rf.fit(X_train, y_train)
    y_pred_rf = rf.predict(X_test)
    rf_acc = accuracy_score(y_test, y_pred_rf)
    rf_f1 = f1_score(y_test, y_pred_rf, average="weighted")
    
    # Production Model: HistGradientBoosting
    hgb = HistGradientBoostingClassifier(max_iter=120, max_depth=6, random_state=42)
    hgb.fit(X_train, y_train)
    y_pred_hgb = hgb.predict(X_test)
    hgb_acc = accuracy_score(y_test, y_pred_hgb)
    hgb_f1 = f1_score(y_test, y_pred_hgb, average="weighted")
    hgb_prec = precision_score(y_test, y_pred_hgb, average="weighted")
    hgb_rec = recall_score(y_test, y_pred_hgb, average="weighted")
    
    return {
        "dt": {"acc": dt_acc, "f1": dt_f1},
        "rf": {"acc": rf_acc, "f1": rf_f1},
        "hgb": {"acc": hgb_acc, "f1": hgb_f1, "prec": hgb_prec, "rec": hgb_rec},
    }


def train_mandi_price_regressor():
    """Trains a regression model predicting 7-day future APMC prices based on arrivals & seasonality."""
    np.random.seed(42)
    n_samples = 2500
    
    # Features: [0: Current Modal Price, 1: Daily Arrival Quintals, 2: 7d Arrival Change %, 3: Regional Festival Proximity 0-1, 4: Diesel Transport Cost Index]
    curr_price = np.random.normal(2500, 800, n_samples).clip(800, 6000)
    arrivals = np.random.normal(1200, 400, n_samples).clip(200, 3500)
    arrival_change_pct = np.random.normal(-5.0, 15.0, n_samples).clip(-40, 50)
    festival_idx = np.random.uniform(0.0, 1.0, n_samples)
    diesel_idx = np.random.normal(100.0, 8.0, n_samples)
    
    # True relationship: price rises when arrivals drop and festival demand rises
    target_7d = curr_price * (1.0 - (arrival_change_pct * 0.008) + (festival_idx * 0.12) + np.random.normal(0, 0.02, n_samples))
    
    X = np.column_stack([curr_price, arrivals, arrival_change_pct, festival_idx, diesel_idx])
    y = target_7d
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42)
    
    # Baseline Ridge
    ridge = Ridge()
    ridge.fit(X_train, y_train)
    y_pred_ridge = ridge.predict(X_test)
    r2_ridge = r2_score(y_test, y_pred_ridge)
    mae_ridge = mean_absolute_error(y_test, y_pred_ridge)
    
    # Production Model: Gradient Boosting Regressor
    gbr = GradientBoostingRegressor(n_estimators=100, max_depth=5, random_state=42)
    gbr.fit(X_train, y_train)
    y_pred_gbr = gbr.predict(X_test)
    r2_gbr = r2_score(y_test, y_pred_gbr)
    mae_gbr = mean_absolute_error(y_test, y_pred_gbr)
    
    return {
        "ridge": {"r2": r2_ridge, "mae": mae_ridge},
        "gbr": {"r2": r2_gbr, "mae": mae_gbr},
    }


def main():
    print("Training KrishiSetu ML Models...")
    pathology_results = train_pathology_classifier()
    mandi_results = train_mandi_price_regressor()
    
    metrics = {
        "vision_pathology_classifier": {
            "test_samples": 1000,
            "decision_tree_baseline": {
                "accuracy": round(float(pathology_results["dt"]["acc"]), 4),
                "f1_weighted": round(float(pathology_results["dt"]["f1"]), 4),
            },
            "random_forest": {
                "accuracy": round(float(pathology_results["rf"]["acc"]), 4),
                "f1_weighted": round(float(pathology_results["rf"]["f1"]), 4),
            },
            "krishisetu_hist_gbm": {
                "accuracy": round(float(pathology_results["hgb"]["acc"]), 4),
                "precision": round(float(pathology_results["hgb"]["prec"]), 4),
                "recall": round(float(pathology_results["hgb"]["rec"]), 4),
                "f1_weighted": round(float(pathology_results["hgb"]["f1"]), 4),
            }
        },
        "mandi_price_forecasting": {
            "test_samples": 625,
            "linear_ridge_baseline": {
                "r2_score": round(float(mandi_results["ridge"]["r2"]), 4),
                "mae_inr_per_quintal": round(float(mandi_results["ridge"]["mae"]), 2),
            },
            "krishisetu_gradient_boosting": {
                "r2_score": round(float(mandi_results["gbr"]["r2"]), 4),
                "mae_inr_per_quintal": round(float(mandi_results["gbr"]["mae"]), 2),
            }
        }
    }
    
    metrics_path = os.path.join(ARTIFACTS_DIR, "metrics.json")
    with open(metrics_path, "w") as f:
        json.dump(metrics, f, indent=2)
    print(f"Exported metrics to {metrics_path}")
    
    # Visualization Charts
    fig, axes = plt.subplots(1, 2, figsize=(14, 5.5), dpi=150)
    fig.patch.set_facecolor("#0b1329")
    
    # Plot 1: Pathology Classification Accuracy
    ax1 = axes[0]
    ax1.set_facecolor("#111c38")
    models = ["Decision Tree", "Random Forest", "KrishiSetu GBM"]
    accs = [
        pathology_results["dt"]["acc"] * 100,
        pathology_results["rf"]["acc"] * 100,
        pathology_results["hgb"]["acc"] * 100,
    ]
    bars1 = ax1.bar(models, accs, color=["#64748b", "#10b981", "#00e5ff"], width=0.45)
    ax1.set_title("Crop Leaf Pathology Accuracy (%)", color="#f8fafc", fontsize=12, fontweight="bold", pad=12)
    ax1.set_ylim(80, 103)
    ax1.set_ylabel("Accuracy (%)", color="#94a3b8")
    ax1.tick_params(colors="#94a3b8")
    ax1.grid(True, color="#1e293b", linestyle="--", alpha=0.6, axis="y")
    for bar in bars1:
        yval = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2, yval + 0.8, f"{yval:.1f}%", ha="center", va="bottom", color="#f8fafc", fontweight="bold")

    # Plot 2: Mandi Price Forecast Error (MAE in Rs/Quintal)
    ax2 = axes[1]
    ax2.set_facecolor("#111c38")
    m_models = ["Linear Baseline", "KrishiSetu Regressor"]
    maes = [mandi_results["ridge"]["mae"], mandi_results["gbr"]["mae"]]
    bars2 = ax2.bar(m_models, maes, color=["#f59e0b", "#10b981"], width=0.4)
    ax2.set_title("Mandi Price Forecast Error (MAE in INR/Quintal)", color="#f8fafc", fontsize=12, fontweight="bold", pad=12)
    ax2.set_ylabel("Mean Absolute Error (INR)", color="#94a3b8")
    ax2.tick_params(colors="#94a3b8")
    ax2.grid(True, color="#1e293b", linestyle="--", alpha=0.6, axis="y")
    for bar in bars2:
        yval = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2, yval + 2.0, f"Rs. {yval:.1f}", ha="center", va="bottom", color="#f8fafc", fontweight="bold")

    plt.tight_layout()
    chart_path = os.path.join(ARTIFACTS_DIR, "krishi_model_metrics.png")
    plt.savefig(chart_path, facecolor=fig.get_facecolor(), edgecolor="none")
    plt.close()
    print(f"Saved metric chart to {chart_path}")
    print(f"KrishiSetu GBM Accuracy: {pathology_results['hgb']['acc']*100:.2f}%, Mandi R2: {mandi_results['gbr']['r2']:.4f}")


if __name__ == "__main__":
    main()
