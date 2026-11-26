# 🎬 DevMind: Master Video Recording & Demo Script

> **Video Title:** DevMind — The Autonomous Agentic AI Software Self-Healing Engine  
> **Presenter:** Kanduri Avinash  
> **Target Video Length:** ~8 to 10 Minutes  
> **Format:** Screen Recording with Voiceover (or PiP Webcam in corner)

---

## 🛠️ Pre-Recording Setup (2 Minutes Before Hitting Record)

1. **Browser Windows to Have Open:**
   - **Tab 1:** DevMind Dashboard → `http://localhost:8501`
   - **Tab 2:** QuickCart Store → Open `c:\TECH\S5\TEXT ANALYTICS\PROJECT\quickcart\index3.html` in Chrome/Brave/Edge
   - **Tab 3:** Cricket Scorer Pro → Open `c:\TECH\S5\TEXT ANALYTICS\PROJECT\cricket-scorer-pro\index.html`
2. **Initial State Check:**
   - In DevMind (`http://localhost:8501`), select **`QuickCart · JavaScript cart-reload persistence bug`** and click **`[ 🔄 Reset Website to Buggy State ]`** so the cart bug is active.
   - Select **`Cricket scorer · JavaScript ball-count bug`** and click **`[ 🔄 Reset Website to Buggy State ]`** so the double-ball bug is active.
3. **Screen Resolution:** 1080p (1920x1080) for crisp text. Zoom browser to 110% if code font looks small.

---

## ⏱️ Video Timeline Overview

```
0:00 ─── 1:15  [Act 1]  The Hook & The Problem with Modern Debugging
1:15 ─── 2:30  [Act 2]  Under The Hood: Text Analytics, Hybrid RAG, & Agentic AI
2:30 ─── 5:30  [Act 3]  LIVE DEMO 1: QuickCart Real E-Commerce Persistence Bug
5:30 ─── 8:00  [Act 4]  LIVE DEMO 2: Cricket Scorer JavaScript Over-Calculation Bug
8:00 ─── 9:15  [Act 5]  Safety First: 3-Iteration Halting Boundary & Enterprise Security
9:15 ─── 10:00 [Act 6]  Summary, 180 Tests Verification, & Outro
```

---

## 🎥 Scene-by-Scene Recording Script

---

### ACT 1: The Hook & Introduction (0:00 – 1:15)

**Visual on Screen:**  
*Start on the DevMind cosmic dashboard (`http://localhost:8501`) with the animated galaxy background.*

**Speaker (Energetic, Confident):**
> *"Every software engineer knows this pain: you get a bug report in production, and you spend hours reading through thousands of lines of code, tracing errors, writing patches, and praying you didn't break anything else.
> 
> Many people try copying errors into ChatGPT. But standard LLMs have huge blind spots: they hallucinate, they don't know if their code actually compiles, and running AI-generated code directly on your computer is a massive security hazard.
> 
> Welcome to **DevMind** — an autonomous, Agentic AI software self-healing system powered by **Text Analytics, Hybrid RAG, and isolated Docker verification**.
> 
> Today, I'm going to demonstrate DevMind solving real bugs live across two separate production web applications: a multi-page e-commerce website called **QuickCart**, and a live sports app called **Cricket Scorer Pro**. Let's dive in!"*

---

### ACT 2: How DevMind Works Under the Hood (1:15 – 2:30)

**Visual on Screen:**  
*Scroll through the DevMind dashboard tabs (`Analyze and repair`, `Run history`, `Guide`). Show the parameter badges and telemetry.*

**Speaker:**
> *"Before we trigger the repairs, let's understand how DevMind works. DevMind is not just another LLM prompt wrapper. It is a multi-stage autonomous pipeline:
> 
> 1. **Text Analytics & Parsing:** When an error or issue is reported, DevMind parses stack traces, extracts error signatures, and normalizes identifiers.
> 2. **Hybrid RAG Retrieval:** Instead of dumping an entire 100,000-line codebase into an expensive LLM context window, DevMind uses **Hybrid Retrieval**:
>    - Lexical **BM25** for exact variable and function names.
>    - Dense **Cosine Similarity** via neural embeddings for conceptual matching.
>    - Fused using **Reciprocal Rank Fusion (RRF with $k=60$)** to pinpoint the exact 15 lines of buggy code.
> 3. **The Agentic ReAct Loop:** DevMind formulates a plan, generates a unified diff, and mounts it into a **disposable, non-root Docker container**.
> 4. **Self-Correction & Reflection:** If tests fail inside the container, DevMind reads the compiler error, reflects, and tries again.
> 5. **Human Review Gate:** And most importantly — DevMind **never touches your files silently**. It waits for human approval before applying changes to disk."*

