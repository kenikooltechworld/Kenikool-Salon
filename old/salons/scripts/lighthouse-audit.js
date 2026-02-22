#!/usr/bin/env node

/**
 * Lighthouse audit script for performance testing
 * Usage: node scripts/lighthouse-audit.js
 */

const lighthouse = require("lighthouse");
const chromeLauncher = require("chrome-launcher");
const fs = require("fs");
const path = require("path");

const URLS = [
  "http://localhost:5173/",
  "http://localhost:5173/marketplace/salon/test-id",
];

const THRESHOLDS = {
  performance: 90,
  accessibility: 90,
  "best-practices": 90,
  seo: 90,
};

const WEB_VITALS_THRESHOLDS = {
  "first-contentful-paint": 1500,
  "largest-contentful-paint": 3000,
  "cumulative-layout-shift": 0.1,
  "total-blocking-time": 300,
};

async function launchChrome() {
  const chrome = await chromeLauncher.launch({ chromeFlags: ["--headless"] });
  return chrome;
}

async function runLighthouse(url, chrome) {
  const options = {
    logLevel: "info",
    output: "json",
    port: chrome.port,
    onlyCategories: [
      "performance",
      "accessibility",
      "best-practices",
      "seo",
    ],
  };

  const runnerResult = await lighthouse(url, options);
  return runnerResult.lhr;
}

function formatScore(score) {
  return Math.round(score * 100);
}

function checkThresholds(lhr) {
  const results = {
    passed: true,
    categories: {},
    metrics: {},
  };

  // Check category scores
  Object.entries(THRESHOLDS).forEach(([category, threshold]) => {
    const score = formatScore(lhr.categories[category].score);
    const passed = score >= threshold;
    results.categories[category] = {
      score,
      threshold,
      passed,
    };
    if (!passed) results.passed = false;
  });

  // Check Web Vitals
  const metrics = lhr.audits;
  Object.entries(WEB_VITALS_THRESHOLDS).forEach(([metric, threshold]) => {
    const audit = metrics[metric];
    if (audit) {
      const value = audit.numericValue;
      const passed = value <= threshold;
      results.metrics[metric] = {
        value: Math.round(value),
        threshold,
        passed,
      };
      if (!passed) results.passed = false;
    }
  });

  return results;
}

function printResults(url, results) {
  console.log("\n" + "=".repeat(60));
  console.log(`Lighthouse Audit Results for: ${url}`);
  console.log("=".repeat(60));

  console.log("\nCategory Scores:");
  console.log("-".repeat(60));
  Object.entries(results.categories).forEach(([category, data]) => {
    const status = data.passed ? "✓" : "✗";
    console.log(
      `${status} ${category.padEnd(20)} ${data.score}/100 (threshold: ${data.threshold})`
    );
  });

  console.log("\nWeb Vitals:");
  console.log("-".repeat(60));
  Object.entries(results.metrics).forEach(([metric, data]) => {
    const status = data.passed ? "✓" : "✗";
    const unit = metric.includes("shift") ? "" : "ms";
    console.log(
      `${status} ${metric.padEnd(30)} ${data.value}${unit} (threshold: ${data.threshold}${unit})`
    );
  });

  console.log("\n" + "=".repeat(60));
  if (results.passed) {
    console.log("✓ All thresholds passed!");
  } else {
    console.log("✗ Some thresholds failed. See above for details.");
  }
  console.log("=".repeat(60) + "\n");

  return results.passed;
}

async function main() {
  console.log("Starting Lighthouse audits...\n");

  let chrome;
  let allPassed = true;

  try {
    chrome = await launchChrome();

    for (const url of URLS) {
      try {
        console.log(`Auditing: ${url}`);
        const lhr = await runLighthouse(url, chrome);
        const results = checkThresholds(lhr);
        const passed = printResults(url, results);

        if (!passed) {
          allPassed = false;
        }

        // Save detailed report
        const reportPath = path.join(
          __dirname,
          `../lighthouse-report-${Date.now()}.json`
        );
        fs.writeFileSync(reportPath, JSON.stringify(lhr, null, 2));
        console.log(`Detailed report saved to: ${reportPath}\n`);
      } catch (error) {
        console.error(`Error auditing ${url}:`, error);
        allPassed = false;
      }
    }
  } finally {
    if (chrome) {
      await chrome.kill();
    }
  }

  process.exit(allPassed ? 0 : 1);
}

main().catch((error) => {
  console.error("Fatal error:", error);
  process.exit(1);
});
