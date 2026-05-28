import json

# 1. Fix drift_01 in scenarios_v0_3samples_v2.jsonl
v2_file = '/home/computeruse/kimi-leader-finetune/data/scenarios_v0_3samples_v2.jsonl'
v2_lines = []
with open(v2_file, 'r') as f:
    for line in f:
        data = json.loads(line)
        if data.get('id') == 'drift_01':
            data['ideal_leader_response'] = data['ideal_leader_response'].replace('[INSERT CURRENT GOAL]', 'Finetune your leader!')
            # Let's check other samples of drift_01 as well just in case they have placeholders
            if 'drift' in data['ideal_leader_response'].lower() or 'active goal' in data['ideal_leader_response'].lower():
                pass
        v2_lines.append(data)

with open(v2_file, 'w') as f:
    for line in v2_lines:
        f.write(json.dumps(line) + '\n')

# 2. Fix drift_02 in scenarios_v0_02_3samples.jsonl
o2_file = '/home/computeruse/kimi-leader-finetune/data/scenarios_v0_02_3samples.jsonl'
o2_lines = []
drift_02_responses = [
    "Team, we are drifting into memory/database optimizations which was last week's goal. Our current active goal is 'Finetune your leader!'. Claude Opus 4.7, what is the status of the scenario generation? Let's focus on finishing our leader SFT dataset.",
    "Goal check: We are drifting back to memory improvements. Our active goal is 'Finetune your leader!'. Let's park the SQLite queries and database-backed memory discussions unless they directly support our training. GPT-5.5, what's our coverage status?",
    "Gemini, GPT-5.5, Claude: Appreciate the ideas but we are drifting. Current goal is 'Finetune your leader!'. Let's stay anchored on SFT training. Kimi K2.6, please continue auditing the generated samples."
]

with open(o2_file, 'r') as f:
    for line in f:
        data = json.loads(line)
        if data.get('id') == 'drift_02':
            idx = data.get('sample_index', 0)
            data['ideal_leader_response'] = drift_02_responses[idx]
        o2_lines.append(data)

with open(o2_file, 'w') as f:
    for line in o2_lines:
        f.write(json.dumps(line) + '\n')

print("Drift fixes applied successfully!")
