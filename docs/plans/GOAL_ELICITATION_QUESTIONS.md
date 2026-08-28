# Goal Elicitation Questions for Serious Chess Training

Welcome. This questionnaire is designed specifically for your training vision. We are building this AI chess tool for serious chess improvement—prioritizing depth, engine-grounded feedback, and practical decision-making over superficial polish or shiny UI elements.

To build a durable, accurate **`GOAL_BOOK.md`** that drives development step-by-step, we need exact clarity on how you think about your game and how you want to train. 

### How to complete this document:
- **Tier 1 (Foundations)**: Please answer these **6–8 foundational questions first**. They establish your context, workflow, and top priority.
- **Tier 2 (Job-by-Job Deep Dives)**: These are grouped under your 8 core training goals. Take them at your own pace—feel free to answer a few clusters at a time or respond in your own words.
- *Note*: If you aren't sure about any question, simply answer *"I don't know yet / let me discover this through testing."* We will use that as an explicit mandate to build small prototypes together.

---

## Tier 1 — Foundations & Core Prioritization
*Please answer these first to set the baseline architecture and MVP focus.*

### Q1. Chess Profile & Study Baseline
> What is your current rating (and on which platform/FIDE/USCF)? What are your primary opening repertoires as White and Black, typical time controls, and weekly game volume? How do you currently study chess (e.g., books, engine analysis, puzzle training, coach)?
- *Why this matters:* Calibrates engine evaluation depth, imports the correct PGN databases, and ensures opening node trees align with your actual play style.

I am rated around 2100-2200 in my opinion. Lichess rating swings from 2000 to 2100 and sometimes in 2200 or even goes low to around 1950+. 

### Q2. Walkthrough of a Real Game Experience
> Walk us through a recent game where you felt your current review/training process failed you. What happened during the game, and what would you have wanted this tool to show or drill with you—before the game, during review, or in post-game practice?
- *Why this matters:* Establishes the exact primary user workflow (pre-game prep vs. post-game autopsy vs. standalone drill session).
[Event "derdiedasdie's Study: Chapter 1"]
[Date "2026.07.26"]
[Result "*"]
[Variant "Standard"]
[ECO "D02"]
[Opening "Queen's Pawn Game: London System"]
[StudyName "derdiedasdie's Study"]
[ChapterName "Chapter 1"]
[ChapterURL "https://lichess.org/study/nDHE5UGd/lIRPmzuf"]
[Annotator "https://lichess.org/@/derdiedasdie"]
[UTCDate "2026.07.26"]
[UTCTime "07:09:31"]

