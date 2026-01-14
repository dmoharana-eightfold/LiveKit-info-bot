'use client';

import React from 'react';
import { AnimatePresence, motion } from 'motion/react';
import { BarVisualizer, useVoiceAssistant } from '@livekit/components-react';
import { cn } from '@/lib/utils';

const MotionContainer = motion.create('div');

const ANIMATION_TRANSITION = {
  type: 'spring',
  stiffness: 675,
  damping: 75,
  mass: 1,
};

interface TileLayoutProps {
  chatOpen: boolean;
}

export function TileLayout({ chatOpen }: TileLayoutProps) {
  const { state: agentState, audioTrack: agentAudioTrack } = useVoiceAssistant();

  return (
    <div className="pointer-events-none fixed inset-x-0 top-16 z-40">
      <div className="relative mx-auto max-w-2xl px-4 md:px-0">
        {/* Audio Visualizer - positioned at top */}
            <AnimatePresence mode="popLayout">
                <MotionContainer
                  key="agent"
                  layoutId="agent"
                  initial={{
                    opacity: 0,
              scale: 0.8,
                  }}
                  animate={{
                    opacity: 1,
              scale: 1,
                  }}
            transition={ANIMATION_TRANSITION}
                  className={cn(
              'bg-background mx-auto aspect-square rounded-xl border transition-all duration-300',
              chatOpen ? 'h-[80px] border-input/50 shadow-lg' : 'h-[120px] border-transparent'
                  )}
                >
                  <BarVisualizer
                    barCount={5}
                    state={agentState}
                    options={{ minHeight: 5 }}
                    trackRef={agentAudioTrack}
              className="flex h-full items-center justify-center gap-1.5"
                  >
                    <span
                      className={cn([
                  'bg-muted min-h-3 w-3 rounded-full',
                        'origin-center transition-colors duration-250 ease-linear',
                  'data-[lk-highlighted=true]:bg-primary data-[lk-muted=true]:bg-muted',
                      ])}
                    />
                  </BarVisualizer>
                </MotionContainer>
            </AnimatePresence>
        
        {/* Agent State Label */}
        {!chatOpen && agentState && (
          <p className="mt-3 text-center text-xs capitalize text-muted-foreground">
            {agentState === 'speaking' && 'Agent speaking...'}
            {agentState === 'listening' && 'Listening...'}
            {agentState === 'thinking' && 'Thinking...'}
            {agentState === 'connecting' && 'Connecting...'}
            {agentState === 'initializing' && 'Initializing...'}
          </p>
        )}
      </div>
    </div>
  );
}
