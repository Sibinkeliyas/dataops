import React from 'react';
import { useParams } from 'react-router-dom';
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { useQuery } from '@tanstack/react-query';
import { fetchProjectDetails } from '../../utils/dataFetching.jsx';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, LineChart, Line } from 'recharts';

const ProjectDetail = () => {
  const { id } = useParams();
  const { data: project, isLoading, error } = useQuery({
    queryKey: ['projectDetails', id],
    queryFn: () => fetchProjectDetails(id),
  });

  if (isLoading) return <div>Loading project details...</div>;
  if (error) return <div>Error loading project details: {error.message}</div>;

  return (
    <div>
      <h2 className="text-2xl font-bold mb-4">{project.name}</h2>
      <Badge variant={project.status === 'Deployed' ? 'success' : project.status === 'Needs Attention' ? 'warning' : 'default'}>
        {project.status}
      </Badge>

      <Tabs defaultValue="overview" className="mt-6">
        <TabsList>
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="performance">Performance</TabsTrigger>
          <TabsTrigger value="versions">Versions</TabsTrigger>
        </TabsList>

        <TabsContent value="overview">
          <Card>
            <CardHeader>
              <CardTitle>Project Overview</CardTitle>
            </CardHeader>
            <CardContent>
              <p><strong>Description:</strong> {project.description}</p>
              <p><strong>Algorithm:</strong> {project.algorithm}</p>
              <p><strong>Datasets:</strong></p>
              <ul className="list-disc list-inside">
                {project.datasets.map((dataset, index) => (
                  <li key={index}>{dataset}</li>
                ))}
              </ul>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="performance">
          <Card>
            <CardHeader>
              <CardTitle>Performance Metrics</CardTitle>
            </CardHeader>
            <CardContent>
              <p><strong>Model Accuracy:</strong> {project.accuracy}%</p>
              <div className="h-64 mt-4">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={project.confusionMatrix}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="name" />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Bar dataKey="truePositive" fill="#8884d8" />
                    <Bar dataKey="falsePositive" fill="#82ca9d" />
                  </BarChart>
                </ResponsiveContainer>
              </div>
              <div className="h-64 mt-8">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={project.rocCurve}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="fpr" />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Line type="monotone" dataKey="tpr" stroke="#8884d8" />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="versions">
          <Card>
            <CardHeader>
              <CardTitle>Model Versions</CardTitle>
            </CardHeader>
            <CardContent>
              {project.versions.map((version, index) => (
                <div key={index} className="mb-4 p-4 border rounded">
                  <h4 className="font-semibold">Version {version.number}</h4>
                  <p>Created: {version.dateCreated}</p>
                  <p>Changes: {version.changeSummary}</p>
                  <div className="mt-2">
                    <Button size="sm" variant="outline" className="mr-2">Rollback</Button>
                    <Button size="sm" variant="outline">Compare</Button>
                  </div>
                </div>
              ))}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default ProjectDetail;