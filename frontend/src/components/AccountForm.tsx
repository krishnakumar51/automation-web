import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card } from "@/components/ui/card";
import { Users, Zap, Loader2 } from "lucide-react";
import { useToast } from "@/hooks/use-toast";
import { createAccounts, createDemo } from "@/services/api";

interface AccountFormProps {
  onAccountsCreated: () => void;
  onCreationStart: () => void;
}

const AccountForm = ({ onAccountsCreated, onCreationStart }: AccountFormProps) => {
  const [count, setCount] = useState(3);
  const [isCreating, setIsCreating] = useState(false);
  const [isDemo, setIsDemo] = useState(false);
  const { toast } = useToast();

  const handleCreateAccounts = async () => {
    if (count < 1 || count > 10) {
      toast({
        title: "Invalid Count",
        description: "Please enter a number between 1 and 10",
        variant: "destructive",
      });
      return;
    }

    setIsCreating(true);
    onCreationStart();

    try {
      const response = await createAccounts(count);
      toast({
        title: "Account Creation Started",
        description: response.message,
      });
      onAccountsCreated();
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to start account creation",
        variant: "destructive",
      });
    } finally {
      setIsCreating(false);
    }
  };

  const handleCreateDemo = async () => {
    setIsDemo(true);
    onCreationStart();

    try {
      const response = await createDemo();
      toast({
        title: "Demo Account Started",
        description: `Creating demo account: ${response.account_data.email}`,
      });
      onAccountsCreated();
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to create demo account",
        variant: "destructive",
      });
    } finally {
      setIsDemo(false);
    }
  };

  return (
    <Card className="p-6 bg-gradient-card border-border/50 shadow-card">
      <div className="space-y-6">
        <div>
          <h2 className="text-xl font-semibold text-foreground mb-2">
            Create Accounts
          </h2>
          <p className="text-sm text-muted-foreground">
            Generate multiple Outlook accounts or create a demo account
          </p>
        </div>

        <div className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="count" className="text-sm font-medium text-foreground">
              Number of Accounts (1-10)
            </Label>
            <Input
              id="count"
              type="number"
              min="1"
              max="10"
              value={count}
              onChange={(e) => setCount(parseInt(e.target.value) || 1)}
              className="bg-background border-border focus:border-primary focus:ring-primary/20"
              disabled={isCreating || isDemo}
            />
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <Button
              onClick={handleCreateAccounts}
              disabled={isCreating || isDemo}
              className="w-full bg-gradient-primary hover:shadow-glow transition-all duration-300 border-0"
            >
              {isCreating ? (
                <>
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  Creating...
                </>
              ) : (
                <>
                  <Users className="w-4 h-4 mr-2" />
                  Create {count} Account{count !== 1 ? 's' : ''}
                </>
              )}
            </Button>

            <Button
              onClick={handleCreateDemo}
              disabled={isCreating || isDemo}
              variant="outline"
              className="w-full border-primary/20 bg-primary/5 hover:bg-primary/10 text-primary hover:text-primary transition-all duration-300"
            >
              {isDemo ? (
                <>
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  Creating Demo...
                </>
              ) : (
                <>
                  <Zap className="w-4 h-4 mr-2" />
                  Quick Demo
                </>
              )}
            </Button>
          </div>
        </div>
      </div>
    </Card>
  );
};

export default AccountForm;