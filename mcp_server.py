"""MCP JSON-RPC stdio server for genpark-episodic-memory-consolidation-decay-skill."""
import sys
import json
from client import EpisodicMemoryConsolidationDecayEngine

engine = EpisodicMemoryConsolidationDecayEngine()

def handle_call_tool(params):
    name = params.get("name")
    args = params.get("arguments", {})
    if name != "manage_episodic_memory":
        return {"error": f"Unknown tool '{name}'"}
        
    action = args.get("action")
    if action == "record_event":
        return engine.record_episodic_event(
            content=args.get("content", ""),
            importance=args.get("importance", 5.0),
            tags=args.get("tags", [])
        )
    elif action == "apply_temporal_decay":
        return engine.apply_temporal_decay(
            elapsed_hours=args.get("elapsed_hours", 0.0)
        )
    elif action == "consolidate_sleep_cycle":
        return engine.consolidate_sleep_cycle()
    elif action == "query_memory":
        return engine.query_memory(
            query=args.get("content", "")
        )
    elif action == "evict_decayed":
        return engine.evict_decayed()
    else:
        return {"error": f"Unknown action '{action}'"}

def main():
    if "--test" in sys.argv:
        print("[TEST] Running self-test for EpisodicMemoryConsolidationDecayEngine...")
        engine.record_episodic_event("User prefers dark roast coffee at 8 AM", importance=8.0, tags=["preference", "routine"])
        engine.record_episodic_event("Temporary delivery tracking number 9942", importance=2.0, tags=["transient"])
        engine.apply_temporal_decay(elapsed_hours=48.0)
        c_res = engine.consolidate_sleep_cycle()
        assert c_res["new_semantic_facts"] >= 1
        q_res = engine.query_memory("coffee")
        assert len(q_res["results"]) > 0
        print(f"[TEST] Success! Matches found: {len(q_res['results'])}")
        return

    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
            method = req.get("method")
            msg_id = req.get("id")
            
            if method == "tools/list":
                resp = {
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "result": {
                        "tools": [
                            {
                                "name": "manage_episodic_memory",
                                "description": "Manage agent episodic memory events, temporal decay calculation, sleep-cycle consolidation, and semantic persona extraction.",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "action": {"type": "string", "enum": ["record_event", "apply_temporal_decay", "consolidate_sleep_cycle", "query_memory", "evict_decayed"]},
                                        "content": {"type": "string"},
                                        "importance": {"type": "number"},
                                        "tags": {"type": "array", "items": {"type": "string"}},
                                        "elapsed_hours": {"type": "number"}
                                    },
                                    "required": ["action"]
                                }
                            }
                        ]
                    }
                }
            elif method == "tools/call":
                res = handle_call_tool(req.get("params", {}))
                resp = {
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "result": {"content": [{"type": "text", "text": json.dumps(res, indent=2)}]}
                }
            else:
                resp = {"jsonrpc": "2.0", "id": msg_id, "result": {}}
            print(json.dumps(resp), flush=True)
        except Exception as e:
            err_resp = {"jsonrpc": "2.0", "id": None, "error": {"code": -32000, "message": str(e)}}
            print(json.dumps(err_resp), flush=True)

if __name__ == "__main__":
    main()
