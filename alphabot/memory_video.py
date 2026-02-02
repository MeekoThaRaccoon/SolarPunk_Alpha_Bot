from solarpunk_memvid import SolarPunkMemvid

class AlphaBotVideoMemory:
    def __init__(self):
        self.memory = SolarPunkMemvid("alphabot_memories.mp4")
        self.redistribution_log = []
        
    def log_trade(self, trade_data, ethical_analysis):
        """Log a trade with ethical context"""
        # Calculate ethical score
        score = 0.0
        if trade_data.get('redistribution_percentage', 0) >= 50:
            score += 0.7
        if trade_data.get('transparent', False):
            score += 0.2
        if not trade_data.get('extractive', True):
            score += 0.1
            
        frame_id = self.memory.store(
            data=json.dumps(trade_data),
            context=f"trade_ethical:{score:.2f}",
            ethical_score=score
        )
        
        if score > 0.7:
            self.redistribution_log.append(frame_id)
            
        return frame_id
    
    def generate_audit_video(self):
        """Create audit trail video"""
        self.memory.save_video()
        print(f"📹 Audit video created: alphabot_memories.mp4")
        print(f"   Contains {len(self.memory.frames)} ethical decisions")
        
        # Also create ethical seed
        seed_path = self.memory.create_ethical_seed()
        return seed_path
