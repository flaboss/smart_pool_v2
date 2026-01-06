
class ImageAnalyzer:
    @staticmethod
    def analyze(image_path: str, t) -> str:
        """
        Analyze the pool water image using basic heuristics on pixel data.
        """
        if not image_path:
            return ""

        try:
            from PIL import Image, ImageStat
            
            with Image.open(image_path) as img:
                # Resize to speed up processing
                img = img.resize((100, 100))
                # Convert to RGB
                img = img.convert('RGB')
                
                # Get average color
                stat = ImageStat.Stat(img)
                r, g, b = stat.mean[:3]
                
                # Heuristics
                # Green water (Algae)
                # Significantly more Green than Blue and Red, or Green dominant
                if g > r and g > b and g > 50:
                    # Additional check: Green should be noticeably higher than Blue
                    if (g - b) > 10:
                        return t("analysis.image_result_green")

                # Muddy/Dirty (Brownish)
                # Read dominant, Blue low
                # Brown is often low Blue, higher Red/Green
                if r > b and g > b and r > 50:
                    # Check for "earthy" tones
                    if abs(r - g) < 30 and (r - b) > 20: 
                         return t("analysis.image_result_muddy")
                
                # Clear Water
                # Usually Blue dominant or balanced light colors (if liner is blue/white)
                # Or just high brightness with Blue dominant
                # Default to clear if no other defects found
                return t("analysis.image_result_clear")

        except ImportError:
            # Fallback if PIL is not installed
            print("PIL not installed, skipping image analysis")
            return ""
        except Exception as e:
            print(f"Error analyzing image: {e}")
            return ""
