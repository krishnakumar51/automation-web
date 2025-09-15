import { FileText, Zap } from "lucide-react";

const Header = () => {
  return (
    <header className="border-b border-border bg-card shadow-card">
      <div className="container mx-auto px-6 py-4">
        <div className="flex items-center space-x-3">
          <div className="flex items-center justify-center w-10 h-10 rounded-lg bg-gradient-primary shadow-glow">
            <FileText className="w-5 h-5 text-primary-foreground" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-foreground">
              CURP-to-PDF Automation Dashboard
            </h1>
            <p className="text-sm text-muted-foreground">
              Process CURP documents and generate PDF reports - v2.0.0
            </p>
          </div>
          <div className="ml-auto flex items-center space-x-2">
            <div className="flex items-center space-x-1 px-3 py-1 bg-success/10 border border-success/20 rounded-full">
              <Zap className="w-3 h-3 text-success" />
              <span className="text-xs font-medium text-success">Live</span>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;