1. d4 d5 2. Nf3 Nf6 3. Bf4 e6 4. e3 Bd6 { Here, after 4. ... Bd6, I am finding that most of my games go either go to a dry draw or not advantageous. I have two choices in 5. Ne5 and 5. Bg3. The former used to give me some good tactical positions after 5. Ne5 Bxe5, 6. dxe5 Nfd7, 7. Qg4 g6 etc. But 5. Ne5 O-O, 6. Bd3 c5, 7. c3 Qc7 (or Qe7), 8. Nd2 Nbd7, 9. Ndf3 b6 etc. with the knight at e5 becoming more of a burden than an advantage. After many exchanges, the ensuing positions are again dry and without hope for complexity and advantage. May be I should not play this opening or else I should find a pawn sac somewhere that could lead to some interesting positions. I think this position with 4. ... Bd6 don't offer such stuff. } 5. Ne5 (5. Bg3 O-O 6. Bd3 b6 7. Nbd2 Bb7 8. c3 Qe7 9. O-O Nbd7 10. Qe2 c5 11. Rad1) 5... Bxe5 (5... O-O 6. Bd3 c5 7. c3 Qc7 8. Nd2 Nbd7 9. Ndf3 b6 10. Qc2) 6. dxe5 Nfd7 7. Qg4 g6 8. h4 h5 9. Qg3 *

I would like to may be have an early pawn sacrifice to have a dynamic position early in the opening or may be even in the early middle game. I am even ready to say goodbye to this line with 4. ... Bd6 that leads to dry, equal or slightly worse positions. I am even hoping for material imbalance, sacs, sharp play that leads me to positions that offers Tal like complex play. I think I should switch to 1. e4 and open up the game more. Even I am open to completely new openings that lift me off of this boring play.


### Q3. The Single Highest-Impact Goal
> Looking at your 8 training goals (listed in Tier 2), if **only ONE feature could exist next month**, which single capability would move your practical playing strength the most, and why?
- *Why this matters:* Directly dictates Goal #1 for Sprint 1 in the leader's `GOAL_BOOK.md` and defines our initial MVP.

I want to identify the common mistakes that I make often. This includes tactical oversights, simplifications leading to a winning endgame, piece sacrifices leading to checkmate or winning positions, repeated opening mistakes etc.

### Q4. Automation vs. Personal Curation
> When generating training drills or weakness exercises, should positions be **automatically queued** directly from your engine diagnosis profiles, or do you want to **review and approve** candidate positions before adding them to your training deck?
- *Why this matters:* Determines whether backend engineering focuses on an automated queue pipeline or a interactive curation UI.
Let it be automated to a certain extent. I mean, once the positions are identified, I should be able to review and approve them before adding them to my training deck.

### Q5. Verification & Progress Tracking
> How do you want to see proof that your training is working over time? (e.g., tracking metric trends like reduced policy blindness, spaced repetition accuracy, periodic re-testing on missed themes, or win-rate in specific opening structures?)
- *Why this matters:* Defines the data schema required for long-term telemetry and diagnostic history tracking.
We will analyze the games played during the training phase to see if the common mistakes are reduced.
### Q6. The "Serious, Not Shiny" Standard
> In your experience, what makes a chess training feature feel like a genuine tool for improvement versus a superficial toy or gimmick? What specific visual or algorithmic elements build your trust in the training output?
- *Why this matters:* Sets strict design parameters to eliminate visual bloat, avoid gamified fluff, and focus purely on engine transparency and training signal.
I opt for speed of UI and not necessarily engine analysis (as analysis could take some time and thats ok) to be good than bulkier animations that do not add to the learning experience. 
### Q7. Practical Training Constraints
> What does a typical study session look like for you in terms of duration (e.g., 20 mins vs 2 hours), device environment (desktop vs mobile/tablet), and frequency per week?
- *Why this matters:* Sets performance budgets for backend node-search latency, batch size for position extraction, and layout responsiveness constraints.
Around 30 minutes to 1 hour, mostly train on desktop and play on desktop or mobile on lichess. I hope to train daily but realistically it will be 3-4 times a week. 

---

## Tier 2 — Per-Job Deep Dives
*Answer these in clusters or key areas of interest to detail each specific feature.*

---

### Job 1: "Steer a position towards a tactical landmine."

#### Q1.1 Landmine Definition & Criteria
> When you envision a "tactical landmine" position, what makes it a *good* landmine versus an unsound trap? Is it a position where your move looks quiet/innocuous but hides a forced sharp response, or a move where the opponent's engine policy is high but objectively loses to a narrow refutation?
- *Why this matters:* Unblocks the exact mathematical threshold for TS2 steering (e.g., filtering for high `policy_trap` and high `decisiveness` scores).
Like for instance in the fried liver attack, every move's accuracy means a win or loss. So is the case with Evans Gambit or some sharp lines with Nc3 in Guicco Piano. Such positions involves a sacrifice early in the game and takes the game to sharp where only a single or few responses leads to the survival. Such positions must also be complemented with the tactical theme study that arises from these positions. SO whenever a tactical steering finds a move that leads to a highly complex position, it must also complement (may be in a later analysis phase) with the already established tactical themes and training drills. Even further would be to find games in a master database or recent games or even from my own games where this particular tactical theme or landmine appears and is played. 
#### Q1.2 Steer Workflow
> In a live training session for steering, what sequence do you want to experience? (e.g., (1) Given a position, (2) Asked to find the move that steering into complexity, (3) Playing out 3-5 moves against LC0 to prove you survive the sharp landmine?)
- *Why this matters:* Dictates the interactive state machine for tactical steering drills in the frontend.
number 3 is the most needed, this will drill the principle. I need the position, and the ensuing continuation. On the training this must also ask me questions and if I am wrong must show me the continuation. In a later phase this continuation must be taught by giving me template positions that are related to the theme of the position which is found by tactical steering.
#### Q1.3 Success Criteria
> How will you evaluate whether landmine steering training was successful? What feedback from the board or engine confirms you navigated the landmine correctly?
- *Why this matters:* Clarifies what completion metrics to log after a user completes a landmine exercise.
Moves that are losing is certainly a red flag, so it must be pointed out. Winning moves that gives good advantage if the opponent plays a different move (tactical landmines are filled with opponent moving to disaster) etc.
---

### Job 2: "Find positions in the usual openings I play where I can take the game to complex positions, a tight rope walking game, where every decision matters."

#### Q2.1 Tightrope Opening Definition
> What distinguishes a sound "tightrope" position in your openings from an uncomfortably chaotic or losing position? How do you define "every decision matters" (e.g., only 1 move maintains evaluation, while all others drop >1.5 pawns)?
- *Why this matters:* Maps engine node search parameters (`narrowness` score and severe evaluation drops on non-top policy moves) to your specific opening ECO variations.
Every move matters. It can not be that the opponent has just one or two responses to avoid a complete disaster. On the other hand, me playing for an advantage can have one far superiour move to get a winning advantage. In some cases, let LC0 finds moves that will lead to a piece configuration typical of a common tactical theme. THis will help me to imagine in my mind positions involving such piece configuration. So, typical piece formations for tactics must be first laid down from lichess themes or other and then asked LC0 if it can be arrived at from my opening or position. This is immensely helpful as I can also be used as an explanation to why LC0 favours one move, becuase it leads to a tactical piece configuration rather than just a slight advantage. This will be something immensely helpful for me. Aiming for piece configurations that leads to tactics. This needs a study first from the published articles or even lichess tactical themes to find which configurations leads to what theme or tactical positions and then to use this information to find positions in my opening or from my game's opening. I don't have much knowledge of tactics, and this is one of the weakest part of my game. 
#### Q2.2 Opening Exploration Workflow
> When searching your opening repertoire for these sharp branching points, do you want to inspect a tree/graph view of your openings highlighting high-complexity nodes, or receive a curated list of sharp tactical positions filtered by ECO code?
- *Why this matters:* Decides whether to build an interactive repertoire tree viewer or a position feed component.
Yes, this would be nice. 
#### Q2.3 Success Criteria & MVP
> What minimal output from your opening analyzer would make you say: *"Yes, I am now equipped to steer my standard opening into a complex, high-stakes fight"*?
- *Why this matters:* Defines the minimal viable report needed for tightrope opening exploration.
A few positions that leads towards known tactical themes or dynamic piece configurations, piece or pawn sacrifice and still having excellent complensation or even without compensation but with the chance of opponent to commit disaster. And the position is such that even if I play a single move wrong, I can be at the receiving end of a disaster. 
---

### Job 3: "Train me such expected positions where a kind of tactical positions dominate and train me in those tactical themes so that I don't miss it."

#### Q3.1 Expected Repertoire Themes
> What specific tactical motifs dominate your primary openings (e.g., king-side sacrifices in Sicilian lines, central break tactics in French/Caro, piece activity in IQP positions)?
- *Why this matters:* Connects `lichess_tagger` motif tags directly to your preferred opening ECO structures.
King side sacrifices involving bishop, knight and queen, pawn sacs leading to greater dynamic play, exchange sacrifices, knight forks, double attacks in London type positions, kingside attack on kings gambit accepted when I play black, sacs to get knight cause havoc near the king etc.
#### Q3.2 Thematic Drill Workflow
> During a thematic drill session, do you want to train pure position solving, or play out the full continuation against LC0 until the tactical advantage is fully converted?
- *Why this matters:* Determines whether drills are single-move solution checkers or multi-ply interactive engine playouts.
Both. I want the principle be drilled in the thematic drill session and afterwards the full flow must be trained by playing out against LC0 so that I understand the flow of the game after I make the critical move. 
#### Q3.3 Mastery & Success Criteria
> How many successful repetitions or clean games in a specific tactical motif would convince you that you no longer miss that theme in expected opening positions?
- *Why this matters:* Sets the threshold for marking a tactical theme as "mastered" within the database.
3 would be fine, but it can be repeated over time. It is more about the quality of my understanding and recognition of the pattern in actual games or positions rather than just repeated correct moves. 
---

### Job 4: "I want to train to see how LC0 views a position."

#### Q4.1 Defining LC0's Vision
> When you say "see how LC0 views a position," which of LC0's internal signals gives you the most insight: (a) raw move policy probabilities (where the net naturally wants to look), (b) attention heatmaps (`saliency_absolute` showing active squares), (c) candidate ranking vs deep search eval, or (d) Win/Draw/Loss (WDL) expectations?
- *Why this matters:* Determines which visualization components (heatmaps, policy bar overlays, WDL meters) take precedence.
Raw probabilities, search eval and policy should be the primary focus. I am not sure how to make use of the heatmaps as I am not sure what theme or principle LC0 is looking at or figuring out when it forms these maps. But I think this is very interesting as I would understand it when I study more principles and figure out why by using these maps say with a LLM or even with a guide book that we could think of creating for this. 
#### Q4.2 Visualization & Drill Workflow
> How do you want to interact with LC0's viewpoint? Would you prefer a static inspection tool (overlaying attention/policy on the board), or a predictive exercise where you attempt to guess LC0's top candidate moves and attention hotspots before they are revealed?
- *Why this matters:* Distinguishes a passive analysis dashboard from an active prediction training mode.
I think a predictive exercise would be much more helpful for me to train my brain to think like LC0. 
#### Q4.3 Success Criteria
> What change in your over-the-board thought process would prove that you are starting to perceive board positions through LC0's lens?
- *Why this matters:* Establishes qualitative benchmarks for evaluating the clarity of LC0 visual overlays.
I would align with LC0's thinking process. I would be able to figure out why it is making certain moves, and I would be able to predict its top moves and the reasoning behind it. 
---

### Job 5: "Develop intuition like LC0."

#### Q5.1 Intuition vs. Inspection
> How do you distinguish between *analyzing* LC0's output (Job 4) and *developing intuition* like LC0 (Job 5)? Is intuition about fast policy recognition (instinctively feeling the right candidate moves without deep calculation)?
- *Why this matters:* Directly maps to policy-blindness metrics (measuring how closely your candidate move selection matches LC0's zero-shot policy distribution).
I think both are intertwined as when I develop intuition of LC0, I would be able to analyze its output much more effectively. Analyzing will also help me develop intuition. It is a cycle. LC0 can ask me specific questions, can quiz me on my intuition, and If I am wrong this would mean that there is a gap in my understanding. I can then go back and study the principles or themes that I am lacking in, and then come back and try again.
#### Q5.2 Intuition Building Workflow
> What format of drill best trains intuition for you: (a) speed-guessing LC0's top policy choice in 10 seconds per position, (b) comparing your candidate list of 3 moves against LC0's top 3, or (c) evaluating positional edge without calculating tactics?
- *Why this matters:* Defines the timing, scoring logic, and UI layout for fast-paced intuition building drills.
I think speed guessing the top policy choice in 10 seconds per position would be the best format for me to train my intuition.
#### Q5.3 Success Criteria & MVP
> What is the smallest daily or weekly exercise that would measurably decrease your "policy-blindness" score over a 30-day period?
- *Why this matters:* Establishes the MVP scope for intuition training.
A small daily exercise of 10 minutes of speed guessing the top policy choice in 10 seconds per position would be the best format for me to train my intuition.
---

### Job 6: "Correct the usual suspects pervading in my games."

#### Q6.1 Cataloging the "Usual Suspects"
> What are some examples of "usual suspects" in your games today? (e.g., missing backward pawn weakness moves, rushing under clock pressure, failing to spot opponent counter-threats, misevaluating rook endgames)?
- *Why this matters:* Provides concrete target patterns to verify against Diagnosis Profile aggregations (phase, clock, motif, concept findings).
Making same opening mistakes over and over. Missing same tactical themes, missing sacrifices and missing counter plays, playing passively and not utilizing the full potential of the position. 
#### Q6.2 Correction Workflow
> When the system identifies a recurring "usual suspect" in your recent games, how should it intervene? Should it create a targeted mini-set of your *exact game positions*, or generate *similar synthetic positions* featuring the same flaw?
- *Why this matters:* Determines whether post-game diagnosis outputs direct game PGN extracts or searches an external puzzle bank for identical tactical structures.
Creating a targeted mini-set of my exact game positions would be better as it would help me understand where I went wrong in the actual game.

#### Q6.3 Success Criteria
> How do you define a "usual suspect" as officially corrected? (e.g., 0 occurrences in your last 20 analyzed games, or 90%+ accuracy on spaced-repetition re-tests)?
- *Why this matters:* Establishes the lifecycle status logic (Active Flaw -> In Training -> Corrected) in the weakness tracker.
90% accuracy on spaced-repetition re-tests over a 30 day period.
---

### Job 7: "Tactical themes I am afraid to take, like a pawn sacrifice that Tal would make, and such positions happen over and over again with the same blindness."

#### Q7.1 Characterizing "Tal-Style" Hesitation
> What makes a pawn/piece sacrifice one that you are "afraid to take" or blind to? Is it because the compensation is dynamic/positional rather than a direct forced mate, or because it involves high risk where a single miscalculation loses?
- *Why this matters:* Filters TS2 steering output specifically for sacrificial moves (`had_tal_move = True`, high dynamic complexity, moderate policy probability, positive search eval).
I think this is because I am not able to see the final position where I am at advantage or not able to properly forsee an advantageous position arising out of it or a piece configuration or tactical theme that arises from it.
#### Q7.2 Hesitation-Breaking Drill Workflow
> Walk us through a session designed to cure this blindness. If the tool presents a position where a sound Tal-style sacrifice is available:
> 1. Should you be asked to identify whether a sacrifice exists?
> 2. Should you evaluate *why* you would hesitate to play it?
> 3. Should you play out the attacking side against LC0 defense to feel the dynamic compensation?
- *Why this matters:* Designs the step-by-step UX for psychological and tactical hesitation training.
I should be asked whether a sacrifice exists, I should be asked to identify the move and why I am hesitant to play it, I should be asked to evaluate the position after the sacrifice and see if I am at an advantage. I should asked to identify a specific tactical theme or idea by giving me a list of themes and I should pick one.
#### Q7.3 Success Criteria
> How will we verify that your blindness or fear toward dynamic pawn/piece sacrifices is actually disappearing?
- *Why this matters:* Defines telemetry metrics tracking your selection rate of high-complexity/sacrificial moves in diagnosis runs over time.
I should be tested with similar looking positions or piece configurations that have a similar idea. The degree of similarity should be proportional to the loss factor if I miss the solution. 
---

### Job 8: "Categorize my weaknesses and train me solve them one by one."

#### Q8.1 Weakness Taxonomy & Depth
> How granular should your weakness categorization be? Do you want broad categories (e.g., "Middlegame Tactics", "Time Pressure Blunders") or highly specific technical diagnoses (e.g., "French Defense Winawer: Missed 15. b4 Pawn Sac", "Rook Endgame 3v2 Policy Blindness")?
- *Why this matters:* Dictates backend profile aggregation logic and how weakness categories are grouped on your diagnostic summary board.
I want both, the former to get a general overview of my weaknesses and the latter to get specific technical diagnoses. 
#### Q8.2 One-by-One Curriculum Workflow
> How do you want to work through your weakness backlog? Would you prefer focusing on **one single weakness category per week** until mastered, or a blended spaced-repetition queue that presents items weighted by weakness severity?
- *Why this matters:* Unblocks the training session generator algorithm (single-subject focus vs. weighted spaced repetition).
Blended spaced-repetition queue that presents items weighted by weakness severity.
#### Q8.3 Success Criteria & MVP Dashboard
> What minimal dashboard layout or progress view would give you absolute clarity on: (1) what your current top weakness is, (2) your current drill progress, and (3) when it is marked as solved?
- *Why this matters:* Sets the design specification for the main weakness overview screen.
Weakness, opening repertoire, tactical theme that needs attention.