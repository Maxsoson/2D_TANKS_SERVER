export function drawHUD(ctx, spriteImage, frames) {
  const hudX = 512 + 8; // зона справа, з відступом
  const hudY = 0;

  // HUD текст
  const textElements = [
    { key: "IP", x: 0, y: 0 },
    { key: "GAME", x: 0, y: 48 },
    { key: "STAGE", x: 0, y: 96 }
  ];

  textElements.forEach(({ key, x, y }) => {
    const frame = frames[`hud-${key.toLowerCase()}`];
    if (frame) {
      ctx.drawImage(spriteImage, frame.x, frame.y, frame.w, frame.h, hudX + x, hudY + y, frame.w, frame.h);
    }
  });

  // Прапор
  const flag = frames["hud-flag"];
  if (flag) {
    ctx.drawImage(spriteImage, flag.x, flag.y, flag.w, flag.h, hudX + 16, 128, flag.w, flag.h);
  }
}
