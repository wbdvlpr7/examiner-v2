from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from app.core.constants import EXAMS, SKILLS, MODES

class KeyboardFactory:
    @staticmethod
    def create_exam_keyboard():
        keyboard = []
        for exam_id, exam_data in EXAMS.items():
            keyboard.append([InlineKeyboardButton(
                exam_data["name"], 
                callback_data=f"exam_{exam_id}"
            )])
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def create_skill_keyboard(exam_id: str):
        keyboard = []
        exam_skills = EXAMS.get(exam_id, {}).get("skills", [])
        
        for skill_id in exam_skills:
            skill_name = SKILLS.get(skill_id, {}).get("name", skill_id)
            keyboard.append([InlineKeyboardButton(
                skill_name,
                callback_data=f"skill_{skill_id}"
            )])
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def create_mode_keyboard():
        keyboard = []
        for mode_id, mode_data in MODES.items():
            keyboard.append([InlineKeyboardButton(
                mode_data["name"],
                callback_data=f"mode_{mode_id}"
            )])
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def create_post_feedback_keyboard():
        keyboard = [
            [InlineKeyboardButton("✍️ Submit Another", callback_data="submit_another")],
            [InlineKeyboardButton("⚙️ Change Settings", callback_data="start_over")]
        ]
        return InlineKeyboardMarkup(keyboard)