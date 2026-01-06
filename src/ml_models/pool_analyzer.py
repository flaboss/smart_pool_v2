
from .image_analyzer import ImageAnalyzer

class PoolAnalyzer:
    @staticmethod
    def analyze(params, t):
        """
        Analyze pool water parameters and return a result.
        
        Args:
            params (dict): Dictionary containing:
                - ph (float)
                - chlorine (float)
                - alkalinity (float)
                - cyanuric_acid (float)
                - observation (str)
                - has_image (bool)
            t (function): Translator function.
            
        Returns:
            dict: {
                "analysis": str,
                "recommendation": str
            }
        """
        analysis_points = []
        recommendations = []
        
        ph = float(params.get('ph', 0))
        chlorine = float(params.get('chlorine', 0))
        
        # pH Analysis
        if ph < 7.2:
            analysis_points.append(t("analysis.ph_low"))
            recommendations.append(t("analysis.rec_ph_up"))
        elif ph > 7.6:
            analysis_points.append(t("analysis.ph_high"))
            recommendations.append(t("analysis.rec_ph_down"))
        else:
            analysis_points.append(t("analysis.ph_ideal"))

        # Chlorine Analysis
        if chlorine < 1.0:
            analysis_points.append(t("analysis.chlorine_low"))
            recommendations.append(t("analysis.rec_chlorine_shock"))
        elif chlorine > 3.0:
            analysis_points.append(t("analysis.chlorine_high"))
            recommendations.append(t("analysis.rec_wait_chlorine"))
        else:
            analysis_points.append(t("analysis.chlorine_ideal"))

        # Alkalinity Analysis (Optional)
        alk_val = params.get('alkalinity')
        if alk_val:
            try:
                alkalinity = float(alk_val)
                if alkalinity < 80:
                    analysis_points.append(t("analysis.alkalinity_low"))
                    recommendations.append(t("analysis.rec_alkalinity_up"))
                elif alkalinity > 120:
                    analysis_points.append(t("analysis.alkalinity_high"))
                    recommendations.append(t("analysis.rec_alkalinity_down"))
            except ValueError:
                pass

        # Cyanuric Acid (Optional)
        cya_val = params.get('cyanuric_acid')
        if cya_val:
            try:
                cyanuric = float(cya_val)
                if cyanuric > 50:
                    analysis_points.append(t("analysis.cyanuric_high"))
                    recommendations.append(t("analysis.rec_drain_water"))
            except ValueError:
                pass

        # Image Analysis
        if params.get('has_image') and params.get('image_path'):
            # In a real scenario, we would pass the actual image path/data
            image_analysis = ImageAnalyzer.analyze(params.get('image_path'), t)
            analysis_points.append(image_analysis)

        # Construct Analysis text
        analysis_text = "\n".join([f"- {point}" for point in analysis_points])
        
        # Construct Recommendation text
        rec_text = "\n".join([f"{i+1}. {rec}" for i, rec in enumerate(recommendations)])
        
        if not recommendations:
            rec_text = t("analysis.water_balanced")

        start_text = t("analysis.result_intro")
        warning_text = t("analysis.safety_warning")

        return {
            "analysis": f"{start_text}\n\n{analysis_text}",
            "recommendation": f"{rec_text}\n\n{warning_text}"
        }
