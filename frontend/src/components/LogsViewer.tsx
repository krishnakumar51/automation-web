import { useEffect, useRef } from "react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Trash2, Terminal } from "lucide-react";
import { LogEntry } from "@/services/api";

interface LogsViewerProps {
  logs: LogEntry[];
  onClearLogs: () => void;
}

const LogsViewer = ({ logs, onClearLogs }: LogsViewerProps) => {
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [logs]);

  const formatTimestamp = (timestamp: string) => {
    return new Date(timestamp).toLocaleTimeString();
  };

  const getLogColor = (message: string) => {
    if (message.toLowerCase().includes('error') || message.toLowerCase().includes('failed')) {
      return 'text-destructive';
    }
    if (message.toLowerCase().includes('success') || message.toLowerCase().includes('created')) {
      return 'text-success';
    }
    if (message.toLowerCase().includes('starting') || message.toLowerCase().includes('processing')) {
      return 'text-warning';
    }
    return 'text-muted-foreground';
  };

  return (
    <Card className="bg-gradient-card border-border/50 shadow-card">
      <div className="p-4 border-b border-border/50">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <Terminal className="w-4 h-4 text-primary" />
            <h3 className="font-semibold text-foreground">Live Logs</h3>
            <span className="text-xs text-muted-foreground bg-muted px-2 py-1 rounded-full">
              {logs.length} entries
            </span>
          </div>
          <Button
            onClick={onClearLogs}
            size="sm"
            variant="outline"
            className="h-8 text-xs border-border/50 hover:bg-accent"
            disabled={logs.length === 0}
          >
            <Trash2 className="w-3 h-3 mr-1" />
            Clear
          </Button>
        </div>
      </div>

      <ScrollArea className="h-64" ref={scrollRef}>
        <div className="p-4 space-y-2">
          {logs.length === 0 ? (
            <div className="text-center py-8">
              <Terminal className="w-8 h-8 mx-auto text-muted-foreground/50 mb-2" />
              <p className="text-sm text-muted-foreground">
                No logs yet. Start creating accounts to see live updates.
              </p>
            </div>
          ) : (
            logs.map((log, index) => (
              <div
                key={index}
                className="flex items-start space-x-3 p-2 rounded-md hover:bg-accent/30 transition-colors"
              >
                <span className="text-xs font-mono text-muted-foreground whitespace-nowrap">
                  {formatTimestamp(log.timestamp)}
                </span>
                <span className="text-xs font-mono text-muted-foreground">
                  #{log.account_id}
                </span>
                <span className={`text-xs flex-1 ${getLogColor(log.message)}`}>
                  {log.message}
                </span>
              </div>
            ))
          )}
        </div>
      </ScrollArea>
    </Card>
  );
};

export default LogsViewer;