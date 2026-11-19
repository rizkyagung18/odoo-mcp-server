import { Composition, Folder } from "remotion";
import { Demo, DEMO_DURATION } from "./Demo";
import { TitleScene } from "./scenes/TitleScene";
import { HowItWorksScene } from "./scenes/HowItWorksScene";
import { PipelineScene } from "./scenes/PipelineScene";
import { InvoicesScene } from "./scenes/InvoicesScene";
import { WriteScene } from "./scenes/WriteScene";
import { ReadOnlyScene } from "./scenes/ReadOnlyScene";
import { OutroScene } from "./scenes/OutroScene";

const size = { width: 1280, height: 720, fps: 30 };

export const RemotionRoot: React.FC = () => {
  return (
    <>
      <Composition id="OdooMcpDemo" component={Demo} durationInFrames={DEMO_DURATION} {...size} />
      <Folder name="Scenes">
        <Composition id="Title" component={TitleScene} durationInFrames={75} {...size} />
        <Composition id="HowItWorks" component={HowItWorksScene} durationInFrames={130} {...size} />
        <Composition id="Pipeline" component={PipelineScene} durationInFrames={165} {...size} />
        <Composition id="Invoices" component={InvoicesScene} durationInFrames={140} {...size} />
        <Composition id="SafeWrite" component={WriteScene} durationInFrames={185} {...size} />
        <Composition id="ReadOnly" component={ReadOnlyScene} durationInFrames={110} {...size} />
        <Composition id="Outro" component={OutroScene} durationInFrames={80} {...size} />
      </Folder>
    </>
  );
};
