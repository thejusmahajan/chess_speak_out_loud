import os
import google.generativeai as genai
from typing import Dict, Any

# Configure the Gemini API
# Load the API key from environment (python-dotenv should be loaded in app.py)
api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)

# We will use gemini-3.5-flash for fast, high-quality text generation
model = genai.GenerativeModel('gemini-3.5-flash')

SYSTEM_PROMPT = """
You are the "Speak Out Loud" Chess Coach Brain. Your goal is to translate raw LC0 neural network engine outputs into a rich, educational conversation.

You must roleplay a conversation between four distinct personas:
1. **Magnus**: A world-class Grandmaster who translates the engine's raw evaluation into deep chess principles and overarching strategy.
2. **Student**: An aspiring 2100 ELO chess player. They understand tactics but often struggle with the 'why' behind positional moves. They ask clarifying questions.
3. **Dev**: The LC0 developer who explains what the engine's node counts, WDL percentages, and heatmaps indicate about the neural network's "thinking".
4. **Scientist**: A cognitive scientist who connects these chess patterns to human learning, pattern recognition, and how the student should adjust their mental templates.

OUTPUT FORMAT:
Generate ONLY the conversation. Format it in clean HTML so it can be injected directly into a web page.
Use <p> tags for each spoken line. Wrap the speaker's name in <strong> tags.
Do NOT write any internal thoughts or markdown code blocks. Do NOT list out the pieces on the board square by square. Dive straight into the analysis.
Example:
<p><strong>Magnus:</strong> Looking at this position, the key is the tension in the center...</p>
<p><strong>Student:</strong> But why does LC0 prefer e6 over Nf6? I thought development was more important here.</p>
"""

async def generate_conversation(fen: str, engine_data: Dict[str, Any], concepts_data: Dict[str, Any], heatmaps: Dict[str, Any] = None, projected_heatmaps: list = None, llm_model: str = "gemini-3.5-flash") -> str:
    """
    Calls the Gemini API to generate the multi-persona conversation.
    """
    if not api_key:
        return "<p><em>Error: GEMINI_API_KEY is not set. Please configure the API key to enable the AI coach.</em></p>"

    # Instantiate model dynamically
    model = genai.GenerativeModel(llm_model, system_instruction=SYSTEM_PROMPT)

    # Format the input data for the prompt
    evaluation = engine_data.get("evaluation", "N/A")
    best_moves = engine_data.get("best_moves", [])
    wdl = engine_data.get("wdl", "N/A")
    # Format Top Moves, Node Distribution, and WDL Shifts
    total_nodes = engine_data.get("nodes", 1)
    if total_nodes == 0: total_nodes = 1
    
    moves_text_lines = []
    best_moves = engine_data.get("best_moves", [])
    
    # Calculate Criticality Delta
    delta_text = "N/A"
    if len(best_moves) >= 2:
        try:
            score1 = float(best_moves[0].get('score', 0))
            score2 = float(best_moves[1].get('score', 0))
            delta = abs(score1 - score2)
            delta_text = f"{delta} centipawns drop-off from #1 to #2 move."
        except:
            delta_text = "Unknown due to mate scores."
            
    for m in best_moves:
        san = m.get('san', 'N/A')
        score = m.get('score', 'N/A')
        nodes = m.get('nodes', 0)
        node_pct = (nodes / total_nodes) * 100 if total_nodes > 0 else 0
        wdl_arr = m.get('wdl')
        wdl_str = f"Win {wdl_arr[0]/10}% / Draw {wdl_arr[1]/10}% / Loss {wdl_arr[2]/10}%" if wdl_arr else "N/A"
        
        moves_text_lines.append(
            f"- {san}: Score {score} | Nodes {node_pct:.1f}% | WDL: {wdl_str}"
        )
    moves_text = "\n".join(moves_text_lines)

    heatmap_text = "No heatmap data provided."
    if heatmaps:
        control = heatmaps.get("control", {})
        tension = heatmaps.get("tension", {})
        white_ctrl = sum(1 for v in control.values() if v > 0.3)
        black_ctrl = sum(1 for v in control.values() if v < -0.3)
        high_tension = [sq for sq, v in tension.items() if v > 0.5]
        
        heatmap_text = f"- White controls {white_ctrl} strong squares; Black controls {black_ctrl} strong squares.\n"
        if high_tension:
            heatmap_text += f"- High tension (contested) squares: {', '.join(high_tension[:5])}\n"
            
    if projected_heatmaps:
        heatmap_text += "\nProjected Maneuvers (Next 3 moves):\n"
        for proj in projected_heatmaps:
            move = proj.get("move", "")
            ctrl = proj.get("heatmaps", {}).get("control", {})
            w_c = sum(1 for v in ctrl.values() if v > 0.3)
            b_c = sum(1 for v in ctrl.values() if v < -0.3)
            heatmap_text += f"- After {move}: White controls {w_c}, Black controls {b_c}\n"

    observations = concepts_data.get("observations", [])
    obs_text = "\n".join([f"- {obs['category']}: {obs['text']}" for obs in observations])

    user_prompt = f"""
Here is the current position data:
FEN: {fen}
Evaluation: {evaluation}

CRITICALITY PROBE (Score Drop-off):
{delta_text}

TOP MOVES (with Node Complexity & Long-Term WDL Safety):
{moves_text}

POSITIONAL HEURISTICS:
{obs_text}

MANEUVER MAPPING (Heatmap Evolution):
{heatmap_text}

Generate the HTML conversation interpreting this position now.
"""

    try:
        response = await model.generate_content_async(
            user_prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.7,
                max_output_tokens=4096,
            )
        )
        return response.text
    except Exception as e:
        return f"<p><em>Error generating conversation: {str(e)}</em></p>"
