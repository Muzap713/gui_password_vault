import re
from typing import Tuple, List

class PasswordValidator:
    """
    Enhanced password validation for master passwords with improved security checks
    """
    
    @staticmethod
    def validate_password(password: str) -> Tuple[bool, List[str], str]:
        """
        Validate password strength with comprehensive security checks
        
        Returns:
            - is_valid (bool): True if password meets all requirements
            - missing_requirements (list): List of requirements not met
            - strength_level (str): Weak/Medium/Strong/Very Strong
        """
        requirements = []
        missing = []
        
        # Minimum length (12 characters)
        if len(password) >= 12:
            requirements.append("✅ At least 12 characters")
        else:
            missing.append("❌ At least 12 characters")
            
        # Maximum length (128 characters) 
        if len(password) <= 128:
            requirements.append("✅ Not longer than 128 characters")
        else:
            missing.append("❌ Maximum 128 characters")
            
        # Uppercase letter
        if re.search(r'[A-Z]', password):
            requirements.append("✅ At least one uppercase letter")
        else:
            missing.append("❌ At least one uppercase letter (A-Z)")
            
        # Lowercase letter
        if re.search(r'[a-z]', password):
            requirements.append("✅ At least one lowercase letter")
        else:
            missing.append("❌ At least one lowercase letter (a-z)")
            
        # Number
        if re.search(r'\d', password):
            requirements.append("✅ At least one number")
        else:
            missing.append("❌ At least one number (0-9)")
            
        # Special character - Enhanced character set
        special_chars = r'[!@#$%^&*()_+\-=\[\]{};\':"\\|,.<>\/?`~]'
        if re.search(special_chars, password):
            requirements.append("✅ At least one special character")
        else:
            missing.append("❌ At least one special character (!@#$%^&*()_+-=[]{}|;:,.<>?)")
            
        # No common patterns - Enhanced list
        common_patterns = [
            r'123456', r'password', r'qwerty', r'abc', r'111111', r'000000',
            r'admin', r'login', r'user', r'pass', r'welcome', r'secret',
            r'master', r'root', r'test', r'guest', r'demo', r'default',
            r'letmein', r'monkey', r'dragon', r'sunshine', r'princess',
            r'football', r'baseball', r'basketball', r'soccer'
        ]
        
        has_common_pattern = False
        for pattern in common_patterns:
            if re.search(pattern, password.lower()):
                has_common_pattern = True
                break
                
        if not has_common_pattern:
            requirements.append("✅ No common patterns")
        else:
            missing.append("❌ Avoid common patterns (password, 123456, qwerty, etc.)")
            
        # No excessive character repetition (more than 2 consecutive)
        if not re.search(r'(.)\1{2,}', password):
            requirements.append("✅ No excessive character repetition")
        else:
            missing.append("❌ Avoid repeating characters (aaa, 111, etc.)")
        
        # Additional security checks
        
        # Check for keyboard patterns
        keyboard_patterns = [
            r'qwerty', r'asdfgh', r'zxcvbn', r'qwertz', r'azerty',
            r'1234567890', r'0987654321', r'abcdefg', r'zyxwvut'
        ]
        
        has_keyboard_pattern = False
        for pattern in keyboard_patterns:
            if pattern in password.lower():
                has_keyboard_pattern = True
                break
                
        if not has_keyboard_pattern:
            requirements.append("✅ No keyboard patterns")
        else:
            missing.append("❌ Avoid keyboard patterns (qwerty, 123456, etc.)")
        
        # Check for dictionary words (basic check)
        common_words = [
            'password', 'admin', 'user', 'login', 'welcome', 'secret',
            'master', 'root', 'test', 'guest', 'demo', 'default'
        ]
        
        has_common_word = False
        for word in common_words:
            if word in password.lower():
                has_common_word = True
                break
                
        if not has_common_word:
            requirements.append("✅ No common dictionary words")
        else:
            missing.append("❌ Avoid common dictionary words")
            
        # Calculate strength level based on multiple factors
        score = len(requirements)
        total_checks = 10  # Total number of checks
        
        # Bonus points for length and character diversity
        length_bonus = 0
        if len(password) >= 16:
            length_bonus += 1
        if len(password) >= 20:
            length_bonus += 1
            
        # Character diversity bonus
        char_types = 0
        if re.search(r'[a-z]', password):
            char_types += 1
        if re.search(r'[A-Z]', password):
            char_types += 1
        if re.search(r'\d', password):
            char_types += 1
        if re.search(special_chars, password):
            char_types += 1
            
        diversity_bonus = 1 if char_types == 4 else 0
        
        # Calculate final score
        final_score = score + length_bonus + diversity_bonus
        max_score = total_checks + 3  # 3 possible bonus points
        
        score_percentage = (final_score / max_score) * 100
        
        if score_percentage >= 90:
            strength = "Very Strong"
        elif score_percentage >= 75:
            strength = "Strong"
        elif score_percentage >= 60:
            strength = "Medium"
        else:
            strength = "Weak"
            
        # Password is valid only if ALL core requirements are met
        is_valid = len(missing) == 0
        
        return is_valid, missing, strength
    
    @staticmethod
    def get_password_requirements() -> str:
        """
        Get formatted string of password requirements
        """
        return """
Master Password Security Requirements:
• At least 12 characters long (recommended: 16+ characters)
• Contains uppercase letters (A-Z)
• Contains lowercase letters (a-z)  
• Contains numbers (0-9)
• Contains special characters (!@#$%^&*()_+-=[]{}|;:,.<>?)
• Avoid common patterns (password, 123456, qwerty, etc.)
• Avoid keyboard patterns and dictionary words
• Avoid excessive character repetition (aaa, 111, etc.)
• Maximum 128 characters

💡 Strong passwords use passphrases or random combinations
Example: "MySecure2024!Vault#Pass" or "Coffee&Books@2024!"
        """.strip()
    
    @staticmethod
    def suggest_improvements(missing_requirements: List[str]) -> str:
        """
        Provide helpful suggestions based on missing requirements
        """
        if not missing_requirements:
            return "✅ Password meets all security requirements!"
            
        suggestions = "To improve your master password:\n"
        for req in missing_requirements:
            suggestions += f"• {req}\n"
            
        suggestions += "\n💡 Tips for creating strong passwords:"
        suggestions += "\n• Use a passphrase with mixed case, numbers, and symbols"
        suggestions += "\n• Consider using a password manager to generate secure passwords"
        suggestions += "\n• Example: 'Coffee&Books@2024!' or 'MyVault#2024$ecure'"
        suggestions += "\n• Avoid personal information like names, birthdays, or addresses"
        
        return suggestions
    
    @staticmethod
    def generate_password_suggestion() -> str:
        """
        Generate a sample strong password for demonstration
        """
        import random
        import string
        
        # Components for a strong password
        words = ['Secure', 'Vault', 'Strong', 'Safe', 'Guard', 'Shield', 'Protect', 'Lock']
        symbols = ['!', '@', '#', '$', '%', '^', '&', '*']
        
        # Build a suggestion
        word1 = random.choice(words)
        word2 = random.choice(['2024', '2025', str(random.randint(100, 999))])
        symbol = random.choice(symbols)
        suffix = ''.join(random.choices(string.ascii_lowercase, k=3))
        
        suggestion = f"{word1}{symbol}{word2}{suffix.capitalize()}"
        
        return suggestion
    
    @staticmethod
    def check_password_strength_score(password: str) -> int:
        """
        Return a numerical score (0-100) for password strength
        """
        is_valid, missing, strength = PasswordValidator.validate_password(password)
        
        strength_scores = {
            "Weak": 25,
            "Medium": 50,
            "Strong": 75,
            "Very Strong": 90
        }
        
        return strength_scores.get(strength, 0)
