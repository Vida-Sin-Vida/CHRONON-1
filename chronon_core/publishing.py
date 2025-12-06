class PublicationChecker:
    """
    Automated 'Pre-flight' check for scientific publication.
    Verifies N, P-value consistency, Residuals, and Reproducibility.
    """
    
    def check_readiness(self, stats, qc_status, cci_score):
        """
        Returns a dict of checks.
        stats: dict with 'n', 'pval', 'slope', 'stderr', 'diagnostics'
        """
        checks = {}
        passed_all = True
        
        # 1. Sample Size
        n = stats.get('n', 0)
        passed = n >= 30
        checks['Sample Size'] = {
            'pass': passed,
            'msg': f"N={n} (Recommended > 30)"
        }
        if not passed: passed_all = False
        
        # 2. QC Status
        passed = (qc_status == "PASS")
        checks['QC Status'] = {
            'pass': passed,
            'msg': f"Status is {qc_status}"
        }
        if not passed: passed_all = False
        
        # 3. CCI Score
        # Strict for publication
        passed = cci_score >= 0.7
        checks['Consistency (CCI)'] = {
            'pass': passed,
            'msg': f"Score={cci_score:.2f} (Target > 0.7)"
        }
        if not passed: passed_all = False
        
        # 4. Statistical Significance (Warning only)
        # We can publish null results, so this is just informational
        pval = stats.get('pval', 1.0)
        is_sig = pval < 0.05
        checks['Significance'] = {
            'pass': True, # Always pass, just info
            'msg': f"p={pval:.4g} ({'Significant' if is_sig else 'Null Result'})"
        }
        
        # 5. Residual Normality (Critical)
        diag = stats.get('diagnostics', {})
        # Check specific test if available
        norm_test = diag.get('NormalitÃ© (Omnibus)') or diag.get('Normality')
        if norm_test:
            passed = norm_test.get('verdict') == "PASS"
            msg = f"p={norm_test.get('pval',0):.3f}"
        else:
            passed = False
            msg = "Test not run"
            
        checks['Residual Normality'] = {
            'pass': passed,
            'msg': msg
        }
        if not passed: passed_all = False
        
        # 6. StdErr Constraint
        # Ensure error isn't infinite or zero
        serr = stats.get('stderr', 0)
        passed = (serr > 0) and (serr != float('inf'))
        checks['Standard Error'] = {
            'pass': passed,
            'msg': "Valid finite error" if passed else "Invalid error"
        }
        if not passed: passed_all = False

        return passed_all, checks
