import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { CheckCircle, AlertTriangle, XCircle } from 'lucide-react';
import { useQuery } from '@tanstack/react-query';
import { fetchPipelines } from '../../utils/dataFetching';

const PipelineMonitoring = () => {
  const { data: pipelines, isLoading, error } = useQuery({
    queryKey: ['pipelines'],
    queryFn: fetchPipelines,
  });

  const [selectedPipeline, setSelectedPipeline] = useState(null);

  const getStatusIcon = (status) => {
    switch (status.toLowerCase()) {
      case 'operational':
        return <CheckCircle className="text-green-500" />;
      case 'warning':
        return <AlertTriangle className="text-yellow-500" />;
      case 'issue':
        return <XCircle className="text-red-500" />;
      default:
        return null;
    }
  };

  const handlePipelineClick = (pipeline) => {
    setSelectedPipeline(pipeline);
  };

  if (isLoading) return <div>Loading pipeline data...</div>;
  if (error) return <div>Error loading pipeline data: {error.message}</div>;

  return (
    <div>
      <h2 className="text-2xl font-bold mb-4">Pipeline Monitoring</h2>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-8">
        {pipelines.map((pipeline) => (
          <Card key={pipeline.id} className="cursor-pointer hover:shadow-lg transition-shadow" onClick={() => handlePipelineClick(pipeline)}>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">
                {pipeline.name}
              </CardTitle>
              {getStatusIcon(pipeline.status)}
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{pipeline.status}</div>
              <p className="text-xs text-muted-foreground">
                Last run: {pipeline.lastRun}
              </p>
              <p className="text-xs text-muted-foreground">
                Success Rate: {pipeline.successRate}
              </p>
              <p className="text-xs text-muted-foreground">
                Avg. Duration: {pipeline.avgDuration}
              </p>
            </CardContent>
          </Card>
        ))}
      </div>

      {selectedPipeline && (
        <Card>
          <CardHeader>
            <CardTitle>{selectedPipeline.name} Details</CardTitle>
          </CardHeader>
          <CardContent>
            <h3 className="font-semibold mb-2">Pipeline Information</h3>
            <ul className="list-disc list-inside mb-4">
              <li>Status: {selectedPipeline.status}</li>
              <li>Last Run: {selectedPipeline.lastRun}</li>
              <li>Success Rate: {selectedPipeline.successRate}</li>
              <li>Average Duration: {selectedPipeline.avgDuration}</li>
            </ul>

            <h3 className="font-semibold mb-2">Recent Runs</h3>
            <ul className="list-disc list-inside mb-4">
              <li>2023-03-24 04:00 PM - Completed successfully</li>
              <li>2023-03-23 09:30 AM - Completed with warnings</li>
              <li>2023-03-22 11:00 AM - Failed</li>
            </ul>

            <h3 className="font-semibold mb-2">Error Logs</h3>
            <pre className="bg-gray-100 p-2 rounded mb-4">
              {`Error: Connection timeout
at DataSource.connect (datasource.js:42:15)
at Pipeline.run (pipeline.js:23:10)
at runPipeline (scheduler.js:56:22)`}
            </pre>

            <div className="flex space-x-2">
              <Button>Start</Button>
              <Button>Stop</Button>
              <Button>Rerun</Button>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default PipelineMonitoring;