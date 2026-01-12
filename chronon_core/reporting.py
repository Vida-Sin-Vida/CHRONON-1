# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~
# Project : CHRONON
# Version : 1.0
# Dev     : Brécheteau.B
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~

import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import datetime
import textwrap

class ReportGenerator:
    """
    Generates a standardized PDF report for CHRONON analysis.
    """
    
    @staticmethod
    def generate_pdf_report(filename, fig_plot, stats_results, metadata=None, description_text="", lang="fr"):
        """
        Creates a premium multi-page PDF report.
        """
        from app.gui.translations import TRANSLATIONS
        t = TRANSLATIONS[lang]["REPORT"]
        
        if metadata is None:
            metadata = {}
            
        # Design Constants
        COLOR_PRIMARY = "#0B2240"
        COLOR_ACCENT = "#1F6AA5"
        COLOR_SUCCESS = "#10B981"
        COLOR_WARNING = "#F59E0B"
        
        epsilon = stats_results.get('slope', 0.0)
        stderr = stats_results.get('stderr', 0.0)
        pval = stats_results.get('pval', 1.0)
        
        # Determine Status
        status_color = COLOR_SUCCESS
        status_text = "VALID"
        if pval > 0.05:
            status_color = COLOR_WARNING
            status_text = "NON SIG"
        
        # If fallback used
        summary_model = stats_results.get('model_summary', '')
        if "DEMING" in summary_model or "BOOTSTRAP" in summary_model:
             status_text += " (FALLBACK)"
             if status_color == COLOR_SUCCESS: 
                 status_color = COLOR_WARNING

        timestamp_str = datetime.datetime.now().strftime('%d/%m/%Y %H:%M')

        with PdfPages(filename) as pdf:
            # ================= PAGE 1: EXECUTIVE SUMMARY =================
            fig_sum = plt.figure(figsize=(8.27, 11.69)) # A4
            ax = fig_sum.add_axes([0, 0, 1, 1])
            ax.axis('off')
            
            # --- Header ---
            rect_header = plt.Rectangle((0, 0.85), 1, 0.15, transform=ax.transAxes, color=COLOR_PRIMARY)
            ax.add_patch(rect_header)
            
            ax.text(0.05, 0.92, "CHRONON", color='white', fontsize=30, weight='bold', transform=ax.transAxes)
            ax.text(0.05, 0.88, t["TITLE"], color='#9CA3AF', fontsize=14, transform=ax.transAxes)
            ax.text(0.95, 0.92, f"{timestamp_str}", color='white', fontsize=12, ha='right', transform=ax.transAxes)
            
            # --- Status Badge ---
            rect_status = plt.Rectangle((0.6, 0.78), 0.35, 0.05, transform=ax.transAxes, color=status_color, alpha=0.9)
            ax.add_patch(rect_status)
            ax.text(0.775, 0.805, status_text, color='white', fontsize=12, weight='bold', ha='center', va='center', transform=ax.transAxes)
            
            # --- Global Metrics (Hero Section) ---
            ax.text(0.05, 0.75, t["MAIN_RESULT"], fontsize=14, weight='bold', color=COLOR_PRIMARY, transform=ax.transAxes)
            
            # Box for Value
            rect_hero = plt.Rectangle((0.05, 0.60), 0.9, 0.12, transform=ax.transAxes, facecolor='#F3F4F6', edgecolor='#E5E7EB')
            ax.add_patch(rect_hero)
            
            ax.text(0.5, 0.68, f"{epsilon:.4e}", fontsize=36, weight='bold', ha='center', color=COLOR_PRIMARY, transform=ax.transAxes)
            ax.text(0.5, 0.62, f"± {stderr:.4e}", fontsize=14, ha='center', color='gray', transform=ax.transAxes)
            
            # --- Detailed Stats Table ---
            ax.text(0.05, 0.55, t["DETAILED_STATS"], fontsize=14, weight='bold', color=COLOR_PRIMARY, transform=ax.transAxes)
            
            cols = [t["TABLE_METRIC"], t["TABLE_VALUE"], t["TABLE_DESC"]]
            rows_data = [
                ["Model", summary_model, "WLS/Deming"],
                ["P-value", f"{pval:.6f}", "Prob (Null Hyp)"],
                ["CI 95%", f"[{stats_results.get('ci_low',0):.2e}, {stats_results.get('ci_high',0):.2e}]", "Confidence Interval"],
                ["R² Fit", f"{stats_results.get('r_squared', 'N/A')}", "Coeff. Determination"]
            ]
            
            table = plt.table(cellText=rows_data, colLabels=cols, cellLoc='left', loc='center', 
                              bbox=[0.05, 0.35, 0.9, 0.18], colColours=[COLOR_ACCENT]*3)
            table.auto_set_font_size(False)
            table.set_fontsize(10)
            table.scale(1, 1.5)
            # Style header
            for (row, col), cell in table.get_celld().items():
                if row == 0:
                    cell.set_text_props(color='white', weight='bold')
                    cell.set_edgecolor('white')
            
            # --- Metadata ---
            ax.text(0.05, 0.30, t["METADATA"], fontsize=14, weight='bold', color=COLOR_PRIMARY, transform=ax.transAxes)
            meta_str = "\n".join([f"• {k}: {v}" for k,v in metadata.items()])
            ax.text(0.05, 0.28, meta_str, fontsize=10, va='top', transform=ax.transAxes, family='monospace', bbox=dict(boxstyle="round,pad=0.5", facecolor="#F9FAFB", edgecolor="#E5E7EB"))

            # --- User Description / Conclusion ---
            if description_text:
                ax.text(0.05, 0.18, t["AUTO_DESC_TITLE"], fontsize=14, weight='bold', color=COLOR_PRIMARY, transform=ax.transAxes)
                wrapped_desc = "\n".join(textwrap.wrap(description_text, width=90))
                ax.text(0.05, 0.16, wrapped_desc, fontsize=11, style='italic', va='top', color='#374151', transform=ax.transAxes)

            # Disclaimer Footer
            ax.text(0.5, 0.02, t["DISCLAIMER"], 
                    ha='center', fontsize=8, color='gray', transform=ax.transAxes)
            
            pdf.savefig(fig_sum)
            
            # ================= PAGE 2: VISUALIZATION =================
            fig_plot.text(0.02, 0.98, t["Visualisation"], color='gray', fontsize=10, weight='bold')
            fig_plot.tight_layout(rect=[0, 0, 1, 0.95])
            pdf.savefig(fig_plot)
            
            # ================= PAGE 3: DIAGNOSTICS =================
            fig_diag = plt.figure(figsize=(8.27, 11.69))
            ax2 = fig_diag.add_axes([0, 0, 1, 1])
            ax2.axis('off')
            
            # Header
            rect_header2 = plt.Rectangle((0, 0.9), 1, 0.1, transform=ax2.transAxes, color=COLOR_ACCENT)
            ax2.add_patch(rect_header2)
            ax2.text(0.05, 0.94, t["DIAGNOSTICS"], color='white', fontsize=20, weight='bold', transform=ax2.transAxes)
            
            # Diagnostics Table
            diag_data = stats_results.get('diagnostics', {})
            if diag_data:
                d_rows = []
                for k, v in diag_data.items():
                    verdict = v.get('verdict', 'Unknown')
                    d_rows.append([k, f"{v.get('stat',0):.4f}", f"{v.get('pval',1):.4f}", verdict])
                
                ax2.text(0.05, 0.85, t["RESIDUALS_TESTS"], fontsize=14, weight='bold', color=COLOR_PRIMARY, transform=ax2.transAxes)
                d_table = plt.table(cellText=d_rows, colLabels=[t["TABLE_TEST"], t["TABLE_STAT"], "P-Value", t["TABLE_RESULT"]], 
                                    loc='center', bbox=[0.05, 0.65, 0.9, 0.15], colColours=[COLOR_PRIMARY]*4)
                d_table.auto_set_font_size(False)
                d_table.set_fontsize(10)
                d_table.scale(1, 1.5)
                for (row, col), cell in d_table.get_celld().items():
                    if row == 0:
                        cell.set_text_props(color='white', weight='bold')
            
            # Residuals Histogram
            residuals = stats_results.get('residuals')
            if residuals is not None:
                ax_hist = fig_diag.add_axes([0.15, 0.25, 0.7, 0.3])
                ax_hist.hist(residuals, bins=15, color=COLOR_ACCENT, alpha=0.7, edgecolor='black')
                ax_hist.set_title(t["HIST_TITLE"])
                ax_hist.set_xlabel("Residual")
                ax_hist.grid(True, alpha=0.3)
                
                ax2.text(0.5, 0.20, t["QQ_HINT"], ha='center', fontsize=10, style='italic', transform=ax2.transAxes)

            pdf.savefig(fig_diag)
            
        return True

# (~ ~ ~ Φ(x) ~ ~ ~
#  Benjamin Brécheteau | Chronon Field 2025
#  ~ ~ ~ ~ ~)
