"""
AI Analyzer - Uses local LLM to analyze trading opportunities
"""

import json
from datetime import datetime

class AIAnalyzer:
    def __init__(self, config):
        self.config = config
        self.model = None
    
    def load_model(self):
        """Load the local LLM model"""
        try:
            from llama_cpp import Llama
            self.model = Llama(
                model_path=self.config['ai']['model_path'],
                n_ctx=self.config['ai']['context_size'],
                verbose=False
            )
        except ImportError:
            print("llama-cpp-python not installed, using simulated analysis")
    
    def analyze(self, opportunity):
        """Analyze a trading opportunity"""
        # If model isn't loaded, use simulated analysis
        if self.model is None:
            return self.simulated_analysis(opportunity)
        
        prompt = f"""
        Analyze this trading opportunity:
        
        Symbol: {opportunity['symbol']}
        Current Price: ${opportunity['price']}
        24h Change: {opportunity.get('change', 0)}%
        Type: {opportunity['type']}
        
        Should we take this trade? Consider:
        1. Risk level
        2. Potential reward
        3. Market conditions
        4. Ethical implications (SolarPunk values)
        
        Respond with JSON:
        {{
            "recommendation": "BUY/SELL/HOLD",
            "confidence": 1-10,
            "reason": "brief explanation",
            "ethical_check": "pass/fail"
        }}
        """
        
        try:
            response = self.model(prompt, max_tokens=200, temperature=0.7)
            analysis_text = response['choices'][0]['text']
            
            # Extract JSON from response
            if '```json' in analysis_text:
                analysis_text = analysis_text.split('```json')[1].split('```')[0]
            
            analysis = json.loads(analysis_text.strip())
            analysis['timestamp'] = datetime.now().isoformat()
            
            return analysis
            
        except Exception as e:
            print(f"AI analysis failed: {e}")
            return self.simulated_analysis(opportunity)
    
    def simulated_analysis(self, opportunity):
        """Fallback simulated analysis"""
        import random
        
        return {
            'recommendation': 'BUY' if random.random() > 0.5 else 'HOLD',
            'confidence': random.randint(5, 9),
            'reason': 'Simulated analysis',
            'ethical_check': 'pass',
            'timestamp': datetime.now().isoformat(),
            'simulated': True
        }
