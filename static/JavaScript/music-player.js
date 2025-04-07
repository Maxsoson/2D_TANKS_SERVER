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
const audio = document.getElementById("audio-player");
const playBtn = document.getElementById("play-btn");
const nextBtn = document.getElementById("next-btn");
const muteBtn = document.getElementById("mute-btn");
const volumeSlider = document.getElementById("volume-slider");
const trackName = document.getElementById("track-name");

let isPlaying = false;

// Початкове налаштування треку
audio.src = tracks[currentTrack];
trackName.textContent = `Now playing: Track ${currentTrack + 1}`;

// ✅ Автозапуск з вимкненим звуком
audio.muted = true;
audio.play().then(() => {
  playBtn.textContent = "⏸︎";
  playBtn.classList.add("playing");
  playBtn.classList.remove("paused");
  isPlaying = true;
}).catch((e) => {
  console.warn("Автовідтворення заблоковано:", e);
});

// ▶️ / ⏸ кнопка
playBtn.addEventListener("click", () => {
  if (isPlaying) {
    audio.pause();
    playBtn.textContent = "▶︎";
    playBtn.classList.remove("playing");
    playBtn.classList.add("paused");
  } else {
    audio.play();
    playBtn.textContent = "⏸︎";
    playBtn.classList.remove("paused");
    playBtn.classList.add("playing");
  }
  isPlaying = !isPlaying;
});

// ⏭ Перехід до наступного треку
nextBtn.addEventListener("click", () => {
  currentTrack = (currentTrack + 1) % tracks.length;
  audio.src = tracks[currentTrack];
  trackName.textContent = `Now playing: Track ${currentTrack + 1}`;
  if (isPlaying) audio.play();
});

// 🔇 / 🔈 кнопка
muteBtn.addEventListener("click", () => {
  audio.muted = !audio.muted;
  muteBtn.textContent = audio.muted ? "🔇" : "🔈";

  if (audio.muted) {
    muteBtn.classList.remove("unmuted");
    muteBtn.classList.add("muted");
  } else {
    muteBtn.classList.remove("muted");
    muteBtn.classList.add("unmuted");
  }
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
  audio.play();
});
