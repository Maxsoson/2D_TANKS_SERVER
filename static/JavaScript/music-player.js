const tracks = [
  "/static/Audio/home1.mp3",
  "/static/Audio/home2.mp3",
  "/static/Audio/home3.mp3",
  "/static/Audio/home4.mp3",
  "/static/Audio/home5.mp3",
  "/static/Audio/home6.mp3",
  "/static/Audio/home7.mp3",
  "/static/Audio/home8.mp3",
  "/static/Audio/troll1.mp3"
];

let currentTrack = 0;
const audio = document.getElementById("index-audio-player");
const playBtn = document.getElementById("index-play-btn");
const nextBtn = document.getElementById("index-next-btn");
const muteBtn = document.getElementById("index-mute-btn");
const volumeSlider = document.getElementById("index-volume-slider");
const trackName = document.getElementById("index-track-name");

let isPlaying = false;

function updateMuteIcon() {
  muteBtn.textContent = audio.muted ? "🔇" : "🔈";
  muteBtn.classList.toggle("index-muted", audio.muted);
  muteBtn.classList.toggle("index-unmuted", !audio.muted);
}

// Початкове налаштування треку
audio.src = tracks[currentTrack];
trackName.textContent = `Now playing: Track ${currentTrack + 1}`;
audio.muted = true;
audio.play().then(() => {
  playBtn.textContent = "⏸︎";
  isPlaying = true;
  updateMuteIcon();
}).catch((e) => {
  console.warn("Автовідтворення заблоковано:", e);
});

// ▶️ / ⏸ кнопка
playBtn.addEventListener("click", () => {
  if (isPlaying) {
    audio.pause();
    playBtn.textContent = "▶︎";
  } else {
    audio.play().then(updateMuteIcon);
    playBtn.textContent = "⏸︎";
  }
  isPlaying = !isPlaying;
});

// ⏭ Перехід до наступного треку
nextBtn.addEventListener("click", () => {
  currentTrack = (currentTrack + 1) % tracks.length;
  audio.src = tracks[currentTrack];
  trackName.textContent = `Now playing: Track ${currentTrack + 1}`;
  if (isPlaying) audio.play().then(updateMuteIcon);
});

// 🔇 / 🔈 кнопка
muteBtn.addEventListener("click", () => {
  audio.muted = !audio.muted;
  updateMuteIcon();
});

// 🎚️ Гучність
volumeSlider.addEventListener("input", () => {
  audio.volume = volumeSlider.value;
});

// 🔁 Автоматичне перемикання треків
audio.addEventListener("ended", () => {
  currentTrack = (currentTrack + 1) % tracks.length;
  audio.src = tracks[currentTrack];
  trackName.textContent = `Now playing: Track ${currentTrack + 1}`;
  audio.play().then(updateMuteIcon);
});
