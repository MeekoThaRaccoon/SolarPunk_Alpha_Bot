"""
AI Analyzer - Uses local LLM to analyze trading opportunities
"""

import json
from typing import Dict, Any, List
import logging
from datetime import datetime
from llama_cpp import Llama
import yaml

logger = logging.getLogger(__name__)

class AIAnalyzer:
    """Analyzes opportunities using local LLM"""
    
    def __init__(self, config):
        self.config = config
        self.model = None
        self.prompts = self.load_prompts()
        
    def load_prompts(self) -> Dict[str, str]:
        """Load analysis prompts from configuration"""
        prompts = {
            'market_analysis': """Analyze this trading opportunity:

Symbol: {symbol}
Market Type: {market_type}
Current Price: ${price}
24h Change: {change}%
Volume: {volume}
Volatility: {volatility}%

Additional Data:
{metadata}

Please provide:
1. Brief analysis of what's happening
2. Potential catalysts or risks
3. Trading recommendation (BUY/SELL/HOLD) with confidence (1-10)
4. Ethical considerations (SolarPunk perspective)
5. Suggested position size (percentage of portfolio)

Format your response as JSON:
{{
  "analysis": "brief explanation",
  "catalysts": ["list", "of", "catalysts"],
  "risks": ["list", "of", "risks"],
  "recommendation": "BUY/SELL/HOLD",
  "confidence": 7,
  "ethical_considerations": "SolarPunk perspective",
  "position_size": 0.05
}}""",
            
            'risk_assessment': """Assess the risks for this trade:
{context}

What could go wrong? Consider:
- Market manipulation
- Liquidity issues
- Regulatory changes
- Technical failures
- Ethical concerns""",
            
            'ethical_check': """SolarPunk Ethical Check:
Trade: {trade_details}

Questions:
1. Does this trade exploit anyone?
2. Does it align with regenerative economics?
3. Could it harm vulnerable communities?
4. Does it concentrate or distribute wealth?
5. Would you be proud to explain this trade to your community?"""
        }
        
        # Override with config prompts if available
        if 'ai' in self.config and 'prompts' in self.config['ai']:
            prompts.update(self.config['ai']['prompts'])
        
        return prompts
    
    def initialize_model(self):
        """Initialize the local LLM"""
        if self.model is None:
            model_path = self.config.get('ai', {}).get('model_path', './models/llama-3.2-7b-q4_k_m.gguf')
            
            try:
                logger.info(f"Loading model from {model_path}")
                self.model = Llama(
                    model_path=model_path,
                    n_ctx=self.config.get('ai', {}).get('context_size', 4096),
                    n_threads=4,
                    verbose=False
                )
                logger.info("Model loaded successfully")
            except Exception as e:
                logger.error(f"Failed to load model: {e}")
                raise
    
    def analyze(self, opportunity: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze a trading opportunity"""
        try:
            self.initialize_model()
            
            # Prepare prompt
            prompt = self.prompts['market_analysis'].format(
                symbol=opportunity.get('symbol', 'Unknown'),
                market_type=opportunity.get('market_type', 'unknown'),
                price=opportunity.get('current_price', 0),
                change=opportunity.get('change_24h', 0),
                volume=opportunity.get('volume', 0),
                volatility=opportunity.get('volatility', 0),
                metadata=json.dumps(opportunity.get('metadata', {}), indent=2)
            )
            
            # Generate analysis
            response = self.model(
                prompt,
                max_tokens=self.config.get('ai', {}).get('max_tokens', 512),
                temperature=self.config.get('ai', {}).get('temperature', 0.7),
                stop=["\n\n", "###", "```"]
            )
            
            analysis_text = response['choices'][0]['text'].strip()
            
            # Parse JSON response
            try:
                # Extract JSON from response (might have markdown)
                if '```json' in analysis_text:
                    analysis_text = analysis_text.split('```json')[1].split('```')[0]
                elif '```' in analysis_text:
                    analysis_text = analysis_text.split('```')[1].split('```')[0]
                
                analysis = json.loads(analysis_text)
                
                # Add metadata
                analysis['timestamp'] = datetime.now().isoformat()
                analysis['model_used'] = self.config.get('ai', {}).get('model_path', 'unknown')
                analysis['opportunity_id'] = f"{opportunity.get('symbol')}_{datetime.now().strftime('%Y%m%d_%H%M')}"
                
                # Perform ethical check
                ethical_result = self.ethical_check(opportunity, analysis)
                analysis['ethical_check'] = ethical_result
                
                # Only approve if ethical check passes
                if not ethical_result.get('passed', False):
                    analysis['recommendation'] = 'HOLD'
                    analysis['confidence'] = 0
                    analysis['ethical_override'] = True
                
                logger.info(f"Analysis complete for {opportunity.get('symbol')}: {analysis.get('recommendation')} with confidence {analysis.get('confidence')}")
                return analysis
                
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse JSON from model response: {e}")
                logger.debug(f"Raw response: {analysis_text}")
                
                # Return fallback analysis
                return {
                    'analysis': 'Failed to parse AI response',
                    'recommendation': 'HOLD',
                    'confidence': 0,
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                }
                
        except Exception as e:
            logger.error(f"Error in AI analysis: {e}")
            return {
                'analysis': f'Analysis failed: {str(e)}',
                'recommendation': 'HOLD',
                'confidence': 0,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def ethical_check(self, opportunity: Dict[str, Any], analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Perform SolarPunk ethical check on trade"""
        try:
            prompt = self.prompts['ethical_check'].format(
                trade_details=json.dumps({
                    'symbol': opportunity.get('symbol'),
                    'recommendation': analysis.get('recommendation'),
                    'potential_impact': 'Unknown'
                }, indent=2)
            )
            
            response = self.model(
                prompt,
                max_tokens=256,
                temperature=0.3,
                stop=["\n\n"]
            )
            
            ethical_text = response['choices'][0]['text'].strip()
            
            # Simple heuristic: look for concerning phrases
            concerning_phrases = [
                'exploit', 'harm', 'vulnerable', 'unethical',
                'questionable', 'concern', 'avoid', 'warning'
            ]
            
            concerning = any(phrase in ethical_text.lower() for phrase in concerning_phrases)
            
            return {
                'passed': not concerning,
                'reasoning': ethical_text,
                'concerning_phrases_found': concerning_phrases if concerning else [],
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error in ethical check: {e}")
            return {
                'passed': False,  # Fail safe: if check fails, don't trade
                'reasoning': f'Ethical check failed: {str(e)}',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def batch_analyze(self, opportunities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Analyze multiple opportunities (placeholder for optimization)"""
        results = []
        
        for opp in opportunities:
            result = self.analyze(opp)
            results.append({
                'opportunity': opp,
                'analysis': result
            })
            
            # Rate limiting
            import time
            time.sleep(1)
        
        return results
