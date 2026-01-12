# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~
# Project : CHRONON
# Version : 1.0
# Dev     : Brécheteau.B
# ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~

from app.gui.translations import TRANSLATIONS

class ScientificInterpreter:
    """
    The 'Scientific Brain' of CHRONON.
    Analyzes statistical results to produce human-readable conclusions.
    """
    
    def interpret(self, stats, qc_status, lang="fr"):
        """
        Main entry point for interpretation.
        """
        t = TRANSLATIONS[lang]["INTERPRETATION"]
        
        result = {
            'conclusion_short': "",
            'summary_5_lines': "",
            'evaluation': "",
            'publication_text': "",
            'signal_strength': "NONE"
        }
        
        slope = stats.get('slope', 0.0)
        pval = stats.get('pval', 1.0)
        n = stats.get('n', 0)
        
        # 1. Determine Signal Strength
        prefix = ""
        if qc_status != "PASS":
            prefix = "[QC FAIL] "
            
        if pval < 0.001:
            result['conclusion_short'] = f"{prefix}{t['STRONG']}"
            result['evaluation'] = t['EVAL_STRONG']
            result['signal_strength'] = "STRONG"
        elif pval < 0.05:
            result['conclusion_short'] = f"{prefix}{t['WEAK']}"
            result['evaluation'] = t['EVAL_WEAK']
            result['signal_strength'] = "WEAK"
        elif pval < 0.10:
            result['conclusion_short'] = f"{prefix}{t['TRACE']}"
            result['evaluation'] = t['EVAL_TRACE']
            result['signal_strength'] = "TRACE"
        else:
            result['conclusion_short'] = f"{prefix}{t['NULL']}"
            result['evaluation'] = t['EVAL_NULL']
            result['signal_strength'] = "NULL"
            
        if qc_status != "PASS":
            result['evaluation'] += t['NOTE_QC_FAIL']

        # 2. Five Line Summary
        res_diag = stats.get('diagnostics', {})
        diag_problems = []
        for k, v in res_diag.items():
            if v.get('verdict') == "FAIL":
                diag_problems.append(k)
        
        diag_txt = t['DIAG_OK'] if not diag_problems else f"{t['DIAG_WARN']}{', '.join(diag_problems)}."
        rec_txt = t['REC_PUBLISH'] if result['signal_strength'] in ['STRONG', 'WEAK'] and not diag_problems else t['REC_CHECK']

        result['summary_5_lines'] = (
            f"1. {t['QC_STATUS']}: {qc_status}\n"
            f"2. {t['SLOPE_OBS']}: {slope:.2e} (p={pval:.4f})\n"
            f"3. {t['INTENSITY']}: {result['signal_strength']}\n"
            f"4. {t['MODEL_RELIABILITY']}: {diag_txt}\n"
            f"5. {t['RECOMMENDATION']}: {rec_txt}"
        )
        
        # 3. Publication Paragraph
        terms = t["PUB_TERMS"]
        
        sig_word = terms["significant"] if pval < 0.05 else terms["non-significant"]
        diag_res = terms["confirmed"] if not diag_problems else f"{terms['issues']}"
        qc_res = terms["passed"] if qc_status=='PASS' else terms["failed"]
        
        result['publication_text'] = t["PUB_TEMPLATE"].format(
            n=n,
            qc_res=qc_res,
            qc_status=qc_status,
            sig_word=sig_word,
            slope=slope,
            stderr=stats.get('stderr', 0),
            pval=pval,
            diag_res=diag_res
        )
        
        return result

# (~ ~ ~ Φ(x) ~ ~ ~
#  Benjamin Brécheteau | Chronon Field 2025
#  ~ ~ ~ ~ ~)