---

### ACT 3: LIVE DEMO 1 — QuickCart Real E-Commerce Website (2:30 – 5:30)

#### Step 1: Show the Bug Live in QuickCart
**Visual on Screen:**  
*Switch to Tab 2 (`quickcart/index3.html`). Show the full store with all banners, product sliders, and deal cards loading crisply.*

**Speaker:**
> *"Here is our first target: **QuickCart**, a modern e-commerce web application with hundreds of products and interactive shopping carts.
> 
> Let's test the shopping cart right now.  
> I'll find a product — say, this luxury bag or sports shoe — and click **'Add to Cart'**.  
> Notice the cart badge at the top right: it increments to **1**. The item is in our cart!
> 
> But watch what happens when a customer refreshes the page or navigates away.  
> *(Press `F5` / Ctrl+R to reload the page)*  
> Look at the cart badge: **It reset back to 0!** The cart items vanished!
> 
> Why? Because while items are saved in browser `localStorage`, the web page forgot to reload them when the window loads. Let's fix this using DevMind."*

#### Step 2: Run DevMind Repair
**Visual on Screen:**  
*Switch back to DevMind (`http://localhost:8501`). In 'Load a demo case', select **`QuickCart · JavaScript cart-reload persistence bug`**.*

**Speaker:**
> *"Now we head over to DevMind.  
> In the demo dropdown, I select: **`QuickCart · JavaScript cart-reload persistence bug`**.  
> DevMind auto-populates the repository folder and the test runner: `node`.  
> We choose mode: **`Repair and test in Docker`**, and click **`Repair and run tests`**!"*

*(Click button. Point mouse to the live progress indicators)*

> *"Watch the live agent execution in real-time:
> - **Stage 1:** Text Analytics parses the bug report.
> - **Stage 2:** Hybrid RAG scans all files and localizes `quickcart/index3.html` around line 2530.
> - **Stage 3:** The Agent diagnoses that inside `window.addEventListener('load')`, the initialization function `loadCartFromStorage()` was omitted.
> - **Stage 4:** DevMind spins up an isolated Docker container, applies the candidate diff, and runs `cart-reload.test.cjs`.
> - **Test Result:** All assertions pass! Exit code 0!"*

#### Step 3: The Human Review Gate & Live Verification
**Visual on Screen:**  
*Scroll down to show the Candidate Patch diff viewer and the prominent **Human Review Gate** callout.*

**Speaker:**
> *"Notice this critical safety feature: even though automated tests passed in the container, DevMind halts and asks:  
> **'Should DevMind update the code in your files?'**  
> 
> It shows us the exact unified diff:  
> At line 2530, it inserts `loadCartFromStorage();`.  
> Our host files on disk are still untouched. Now, as the human engineer, I click:  
> **`[ ✅ Yes, Update Code in Files ]`**!"*

*(Click the green button. Show the success banner: 'Target file index3.html updated successfully!')*

> *"The file is updated! Let's verify it live in the browser.  
> *(Switch back to QuickCart tab)*  
> I reload QuickCart (`F5`).  
> I click **'Add to Cart'** on an item → Cart shows **1**.  
> Now I hit **Refresh** (`F5`) again...  
> **BOOM! The cart badge remains 1!** The item is still there! The cart persistence bug is completely solved!"*

*(Optional: Point to the `[ 🔄 Reset Website to Buggy State ]` button in DevMind to show that instructors can reproduce the bug anytime).*

---

### ACT 4: LIVE DEMO 2 — Cricket Scorer Web App (5:30 – 8:00)

#### Step 1: Show the Bug Live in Cricket Scorer
**Visual on Screen:**  
*Switch to Tab 3 (`cricket-scorer-pro/index.html`). Show the scoreboard interface with score, wickets, and overs.*

**Speaker:**
> *"Now let's look at our second real-world application: **Cricket Scorer Pro**, a live JavaScript sports match scoring engine.
> 
> In cricket, an over consists of 6 legal deliveries.  
> Let's start scoring a match.  
> Watch the ball count closely. When the batsman scores 1 run, the ball count should increment by 1.  
> But watch what happens when I click **'1 Run'**:  
> *(Click 1 run button)*  
> Look at the overs display: **It recorded 2 balls instead of 1!**  
> If I score another ball, it jumps to 4 balls! An entire 6-ball over ends after only 3 deliveries!  
> That's a game-breaking bug in `script.js`."*

