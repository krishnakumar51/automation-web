import { useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useToast } from "@/hooks/use-toast";
import { Loader2, FileText, PlayCircle } from "lucide-react";
import { processRealCURP, processDemoCURP, ProcessCURPRequest } from "@/services/api";

interface ProcessFormProps {
  onProcessCreated: () => void;
  onProcessStart: () => void;
}

const ProcessForm = ({ onProcessCreated, onProcessStart }: ProcessFormProps) => {
  const [curpData, setCurpData] = useState<ProcessCURPRequest>({
    curp_id: "",
    first_name: "",
    last_name: "",
    date_of_birth: "",
  });
  const [demoCount, setDemoCount] = useState(1);
  const [isProcessing, setIsProcessing] = useState(false);
  const [isDemoProcessing, setIsDemoProcessing] = useState(false);
  const { toast } = useToast();

  const validateCURP = (curp: string): boolean => {
    // Basic CURP validation - 18 characters
    return curp.length === 18 && /^[A-Z]{4}\d{6}[HM][A-Z]{5}\d{2}$/.test(curp);
  };

  const handleProcessCURP = async () => {
    if (!curpData.curp_id || !curpData.first_name || !curpData.last_name || !curpData.date_of_birth) {
      toast({
        title: "Validation Error",
        description: "Please fill in all required fields",
        variant: "destructive",
      });
      return;
    }

    if (!validateCURP(curpData.curp_id)) {
      toast({
        title: "Invalid CURP",
        description: "CURP must be 18 characters in the correct format",
        variant: "destructive",
      });
      return;
    }

    setIsProcessing(true);
    onProcessStart();

    try {
      const response = await processRealCURP(curpData);
      toast({
        title: "Process Started",
        description: `Started processing CURP: ${response.curp_data.curp_id}`,
      });
      onProcessCreated();
      setCurpData({
        curp_id: "",
        first_name: "",
        last_name: "",
        date_of_birth: "",
      });
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to start CURP processing",
        variant: "destructive",
      });
    } finally {
      setIsProcessing(false);
    }
  };

  const handleDemoProcess = async () => {
    if (demoCount < 1 || demoCount > 5) {
      toast({
        title: "Invalid Count",
        description: "Demo count must be between 1 and 5",
        variant: "destructive",
      });
      return;
    }

    setIsDemoProcessing(true);
    onProcessStart();

    try {
      const response = await processDemoCURP(demoCount);
      toast({
        title: "Demo Process Started",
        description: `Started processing ${response.process_ids.length} demo CURPs`,
      });
      onProcessCreated();
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to start demo processing",
        variant: "destructive",
      });
    } finally {
      setIsDemoProcessing(false);
    }
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      {/* Real CURP Processing Form */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <FileText className="w-5 h-5" />
            Process Real CURP
          </CardTitle>
          <CardDescription>
            Enter CURP details to start the processing workflow
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="curp_id">CURP ID *</Label>
            <Input
              id="curp_id"
              placeholder="e.g., AAAA123456HDFBBB01"
              value={curpData.curp_id}
              onChange={(e) => setCurpData({ ...curpData, curp_id: e.target.value.toUpperCase() })}
              maxLength={18}
              className="font-mono"
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="first_name">First Name *</Label>
              <Input
                id="first_name"
                placeholder="Enter first name"
                value={curpData.first_name}
                onChange={(e) => setCurpData({ ...curpData, first_name: e.target.value })}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="last_name">Last Name *</Label>
              <Input
                id="last_name"
                placeholder="Enter last name"
                value={curpData.last_name}
                onChange={(e) => setCurpData({ ...curpData, last_name: e.target.value })}
              />
            </div>
          </div>

          <div className="space-y-2">
            <Label htmlFor="date_of_birth">Date of Birth *</Label>
            <Input
              id="date_of_birth"
              type="date"
              value={curpData.date_of_birth}
              onChange={(e) => setCurpData({ ...curpData, date_of_birth: e.target.value })}
            />
          </div>

          <Button 
            onClick={handleProcessCURP} 
            disabled={isProcessing}
            className="w-full"
          >
            {isProcessing ? (
              <>
                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                Starting Process...
              </>
            ) : (
              <>
                <FileText className="w-4 h-4 mr-2" />
                Start Processing
              </>
            )}
          </Button>
        </CardContent>
      </Card>

      {/* Demo Processing Form */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <PlayCircle className="w-5 h-5" />
            Demo Processing
          </CardTitle>
          <CardDescription>
            Process demo CURPs for testing (1-5 processes)
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="demo_count">Number of Demo Processes</Label>
            <Input
              id="demo_count"
              type="number"
              min="1"
              max="5"
              value={demoCount}
              onChange={(e) => setDemoCount(parseInt(e.target.value) || 1)}
            />
          </div>

          <div className="text-sm text-muted-foreground bg-muted/50 p-3 rounded-md">
            <p className="font-medium mb-1">Demo will create:</p>
            <ul className="list-disc list-inside space-y-1">
              <li>{demoCount} random CURP{demoCount > 1 ? 's' : ''}</li>
              <li>Simulated processing workflow</li>
              <li>Test data for all stages</li>
            </ul>
          </div>

          <div className="grid grid-cols-3 gap-2">
            {[1, 3, 5].map((count) => (
              <Button
                key={count}
                variant="outline"
                size="sm"
                onClick={() => setDemoCount(count)}
                className={demoCount === count ? "bg-primary/10" : ""}
              >
                {count} Process{count > 1 ? 'es' : ''}
              </Button>
            ))}
          </div>

          <Button 
            onClick={handleDemoProcess} 
            disabled={isDemoProcessing}
            className="w-full"
            variant="secondary"
          >
            {isDemoProcessing ? (
              <>
                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                Starting Demo...
              </>
            ) : (
              <>
                <PlayCircle className="w-4 h-4 mr-2" />
                Start Demo Processing
              </>
            )}
          </Button>
        </CardContent>
      </Card>
    </div>
  );
};

export default ProcessForm;