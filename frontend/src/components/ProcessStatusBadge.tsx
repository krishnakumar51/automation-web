import { Badge } from "@/components/ui/badge";
import { CheckCircle, Clock, Loader2, XCircle } from "lucide-react";

interface ProcessStatusBadgeProps {
  status: 'pending' | 'in_progress' | 'completed' | 'failed';
}

const ProcessStatusBadge = ({ status }: ProcessStatusBadgeProps) => {
  const getStatusConfig = () => {
    switch (status) {
      case 'completed':
        return {
          icon: CheckCircle,
          text: 'Completed',
          className: 'bg-success/10 text-success border-success/20 hover:bg-success/20',
        };
      case 'in_progress':
        return {
          icon: Loader2,
          text: 'Processing',
          className: 'bg-blue-500/10 text-blue-500 border-blue-500/20 hover:bg-blue-500/20',
          animate: true,
        };
      case 'pending':
        return {
          icon: Clock,
          text: 'Pending',
          className: 'bg-pending/10 text-pending border-pending/20 hover:bg-pending/20',
        };
      case 'failed':
        return {
          icon: XCircle,
          text: 'Failed',
          className: 'bg-destructive/10 text-destructive border-destructive/20 hover:bg-destructive/20',
        };
      default:
        return {
          icon: Clock,
          text: 'Unknown',
          className: 'bg-muted text-muted-foreground border-border',
        };
    }
  };

  const { icon: Icon, text, className, animate } = getStatusConfig();

  return (
    <Badge variant="outline" className={className}>
      <Icon className={`w-3 h-3 mr-1 ${animate ? 'animate-spin' : ''}`} />
      {text}
    </Badge>
  );
};

export default ProcessStatusBadge;