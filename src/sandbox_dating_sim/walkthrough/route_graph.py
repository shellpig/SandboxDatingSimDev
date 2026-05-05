from sandbox_dating_sim.schema.blueprint import EventBlueprint

def build_route_graph(bp: EventBlueprint) -> str:
    lines = ["```mermaid", "flowchart TD"]
    
    for ev in bp.events:
        # Node
        title = ev.title.replace('"', '\\"') if ev.title else ev.event_id
        lines.append(f'    {ev.event_id}["{title}"]')
        
    lines.append('    free_roam(("free_roam"))')
    
    endings = set()
    
    # Collect edges
    for ev in bp.events:
        for ch in ev.choices:
            ch_label = ch.choice_label[:20] + "..." if len(ch.choice_label) > 20 else ch.choice_label
            ch_label = ch_label.replace('"', '\\"')
            
            goto_target = None
            ending_id = None
            for r in ch.result:
                r = r.strip()
                if r.startswith("goto: "):
                    goto_target = r.split(": ")[1].strip()
                elif r.startswith("ending: "):
                    ending_id = r.split(": ")[1].strip()
            
            if goto_target:
                lines.append(f'    {ev.event_id} -- "{ch_label}" --> {goto_target}')
            elif ending_id:
                endings.add(ending_id)
                lines.append(f'    {ev.event_id} -- "{ch_label}" --> {ending_id}')
                
    for end in endings:
        lines.append(f'    {end}("{end}")')
        
    lines.append("```")
    lines.append("")
    lines.append("### Adjacency Summary")
    lines.append("")
    
    for ev in bp.events:
        lines.append(f"- **{ev.event_id}**")
        for ch in ev.choices:
            goto_target = None
            ending_id = None
            for r in ch.result:
                r = r.strip()
                if r.startswith("goto: "):
                    goto_target = r.split(": ")[1].strip()
                elif r.startswith("ending: "):
                    ending_id = r.split(": ")[1].strip()
            target = f"goto: {goto_target}" if goto_target else f"ending: {ending_id}"
            lines.append(f"  - [{ch.choice_id}] {ch.choice_label} -> {target}")
            
    return "\n".join(lines)
