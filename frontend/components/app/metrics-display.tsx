'use client';

import React, { useEffect, useState } from 'react';
import { useDataChannel } from '@livekit/components-react';
import { cn } from '@/lib/utils';

interface MetricsData {
  llm?: {
    prompt_tokens: number;
    completion_tokens: number;
    total_tokens: number;
    tokens_per_second: number;
    ttft: number;
    duration: number;
  };
  stt?: {
    // duration: number;
    audio_duration: number;
    // streamed: boolean;
  };
  tts?: {
    ttfb: number;
    duration: number;
    audio_duration: number;
    characters_count: number;
    streamed: boolean;
  };
  eou?: {
    end_of_utterance_delay: number;
    transcription_delay: number;
  };
  usage_summary?: {
    llm_prompt_tokens: number;
    llm_completion_tokens: number;
    tts_characters_count: number;
    stt_audio_duration: number;
  };
}

function MetricRow({ label, value }: { label: string; value: string | number }) {
  return (
    <div className="flex justify-between text-xs py-0.5">
      <span className="text-muted-foreground">{label}</span>
      <span className="font-mono">{value}</span>
    </div>
  );
}

export function MetricsDisplay({ className }: { className?: string }) {
  const [metrics, setMetrics] = useState<MetricsData>({});
  const [isOpen, setIsOpen] = useState(true);

  const { message } = useDataChannel('agent_metrics');

  useEffect(() => {
    if (message) {
      try {
        const payload = JSON.parse(new TextDecoder().decode(message.payload));
        if (payload.type === 'metrics') {
          setMetrics((prev) => ({
            ...prev,
            [payload.metrics_type]: payload.data,
          }));
        }
      } catch (error) {
        console.error('Error parsing metrics:', error);
      }
    }
  }, [message]);

  const hasMetrics = metrics.llm || metrics.stt || metrics.tts || metrics.eou;

  if (!isOpen) {
    return (
      <button
        onClick={() => setIsOpen(true)}
        className="fixed top-4 right-4 z-50 rounded border bg-background px-2 py-1 text-xs"
      >
        Show Metrics
      </button>
    );
  }

  return (
    <div
      className={cn(
        'fixed top-4 right-4 z-50 w-64 rounded border bg-background text-sm shadow-md',
        className
      )}
    >
      <div className="flex items-center justify-between border-b px-3 py-2">
        <span className="font-medium text-xs">Metrics</span>
        <button
          onClick={() => setIsOpen(false)}
          className="text-muted-foreground hover:text-foreground text-xs"
        >
          Close
        </button>
      </div>

      <div className="p-3 space-y-3 max-h-[60vh] overflow-y-auto">
        {/* LLM */}
        {metrics.llm && (
          <div>
            <div className="text-xs font-medium mb-1 border-b pb-1">LLM</div>
            <MetricRow label="Prompt Tokens" value={metrics.llm.prompt_tokens} />
            <MetricRow label="Completion Tokens" value={metrics.llm.completion_tokens} />
            <MetricRow label="Tokens/sec" value={metrics.llm.tokens_per_second.toFixed(1)} />
            <MetricRow label="TTFT" value={`${metrics.llm.ttft.toFixed(3)}s`} />
            <MetricRow label="Duration" value={`${metrics.llm.duration.toFixed(3)}s`} />
          </div>
        )}

        {/* STT */}
        {metrics.stt && (
          <div>
            <div className="text-xs font-medium mb-1 border-b pb-1">STT</div>
            {/* <MetricRow label="Duration" value={`${metrics.stt.duration.toFixed(3)}s`} /> */}
            <MetricRow label="Audio Duration" value={`${metrics.stt.audio_duration.toFixed(3)}s`} />
            {/* <MetricRow label="Streamed" value={metrics.stt.streamed ? 'Yes' : 'No'} /> */}
          </div>
        )}

        {/* TTS */}
        {metrics.tts && (
          <div>
            <div className="text-xs font-medium mb-1 border-b pb-1">TTS</div>
            <MetricRow label="TTFB" value={`${metrics.tts.ttfb.toFixed(3)}s`} />
            <MetricRow label="Duration" value={`${metrics.tts.duration.toFixed(3)}s`} />
            <MetricRow label="Audio Duration" value={`${metrics.tts.audio_duration.toFixed(3)}s`} />
            <MetricRow label="Characters" value={metrics.tts.characters_count} />
          </div>
        )}

        {/* EOU */}
        {metrics.eou && (
          <div>
            <div className="text-xs font-medium mb-1 border-b pb-1">EOU</div>
            <MetricRow label="EOU Delay" value={`${metrics.eou.end_of_utterance_delay.toFixed(3)}s`} />
            <MetricRow label="Transcription Delay" value={`${metrics.eou.transcription_delay.toFixed(3)}s`} />
          </div>
        )}

        {/* Usage Summary */}
        {metrics.usage_summary && (
          <div>
            <div className="text-xs font-medium mb-1 border-b pb-1">Usage</div>
            <MetricRow label="LLM Prompt" value={metrics.usage_summary.llm_prompt_tokens} />
            <MetricRow label="LLM Completion" value={metrics.usage_summary.llm_completion_tokens} />
            <MetricRow label="TTS Characters" value={metrics.usage_summary.tts_characters_count} />
            <MetricRow label="STT Audio" value={`${metrics.usage_summary.stt_audio_duration.toFixed(2)}s`} />
          </div>
        )}

        {/* Empty state */}
        {!hasMetrics && (
          <div className="text-xs text-muted-foreground text-center py-4">
            Waiting for metrics...
          </div>
        )}

        {/* Clear button */}
        {hasMetrics && (
          <button
            onClick={() => setMetrics({})}
            className="w-full text-xs text-muted-foreground hover:text-foreground border rounded py-1 mt-2"
          >
            Clear
          </button>
        )}
      </div>
    </div>
  );
}
