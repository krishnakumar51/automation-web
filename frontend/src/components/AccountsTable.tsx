import { useState } from "react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { 
  RefreshCw, 
  Trash2, 
  Eye, 
  EyeOff, 
  Copy,
  Users,
  AlertTriangle
} from "lucide-react";
import { useToast } from "@/hooks/use-toast";
import { Account, deleteAccount, clearAllAccounts } from "@/services/api";
import StatusBadge from "./StatusBadge";

interface AccountsTableProps {
  accounts: Account[];
  onRefresh: () => void;
  isLoading: boolean;
}

const AccountsTable = ({ accounts, onRefresh, isLoading }: AccountsTableProps) => {
  const [showPasswords, setShowPasswords] = useState<{ [key: number]: boolean }>({});
  const [deletingIds, setDeletingIds] = useState<Set<number>>(new Set());
  const [clearingAll, setClearingAll] = useState(false);
  const { toast } = useToast();

  const togglePasswordVisibility = (accountId: number) => {
    setShowPasswords(prev => ({
      ...prev,
      [accountId]: !prev[accountId]
    }));
  };

  const copyToClipboard = async (text: string, label: string) => {
    try {
      await navigator.clipboard.writeText(text);
      toast({
        title: "Copied!",
        description: `${label} copied to clipboard`,
      });
    } catch (error) {
      toast({
        title: "Copy failed",
        description: "Unable to copy to clipboard",
        variant: "destructive",
      });
    }
  };

  const handleDeleteAccount = async (accountId: number) => {
    setDeletingIds(prev => new Set(prev).add(accountId));
    
    try {
      await deleteAccount(accountId);
      toast({
        title: "Account Deleted",
        description: "Account has been successfully deleted",
      });
      onRefresh();
    } catch (error) {
      toast({
        title: "Delete Failed",
        description: "Failed to delete account",
        variant: "destructive",
      });
    } finally {
      setDeletingIds(prev => {
        const newSet = new Set(prev);
        newSet.delete(accountId);
        return newSet;
      });
    }
  };

  const handleClearAll = async () => {
    setClearingAll(true);
    
    try {
      await clearAllAccounts();
      toast({
        title: "All Accounts Cleared",
        description: "All accounts have been successfully deleted",
      });
      onRefresh();
    } catch (error) {
      toast({
        title: "Clear Failed",
        description: "Failed to clear all accounts",
        variant: "destructive",
      });
    } finally {
      setClearingAll(false);
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  return (
    <Card className="bg-gradient-card border-border/50 shadow-card">
      <div className="p-4 border-b border-border/50">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <Users className="w-4 h-4 text-primary" />
            <h3 className="font-semibold text-foreground">Created Accounts</h3>
            <Badge variant="outline" className="bg-primary/10 text-primary border-primary/20">
              {accounts.length} total
            </Badge>
          </div>
          <div className="flex items-center space-x-2">
            <Button
              onClick={onRefresh}
              size="sm"
              variant="outline"
              className="h-8 border-border/50 hover:bg-accent"
              disabled={isLoading}
            >
              <RefreshCw className={`w-3 h-3 mr-1 ${isLoading ? 'animate-spin' : ''}`} />
              Refresh
            </Button>
            {accounts.length > 0 && (
              <Button
                onClick={handleClearAll}
                size="sm"
                variant="outline"
                className="h-8 border-destructive/20 text-destructive hover:bg-destructive/10"
                disabled={clearingAll}
              >
                <Trash2 className="w-3 h-3 mr-1" />
                {clearingAll ? 'Clearing...' : 'Clear All'}
              </Button>
            )}
          </div>
        </div>
      </div>

      <div className="overflow-x-auto">
        {accounts.length === 0 ? (
          <div className="text-center py-12">
            <Users className="w-12 h-12 mx-auto text-muted-foreground/30 mb-4" />
            <h4 className="text-lg font-medium text-foreground mb-2">No Accounts Yet</h4>
            <p className="text-sm text-muted-foreground">
              Create your first account to see it appear here
            </p>
          </div>
        ) : (
          <Table>
            <TableHeader>
              <TableRow className="border-border/50 hover:bg-transparent">
                <TableHead className="text-muted-foreground">ID</TableHead>
                <TableHead className="text-muted-foreground">Name</TableHead>
                <TableHead className="text-muted-foreground">Email</TableHead>
                <TableHead className="text-muted-foreground">Password</TableHead>
                <TableHead className="text-muted-foreground">Birth Date</TableHead>
                <TableHead className="text-muted-foreground">Status</TableHead>
                <TableHead className="text-muted-foreground">Created</TableHead>
                <TableHead className="text-muted-foreground w-20">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {accounts.map((account) => (
                <TableRow 
                  key={account.id} 
                  className="border-border/50 hover:bg-accent/30 transition-colors"
                >
                  <TableCell className="font-mono text-sm text-foreground">
                    #{account.id}
                  </TableCell>
                  <TableCell className="text-foreground">
                    {account.first_name} {account.last_name}
                  </TableCell>
                  <TableCell>
                    <div className="flex items-center space-x-2">
                      <span className="font-mono text-sm text-foreground">
                        {account.email}
                      </span>
                      <Button
                        onClick={() => copyToClipboard(account.email, 'Email')}
                        size="sm"
                        variant="ghost"
                        className="h-6 w-6 p-0 hover:bg-accent"
                      >
                        <Copy className="w-3 h-3" />
                      </Button>
                    </div>
                  </TableCell>
                  <TableCell>
                    <div className="flex items-center space-x-2">
                      <span className="font-mono text-sm text-foreground">
                        {showPasswords[account.id] ? account.password : '••••••••'}
                      </span>
                      <Button
                        onClick={() => togglePasswordVisibility(account.id)}
                        size="sm"
                        variant="ghost"
                        className="h-6 w-6 p-0 hover:bg-accent"
                      >
                        {showPasswords[account.id] ? (
                          <EyeOff className="w-3 h-3" />
                        ) : (
                          <Eye className="w-3 h-3" />
                        )}
                      </Button>
                      <Button
                        onClick={() => copyToClipboard(account.password, 'Password')}
                        size="sm"
                        variant="ghost"
                        className="h-6 w-6 p-0 hover:bg-accent"
                      >
                        <Copy className="w-3 h-3" />
                      </Button>
                    </div>
                  </TableCell>
                  <TableCell className="text-sm text-foreground">
                    {account.birth_month} {account.birth_day}, {account.birth_year}
                  </TableCell>
                  <TableCell>
                    <StatusBadge status={account.status} />
                  </TableCell>
                  <TableCell className="text-sm text-muted-foreground">
                    {formatDate(account.created_at)}
                  </TableCell>
                  <TableCell>
                    <Button
                      onClick={() => handleDeleteAccount(account.id)}
                      size="sm"
                      variant="ghost"
                      className="h-6 w-6 p-0 text-destructive hover:bg-destructive/10"
                      disabled={deletingIds.has(account.id)}
                    >
                      {deletingIds.has(account.id) ? (
                        <RefreshCw className="w-3 h-3 animate-spin" />
                      ) : (
                        <Trash2 className="w-3 h-3" />
                      )}
                    </Button>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        )}
      </div>
    </Card>
  );
};

export default AccountsTable;