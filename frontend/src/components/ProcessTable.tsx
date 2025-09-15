import { useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Progress } from "@/components/ui/progress";
import { Badge } from "@/components/ui/badge";
import { useToast } from "@/hooks/use-toast";
import { 
  RefreshCw, 
  Trash2, 
  Eye, 
  Mail, 
  Building, 
  FileText, 
  CheckCircle,
  Clock,
  AlertCircle,
  Loader2
} from "lucide-react";
import { Process, deleteProcess, clearAllProcesses } from "@/services/api";
import ProcessStatusBadge from "./ProcessStatusBadge";
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from "@/components/ui/collapsible";

interface ProcessTableProps {
  processes: Process[];
  onRefresh: () => void;
  isLoading: boolean;
}

const ProcessTable = ({ processes, onRefresh, isLoading }: ProcessTableProps) => {
  const [deletingProcesses, setDeletingProcesses] = useState<Set<string>>(new Set());
  const [isClearingAll, setIsClearingAll] = useState(false);
  const [expandedProcess, setExpandedProcess] = useState<string | null>(null);
  const { toast } = useToast();

  const handleDeleteProcess = async (processId: string) => {
    setDeletingProcesses(prev => new Set([...prev, processId]));
    
    try {
      await deleteProcess(processId);
      toast({
        title: "Process Deleted",
        description: "Process has been successfully deleted",
      });
      onRefresh();
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to delete process",
        variant: "destructive",
      });
    } finally {
      setDeletingProcesses(prev => {
        const newSet = new Set(prev);
        newSet.delete(processId);
        return newSet;
      });
    }
  };

  const handleClearAll = async () => {
    setIsClearingAll(true);
    
    try {
      await clearAllProcesses();
      toast({
        title: "All Processes Cleared",
        description: "All processes have been successfully deleted",
      });
      onRefresh();
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to clear all processes",
        variant: "destructive",
      });
    } finally {
      setIsClearingAll(false);
    }
  };

  const getStageIcon = (stage: string) => {
    switch (stage) {
      case 'outlook_creation':
        return <Mail className="w-4 h-4" />;
      case 'imss_processing':
        return <Building className="w-4 h-4" />;
      case 'email_monitoring':
        return <Mail className="w-4 h-4" />;
      case 'pdf_ready':
        return <FileText className="w-4 h-4" />;
      case 'error':
        return <AlertCircle className="w-4 h-4" />;
      default:
        return <Clock className="w-4 h-4" />;
    }
  };

  const getStageLabel = (stage: string) => {
    switch (stage) {
      case 'outlook_creation':
        return 'Creating Account';
      case 'imss_processing':
        return 'IMSS Processing';
      case 'email_monitoring':
        return 'Monitoring Email';
      case 'pdf_ready':
        return 'PDF Ready';
      case 'error':
        return 'Error';
      default:
        return 'Unknown';
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString();
  };

  const truncateId = (id: string) => {
    return `${id.substring(0, 8)}...`;
  };

  if (processes.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center justify-between">
            <span>Active Processes (0)</span>
            <Button 
              variant="outline" 
              size="sm" 
              onClick={onRefresh}
              disabled={isLoading}
            >
              <RefreshCw className={`w-4 h-4 mr-2 ${isLoading ? 'animate-spin' : ''}`} />
              Refresh
            </Button>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center py-12 text-muted-foreground">
            <FileText className="w-12 h-12 mx-auto mb-4 opacity-50" />
            <p className="text-lg font-medium mb-2">No processes yet</p>
            <p>Start by creating a new CURP process or demo above</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center justify-between">
          <span>Active Processes ({processes.length})</span>
          <div className="flex gap-2">
            <Button 
              variant="outline" 
              size="sm" 
              onClick={onRefresh}
              disabled={isLoading}
            >
              <RefreshCw className={`w-4 h-4 mr-2 ${isLoading ? 'animate-spin' : ''}`} />
              Refresh
            </Button>
            <Button 
              variant="destructive" 
              size="sm" 
              onClick={handleClearAll}
              disabled={isClearingAll || processes.length === 0}
            >
              {isClearingAll ? (
                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
              ) : (
                <Trash2 className="w-4 h-4 mr-2" />
              )}
              Clear All
            </Button>
          </div>
        </CardTitle>
        <CardDescription>
          Auto-refresh every 10 seconds • Click process for details
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-2">
          {processes.map((process) => (
            <Collapsible 
              key={process.process_id}
              open={expandedProcess === process.process_id}
              onOpenChange={(open) => setExpandedProcess(open ? process.process_id : null)}
            >
              <CollapsibleTrigger asChild>
                <div className="w-full p-4 border rounded-lg hover:bg-muted/50 transition-colors cursor-pointer">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-4 flex-1">
                      <div className="font-mono text-sm text-muted-foreground">
                        {truncateId(process.process_id)}
                      </div>
                      <div>
                        <div className="font-medium">
                          {process.first_name} {process.last_name}
                        </div>
                        <div className="text-sm text-muted-foreground">
                          {process.curp_id}
                        </div>
                      </div>
                    </div>
                    
                    <div className="flex items-center gap-4">
                      <div className="text-center">
                        <ProcessStatusBadge status={process.overall_status} />
                        <div className="flex items-center gap-1 mt-1 text-xs text-muted-foreground">
                          {getStageIcon(process.current_stage)}
                          {getStageLabel(process.current_stage)}
                        </div>
                      </div>
                      
                      <div className="w-24">
                        <Progress value={process.progress_percentage} className="h-2" />
                        <div className="text-xs text-center mt-1 text-muted-foreground">
                          {process.progress_percentage}%
                        </div>
                      </div>
                      
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={(e) => {
                          e.stopPropagation();
                          handleDeleteProcess(process.process_id);
                        }}
                        disabled={deletingProcesses.has(process.process_id)}
                      >
                        {deletingProcesses.has(process.process_id) ? (
                          <Loader2 className="w-4 h-4 animate-spin" />
                        ) : (
                          <Trash2 className="w-4 h-4" />
                        )}
                      </Button>
                    </div>
                  </div>
                </div>
              </CollapsibleTrigger>
              
              <CollapsibleContent>
                <div className="px-4 pb-4 pt-2 border-l border-r border-b rounded-b-lg bg-muted/20">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <h4 className="font-medium mb-2">Process Details</h4>
                      <div className="space-y-1 text-sm">
                        <div><span className="text-muted-foreground">Process ID:</span> {process.process_id}</div>
                        <div><span className="text-muted-foreground">Email:</span> {process.email || 'Not assigned'}</div>
                        <div><span className="text-muted-foreground">Created:</span> {formatDate(process.created_at)}</div>
                        <div><span className="text-muted-foreground">Updated:</span> {formatDate(process.updated_at)}</div>
                      </div>
                    </div>
                    
                    <div>
                      <h4 className="font-medium mb-2">Service Status</h4>
                      <div className="space-y-2">
                        <div className="flex justify-between items-center">
                          <span className="text-sm flex items-center gap-2">
                            <Mail className="w-4 h-4" />
                            Outlook
                          </span>
                          <Badge variant={process.outlook_status === 'completed' ? 'default' : 'secondary'}>
                            {process.outlook_status || 'pending'}
                          </Badge>
                        </div>
                        <div className="flex justify-between items-center">
                          <span className="text-sm flex items-center gap-2">
                            <Building className="w-4 h-4" />
                            IMSS
                          </span>
                          <Badge variant={process.imss_status === 'completed' ? 'default' : 'secondary'}>
                            {process.imss_status || 'pending'}
                          </Badge>
                        </div>
                        <div className="flex justify-between items-center">
                          <span className="text-sm flex items-center gap-2">
                            <Mail className="w-4 h-4" />
                            Email
                          </span>
                          <Badge variant={process.email_status === 'completed' ? 'default' : 'secondary'}>
                            {process.email_status || 'pending'}
                          </Badge>
                        </div>
                        <div className="flex justify-between items-center">
                          <span className="text-sm flex items-center gap-2">
                            <FileText className="w-4 h-4" />
                            PDF
                          </span>
                          <Badge variant={process.pdf_status === 'completed' ? 'default' : 'secondary'}>
                            {process.pdf_status || 'pending'}
                          </Badge>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </CollapsibleContent>
            </Collapsible>
          ))}
        </div>
      </CardContent>
    </Card>
  );
};

export default ProcessTable;