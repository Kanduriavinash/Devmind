const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const test = require("node:test");
const vm = require("node:vm");

test("each legal scoring delivery adds exactly one ball", () => {
  const context = vm.createContext({
    window: {},
    document: { getElementById: () => null },
    localStorage: { setItem() {}, getItem() { return null; }, removeItem() {} },
    prompt: () => "0",
    alert() {},
    console,
    setTimeout,
    Math,
  });
  const appSource = fs.readFileSync(path.join(__dirname, "..", "script.js"), "utf8");
  vm.runInContext(appSource, context, { filename: "script.js" });
  vm.runInContext(`
    matchState = {
      status: "live", innings: 1, battingTeam: 1, bowlingTeam: 2,
      team1Squad: ["Batter", "Runner"], team2Squad: ["Bowler"],
      score: 0, wickets: 0, balls: 0, oversLimit: 10,
      strikerName: "Batter", nonStrikerName: "Runner", currentBowlerName: "Bowler",
      currentOver: [], freeHitActive: false,
      stats: {
        Batter: { batting: { runs: 0, balls: 0, fours: 0, sixes: 0 } },
        Runner: { batting: { runs: 0, balls: 0, fours: 0, sixes: 0 } },
        Bowler: { bowling: { runs: 0, balls: 0, maidens: 0 } },
      },
      timeline: { 1: [], 2: [] },
    };
    matchHistory = [];
    updateUI = () => {};
    saveState = () => {};
    checkInningsOrOverEnd = () => {};
    addRun(1);
  `, context);
  const result = vm.runInContext("({ balls: matchState.balls, score: matchState.score, batterRuns: matchState.stats.Batter.batting.runs })", context);
  assert.deepEqual({ ...result }, { balls: 1, score: 1, batterRuns: 1 });
});