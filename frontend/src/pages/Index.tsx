import { useState, useEffect } from "react";
import { useToast } from "@/hooks/use-toast";
import Header from "@/components/Header";
import ProcessForm from "@/components/ProcessForm";
import LogsViewer from "@/components/LogsViewer";
import ProcessTable from "@/components/ProcessTable";
import { getProcesses, getLogs, Process, LogEntry } from "@/services/api";

const Index = () => {
  const [processes, setProcesses] = useState<Process[]>([]);
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [isProcessing, setIsProcessing] = useState(false);
  const [isLoadingProcesses, setIsLoadingProcesses] = useState(false);
  const { toast } = useToast();

  // Fetch processes
  const fetchProcesses = async () => {
    setIsLoadingProcesses(true);
    try {
      const data = await getProcesses();
      setProcesses(data);
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to fetch processes",
        variant: "destructive",
      });
    } finally {
      setIsLoadingProcesses(false);
    }
  };

  // Fetch logs
  const fetchLogs = async () => {
    try {
      const data = await getLogs();
      setLogs(data.logs);
    } catch (error) {
      // Silently fail for logs to avoid spam
      console.error("Failed to fetch logs:", error);
    }
  };

  // Clear logs
  const clearLogs = () => {
    setLogs([]);
  };

  // Handle process creation start
  const handleProcessStart = () => {
    setIsProcessing(true);
  };

  // Handle processes created
  const handleProcessCreated = () => {
    fetchProcesses();
  };

  // Auto-refresh logs when processing
  useEffect(() => {
    if (isProcessing) {
      const interval = setInterval(fetchLogs, 2000);
      const timeout = setTimeout(() => {
        setIsProcessing(false);
      }, 60000); // Stop after 1 minute

      return () => {
        clearInterval(interval);
        clearTimeout(timeout);
      };
    }
  }, [isProcessing]);

  // Auto-refresh processes periodically
  useEffect(() => {
    fetchProcesses();
    const interval = setInterval(fetchProcesses, 10000); // Every 10 seconds
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="min-h-screen bg-background">
      <Header />
      
      <main className="container mx-auto px-6 py-8">
        <div className="space-y-8">
          {/* Process Forms */}
          <ProcessForm 
            onProcessCreated={handleProcessCreated}
            onProcessStart={handleProcessStart}
          />
          
          <div className="grid grid-cols-1 xl:grid-cols-2 gap-8">
            {/* Left Column - Process Table */}
            <div>
              <ProcessTable 
                processes={processes}
                onRefresh={fetchProcesses}
                isLoading={isLoadingProcesses}
              />
            </div>

            {/* Right Column - Logs */}
            <div>
              <LogsViewer 
                logs={logs} 
                onClearLogs={clearLogs}
              />
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};

export default Index;
