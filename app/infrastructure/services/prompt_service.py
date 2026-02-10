from typing import Dict
import yaml
import os
from pathlib import Path

class PromptService:
    def __init__(self):
        self.prompts = self._load_prompts()
    
    def _load_prompts(self) -> Dict:
        """Load prompts from YAML files"""
        prompts = {}
        prompts_dir = Path(__file__).parent.parent.parent / "configs" / "prompts"
        
        # Load exam-specific prompts
        for exam_file in prompts_dir.glob("*.yaml"):
            exam_name = exam_file.stem
            with open(exam_file, 'r', encoding='utf-8') as f:
                prompts[exam_name] = yaml.safe_load(f)
        
        return prompts
    
    def get_writing_prompt(self, exam: str, mode: str, user_text: str) -> str:
        """Get writing evaluation prompt"""
        exam_prompts = self.prompts.get(exam, {})
        writing_prompts = exam_prompts.get("writing", {})
        
        if mode == "examiner":
            template = writing_prompts.get("examiner", "")
        else:  # coach
            template = writing_prompts.get("coach", "")
        
        return template.replace("{{ESSAY}}", user_text)
    
    def get_speaking_prompt(self, exam: str, mode: str, transcript: str, duration: int = None) -> str:
        """Get speaking evaluation prompt"""
        exam_prompts = self.prompts.get(exam, {})
        speaking_prompts = exam_prompts.get("speaking", {})
        
        if mode == "examiner":
            template = speaking_prompts.get("examiner", "")
        else:  # coach
            template = speaking_prompts.get("coach", "")
        
        # Replace placeholders
        template = template.replace("{{TRANSCRIPT}}", transcript)
        if duration:
            template = template.replace("{{DURATION}}", str(duration))
        
        return template
    
    def get_paraphrase_prompt(self, exam: str, mode: str, text: str) -> str:
        """Get paraphrase prompt"""
        exam_prompts = self.prompts.get(exam, {})
        paraphrase_prompts = exam_prompts.get("paraphrase", {})
        
        if mode == "examiner":
            template = paraphrase_prompts.get("examiner", "")
        else:  # coach
            template = paraphrase_prompts.get("coach", "")
        
        return template.replace("{{TEXT}}", text)

# Singleton instance
prompt_service = PromptService()