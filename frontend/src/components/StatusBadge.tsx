import { Badge } from "@/components/ui/badge";
import { CheckCircle, Clock, XCircle } from "lucide-react";

interface StatusBadgeProps {
  status: 'pending' | 'success' | 'failed';
}

const StatusBadge = ({ status }: StatusBadgeProps) => {
  const getStatusConfig = () => {
    switch (status) {
      case 'success':
        return {
          icon: CheckCircle,
          text: 'Success',
          className: 'bg-success/10 text-success border-success/20 hover:bg-success/20',
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

  const { icon: Icon, text, className } = getStatusConfig();

  return (
    <Badge variant="outline" className={className}>
      <Icon className="w-3 h-3 mr-1" />
      {text}
    </Badge>
  );
};

export default StatusBadge;