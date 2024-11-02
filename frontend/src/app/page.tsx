'use client'

import VideoFrame from "@/components/VideoFrame";
import SettingsButton from "@/components/SettingsButton";
import { AppProvider } from "@/contexts/App";

export default function Home() {
  return (
    <AppProvider>
      <div className="container flex mx-auto p-6 flex-row justify-between items-center">
        <h2 className="scroll-m-20 text-3xl font-semibold tracking-tight">
          {/* TODO: Find a better title */}
          Computer e2e testing
        </h2>

        <SettingsButton />
      </div>
      <VideoFrame />
    </AppProvider>
  );
}
