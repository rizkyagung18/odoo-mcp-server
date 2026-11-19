import { linearTiming, TransitionSeries } from "@remotion/transitions";
import { fade } from "@remotion/transitions/fade";
import { TitleScene } from "./scenes/TitleScene";
import { HowItWorksScene } from "./scenes/HowItWorksScene";
import { PipelineScene } from "./scenes/PipelineScene";
import { InvoicesScene } from "./scenes/InvoicesScene";
import { WriteScene } from "./scenes/WriteScene";
import { ReadOnlyScene } from "./scenes/ReadOnlyScene";
import { OutroScene } from "./scenes/OutroScene";

// 885 frames of scenes - 6 fades x 10 frames = 825 frames (27.5 s at 30 fps).
export const DEMO_DURATION = 825;

export const Demo = () => (
  <TransitionSeries>
    <TransitionSeries.Sequence name="Title" durationInFrames={75}>
      <TitleScene />
    </TransitionSeries.Sequence>
    <TransitionSeries.Transition presentation={fade()} timing={linearTiming({ durationInFrames: 10 })} />
    <TransitionSeries.Sequence name="How it works" durationInFrames={130}>
      <HowItWorksScene />
    </TransitionSeries.Sequence>
    <TransitionSeries.Transition presentation={fade()} timing={linearTiming({ durationInFrames: 10 })} />
    <TransitionSeries.Sequence name="Pipeline" durationInFrames={165}>
      <PipelineScene />
    </TransitionSeries.Sequence>
    <TransitionSeries.Transition presentation={fade()} timing={linearTiming({ durationInFrames: 10 })} />
    <TransitionSeries.Sequence name="Invoices" durationInFrames={140}>
      <InvoicesScene />
    </TransitionSeries.Sequence>
    <TransitionSeries.Transition presentation={fade()} timing={linearTiming({ durationInFrames: 10 })} />
    <TransitionSeries.Sequence name="Safe write" durationInFrames={185}>
      <WriteScene />
    </TransitionSeries.Sequence>
    <TransitionSeries.Transition presentation={fade()} timing={linearTiming({ durationInFrames: 10 })} />
    <TransitionSeries.Sequence name="Read-only" durationInFrames={110}>
      <ReadOnlyScene />
    </TransitionSeries.Sequence>
    <TransitionSeries.Transition presentation={fade()} timing={linearTiming({ durationInFrames: 10 })} />
    <TransitionSeries.Sequence name="Outro" durationInFrames={80}>
      <OutroScene />
    </TransitionSeries.Sequence>
  </TransitionSeries>
);
