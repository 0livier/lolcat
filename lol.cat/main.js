import "./style.css";
import lolcats from "./data.js";

const background = document.getElementById("background");
const title = document.getElementById("title");
const subtitle = document.getElementById("subtitle");

let currentDate = "";

function updateContent() {
    const today = new Date().toISOString().split("T")[0];
    if (today !== currentDate) {
        currentDate = lolcats[today] ? today : "2024-10-19";
        const content = lolcats[currentDate];

        title.innerHTML = `<a href="https://www.google.com/search?q=${encodeURIComponent(content[0])}" target="_blank" rel="noopener noreferrer">${content[0]}</a>`;
        subtitle.textContent = content[1];
        background.style.backgroundImage = `url(/lulz/${currentDate}.webp)`;
    }
}

updateContent();
setInterval(updateContent, 60000);
