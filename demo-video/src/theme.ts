import { loadFont as loadInter } from "@remotion/google-fonts/Inter";
import { loadFont as loadMono } from "@remotion/google-fonts/JetBrainsMono";

export const { fontFamily: sans } = loadInter("normal", {
  weights: ["400", "600", "800"],
  subsets: ["latin"],
});
export const { fontFamily: mono } = loadMono("normal", {
  weights: ["400", "600"],
  subsets: ["latin"],
});

export const colors = {
  bg: "#0d0e14",
  card: "#171923",
  cardBorder: "#262938",
  text: "#eceef5",
  muted: "#9399ab",
  accent: "#a78bfa", // violet
  accentDim: "#3b2f63",
  green: "#4ade80",
  amber: "#fbbf24",
  red: "#f87171",
};

export const FPS = 30;
