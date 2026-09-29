"""Client module for EpisodicMemoryConsolidationDecayEngine (100% Python Standard Library)."""
import json
import time
import math
import uuid
from typing import Dict, Any, List, Optional

class EpisodicMemoryConsolidationDecayEngine:
    """Implements an Ebbinghaus retention decay curve combined with sleep-cycle
    episodic-to-semantic consolidation for long-term autonomous personal agents."""
    
    def __init__(self, half_life_hours: float = 24.0):
        self.half_life_hours = half_life_hours
        self.episodic_buffer: Dict[str, Dict[str, Any]] = {}
        self.semantic_persona: Dict[str, Dict[str, Any]] = {}
        
    def record_episodic_event(self, content: str, importance: float = 5.0, tags: Optional[List[str]] = None) -> Dict[str, Any]:
        """Records a new episodic memory item in the short-to-medium term buffer."""
        mem_id = f"ep_{uuid.uuid4().hex[:8]}"
        importance_clamped = max(1.0, min(10.0, float(importance)))
        record = {
            "id": mem_id,
            "content": content,
            "created_at": time.time(),
            "last_accessed": time.time(),
            "access_count": 1,
            "importance": importance_clamped,
            "tags": tags or [],
            "retention_score": 1.0,
            "consolidated": False
        }
        self.episodic_buffer[mem_id] = record
        return {
            "status": "success",
            "memory_id": mem_id,
            "importance": importance_clamped,
            "tags": record["tags"]
        }

    def apply_temporal_decay(self, elapsed_hours: float = 0.0) -> Dict[str, Any]:
        """Calculates Ebbinghaus retention: R = exp(-decay_rate * (t / strength)).
        Strength scales with importance and access frequency."""
        now = time.time()
        decayed_stats = []
        for mid, mem in self.episodic_buffer.items():
            delta_hours = elapsed_hours if elapsed_hours > 0 else (now - mem["last_accessed"]) / 3600.0
            # Stability factor S scales with importance (1-10) and access frequency
            stability = self.half_life_hours * (mem["importance"] / 5.0) * math.log2(mem["access_count"] + 1)
            retention = math.exp(-max(0.0, delta_hours) / max(1.0, stability))
            mem["retention_score"] = round(retention, 4)
            decayed_stats.append({"id": mid, "retention": mem["retention_score"], "content": mem["content"][:30]})
            
        return {
            "status": "success",
            "total_items": len(self.episodic_buffer),
            "sample_retention": decayed_stats[:5]
        }

    def consolidate_sleep_cycle(self, retention_threshold: float = 0.4) -> Dict[str, Any]:
        """Simulates a sleep consolidation phase: clusters high-importance or repeatedly accessed
        episodic memories into permanent semantic persona facts, marking episodic items as consolidated."""
        consolidated_facts = []
        tag_clusters: Dict[str, List[str]] = {}
        
        for mid, mem in self.episodic_buffer.items():
            if mem["retention_score"] >= retention_threshold or mem["importance"] >= 7.5:
                for tag in mem["tags"]:
                    tag_clusters.setdefault(tag, []).append(mem["content"])
                mem["consolidated"] = True
                
        # Synthesize into semantic persona
        for tag, items in tag_clusters.items():
            fact_id = f"fact_{tag}"
            summary = f"Synthesized insight from {len(items)} interactions: " + " | ".join(items[-3:])
            self.semantic_persona[fact_id] = {
                "fact_id": fact_id,
                "domain": tag,
                "summary": summary,
                "evidence_count": len(items),
                "updated_at": time.time()
            }
            consolidated_facts.append(summary)
            
        return {
            "status": "success",
            "cycle": "sleep_consolidation",
            "new_semantic_facts": len(consolidated_facts),
            "facts": consolidated_facts,
            "total_semantic_persona_size": len(self.semantic_persona)
        }

    def query_memory(self, query: str, top_k: int = 5) -> Dict[str, Any]:
        """Searches across both semantic persona facts and active episodic memories."""
        query_words = set(query.lower().split())
        scored_episodic = []
        now = time.time()
        
        for mid, mem in self.episodic_buffer.items():
            text = (mem["content"] + " " + " ".join(mem["tags"])).lower()
            overlap = sum(1 for w in query_words if w in text)
            if overlap > 0:
                mem["access_count"] += 1
                mem["last_accessed"] = now
                score = overlap * mem["retention_score"] * (mem["importance"] / 5.0)
                scored_episodic.append({
                    "id": mid,
                    "type": "episodic",
                    "score": round(score, 3),
                    "content": mem["content"],
                    "retention": mem["retention_score"]
                })
                
        scored_semantic = []
        for fid, fact in self.semantic_persona.items():
            text = (fact["domain"] + " " + fact["summary"]).lower()
            overlap = sum(1 for w in query_words if w in text)
            if overlap > 0:
                score = overlap * 2.0  # Semantic facts receive boosted retrieval priority
                scored_semantic.append({
                    "id": fid,
                    "type": "semantic",
                    "score": round(score, 3),
                    "content": fact["summary"]
                })
                
        all_results = sorted(scored_semantic + scored_episodic, key=lambda x: x["score"], reverse=True)[:top_k]
        return {
            "status": "success",
            "query": query,
            "total_matches": len(all_results),
            "results": all_results
        }

    def evict_decayed(self, min_retention: float = 0.15) -> Dict[str, Any]:
        """Purges decayed, unconsolidated ephemeral noise to conserve context window."""
        evicted = []
        for mid in list(self.episodic_buffer.keys()):
            mem = self.episodic_buffer[mid]
            if mem["retention_score"] < min_retention and not mem["consolidated"]:
                evicted.append(mid)
                del self.episodic_buffer[mid]
        return {
            "status": "success",
            "evicted_count": len(evicted),
            "remaining_buffer_size": len(self.episodic_buffer)
        }
