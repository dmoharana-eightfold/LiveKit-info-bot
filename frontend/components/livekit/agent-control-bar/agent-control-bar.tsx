'use client';

import { type HTMLAttributes, useCallback, useState } from 'react';
import { Track } from 'livekit-client';
import { useChat, useRemoteParticipants, useTrackToggle } from '@livekit/components-react';
import {
  ChatTextIcon,
  MicrophoneIcon,
  MicrophoneSlashIcon,
  PhoneDisconnectIcon,
} from '@phosphor-icons/react/dist/ssr';
import { Button } from '@/components/livekit/button';
import { Toggle } from '@/components/livekit/toggle';
import { cn } from '@/lib/utils';
import { ChatInput } from './chat-input';

export interface ControlBarControls {
  leave?: boolean;
  microphone?: boolean;
  chat?: boolean;
  camera?: boolean;
  screenShare?: boolean;
}

export interface AgentControlBarProps {
  controls?: ControlBarControls;
  isConnected?: boolean;
  onDisconnect?: () => void;
  onChatOpenChange?: (open: boolean) => void;
}

/**
 * A simplified control bar for voice-only assistant interfaces
 */
export function AgentControlBar({
  controls,
  className,
  isConnected = false,
  onDisconnect,
  onChatOpenChange,
  ...props
}: AgentControlBarProps & HTMLAttributes<HTMLDivElement>) {
  const { send } = useChat();
  const participants = useRemoteParticipants();
  const [chatOpen, setChatOpen] = useState(false);

  // Use the track toggle hook to get mic state
  const { enabled: micEnabled, toggle: toggleMic } = useTrackToggle({
    source: Track.Source.Microphone,
  });

  const handleSendMessage = async (message: string) => {
    await send(message);
  };

  const handleToggleTranscript = useCallback(
    (open: boolean) => {
      setChatOpen(open);
      onChatOpenChange?.(open);
    },
    [onChatOpenChange, setChatOpen]
  );

  const visibleControls = {
    leave: controls?.leave ?? true,
    microphone: controls?.microphone ?? true,
    chat: controls?.chat ?? true,
  };

  const isAgentAvailable = participants.some((p) => p.isAgent);

  return (
    <div
      aria-label="Voice assistant controls"
      className={cn(
        'bg-background border-input/50 dark:border-muted flex flex-col rounded-[31px] border p-3 drop-shadow-md/3',
        className
      )}
      {...props}
    >
      {/* Chat Input */}
      {visibleControls.chat && (
        <ChatInput chatOpen={chatOpen} isAgentAvailable={isAgentAvailable} onSend={handleSendMessage} />
      )}

      <div className="flex gap-1">
        <div className="flex grow gap-1">
          {/* Toggle Microphone - Icon changes based on state */}
          {visibleControls.microphone && (
            <Toggle
              size="icon"
              variant="secondary"
              aria-label={micEnabled ? 'Mute microphone' : 'Unmute microphone'}
              pressed={micEnabled}
              onPressedChange={toggleMic}
              className={cn(
                'transition-colors',
                micEnabled && 'bg-primary text-primary-foreground hover:bg-primary/90'
              )}
            >
              {micEnabled ? (
                <MicrophoneIcon weight="bold" className="size-5" />
              ) : (
                <MicrophoneSlashIcon weight="bold" className="size-5" />
              )}
            </Toggle>
          )}

          {/* Toggle Transcript */}
          <Toggle
            size="icon"
            variant="secondary"
            aria-label="Toggle transcript"
            pressed={chatOpen}
            onPressedChange={handleToggleTranscript}
          >
            <ChatTextIcon weight="bold" />
          </Toggle>
        </div>

        {/* Disconnect */}
        {visibleControls.leave && (
          <Button variant="destructive" onClick={onDisconnect} disabled={!isConnected} className="font-mono">
            <PhoneDisconnectIcon weight="bold" />
            <span className="hidden md:inline">END CALL</span>
            <span className="inline md:hidden">END</span>
          </Button>
        )}
      </div>
    </div>
  );
}
