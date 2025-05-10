import React from 'react';
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { useQuery } from '@tanstack/react-query';
import { fetchDatabricksModels } from '../../utils/dataFetching';
import { Database, ExternalLink, Download } from 'lucide-react';

const DatabricksIntegration = () => {
  const { data: models, isLoading, error } = useQuery({
    queryKey: ['databricksModels'],
    queryFn: fetchDatabricksModels,
  });

  if (isLoading) return <div>Loading Databricks models...</div>;
  if (error) return <div>Error loading Databricks models: {error.message}</div>;

  return (
    <div>
      <h2 className="text-2xl font-bold mb-4">Databricks Integration</h2>
      <p className="mb-6">Manage and import models developed in Databricks for use in Azure AI Studio projects.</p>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {models.map(model => (
          <Card key={model.id}>
            <CardHeader>
              <CardTitle className="flex items-center justify-between">
                <span>{model.name}</span>
                <Badge>{model.type}</Badge>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-gray-600 mb-2">Version: {model.version}</p>
              <p className="text-sm text-gray-600 mb-4">Last Updated: {model.lastUpdated}</p>
              <div className="flex space-x-2">
                <Button size="sm" onClick={() => window.open(model.databricksUrl, '_blank')}>
                  <ExternalLink className="w-4 h-4 mr-2" />
                  View in Databricks
                </Button>
                <Button size="sm" variant="outline">
                  <Download className="w-4 h-4 mr-2" />
                  Import Model
                </Button>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      <Card className="mt-8">
        <CardHeader>
          <CardTitle>Documentation</CardTitle>
        </CardHeader>
        <CardContent>
          <h3 className="text-lg font-semibold mb-2">Using Databricks Models in Azure AI Studio</h3>
          <ol className="list-decimal list-inside space-y-2">
            <li>Select the Databricks model you want to use from the list above.</li>
            <li>Click "Import Model" to bring the model into Azure AI Studio.</li>
            <li>In Azure AI Studio, navigate to your project and select "Add Model".</li>
            <li>Choose the imported Databricks model from the list of available models.</li>
            <li>Configure any necessary parameters or settings for the model.</li>
            <li>Deploy the model or incorporate it into your existing AI workflow.</li>
          </ol>
          <p className="mt-4">For more detailed instructions, please refer to the <a href="#" className="text-blue-500 hover:underline">Databricks Integration Guide</a>.</p>
        </CardContent>
      </Card>
    </div>
  );
};

export default DatabricksIntegration;