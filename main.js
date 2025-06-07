import "./style.css";
import lolcats from "./data.js";

const background = document.getElementById("background");
const title = document.getElementById("title");
const helloCurious = document.getElementById("date");
const subtitle = document.getElementById("subtitle");
const explanation = document.getElementById("explanation");

let isCatalan = navigator.languages?.some((lang) => lang === "ca" || lang.startsWith("ca-"));

let today = "";
let touchStartX = 0;
let touchEndX = 0;

// Add toggle button functionality
document.getElementById("toggle-catalan").addEventListener("click", () => {
    isCatalan = !isCatalan;
    updateContent(true);
});

function getDateFromURL() {
  const dateParam = window.location.search.slice(1);
  if (dateParam && /^\d{4}-\d{2}-\d{2}$/.test(dateParam)) {
    return dateParam;
  }
  return null;
}

function formatDate(dateStr) {
  if (isCatalan) {
    // Convert YYYY-MM-DD to DD/MM/YYYY
    const [year, month, day] = dateStr.split("-");
    return `${day}/${month}/${year}`;
  }

  return dateStr;
}

function updateContent(force = false) {
  const urlDate = getDateFromURL();
  let date = urlDate || new Date().toISOString().split("T")[0];
  date = lolcats[date] ? date : Object.keys(lolcats)[0];

  if (today !== date || force) {
    today = date;
    const content = lolcats[today];

    title.innerHTML = `<a href="${content[0]}" target="_blank" rel="noopener noreferrer">${
      content[isCatalan ? 2 : 1]
    } ↗️</a>`;
    explanation.textContent = content[isCatalan ? 4 : 3];
    subtitle.textContent = content[isCatalan ? 6 : 5];
    helloCurious.textContent = "🗓️ " + formatDate(today);
    background.style.backgroundImage = `url(/lulz/${date}.webp)`;
  }
}

function navigateDate(direction) {
  const allDates = Object.keys(lolcats).sort();
  const currentIndex = allDates.indexOf(getDateFromURL());
  let date;
  if (currentIndex === -1) {
    // If current date is not in the array, use the first available date
    date = allDates[0];
  } else {
    // Move to next or previous date
    const newIndex = currentIndex + direction;
    if (newIndex >= 0 && newIndex < allDates.length) {
      date = allDates[newIndex];
    } else {
      // If we're at the start or end, stay at current date
      date = allDates[currentIndex];
    }
  }
  window.history.pushState({}, "", `?${date}`);

  updateContent();
}

function changeDate(newDate) {
  const allDates = Object.keys(lolcats).sort();

  if (lolcats[newDate]) {
    // If the date exists, use it directly
    date = newDate;
  } else {
    // Find the closest available date
    const currentIndex = allDates.indexOf(date);
    if (currentIndex === -1) {
      // If current date is not in the array, use the first available date
      date = allDates[0];
    } else {
      // Find the next or previous date based on whether newDate is before or after current date
      const newDateObj = new Date(newDate);
      const currentDateObj = new Date(date);

      if (newDateObj > currentDateObj) {
        // Looking for next date
        date = allDates.slice(currentIndex + 1)[0] || allDates[currentIndex];
      } else {
        // Looking for previous date
        date = allDates.slice(0, currentIndex).pop() || allDates[currentIndex];
      }
    }
  }

  updateContent();
}

function checkMidnightUpdate() {
  const now = new Date();
  if (now.getHours() === 0 && now.getMinutes() === 0) {
    updateContent();
  }
}

function handleSwipe() {
  const swipeThreshold = 50; // Minimum distance for a swipe
  const swipeDistance = touchEndX - touchStartX;

  if (Math.abs(swipeDistance) > swipeThreshold) {
    if (swipeDistance > 0) {
      navigateDate(-1); // Swipe right
    } else {
      navigateDate(1); // Swipe left
    }
  }
}

document.addEventListener("touchstart", (event) => {
  touchStartX = event.changedTouches[0].screenX;
});

document.addEventListener("touchend", (event) => {
  touchEndX = event.changedTouches[0].screenX;
  handleSwipe();
});

document.addEventListener("keydown", (event) => {
  if (event.key === "ArrowLeft") {
    navigateDate(-1);
  } else if (event.key === "ArrowRight") {
    navigateDate(1);
  }
});

updateContent();
setInterval(checkMidnightUpdate, 60000); // Check every minute
