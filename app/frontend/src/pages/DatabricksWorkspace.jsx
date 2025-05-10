import React, { useState } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { AlertCircle, CheckCircle, AlertTriangle } from 'lucide-react';

const DatabricksWorkspace = () => {
  const [clusterStatus, setClusterStatus] = useState('stopped');
  const [clusterMetrics, setClusterMetrics] = useState({
    cpuUtilization: 0,
    memoryUsage: 0,
    activeJobs: 0,
  });

  const handleStartCluster = () => {
    setClusterStatus('running');
    setClusterMetrics({
      cpuUtilization: 30,
      memoryUsage: 40,
      activeJobs: 2,
    });
  };

  const handleStopCluster = () => {
    setClusterStatus('stopped');
    setClusterMetrics({
      cpuUtilization: 0,
      memoryUsage: 0,
      activeJobs: 0,
    });
  };

  const getStatusIcon = () => {
    switch (clusterStatus) {
      case 'running':
        return <CheckCircle className="text-green-500" />;
      case 'stopped':
        return <AlertCircle className="text-red-500" />;
      case 'scaling':
        return <AlertTriangle className="text-yellow-500" />;
      default:
        return null;
    }
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-6">Databricks Workspace</h1>
      
      <Card className="mb-8">
        <CardHeader>
          <CardTitle className="flex items-center">
            Workspace Launcher
          </CardTitle>
        </CardHeader>
        <CardContent>
          <Button className="w-full mb-4">Open Databricks Workspace</Button>
          <p className="text-sm text-gray-500">Access the Databricks environment for advanced data engineering tasks.</p>
        </CardContent>
      </Card>

      <Card className="mb-8">
        <CardHeader>
          <CardTitle className="flex items-center">
            Cluster Status {getStatusIcon()}
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="mb-4">Current Status: {clusterStatus.charAt(0).toUpperCase() + clusterStatus.slice(1)}</p>
          <div className="grid grid-cols-3 gap-4 mb-4">
            <div>
              <p className="font-semibold">CPU Utilization</p>
              <p>{clusterMetrics.cpuUtilization}%</p>
            </div>
            <div>
              <p className="font-semibold">Memory Usage</p>
              <p>{clusterMetrics.memoryUsage}%</p>
            </div>
            <div>
              <p className="font-semibold">Active Jobs</p>
              <p>{clusterMetrics.activeJobs}</p>
            </div>
          </div>
          <div className="flex space-x-4">
            <Button onClick={handleStartCluster} disabled={clusterStatus === 'running'}>Start Cluster</Button>
            <Button onClick={handleStopCluster} disabled={clusterStatus === 'stopped'}>Stop Cluster</Button>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Configure Cluster</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="mb-4">Adjust cluster settings to optimize performance and resource allocation.</p>
          <Button>Open Configuration Dialog</Button>
        </CardContent>
      </Card>
    </div>
  );
};

export default DatabricksWorkspace;