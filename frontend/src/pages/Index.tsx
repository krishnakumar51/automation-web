import { useState, useEffect } from "react";
import { useToast } from "@/hooks/use-toast";
import Header from "@/components/Header";
import AccountForm from "@/components/AccountForm";
import LogsViewer from "@/components/LogsViewer";
import AccountsTable from "@/components/AccountsTable";
import { getAccounts, getLogs, Account, LogEntry } from "@/services/api";

const Index = () => {
  const [accounts, setAccounts] = useState<Account[]>([]);
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [isCreating, setIsCreating] = useState(false);
  const [isLoadingAccounts, setIsLoadingAccounts] = useState(false);
  const { toast } = useToast();

  // Fetch accounts
  const fetchAccounts = async () => {
    setIsLoadingAccounts(true);
    try {
      const data = await getAccounts();
      setAccounts(data);
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to fetch accounts",
        variant: "destructive",
      });
    } finally {
      setIsLoadingAccounts(false);
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

  // Handle account creation start
  const handleCreationStart = () => {
    setIsCreating(true);
  };

  // Handle accounts created
  const handleAccountsCreated = () => {
    fetchAccounts();
  };

  // Auto-refresh logs when creating
  useEffect(() => {
    if (isCreating) {
      const interval = setInterval(fetchLogs, 2000);
      const timeout = setTimeout(() => {
        setIsCreating(false);
      }, 60000); // Stop after 1 minute

      return () => {
        clearInterval(interval);
        clearTimeout(timeout);
      };
    }
  }, [isCreating]);

  // Auto-refresh accounts periodically
  useEffect(() => {
    fetchAccounts();
    const interval = setInterval(fetchAccounts, 10000); // Every 10 seconds
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="min-h-screen bg-background">
      <Header />
      
      <main className="container mx-auto px-6 py-8">
        <div className="grid grid-cols-1 xl:grid-cols-2 gap-8">
          {/* Left Column */}
          <div className="space-y-6">
            <AccountForm 
              onAccountsCreated={handleAccountsCreated}
              onCreationStart={handleCreationStart}
            />
            
            <LogsViewer 
              logs={logs} 
              onClearLogs={clearLogs}
            />
          </div>

          {/* Right Column */}
          <div>
            <AccountsTable 
              accounts={accounts}
              onRefresh={fetchAccounts}
              isLoading={isLoadingAccounts}
            />
          </div>
        </div>
      </main>
    </div>
  );
};

export default Index;
