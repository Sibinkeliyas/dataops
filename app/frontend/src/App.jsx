import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider } from 'next-themes';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Toaster } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import Layout from './components/Layout';
import Login from './pages/Login';
import Index from './pages/Index';
import Home from './pages/Home';
import Dashboard from './pages/Dashboard';
import DataCatalog from './pages/DataCatalog';
import BiAnalytics from './pages/BiAnalytics';
import MachineLearningAI from './pages/MachineLearningAI';
import DataEngineering from './pages/DataEngineering';
import DatabricksWorkspace from './pages/DatabricksWorkspace';
import AICopilot from './pages/AICopilot';
import ARSolutions from './pages/ARSolutions';
import DataOpsPortal from './pages/DataOpsPortal';
import SupportResources from './pages/SupportResources';
import AdminPage from './pages/AdminPage';
import AskQueries from './pages/AskQueries';
import { useSelector } from 'react-redux';

const queryClient = new QueryClient();

const App = () => {
  const [isLogged, setIsLogged] = useState(true);
  const [userEmail, setUserEmail] = useState('');

  const {isAuthenticated, user } = useSelector((state) => state.authReducer);

  const ProtectedRoute = ({ children }) => {
    if (!isLogged) {
      return <Navigate to="/login" replace />;
    }
    return children;
  };


  const AdminRoute = ({ children }) => {
    if (!isLogged || user?.role?.role !== 'Admin') {
      return <Navigate to="/" replace />;
    }
    return children;
  };

  return (
    <ThemeProvider attribute="class" defaultTheme="system" enableSystem>
      <QueryClientProvider client={queryClient}>
        <TooltipProvider>
          <Router>
            <Routes>
              <Route path="/login" element={<Login setIsLogged={setIsLogged} setUserEmail={setUserEmail} />} />
              <Route
                path="*"
                element={
                  <ProtectedRoute>
                    <Layout userEmail={userEmail}>
                      <Routes>
                        <Route path="/" element={<Index />} />
                        <Route path="/home" element={<Home />} />
                        <Route path="/dashboard" element={<Dashboard />} />
                        <Route path="/data-catalog" element={<DataCatalog />} />
                        <Route path="/bi-analytics" element={<BiAnalytics />} />
                        <Route path="/machine-learning-ai" element={<MachineLearningAI />} />
                        <Route path="/data-engineering" element={<DataEngineering />} />
                        <Route path="/data-engineering/databricks" element={<DatabricksWorkspace />} />
                        <Route path="/ai-copilot" element={<AICopilot />} />
                        <Route path="/ar-solutions" element={<ARSolutions />} />
                        <Route path="/dataops-portal" element={<DataOpsPortal />} />
                        <Route path="/support-resources" element={<SupportResources />} />
                        <Route path="/ask-queries" element={<AskQueries />} />
                        <Route path="/admin" element={<AdminRoute><AdminPage /></AdminRoute>} />
                      </Routes>
                    </Layout>
                  </ProtectedRoute>
                }
              />
            </Routes>
          </Router>
          <Toaster />
        </TooltipProvider>
      </QueryClientProvider>
    </ThemeProvider>
  );
};

export default App;