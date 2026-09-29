"""Example usage for EpisodicMemoryConsolidationDecayEngine."""
import json
from client import EpisodicMemoryConsolidationDecayEngine

def main():
    print("=== Episodic Memory Consolidation & Decay Demo ===")
    mem = EpisodicMemoryConsolidationDecayEngine(half_life_hours=24.0)
    
    # 1. Record events
    mem.record_episodic_event("Prefers concise bullet points in executive summaries", importance=9.0, tags=["communication", "work"])
    mem.record_episodic_event("Ordered Italian dinner from Mario's", importance=3.0, tags=["food"])
    mem.record_episodic_event("Morning standup meeting is daily at 9:30 AM", importance=8.5, tags=["schedule", "work"])
    
    # 2. Simulate 36 hours elapsed
    print("
--- Applying 36 Hours Decay ---")
    decay_res = mem.apply_temporal_decay(elapsed_hours=36.0)
    print(json.dumps(decay_res, indent=2))
    
    # 3. Trigger sleep consolidation cycle
    print("
--- Triggering Sleep Consolidation ---")
    c_res = mem.consolidate_sleep_cycle()
    print(json.dumps(c_res, indent=2))
    
    # 4. Query hybrid memory
    print("
--- Querying 'summaries meeting' ---")
    q_res = mem.query_memory("summaries meeting")
    print(json.dumps(q_res, indent=2))

if __name__ == "__main__":
    main()
