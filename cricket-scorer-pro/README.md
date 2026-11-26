# Cricket Scorer Pro

A premium live cricket scoring web app for scoring local matches ball by ball — with a clean dashboard, full scorecards, innings tracking, toss simulation, match persistence, and printable match reports.

**Repository:** [Kanduriavinash/cricket-scorer-pro](https://github.com/Kanduriavinash/cricket-scorer-pro)

**Live Demo:** [Cricket Scorer Pro](https://kanduriavinash.github.io/cricket-scorer-pro/)

---

## Overview

Cricket Scorer Pro is a browser-based cricket scoring application built to make live match scoring simple, fast, and professional-looking. It is designed for school games, local tournaments, street cricket, practice matches, and small events where you want a complete digital scorebook without needing a complex setup.

The app lets you:

- create a match with custom team names and squads
- choose toss behavior with manual, direct, or interactive coin toss setup
- score every ball live
- track batting, bowling, extras, partnerships, and run rates
- manage wickets and new batters
- run a full 2-innings chase with target and required rate
- undo mistakes during scoring
- resume unfinished matches automatically
- store completed matches in browser history
- print or save full scorecards as PDF

---

## Main Features

### 1. Match Setup

Before the game starts, the app allows full match configuration:

- team 1 and team 2 naming
- custom squad input, one player per line
- automatic default squad generation if no players are entered
- overs limit selection (default: 10 overs)
- custom wide and no-ball penalty settings
- toggle to enable or disable free hit on no-ball
- option to count no-ball as a legal delivery or rebowl it

### 2. Toss System

The app supports three toss flows:

- `Manual` — enter toss winner and decision
- `Interactive Coin Toss` — launch a coin-flip animation and let the toss winner choose to bat or bowl
- `Skip Toss` — directly choose the team batting first

### 3. Live Ball-by-Ball Scoring

During the match, scorers can record:

- dot balls and normal runs: `0`, `1`, `2`, `3`, `4`, `6`
- extras: `Wide`, `No Ball`, `Bye`, `Leg Bye`
- wickets with dismissal details
- strike rotation
- manual strike swap
- undo for the last action

The live dashboard updates instantly with:

- score and wickets
- overs
- current run rate
- required run rate in the chase
- current over summary
- live batting table
- live bowling table
- partnership details
- free hit indicator
- boundary celebrations for 4s and 6s

### 4. Wicket Management

The wicket flow includes:

- striker or non-striker dismissal selection
- dismissal types: bowled, caught, LBW, run out, stumped, hit wicket, and retired hurt
- optional fielder name entry for supported dismissals
- automatic next batter selection
- fall of wicket tracking
- correct bowler wicket attribution where applicable

### 5. Full Scorecard and Timeline

The app provides dedicated match views:

- `Live Score`
- `Full Scorecard`
- `Ball By Ball`

The full scorecard includes:

- batting cards for both innings
- bowling tables
- extras breakdown
- fall of wickets
- innings totals

The ball-by-ball timeline records match events in reverse chronological order for quick review.

### 6. Two-Sider / Common Player Support

One unique feature of this app is support for "common players" or "two-siders" who play for both teams in informal matches.

You can mark a player as a two-sider from the edit player flow, and the app will:

- duplicate the player into both teams with separate innings identities
- mark the player visually in score displays
- keep stats separated correctly for each team/innings

### 7. Auto Save and Resume

The app automatically saves live progress in the browser using `localStorage`. If the page is refreshed or reopened, the scorer can:

- resume the active match
- discard the saved match and start fresh

This is especially useful during long matches or accidental browser reloads.

### 8. Match History

Completed matches are saved locally in a past matches section. From there, users can:

- review previous match summaries
- open old scorecards
- print past scorecards
- delete saved history entries

### 9. Print / PDF Export

The scorecard tab is optimized for printing:

- print directly from the browser
- save a clean PDF match report
- share the final scorecard after the match

---

## How the App Works

1. Enter teams, squads, overs, toss settings, and match rules.
2. Start the match.
3. Score each delivery using the live controls.
4. Select wicket details and next batters whenever a wicket falls.
5. Select the next bowler at the end of each over.
6. Complete the first innings.
7. Start the chase automatically in innings two.
8. View the winner, summary, scorecard, and timeline after the match ends.

---

## Tech Stack

### Working Scorer App (Live)

The complete, fully functional cricket scoring experience lives in:

```
_cricket_score_board_backup/
├── index.html    ← Full app markup and screens
├── style.css     ← All UI styles (dark theme, glassmorphism)
└── script.js     ← All scoring logic, persistence, and state
```

Technologies used:

- **HTML5** — semantic structure and screen management
- **CSS3** — dark mode, glassmorphism, animations, responsive layout
- **Vanilla JavaScript** — all game logic, localStorage persistence, DOM updates
- **Browser `localStorage`** — match save/resume and match history

This is the version deployed live at [kanduriavinash.github.io/cricket-scorer-pro](https://kanduriavinash.github.io/cricket-scorer-pro/).

### Next.js Setup (In Progress)

This repo also includes a Next.js project scaffold at the root level (added for future migration):

```
src/pages/
src/styles/
next.config.mjs
package.json
```

The Next.js version is currently a starter scaffold and does not yet contain the full cricket scorer experience. The HTML/JS/CSS version in `_cricket_score_board_backup/` remains the reference and active implementation.

---

## Project Structure

```
.
├── _cricket_score_board_backup/
│   ├── index.html          ← The working cricket scoring app
│   ├── script.js           ← All scoring logic
│   └── style.css           ← Full UI styles
├── public/
├── src/
│   ├── pages/              ← Next.js page scaffold
│   └── styles/
├── package.json
├── next.config.mjs
└── README.md
```

---

## Getting Started

### Option 1: Run the Working Scorer (Recommended)

Simply open the file in your browser:

```
_cricket_score_board_backup/index.html
```

No build step, no server, no dependencies — it runs entirely in the browser.

Or visit the live version directly: [Cricket Scorer Pro →](https://kanduriavinash.github.io/cricket-scorer-pro/)

### Option 2: Run the Next.js App

Install dependencies:

```bash
npm install
```

Start the development server:

```bash
npm run dev
```

Then open [http://localhost:3000](http://localhost:3000).

> **Note:** The current Next.js app is a starter scaffold and does not yet include the full cricket scoring system.

---

## Use Cases

This app is useful for:

- local cricket tournaments
- school and college matches
- practice games
- community cricket events
- box cricket and street cricket
- small organizers who want digital scoring without a paid platform

---

## Future Improvements

Possible future upgrades:

- migrate full scorer logic into the Next.js app
- player profiles and season stats
- cloud database support
- user authentication
- online multi-user scoring
- live public match sharing
- mobile-first optimization
- PWA/offline support
- team logos and branding
- admin dashboard
- export to Excel or JSON

---

## Why This Project

Cricket Scorer Pro was built to provide a modern, attractive, and practical cricket scoring experience for real match situations. Instead of a basic scoreboard only showing runs and wickets, this app offers a complete mini scoring system — with setup, live scoring, analytics, history, and printable reports — all in a single HTML file that runs in any browser.

---

## Author

Created by **Avinash Kanduri**

GitHub: [Kanduriavinash](https://github.com/Kanduriavinash)

---

## License

This project is open source. You can add your preferred license in this repository if you want others to reuse or contribute formally.