#### Step 2: DevMind Self-Healing
**Visual on Screen:**  
*Switch to DevMind (`http://localhost:8501`). Select **`Cricket scorer · JavaScript ball-count bug`** and click **`Repair and run tests`**.*

**Speaker:**
> *"Let's hand this over to DevMind.  
> I select the **`Cricket scorer`** preset and click **`Repair and run tests`**.  
> 
> DevMind's RAG engine scans the script:
> - It retrieves function `addRun(run)` at line 451 in `script.js`.
> - It identifies that the developer mistakenly wrote `matchState.balls += 2;` instead of `matchState.balls += 1;`.
> - It generates the unified diff replacing `+= 2` with `+= 1`.
> - It tests the patch inside Docker using Node test runner `score.test.js`.
> - Result: **Tests Passed!**"
> 
> Now, we review the diff and click **`[ ✅ Yes, Update Code in Files ]`**.  
> DevMind writes the verified line to disk."*

#### Step 3: Live Verification
**Visual on Screen:**  
*Switch back to Cricket Scorer (`index.html`), refresh the page, and click '1 Run'.*

**Speaker:**
> *"Let's verify live in the app. I refresh the cricket scorer.  
> I click **'1 Run'**...  
> And look at the overs: **0.1 Overs! Exactly 1 legal delivery!**  
> Another delivery → **0.2 Overs!** The match tracking is now 100% accurate!"*

---

### ACT 5: Safety First — The 3-Attempt Halting Boundary (8:00 – 9:15)

**Visual on Screen:**  
*In DevMind, select **`Boundary limit test · Max 3 attempts limit demo`** and click **`Repair and run tests`**.*

**Speaker:**
> *"Now, here is the most important question an enterprise or faculty examiner will ask:  
> *'What happens if an AI agent can't solve a bug? Will it loop forever, blow up your API bills, or break production files?'*
> 
> DevMind has a built-in **Deterministic Safety Halting Policy**. Let me show you.  
> 
> I'll select the **`Boundary limit test`** preset.  
> Watch the iteration tracker:
> - **Attempt 1:** The candidate patch fails tests inside Docker.
> - **Attempt 2:** DevMind reflects on the failure traceback and tries an alternative patch. Tests fail again.
> - **Attempt 3:** DevMind attempts a final time. Tests fail again.
> - **The Safety Halt:** Instead of running infinitely, DevMind immediately halts with status:  
>   **`repair_attempt_limit_reached`**!
> 
> It displays a prominent alert informing the developer that candidate patches failed verification, and **zero files were modified on host disk**. That is enterprise-grade safety."*

---

### ACT 6: Empirical Results & Conclusion (9:15 – 10:00)

**Visual on Screen:**  
*Show terminal with `pytest` passing 180 tests, and open [`DEVMIND_MASTER_EXPLAINER.md`](file:///c:/TECH/S5/TEXT%20ANALYTICS/PROJECT/DEVMIND_MASTER_EXPLAINER.md).*

**Speaker:**
> *"To ensure academic rigor and complete reliability:
> - DevMind is backed by **180 automated unit and integration tests** passing with 0 failures across Python, Node, RAG, and UI components.
> - In retrieval benchmarks on SWE-bench Lite instances, our Hybrid RAG (BM25 + Cosine + RRF $k=60$) reduced LLM token consumption by over 60% compared to brute-force file feeding.
> - And because our RAG isolates code down to 15 lines, DevMind can run locally on **1.7B edge LLMs** with full privacy and zero cloud API dependency.
> 
> In summary, DevMind bridges the gap between raw LLMs and dependable software engineering — giving developers automated diagnosis, safe container testing, and verified self-healing.
> 
> Thank you for watching!"*

---

## 💡 Quick Tips for a Flawless Recording
1. **Pacing:** Speak clearly and leave a 1-second pause before and after clicking buttons so your video edits are clean.
2. **Side-by-Side View (Optional):** If you have a wide monitor, put DevMind on the left half and QuickCart on the right half. When you click "Update Code in Files", refreshing the right window instantly shows the fix!
3. **If You Make a Stumble:** Don't stop the recording! Just pause for 2 seconds, repeat that sentence, and edit out the pause later.
