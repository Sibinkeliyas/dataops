import React from 'react';
import { Routes, Route, Link } from 'react-router-dom';
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Brain, Code, Zap, BarChart, FileText, Database } from 'lucide-react';
import ProjectsOverview from '../components/MachineLearning/ProjectsOverview';
import ProjectDetail from '../components/MachineLearning/ProjectDetail';
import DatabricksIntegration from '../components/MachineLearning/DatabricksIntegration';

const MachineLearningAI = () => {
  return (
    <div className="container mx-auto px-4 py-8">
      <nav className="text-sm mb-4" aria-label="Breadcrumb">
        <ol className="list-none p-0 inline-flex">
          <li className="flex items-center">
            <Link to="/" className="text-blue-500">Home</Link>
            <span className="mx-2">/</span>
          </li>
          <li className="flex items-center">
            Machine Learning and AI
          </li>
        </ol>
      </nav>

      <h1 className="text-3xl font-bold mb-6">Machine Learning and AI</h1>
      <p className="text-lg mb-8">Build predictive models, integrate with Azure AI Studio, and utilize user-friendly ML interfaces.</p>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <Brain className="mr-2" /> AI Projects
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p>Manage and monitor your AI and ML projects.</p>
            <Link to="/machine-learning-ai/projects">
              <Button className="mt-4">View Projects</Button>
            </Link>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <Code className="mr-2" /> Azure AI Studio
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p>Access Azure AI Studio for advanced AI development and deployment.</p>
            <Button className="mt-4" onClick={() => window.open('https://studio.azureml.net', '_blank')}>Open AI Studio</Button>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <Database className="mr-2" /> Databricks Integration
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p>Integrate models and data from Databricks.</p>
            <Link to="/machine-learning-ai/databricks">
              <Button className="mt-4">Manage Integration</Button>
            </Link>
          </CardContent>
        </Card>
      </div>

      <Routes>
        <Route path="/" element={<ProjectsOverview />} />
        <Route path="/projects" element={<ProjectsOverview />} />
        <Route path="/projects/:id" element={<ProjectDetail />} />
        <Route path="/databricks" element={<DatabricksIntegration />} />
      </Routes>
    </div>
  );
};

export default MachineLearningAI;