import "./style.css";
import lolcats from "./data.js";

const background = document.getElementById("background");
const title = document.getElementById("title");
const helloCurious = document.getElementById("date");
const subtitle = document.getElementById("subtitle");

let today = "";
let touchStartX = 0;
let touchEndX = 0;

function getDateFromURL() {
    const dateParam = window.location.search.slice(1);
    if (dateParam && /^\d{4}-\d{2}-\d{2}$/.test(dateParam)) {
        return dateParam;
    }
    return null;
}

function updateContent() {
    const urlDate = getDateFromURL();
    let date = urlDate || new Date().toISOString().split("T")[0];
    date = lolcats[date] ? date : "2024-10-19";

    if (today !== date) {
        today = date;
        const content = lolcats[today];

        title.innerHTML = `<a href="https://www.google.com/search?q=${encodeURIComponent(content[0])}" target="_blank" rel="noopener noreferrer">${content[0]} ↗️</a>`;
        subtitle.textContent = content[1];
        helloCurious.textContent = "🗓️ " + today;
        background.style.backgroundImage = `url(/lulz/${date}.jpg)`;
    }
}

function changeDate(direction) {
    const currentDate = new Date(today);
    currentDate.setDate(currentDate.getDate() + direction);
    let newDate = currentDate.toISOString().split("T")[0];
    if (newDate == today) { // TZ hour change or something?
        currentDate.setDate(currentDate.getDate() + direction);
        newDate = currentDate.toISOString().split("T")[0];
    }

    if (lolcats[newDate]) {
        window.history.pushState({}, "", `?${newDate}`);
        updateContent();
    }
}

function checkMidnightUpdate() {
    const now = new Date();
    if (now.getHours() === 0 && now.getMinutes() === 0) {
        window.history.pushState({}, "", `?${new Date().toISOString().split("T")[0]}`);
        updateContent();
    }
}

function handleSwipe() {
    const swipeThreshold = 50; // Minimum distance for a swipe
    const swipeDistance = touchEndX - touchStartX;
    
    if (Math.abs(swipeDistance) > swipeThreshold) {
        if (swipeDistance > 0) {
            changeDate(1); // Swipe right
        } else {
            changeDate(-1); // Swipe left
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
        changeDate(-1);
    } else if (event.key === "ArrowRight") {
        changeDate(1);
    }
});

updateContent();
setInterval(checkMidnightUpdate, 60000); // Check every minute
