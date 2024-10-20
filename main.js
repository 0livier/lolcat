import "./style.css";
import lolcats from "./data.js";

const background = document.getElementById("background");
const title = document.getElementById("title");
const helloCurious = document.getElementById("date");
const subtitle = document.getElementById("subtitle");

let today = "";

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
        background.style.backgroundImage = `url(/lulz/${date}.webp)`;
    }
}

updateContent();
setInterval(updateContent, 60000);
