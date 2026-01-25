function updateFavicon() {
  const isDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
  const favicon = document.getElementById("favicon");
  favicon.href = isDark
    ? "Logo&Pics/mainlogo_dark.png"
    : "Logo&Pics/mainlogo.png";
}

// run once on load
updateFavicon();

// update if user switches theme while browsing
window
  .matchMedia("(prefers-color-scheme: dark)")
  .addEventListener("change", updateFavicon);

function applyTheme() {
  const isDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
  const logo = document.getElementById("logo");

  if (!logo) return;

  logo.src = isDark ? "Logo&Pics/mainlogo_dark.png" : "Logo&Pics/mainlogo.png";
}

// run on load
applyTheme();

// listen for system changes live
window
  .matchMedia("(prefers-color-scheme: dark)")
  .addEventListener("change", applyTheme);

let sending_mode = "user";

function setMode(mode) {
  document.body.className = mode;
  document
    .getElementById("userBtn")
    .classList.toggle("active", mode === "user");
  document
    .getElementById("trainerBtn")
    .classList.toggle("active", mode === "trainer");
  if (mode === "user") {
    sending_mode = "user";
  }
}

//   function trainerLogin() {
//     const u = document.getElementById("trainerUser").value;
//     const p = document.getElementById("trainerPass").value;

//     if (!u || !p) {
//       alert("Trainer credentials required");
//       return;
//     }

//     alert("Trainer mode unlocked (UI only)");
//   }
async function trainerLogin() {
  const username = document.getElementById("trainerUser").value;
  const password = document.getElementById("trainerPass").value;

  if (!username || !password) {
    alert("Trainer credentials required");
    return;
  }

  const response = await fetch("users.txt");
  const text = await response.text();

  const trainers = text.trim().split("\n");

  for (let trainer of trainers) {
    const [u, p] = trainer.split(",");

    if (u === username && p === password) {
      alert("Trainer mode unlocked");
      sending_mode = "trainer";
      return;
    }
  }
  alert("Invalid trainer credentials");
}

function clearInput() {
  document.getElementById("textInput").value = "";
}
async function pasteInput() {
  try {
    const text = await navigator.clipboard.readText();
    if (text.length === 0) {
      alert("Clipboard is empty");
      return;
    }
    document.getElementById("textInput").value = text;
  } catch (err) {
    alert("Clipboard access denied");
  }
}

function clearResult() {
  document.getElementById("result").innerHTML = "Output will appear here…";
}

async function copyResult() {
  const text = document.getElementById("result").innerText;
  await navigator.clipboard.writeText(text);
  alert("Copied to clipboard");
}

function downloadResult() {
  const text = document.getElementById("result").innerText;
  const blob = new Blob([text], { type: "text/plain" });
  const a = document.createElement("a");
  a.href = URL.createObjectURL(blob);
  a.download = "grammerly_result.txt";
  a.click();
}
function animateWall() {
  const wall = document.querySelector(".wall");
  const particlesContainer = wall.querySelector(".particles");

  // Remove class if exists, force reflow
  wall.classList.remove("glow-bright");
  void wall.offsetWidth; // force reflow

  // Add class to start animation
  wall.classList.add("glow-bright");

  // Remove class after animation ends so it doesn't stick
  wall.addEventListener("animationend", function handler() {
    wall.classList.remove("glow-bright");
    wall.removeEventListener("animationend", handler);
  });

  const wallRect = wall.getBoundingClientRect();

  for (let i = 0; i < 30; i++) {
    const p = document.createElement("div");
    p.className = "particle";

    // random position inside the wall
    p.style.left = `${Math.random() * wall.offsetWidth}px`;
    p.style.top = `${Math.random() * wall.offsetHeight}px`;

    particlesContainer.appendChild(p);

    // random direction toward output panel
    const dx = 150 + Math.random() * 50; // move right
    const dy = -30 + Math.random() * 60; // slight up/down

    p.animate(
      [
        { transform: `translate(0,0) scale(1)`, opacity: 1 },
        { transform: `translate(${dx}px, ${dy}px) scale(0.1)`, opacity: 0 },
      ],
      { duration: 2000, easing: "ease-out" },
    );

    // remove particle after animation
    setTimeout(() => p.remove(), 2000);
  }
}
