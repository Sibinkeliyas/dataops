import React from 'react';
import { Link } from 'react-router-dom';
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { useQuery } from '@tanstack/react-query';
import { fetchAIProjects } from '../../utils/dataFetching.jsx';
import { Activity, AlertTriangle, CheckCircle } from 'lucide-react';

const ProjectCard = ({ project }) => {
  const getStatusIcon = (status) => {
    switch (status) {
      case 'Active':
        return <Activity className="text-blue-500" />;
      case 'Deployed':
        return <CheckCircle className="text-green-500" />;
      case 'Needs Attention':
        return <AlertTriangle className="text-yellow-500" />;
      default:
        return null;
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center justify-between">
          <span>{project.name}</span>
          <Badge variant={project.status === 'Deployed' ? 'success' : project.status === 'Needs Attention' ? 'warning' : 'default'}>
            {getStatusIcon(project.status)}
            <span className="ml-2">{project.status}</span>
          </Badge>
        </CardTitle>
      </CardHeader>
      <CardContent>
        <p className="text-sm text-gray-600 mb-2">Type: {project.type}</p>
        <p className="text-sm text-gray-600 mb-4">Last Updated: {project.lastUpdated}</p>
        <div className="flex space-x-2">
          <Button size="sm" onClick={() => window.open('https://studio.azureml.net', '_blank')}>Open in Azure AI Studio</Button>
          <Link to={`/machine-learning-ai/projects/${project.id}`}>
            <Button size="sm" variant="outline">View Details</Button>
          </Link>
        </div>
      </CardContent>
    </Card>
  );
};

const ProjectsOverview = () => {
  const { data: projects, isLoading, error } = useQuery({
    queryKey: ['aiProjects'],
    queryFn: fetchAIProjects,
  });

  if (isLoading) return <div>Loading projects...</div>;
  if (error) return <div>Error loading projects: {error.message}</div>;

  return (
    <div>
      <h2 className="text-2xl font-bold mb-4">AI Projects Overview</h2>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {projects.map(project => (
          <ProjectCard key={project.id} project={project} />
        ))}
      </div>
    </div>
  );
};

export default ProjectsOverview;